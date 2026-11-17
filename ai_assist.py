"""AI review assistant for Hybrid Skills Verifier.

The AI suggests rubric scores, flags claims that may not match the saved notebook
evidence, and drafts follow-up questions. It never makes the review decision.
Uses only Python's standard library. Requires an API key at run time:

    OPENAI_API_KEY     (optional HSV_MODEL, HSV_BASE_URL for compatible services)
    ANTHROPIC_API_KEY  (optional HSV_MODEL)
"""
import json
import os
import urllib.error
import urllib.request

RUBRIC = {
    'workflow': 'Explains preprocessing, the quantum feature map/kernel, and how the SVM uses it.',
    'classical_comparison': 'Compares quantum and classical models on matched inputs and reports results accurately.',
    'limitations': 'States what the results do not show (sample size, tuning, simulation, no quantum advantage claim).',
}
SCORE_MEANING = '0 = missing, 1 = partial, 2 = clear'
AI_NOTICE = ('AI suggestions are advisory. The human reviewer chooses every score and the decision. '
             'Quotes are checked against the learner text; numbers and reasoning still need human review.')

SYSTEM_PROMPT = (
    'You assist a human reviewer assessing a learner\'s written explanation of a hybrid '
    'quantum-classical notebook. You do not grade or certify. Base every judgment only on the '
    'learner explanation and the saved notebook evidence provided. Quote the learner exactly. '
    'Return JSON only, with this shape: '
    '{"suggested_scores": {"workflow": {"score": 0|1|2, "quote": "exact learner sentence or empty", '
    '"reason": "one sentence"}, "classical_comparison": {...}, "limitations": {...}}, '
    '"flags": [{"claim": "learner claim", "issue": "why it may not match the evidence"}], '
    '"follow_up_questions": ["3 to 5 questions based on this learner\'s own results"]}'
)


def build_prompt(evidence, explanation):
    saved = '\n\n'.join(c['saved_text'] for c in evidence.get('saved_model_comparisons', []))
    rubric = '\n'.join(f'- {k}: {v}' for k, v in RUBRIC.items())
    return (f'Rubric ({SCORE_MEANING}):\n{rubric}\n\n'
            f'Saved notebook evidence (not re-executed):\n'
            f'- Code cells: {evidence.get("code_cells")}\n'
            f'- Saved execution errors: {json.dumps(evidence.get("saved_execution_errors", []))}\n'
            f'- Saved model comparison table:\n{saved or "none found"}\n\n'
            f'Learner explanation:\n"""\n{explanation}\n"""')


def _post(url, headers, body, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', 'replace')[:300]
        raise ValueError(f'AI service returned HTTP {exc.code}: {detail}') from None
    except urllib.error.URLError as exc:
        raise ValueError(f'Could not reach AI service: {exc.reason}') from None


def call_model(system, user):
    """Send one request to the configured AI service and return (text, provider, model)."""
    if os.environ.get('OPENAI_API_KEY'):
        model = os.environ.get('HSV_MODEL', 'gpt-4.1-mini')
        base = os.environ.get('HSV_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
        data = _post(f'{base}/chat/completions',
                     {'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY']},
                     {'model': model, 'temperature': 0, 'response_format': {'type': 'json_object'},
                      'messages': [{'role': 'system', 'content': system},
                                   {'role': 'user', 'content': user}]})
        return data['choices'][0]['message']['content'], 'openai-compatible', model
    if os.environ.get('ANTHROPIC_API_KEY'):
        model = os.environ.get('HSV_MODEL', 'claude-sonnet-4-5')
        data = _post('https://api.anthropic.com/v1/messages',
                     {'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01'},
                     {'model': model, 'max_tokens': 1500, 'temperature': 0, 'system': system,
                      'messages': [{'role': 'user', 'content': user}]})
        text = ''.join(b.get('text', '') for b in data.get('content', []) if b.get('type') == 'text')
        return text, 'anthropic', model
    raise ValueError('No AI key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY, '
                     'or run the review without --ai-suggestions.')


def _parse_json(text):
    text = text.strip()
    if text.startswith('```'):
        text = text.strip('`')
        text = text[text.find('{'):]
    start, end = text.find('{'), text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('AI response did not contain JSON.')
    return json.loads(text[start:end + 1])


def _normalize(s):
    return ' '.join(s.replace('\u2019', "'").replace('\u2018', "'")
                    .replace('\u201c', '"').replace('\u201d', '"').split()).lower()


def validate_suggestions(raw, explanation):
    """Check the AI output's structure and verify that quotes appear in the learner text."""
    if not isinstance(raw, dict) or not isinstance(raw.get('suggested_scores'), dict):
        raise ValueError('AI response is missing suggested_scores.')
    learner = _normalize(explanation)
    scores = {}
    for key in RUBRIC:
        item = raw['suggested_scores'].get(key)
        if not isinstance(item, dict) or type(item.get('score')) is not int or item['score'] not in (0, 1, 2):
            raise ValueError(f'AI response has an invalid score for {key}.')
        quote = str(item.get('quote', '')).strip()
        scores[key] = {'score': item['score'], 'quote': quote,
                       'quote_found_in_explanation': bool(quote) and _normalize(quote) in learner,
                       'reason': str(item.get('reason', '')).strip()}
    flags = [{'claim': str(f.get('claim', '')), 'issue': str(f.get('issue', ''))}
             for f in raw.get('flags', []) if isinstance(f, dict)]
    questions = [str(q).strip() for q in raw.get('follow_up_questions', []) if str(q).strip()][:5]
    return {'suggested_scores': scores, 'flags': flags, 'follow_up_questions': questions}


def suggest(evidence, explanation, model_call=call_model):
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError('Explanation must be nonempty.')
    text, provider, model = model_call(SYSTEM_PROMPT, build_prompt(evidence, explanation))
    result = validate_suggestions(_parse_json(text), explanation)
    result.update(provider=provider, model=model, notice=AI_NOTICE,
                  notebook_sha256=evidence.get('sha256'))
    return result


def compare(ai, human_scores):
    """Show where the human reviewer agreed or disagreed with the AI suggestion."""
    rows = {}
    for key, human in zip(RUBRIC, human_scores):
        suggested = ai['suggested_scores'][key]['score']
        rows[key] = {'ai_suggested': suggested, 'reviewer': human, 'agreed': suggested == human}
    return {'by_dimension': rows, 'agreed_count': sum(r['agreed'] for r in rows.values()),
            'total': len(rows)}
