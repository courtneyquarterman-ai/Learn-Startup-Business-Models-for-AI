# Hybrid Skills Verifier

A small local Python prototype that helps a human reviewer assess a learner's hybrid quantum-classical notebook. It inspects the saved notebook evidence, uses an AI assistant to suggest rubric scores and follow-up questions, and records the reviewer's own scores and decision. The AI suggests; the human decides.

The AI is free: by default it uses an open-source model (Qwen2.5-1.5B-Instruct) that runs on your own computer or in Google Colab. No API key, account, or payment is needed. The rest of the tool uses only Python 3's standard library. This version is a command-line application, not a hosted website.

## How it works

1. **Inspect** the notebook: code cells, saved errors, the saved quantum/classical comparison, and a SHA-256 fingerprint. The notebook is not executed.
2. **AI suggest**: an AI model reads the learner explanation (split into numbered sentences) next to the saved evidence. For each rubric area it suggests a score and points to the learner sentence that supports it, flags claims that may not match the evidence, and drafts 3 to 5 follow-up questions. The tool pulls the exact sentence from the learner text itself, so quotes cannot be invented, and marks any it cannot match.
3. **Human review**: the reviewer enters their own scores, feedback, and decision. The report shows the AI suggestion beside each human score and where they agree or differ.

## Start here

Clone or download this repository, open a terminal in the project folder (`Learn-Startup-Business-Models-for-AI`), and run:

```sh
python verifier.py inspect samples/quantum_bloom.ipynb
```

Use `python3` if that is your Python command. The output lists code cells, saved execution errors, the saved quantum/classical comparison, and a fingerprint of the notebook. An empty error list means no errors were saved; it does not mean every cell was executed successfully.

The learner's explanation is in `explanation.txt`. It covers the preprocessing, quantum kernel, classical baseline, and what the results do and do not show.

## AI suggestions (free, no key)

The free AI needs two packages that Google Colab already has: `transformers` and `torch`. On your own computer, run `pip install transformers torch` once. Then:

```sh
python verifier.py suggest samples/quantum_bloom.ipynb --explanation explanation.txt --output reports/ai-suggestions.json
```

The first run downloads the model once (about 3 GB). In Colab, choose Runtime > Change runtime type > T4 GPU (free) for a fast run. On a plain CPU it takes several minutes (about 7.5 minutes on 2 cores during development).

What to expect from the small free model: suggested scores and follow-up questions are usually reasonable, but the supporting sentences it picks can be poor matches and its flags are often wrong. Treat flags as prompts to check the saved table, never as findings. A real run is saved in `evidence/ai-suggestions-local-run.json` with a developer review of its quality. Add `!` before each command in Colab. To see exactly what the AI receives, add `--show-prompt`.

Privacy: with the free local model, the learner explanation stays on your computer or Colab session. Only the model download comes from Hugging Face.

Optional settings: `HSV_MODEL` chooses a different Hugging Face model (for example `Qwen/Qwen2.5-3B-Instruct` for better quality on a GPU). If you ever want a hosted model instead, set `OPENAI_API_KEY` (optional `HSV_BASE_URL`) or `ANTHROPIC_API_KEY`; the tool then uses that service and sends the explanation and comparison table to it.

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

The automated AI tests use a simulated AI, so no model download is needed. A real run with the free local model is recorded in `evidence/ai-suggestions-local-run.json`. See `docs/verification.md` for requirement mapping and limits. `evidence/inspection.json` is an actual inspection of the sample. Automated checks do not replace a participant session.

## Rerunning the quantum experiment

This prototype does not execute notebooks. To verify the experiment separately, open the sample in Jupyter or Colab and run all cells in order; its setup cell installs missing dependencies. Review that cell first. The experiment was rerun sequentially during development; all 10 code cells completed. See `docs/notebook-rerun.md` for the method and limits, and `requirements.txt` for the optional packages.

## Project files

| File | Purpose |
|---|---|
| `verifier.py` | Inspect, suggest, and review commands; report generation |
| `ai_assist.py` | AI prompt, free local model and optional hosted services, output checks, AI vs reviewer comparison |
| `explanation.txt` | Learner explanation |
| `requirements.txt` | Dependencies (free AI: transformers, torch; optional notebook rerun packages) |
| `docs/prd.md` | Product requirements |
| `docs/plan.md` | Implementation plan |
| `docs/verification.md` | Verification report |
| `docs/user-test.md` | User test notes |
| `docs/ai-use-log.md` | AI-use log |
| `final-submission/` | Final presentation (.pptx) and final project report (.pdf) |
| `docs/reviewer-session-guide.md` | Script for a real reviewer session |
| `tests/` | Automated tests |
| `evidence/` | Test output, inspection, and notebook rerun records |

## What remains before submission
1. Run the free AI suggestion yourself in Colab and check that the output makes sense.
2. Conduct the real session in `docs/user-test.md` and record actual observations.
3. Update the PRD based on that feedback, implement any necessary changes, and rerun tests.
4. Commit the changes, including the test notes. Submit the repository link.

## Development record
AI assistance was used to draft the documents, code, and automated tests, as the assignment permits. See `docs/ai-use-log.md`. The sample notebook was supplied by the student from the Quantum BLOOM IQ Hackathon. This is a prototype, not a completed user-tested product.
