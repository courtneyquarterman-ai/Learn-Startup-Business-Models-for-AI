# AI-use log

This log records how AI was used to build Hybrid Skills Verifier. It is separate from the AI feature inside the product (see `ai_assist.py` and `docs/prd.md`, "Role of AI").

Tool used for development: Perplexity Computer (AI assistant and coding agent).

| Date | What AI did | What the student did |
|---|---|---|
| Oct 13, 2026 | Proposed the product idea and working name "Hybrid Skills Verifier" from the student's quantum practitioner concept; drafted a one-pager and invention disclosure text. | Supplied the concept, asked for clarification and revisions, chose the direction. |
| Oct 27, 2026 | Drafted check-in posts (problem statement, customer description) and updated the Business Model Canvas slides using the student's customer discovery conversations. | Ran the customer discovery conversations, supplied the assignment prompts, reviewed and edited drafts. |
| Nov 10, 2026 | Drafted the PRD, implementation plan, `verifier.py`, automated tests, verification record, reviewer session guide, and a learner explanation draft. Reran the supplied notebook to confirm its saved results. | Supplied the Quantum BLOOM hackathon notebook and the assignment requirements; uploaded the files to GitHub. |
| Nov 17, 2026 | Restored the repository folder structure so the README commands and tests work; drafted `explanation.txt`; added the AI review assistant (`ai_assist.py`, `suggest` command, side-by-side report), 7 new tests, `requirements.txt`, and this log; updated the README, PRD, plan, verification record, user test, and session guide. | Ran the tool, reviewed and approved the learner explanation wording, decided to add an AI feature to the product, approved each change pushed to GitHub. |
| Nov 17, 2026 (later) | Switched the product's AI to a free open-source model (Qwen2.5-1.5B-Instruct) that runs locally with no key; ran it three times on the real explanation, changed the prompts after each run, and recorded the results and their weaknesses. | Decided the product must use AI without any paid key or account. |

## Checks on AI-generated work
- All automated tests were run after each change (14 pass; see `evidence/automated-tests.txt`).
- Numbers in `explanation.txt` were taken from the notebook's saved outputs and checked against `evidence/rerun/breast_cancer_qml_results/three_model_baseline.csv`.
- The product's AI output was reviewed by the developer agent against the saved table; incorrect flags are recorded in `evidence/ai-suggestions-local-run.json`.
- The AI-generated code has not been independently reviewed by another person. The real user test is still pending.

## Limits
AI drafted most of the code and documents. The git history attributes commits to the student account with an AI co-author trailer. This log does not establish that the student independently wrote the code; it records how the work was produced.
