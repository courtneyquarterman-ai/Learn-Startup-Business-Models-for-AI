"""Local notebook evidence inspector, AI review assistant, and human review report generator."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
from datetime import datetime, timezone
import ai_assist

LIMITATION = ('Notebook code was not executed. Saved outputs do not prove correctness '
              'or learner understanding. This is a human review record, not a credential.')


def inspect_notebook(path):
    raw = Path(path).read_bytes()
    nb = json.loads(raw)
    if not isinstance(nb, dict) or nb.get('nbformat') != 4 or not isinstance(nb.get('cells'), list):
        raise ValueError('Expected a version 4 notebook with a cells list.')
    code = []
    errors = []
    comparisons = []
    for i, cell in enumerate(nb['cells']):
        if not isinstance(cell, dict) or cell.get('cell_type') not in ('code', 'markdown', 'raw'):
            raise ValueError(f'Invalid notebook cell {i}.')
        if cell['cell_type'] != 'code':
            continue
        code.append(cell)
        outputs = cell.get('outputs', [])
        if not isinstance(outputs, list):
            raise ValueError(f'Invalid outputs in cell {i}.')
        for output in outputs:
            if not isinstance(output, dict):
                raise ValueError(f'Invalid output in cell {i}.')
            if output.get('output_type') == 'error':
                errors.append({'cell': i, 'error': str(output.get('ename', 'Error')),
                               'message': str(output.get('evalue', ''))})
            data = output.get('data', {})
            if not isinstance(data, dict):
                raise ValueError(f'Invalid output data in cell {i}.')
            text = data.get('text/plain', output.get('text', ''))
            if isinstance(text, list) and all(isinstance(v, str) for v in text):
                text = ''.join(text)
            if not isinstance(text, str):
                raise ValueError(f'Invalid output text in cell {i}.')
            if 'RBF SVM' in text and 'Quantum ZZ SVM' in text:
                comparisons.append({'cell': i, 'saved_text': text})
    return {'notebook': Path(path).name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'code_cells': len(code), 'saved_execution_errors': errors,
            'saved_model_comparisons': comparisons, 'limitation': LIMITATION}


def text_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def make_review(evidence, explanation, reviewer, feedback, scores, decision, ai=None):
    if not all(isinstance(t, str) and t.strip() for t in (explanation, reviewer, feedback)):
        raise ValueError('Explanation, reviewer, and feedback must be nonempty.')
    if len(scores) != 3 or any(type(s) is not int or s not in (0, 1, 2) for s in scores):
        raise ValueError('Provide three integer rubric scores, each 0 to 2.')
    if decision not in ('needs-revision', 'meets-prototype-rubric'):
        raise ValueError('Choose an explicit reviewer decision.')
    review = {'created_at': datetime.now(timezone.utc).isoformat(), 'evidence': evidence,
              'explanation': explanation, 'reviewer': reviewer, 'feedback': feedback,
              'rubric': dict(zip(('workflow', 'classical_comparison', 'limitations'), scores)),
              'decision': decision, 'decision_made_by': 'human reviewer'}
    if ai is not None:
        if ai.get('notebook_sha256') != evidence['sha256']:
            raise ValueError('AI suggestions were made for a different notebook.')
        if ai.get('explanation_sha256') != text_sha256(explanation):
            raise ValueError('AI suggestions were made for a different explanation. Run suggest again.')
        review['ai_assist'] = ai
        review['ai_vs_reviewer'] = ai_assist.compare(ai, scores)
    return review


def render_ai_section(review):
    ai, cmp = review.get('ai_assist'), review.get('ai_vs_reviewer')
    if not ai:
        return ''
    e = html.escape
    rows = ''.join(
        f'<tr><td>{e(k)}</td><td>{v["score"]}</td><td>{cmp["by_dimension"][k]["reviewer"]}</td>'
        f'<td>{"yes" if cmp["by_dimension"][k]["agreed"] else "no"}</td>'
        f'<td>{e(v["quote"]) or "(none)"}{"" if v["quote_found_in_explanation"] else " <b>[quote not found in explanation]</b>"}</td>'
        f'<td>{e(v["reason"])}</td></tr>' for k, v in ai['suggested_scores'].items())
    flags = ''.join(f'<li>{e(f["claim"])}: {e(f["issue"])}</li>' for f in ai['flags']) or '<li>None</li>'
    qs = ''.join(f'<li>{e(q)}</li>' for q in ai['follow_up_questions']) or '<li>None</li>'
    return (f'<h2>AI assistant suggestions</h2><p>{e(ai["notice"])} Model: {e(ai["provider"])} / {e(ai["model"])}. '
            f'Reviewer agreed on {cmp["agreed_count"]} of {cmp["total"]} scores.</p>'
            '<table><tr><th>Rubric area</th><th>AI</th><th>Reviewer</th><th>Agreed</th>'
            f'<th>Learner quote</th><th>AI reason</th></tr>{rows}</table>'
            f'<h3>Possible mismatches flagged by AI</h3><ul>{flags}</ul>'
            f'<h3>Suggested follow-up questions</h3><ol>{qs}</ol>')


def render_report(review):
    # All report data is rendered as escaped text, including notebook outputs.
    safe = html.escape(json.dumps(review, indent=2, ensure_ascii=False))
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Hybrid Skills Verifier assessment</title><style>'
            'body{max-width:900px;margin:40px auto;padding:0 24px;font:17px system-ui;'
            'color:#183037;background:#f5f8f7}h1{color:#125b56}'
            'pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:24px;'
            'border:1px solid #cbd9d6;border-radius:12px;font-size:14px;line-height:1.6}'
            'table{border-collapse:collapse;background:white;font-size:14px;width:100%}'
            'td,th{border:1px solid #cbd9d6;padding:8px;text-align:left;vertical-align:top}'
            '</style><h1>Hybrid Skills Verifier</h1><p>Notebook evidence and human assessment</p>'
            '<p>' + html.escape(LIMITATION) + '</p>'
            '<h2>Reviewer decision</h2><p>' + html.escape(review['decision']) + ' (decided by '
            + html.escape(review['reviewer']) + ')</p>' + render_ai_section(review)
            + '<h2>Full record</h2><pre>' + safe + '</pre></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('inspect')
    check.add_argument('notebook')
    hint = sub.add_parser('suggest', help='Ask the AI assistant for advisory scores and questions')
    hint.add_argument('notebook')
    hint.add_argument('--explanation', required=True, help='Path to learner-written text file')
    hint.add_argument('--output', default='reports/ai-suggestions.json', help='Where to save suggestions')
    hint.add_argument('--show-prompt', action='store_true', help='Print what would be sent to the AI and stop')
    review = sub.add_parser('review')
    review.add_argument('notebook')
    review.add_argument('--explanation', required=True, help='Path to learner-written text file')
    review.add_argument('--reviewer', required=True)
    review.add_argument('--feedback', required=True)
    review.add_argument('--scores', type=int, nargs=3, required=True)
    review.add_argument('--decision', choices=['needs-revision', 'meets-prototype-rubric'], required=True)
    review.add_argument('--output', default='reports/assessment', help='Output path prefix')
    review.add_argument('--ai-suggestions', help='Optional JSON file saved by the suggest command')
    args = parser.parse_args(argv)
    try:
        evidence = inspect_notebook(args.notebook)
        if args.command == 'inspect':
            print(json.dumps(evidence, indent=2, ensure_ascii=False))
        elif args.command == 'suggest':
            explanation = Path(args.explanation).read_text(encoding='utf-8')
            if args.show_prompt:
                print(ai_assist.SYSTEM_PROMPT + '\n\n' + ai_assist.build_prompt(evidence, explanation))
                return 0
            result = ai_assist.suggest(evidence, explanation)
            result['explanation_sha256'] = text_sha256(explanation)
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print(f'Saved {out}. These are suggestions only; the reviewer decides.')
        else:
            ai = None
            if args.ai_suggestions:
                ai = json.loads(Path(args.ai_suggestions).read_text(encoding='utf-8'))
            result = make_review(evidence, Path(args.explanation).read_text(encoding='utf-8'),
                                 args.reviewer, args.feedback, args.scores, args.decision, ai)
            base = Path(args.output)
            base.parent.mkdir(parents=True, exist_ok=True)
            Path(str(base) + '.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            Path(str(base) + '.html').write_text(render_report(result), encoding='utf-8')
            print(f'Saved {base}.json and {base}.html')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
