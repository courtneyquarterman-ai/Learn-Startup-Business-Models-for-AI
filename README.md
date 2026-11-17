# Hybrid Skills Verifier

A small local Python prototype that helps a human reviewer assess a learner's hybrid quantum-classical notebook. It inspects the saved notebook evidence, uses an AI assistant to suggest rubric scores and follow-up questions, and records the reviewer's own scores and decision. The AI suggests; the human decides.

It uses only Python 3's standard library, so nothing needs to be installed. The AI step needs an API key (see below). Everything else works without one. This version is a command-line application, not a hosted website.

## How it works

1. **Inspect** the notebook: code cells, saved errors, the saved quantum/classical comparison, and a SHA-256 fingerprint. The notebook is not executed.
2. **AI suggest** (optional): an AI model reads the learner explanation next to the saved evidence. For each rubric area it suggests a score with an exact quote from the learner, flags claims that may not match the evidence, and drafts 3 to 5 follow-up questions. The tool checks that every quote really appears in the learner text.
3. **Human review**: the reviewer enters their own scores, feedback, and decision. The report shows the AI suggestion beside each human score and where they agree or differ.

## Start here

Clone or download this repository, open a terminal in the project folder (`Learn-Startup-Business-Models-for-AI`), and run:

```sh
python verifier.py inspect samples/quantum_bloom.ipynb
```

Use `python3` if that is your Python command. The output lists code cells, saved execution errors, the saved quantum/classical comparison, and a fingerprint of the notebook. An empty error list means no errors were saved; it does not mean every cell was executed successfully.

The learner's explanation is in `explanation.txt`. It covers the preprocessing, quantum kernel, classical baseline, and what the results do and do not show.

## AI suggestions (optional)

Set one API key, then run `suggest`:

```sh
export OPENAI_API_KEY="your-key"        # or: export ANTHROPIC_API_KEY="your-key"
python verifier.py suggest samples/quantum_bloom.ipynb --explanation explanation.txt --output reports/ai-suggestions.json
```

In Colab, set the key with `import os; os.environ["OPENAI_API_KEY"] = "your-key"` (or use Colab Secrets) and add `!` before each command.

Optional settings: `HSV_MODEL` chooses the model (defaults: `gpt-4.1-mini` for OpenAI, `claude-sonnet-4-5` for Anthropic). `HSV_BASE_URL` points to another OpenAI-compatible service. To see exactly what will be sent to the AI before sending anything, add `--show-prompt`.

Privacy: the `suggest` step sends the learner explanation and the saved model comparison table to the chosen AI provider. Do not use it with explanations the learner has not agreed to share. Without `suggest`, nothing leaves your computer.

## Human review

The reviewer reads the explanation (and the AI suggestions, if used) and chooses their own scores, feedback, and decision. Replace the example values with their actual judgment:

```sh
python verifier.py review samples/quantum_bloom.ipynb --explanation explanation.txt --reviewer "Reviewer name" --feedback "Replace with actual reviewer feedback" --scores 1 1 1 --decision needs-revision --ai-suggestions reports/ai-suggestions.json --output reports/my-assessment
```

Leave out `--ai-suggestions ...` to review without AI. Open `reports/my-assessment.html` in your browser. The JSON beside it contains the same data. Reports stay on your computer. Running the same output prefix replaces the previous report, so use a different prefix for each review.

Scores are ordered: workflow explanation, classical comparison, limitations. Each is 0 (missing), 1 (partial), or 2 (clear). The reviewer explicitly selects `needs-revision` or `meets-prototype-rubric`. Neither the tool nor the AI certifies a learner. The tool refuses AI suggestions made for a different notebook or a different version of the explanation.

## Verify the application

```sh
python -m unittest discover -s tests -v
```

The AI tests use a simulated AI service, so no key or internet is needed. See `docs/verification.md` for requirement mapping and limits. `evidence/inspection.json` is an actual inspection of the sample. Automated checks do not replace a participant session.

## Rerunning the quantum experiment

This prototype does not execute notebooks. To verify the experiment separately, open the sample in Jupyter or Colab and run all cells in order; its setup cell installs missing dependencies. Review that cell first. The experiment was rerun sequentially during development; all 10 code cells completed. See `docs/notebook-rerun.md` for the method and limits, and `requirements.txt` for the optional packages.

## Project files

| File | Purpose |
|---|---|
| `verifier.py` | Inspect, suggest, and review commands; report generation |
| `ai_assist.py` | AI prompt, AI service connection, output checks, AI vs reviewer comparison |
| `explanation.txt` | Learner explanation |
| `requirements.txt` | Dependencies (none for the tool; optional ones for the notebook rerun) |
| `docs/prd.md` | Product requirements |
| `docs/plan.md` | Implementation plan |
| `docs/verification.md` | Verification report |
| `docs/user-test.md` | User test notes |
| `docs/ai-use-log.md` | AI-use log |
| `docs/reviewer-session-guide.md` | Script for a real reviewer session |
| `tests/` | Automated tests |
| `evidence/` | Test output, inspection, and notebook rerun records |

## What remains before submission
1. Run a real AI suggestion with your API key and check that the output makes sense.
2. Conduct the real session in `docs/user-test.md` and record actual observations.
3. Update the PRD based on that feedback, implement any necessary changes, and rerun tests.
4. Commit the changes, including the test notes. Submit the repository link.

## Development record
AI assistance was used to draft the documents, code, and automated tests, as the assignment permits. See `docs/ai-use-log.md`. The sample notebook was supplied by the student from the Quantum BLOOM IQ Hackathon. This is a prototype, not a completed user-tested product.
