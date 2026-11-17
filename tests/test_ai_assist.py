import contextlib
import http.server
import io
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest import mock

import ai_assist
from verifier import inspect_notebook, main, make_review, render_report, text_sha256

SAMPLE = Path(__file__).resolve().parents[1] / 'samples/quantum_bloom.ipynb'
EXPLANATION = ('I held back 20% of the data as a test set. '
               'The quantum model caught 12 of 42 malignant tumors. '
               'Everything ran in simulation.')
GOOD = {'suggested_scores': {
            'workflow': {'score': 1, 'quote': 'I held back 20% of the data as a test set.', 'reason': 'Split only.'},
            'classical_comparison': {'score': 2, 'quote': 'The quantum model caught 12 of 42 malignant tumors.',
                                     'reason': 'Matches table.'},
            'limitations': {'score': 1, 'quote': 'This sentence is not in the text.', 'reason': 'Brief.'}},
        'flags': [{'claim': '12 of 42', 'issue': 'Consistent with 0.2857 recall.'}],
        'follow_up_questions': ['Why did the quantum model miss so many malignant tumors?']}


def fake_call(response):
    return lambda system, user: (json.dumps(response), 'test', 'fake-model')


class AIAssistTests(unittest.TestCase):
    def setUp(self):
        self.evidence = inspect_notebook(SAMPLE)

    def test_prompt_contains_evidence_and_explanation(self):
        prompt = ai_assist.build_prompt(self.evidence, EXPLANATION)
        self.assertIn('Quantum ZZ SVM', prompt)
        self.assertIn('12 of 42', prompt)

    def test_valid_suggestions_and_quote_check(self):
        result = ai_assist.suggest(self.evidence, EXPLANATION, fake_call(GOOD))
        s = result['suggested_scores']
        self.assertTrue(s['workflow']['quote_found_in_explanation'])
        self.assertFalse(s['limitations']['quote_found_in_explanation'])
        self.assertEqual(result['notebook_sha256'], self.evidence['sha256'])
        self.assertIn('advisory', result['notice'])

    def test_sentence_numbers_become_exact_quotes(self):
        r = json.loads(json.dumps(GOOD))
        r['suggested_scores']['limitations'] = {'score': 1, 'sentence': 'S3', 'reason': 'Brief.'}
        r['suggested_scores']['workflow'] = {'score': 1, 'sentence': 99, 'reason': 'Out of range.'}
        s = ai_assist.suggest(self.evidence, EXPLANATION, fake_call(r))['suggested_scores']
        self.assertEqual(s['limitations']['quote'], 'Everything ran in simulation.')
        self.assertTrue(s['limitations']['quote_found_in_explanation'])
        self.assertFalse(s['workflow']['quote_found_in_explanation'])
        self.assertIn('[S2] The quantum model caught 12 of 42', ai_assist.build_prompt(self.evidence, EXPLANATION))

    def test_unreadable_flags_do_not_block_scores(self):
        def call(system, user):
            if 'follow-up questions' in system or 'saved model comparison table and' in system or 'at most 3' in system:
                return 'broken {', 't', 'm'
            return json.dumps({'score': '2', 'sentence': 1}), 't', 'm'
        r = ai_assist.suggest(self.evidence, EXPLANATION, call)
        self.assertEqual(r['suggested_scores']['workflow']['score'], 2)
        self.assertEqual(r['flags'], [])
        self.assertEqual(len(r['ai_notes']), 2)

    def test_invalid_ai_scores_rejected(self):
        bad = json.loads(json.dumps(GOOD))
        bad['suggested_scores']['workflow']['score'] = 3
        with self.assertRaises(ValueError):
            ai_assist.suggest(self.evidence, EXPLANATION, fake_call(bad))
        with self.assertRaises(ValueError):
            ai_assist.suggest(self.evidence, EXPLANATION, lambda s, u: ('not json', 't', 'm'))

    def test_no_key_uses_free_local_model(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(ai_assist, 'call_local_model', return_value=('{}', 'local', 'm')) as local:
            self.assertEqual(ai_assist.call_model('s', 'u')[1], 'local')
        local.assert_called_once()

    def test_human_decides_and_agreement_recorded(self):
        ai = ai_assist.suggest(self.evidence, EXPLANATION, fake_call(GOOD))
        ai['explanation_sha256'] = text_sha256(EXPLANATION)
        review = make_review(self.evidence, EXPLANATION, 'Tester', 'Feedback', [1, 1, 1], 'needs-revision', ai)
        self.assertEqual(review['decision_made_by'], 'human reviewer')
        self.assertEqual(review['ai_vs_reviewer']['agreed_count'], 2)
        page = render_report(review)
        self.assertIn('quote not found', page)
        with self.assertRaises(ValueError):
            make_review(self.evidence, 'changed text', 'Tester', 'Feedback', [1, 1, 1], 'needs-revision', ai)

    def test_ai_text_is_escaped(self):
        evil = json.loads(json.dumps(GOOD))
        evil['follow_up_questions'] = ['<script>alert(1)</script>']
        ai = ai_assist.suggest(self.evidence, EXPLANATION, fake_call(evil))
        ai['explanation_sha256'] = text_sha256(EXPLANATION)
        page = render_report(make_review(self.evidence, EXPLANATION, 'T', 'F', [1, 1, 1], 'needs-revision', ai))
        self.assertNotIn('<script>', page)

    def test_end_to_end_with_simulated_openai_server(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                assert body['messages'][0]['role'] == 'system'
                out = json.dumps({'choices': [{'message': {'content': json.dumps(GOOD)}}]}).encode()
                self.send_response(200); self.send_header('Content-Type', 'application/json')
                self.end_headers(); self.wfile.write(out)
            def log_message(self, *a):
                pass
        server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = {'OPENAI_API_KEY': 'test-key', 'HSV_BASE_URL': f'http://127.0.0.1:{server.server_port}'}
        try:
            with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, env, clear=True):
                exp = Path(d) / 'explanation.txt'; exp.write_text(EXPLANATION, encoding='utf-8')
                sug = Path(d) / 'ai.json'; base = Path(d) / 'report'
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(['suggest', str(SAMPLE), '--explanation', str(exp),
                                           '--output', str(sug)]), 0)
                    self.assertEqual(main(['review', str(SAMPLE), '--explanation', str(exp),
                                           '--reviewer', 'Tester', '--feedback', 'Test', '--scores', '1', '2', '0',
                                           '--decision', 'needs-revision', '--ai-suggestions', str(sug),
                                           '--output', str(base)]), 0)
                report = json.loads(Path(str(base) + '.json').read_text())
                self.assertEqual(report['ai_vs_reviewer']['agreed_count'], 2)
                self.assertIn('AI assistant suggestions', Path(str(base) + '.html').read_text())
        finally:
            server.shutdown(); server.server_close()


if __name__ == '__main__':
    unittest.main()
