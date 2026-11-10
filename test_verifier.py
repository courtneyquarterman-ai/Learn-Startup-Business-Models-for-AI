import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from verifier import inspect_notebook, make_review, render_report, main

SAMPLE = Path(__file__).resolve().parents[1] / 'samples/quantum_bloom.ipynb'

class VerifierTests(unittest.TestCase):
    def test_sample_evidence(self):
        e = inspect_notebook(SAMPLE)
        self.assertEqual(e['code_cells'], 10)
        self.assertEqual(e['saved_execution_errors'], [])
        self.assertEqual(len(e['saved_model_comparisons']), 1)
        self.assertEqual(len(e['sha256']), 64)
        self.assertIn('not executed', e['limitation'])

    def test_review_validation(self):
        e = inspect_notebook(SAMPLE)
        for explanation, scores, decision in [('', [1,1,1], 'needs-revision'),
                ('text', [3,1,1], 'needs-revision'), ('text', [1,1], 'needs-revision'),
                ('text', [1,1,1], 'automatic-pass')]:
            with self.assertRaises(ValueError):
                make_review(e, explanation, 'Tester', 'Feedback', scores, decision)

    def test_escape(self):
        r = make_review(inspect_notebook(SAMPLE), '<script>alert(1)</script>',
                        'Tester', '<img src=x>', [1,1,1], 'needs-revision')
        page = render_report(r)
        self.assertNotIn('<script>', page)
        self.assertIn('&lt;script&gt;', page)

    def test_bad_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'bad.ipynb'
            for content in ('{', '{}', '{"nbformat":4,"cells":[null]}',
                            '{"nbformat":4,"cells":[{"cell_type":"code","outputs":[null]}]}'):
                path.write_text(content)
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(main(['inspect', str(path)]), 1)
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(['inspect', str(Path(d)/'missing')]), 1)

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            explanation = Path(d)/'explanation.txt'
            explanation.write_text('AUTOMATED TEST INPUT: workflow explanation placeholder.')
            base = Path(d)/'assessment'
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['review', str(SAMPLE), '--explanation', str(explanation),
                    '--reviewer', 'Automated test fixture', '--feedback', 'Test only',
                    '--scores', '1', '1', '0', '--decision', 'needs-revision', '--output', str(base)]), 0)
            r = json.loads(Path(str(base)+'.json').read_text())
            self.assertEqual(r['decision'], 'needs-revision')
            self.assertEqual(r['rubric']['limitations'], 0)
            self.assertIn(r['evidence']['sha256'], Path(str(base)+'.html').read_text())

if __name__ == '__main__':
    unittest.main()
