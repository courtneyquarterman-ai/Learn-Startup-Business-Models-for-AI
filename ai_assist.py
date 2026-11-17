"""AI review assistant for Hybrid Skills Verifier.

The AI suggests rubric scores, flags claims that may not match the saved notebook
evidence, and drafts follow-up questions. It never makes the review decision.
Two ways to run the AI:

    Free, no key (default): an open-source model runs on your own computer or in
    Google Colab through Hugging Face transformers. Needs `pip install transformers torch`
    (already installed in Colab). Default model: Qwen/Qwen2.5-1.5B-Instruct (Apache 2.0).
    Change it with HSV_MODEL.

    Hosted (optional, paid): set OPENAI_API_KEY (optional HSV_BASE_URL) or ANTHROPIC_API_KEY.
"""
import json
import os
import re
import urllib.error
import urllib.request

RUBRIC = {
    'workflow': 'Explains preprocessing, the quantum feature map/kernel, and how the SVM uses it.',
    'classical_comparison': 'Compares quantum and classical models on matched inputs and reports results accurately.',
    'limitations': 'States what the results do not show (sample size, tuning, simulation, no quantum advantage claim).',
}
SCORE_MEANING = '0 = missing, 1 = partial, 2 = clear'
AI_NOTICE = ('AI suggestions are advisory. The human reviewer chooses every score and the decision. '
             'Quotes are pulled from the learner text by the tool. AI flags are often wrong, especially '
             'with small free models: check each one against the saved table before acting on it.')

BASE_INSTRUCTIONS = (
    'You assist a human reviewer assessing a learner\'s written explanation of a hybrid '
    'quantum-classical notebook. You do not grade or certify. Base every judgment only on the '
    'learner explanation and the saved notebook evidence provided. The learner sentences are '
    'numbered [S1], [S2], ... Return JSON only, with no other text.'
)


def area_prompt(key):
    """One small task per rubric area works better with small free models."""
    return (BASE_INSTRUCTIONS + f'\n\nYour task: score ONE rubric area, "{key}": {RUBRIC[key]} '
            f'Scale: {SCORE_MEANING}. Read the learner sentences and decide how well THIS learner meets '
            'this one criterion. Return: {"score": <0, 1 or 2>, "sentence": <number of the one learner '
            'sentence that best supports your score, or 0 if none>, "reason": "<one sentence in your own words>"}')


FLAGS_PROMPT = (
    BASE_INSTRUCTIONS + '\n\nYour task: check only the learner sentences that contain numbers against the '
    'saved model comparison table. List at most 3 numbers or claims that do NOT match the table. If they all '
    'match, return an empty list. Return: {"flags": [{"claim": "<the learner claim>", "issue": "<what the '
    'table shows instead>"}]}'
)

QUESTIONS_PROMPT = (
    BASE_INSTRUCTIONS + '\n\nYour task: write 3 to 5 short follow-up questions a reviewer could ask this '
    'learner, in person, to check that they understand their own results and reasoning. Return: '
    '{"follow_up_questions": ["<question>", "<question>", "<question>"]}'
)

SYSTEM_PROMPT = '\n\n---\n\n'.join([area_prompt(k) for k in RUBRIC] + [FLAGS_PROMPT, QUESTIONS_PROMPT])


def split_sentences(text):
    """Split learner text into numbered sentences (bullets and lines count as sentences)."""
    parts = []
    for line in text.splitlines():
        line = line.strip().lstrip('-*').strip()
        if line:
            pieces = [p.strip() for p in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9(])', line) if p.strip()]
            for piece in pieces:   # keep headings like "1. The workflow" together
                if parts and re.fullmatch(r'\d+[.)]', parts[-1]):
                    parts[-1] += ' ' + piece
                else:
                    parts.append(piece)
    return parts


def build_prompt(evidence, explanation):
    saved = '\n\n'.join(c['saved_text'] for c in evidence.get('saved_model_comparisons', []))
    rubric = '\n'.join(f'- {k}: {v}' for k, v in RUBRIC.items())
    return (f'Rubric ({SCORE_MEANING}):\n{rubric}\n\n'
            f'Saved notebook evidence (not re-executed):\n'
            f'- Code cells: {evidence.get("code_cells")}\n'
            f'- Saved execution errors: {json.dumps(evidence.get("saved_execution_errors", []))}\n'
            f'- Saved model comparison table:\n{saved or "none found"}\n\n'
            'Learner explanation (numbered sentences):\n'
            + '\n'.join(f'[S{i}] {t}' for i, t in enumerate(split_sentences(explanation), 1)))


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


LOCAL_DEFAULT_MODEL = 'Qwen/Qwen2.5-1.5B-Instruct'
_local_cache = {}


def call_local_model(system, user):
    """Run a free open-source model on this machine. No key, no account, nothing sent online
    except the one-time model download from Hugging Face."""
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        raise ValueError('The free local AI needs two packages. Run: pip install transformers torch '
                         '(already installed in Google Colab).') from None
    name = os.environ.get('HSV_MODEL', LOCAL_DEFAULT_MODEL)
    if name not in _local_cache:
        tok = AutoTokenizer.from_pretrained(name)
        dtype = torch.float16 if torch.cuda.is_available() else torch.bfloat16
        model = AutoModelForCausalLM.from_pretrained(name, dtype=dtype)
        model.to('cuda' if torch.cuda.is_available() else 'cpu').eval()
        _local_cache[name] = (tok, model)
    tok, model = _local_cache[name]
    messages = [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}]
    inputs = tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors='pt',
                                     return_dict=True).to(model.device)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=400, do_sample=False,
                             pad_token_id=tok.eos_token_id)
    text = tok.decode(out[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return text, 'local (Hugging Face transformers)', name


def call_model(system, user):
    """Send one request to the configured AI and return (text, provider, model).
    Uses a hosted service only if its key is set; otherwise the free local model."""
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
    return call_local_model(system, user)


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
    sentences = split_sentences(explanation)
    scores = {}
    for key in RUBRIC:
        item = raw['suggested_scores'].get(key)
        if isinstance(item, (int, str)) and not isinstance(item, bool):   # small models sometimes return just a score
            item = {'score': item}
        if isinstance(item, dict) and isinstance(item.get('score'), str) and item['score'].strip().isdigit():
            item['score'] = int(item['score'].strip())
        if not isinstance(item, dict) or type(item.get('score')) is not int or item['score'] not in (0, 1, 2):
            raise ValueError(f'AI response has an invalid score for {key}.')
        number = item.get('sentence')
        if isinstance(number, str) and number.strip().upper().lstrip('S').isdigit():
            number = int(number.strip().upper().lstrip('S'))
        if type(number) is int and 1 <= number <= len(sentences):
            quote = sentences[number - 1]   # pulled from the learner text by the tool, not the AI
        else:
            quote = str(item.get('quote', '')).strip()
        scores[key] = {'score': item['score'], 'quote': quote,
                       'quote_found_in_explanation': bool(quote) and _normalize(quote) in learner,
                       'reason': str(item.get('reason', '')).strip() or '(AI gave no reason)'}
    flags = [{'claim': str(f.get('claim', '')), 'issue': str(f.get('issue', ''))}
             for f in raw.get('flags', []) if isinstance(f, dict)]
    questions = [str(q).strip() for q in raw.get('follow_up_questions', []) if str(q).strip()][:5]
    return {'suggested_scores': scores, 'flags': flags, 'follow_up_questions': questions}


def suggest(evidence, explanation, model_call=call_model):
    if not isinstance(explanation, str) or not explanation.strip():
        raise ValueError('Explanation must be nonempty.')
    user = build_prompt(evidence, explanation)
    raw, provider, model = {'suggested_scores': {}}, None, None
    for key in RUBRIC:
        text, provider, model = model_call(area_prompt(key), user)
        item = _parse_json(text)
        if isinstance(item.get('suggested_scores'), dict):   # model answered for all areas at once
            item = item['suggested_scores'].get(key, {})
        elif key in item and 'score' not in item:
            item = item[key]
        raw['suggested_scores'][key] = item
    notes = []
    for field, prompt in (('flags', FLAGS_PROMPT), ('follow_up_questions', QUESTIONS_PROMPT)):
        text, provider, model = model_call(prompt, user)
        try:
            value = _parse_json(text).get(field, [])
        except ValueError:          # includes JSON errors; scores above are still usable
            value = None
        if not isinstance(value, list):
            value = []
            notes.append(f'The AI response for {field} could not be read, so none are shown.')
        raw[field] = value
    result = validate_suggestions(raw, explanation)
    result['flags'] = result['flags'][:3]
    if notes:
        result['ai_notes'] = notes
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
