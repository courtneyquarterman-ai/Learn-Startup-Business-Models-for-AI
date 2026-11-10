"""Local notebook evidence inspector and human review report generator."""
import argparse
import hashlib
import html
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

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


def make_review(evidence, explanation, reviewer, feedback, scores, decision):
    if not all(isinstance(t, str) and t.strip() for t in (explanation, reviewer, feedback)):
        raise ValueError('Explanation, reviewer, and feedback must be nonempty.')
    if len(scores) != 3 or any(type(s) is not int or s not in (0, 1, 2) for s in scores):
        raise ValueError('Provide three integer rubric scores, each 0 to 2.')
    if decision not in ('needs-revision', 'meets-prototype-rubric'):
        raise ValueError('Choose an explicit reviewer decision.')
    return {'created_at': datetime.now(timezone.utc).isoformat(), 'evidence': evidence,
            'explanation': explanation, 'reviewer': reviewer, 'feedback': feedback,
            'rubric': dict(zip(('workflow', 'classical_comparison', 'limitations'), scores)),
            'decision': decision}


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
            '</style><h1>Hybrid Skills Verifier</h1><p>Notebook evidence and human assessment</p>'
            '<p>' + html.escape(LIMITATION) + '</p><pre>' + safe + '</pre></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    check = sub.add_parser('inspect')
    check.add_argument('notebook')
    review = sub.add_parser('review')
    review.add_argument('notebook')
    review.add_argument('--explanation', required=True, help='Path to learner-written text file')
    review.add_argument('--reviewer', required=True)
    review.add_argument('--feedback', required=True)
    review.add_argument('--scores', type=int, nargs=3, required=True)
    review.add_argument('--decision', choices=['needs-revision', 'meets-prototype-rubric'], required=True)
    review.add_argument('--output', default='reports/assessment', help='Output path prefix')
    args = parser.parse_args(argv)
    try:
        evidence = inspect_notebook(args.notebook)
        if args.command == 'inspect':
            print(json.dumps(evidence, indent=2, ensure_ascii=False))
        else:
            result = make_review(evidence, Path(args.explanation).read_text(encoding='utf-8'),
                                 args.reviewer, args.feedback, args.scores, args.decision)
            base = Path(args.output)
            base.parent.mkdir(parents=True, exist_ok=True)
            Path(str(base) + '.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
            Path(str(base) + '.html').write_text(render_report(result), encoding='utf-8')
            print(f'Saved {base}.json and {base}.html')
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
