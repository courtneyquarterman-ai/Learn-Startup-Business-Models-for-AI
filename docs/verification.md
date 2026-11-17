# Verification record

Executed during prototype development on November 10, 2026. This records software verification, not a participant session or a fresh quantum experiment.

Command: `python -m unittest discover -s tests -v`
Result: 14 tests passed (5 core, 9 AI assistant). Full captured output: `evidence/automated-tests.txt`.

| Requirement ID | Acceptance criterion | Result | Evidence |
|---|---|---|---|
| R1 | Extract counts, saved errors, comparison, and fingerprint | PASS | `test_sample_evidence`; `evidence/inspection.json`: 10 code cells, zero saved errors, one comparison, 64-character SHA-256 |
| R2 | Reject missing and malformed files with nonzero exit | PASS | `test_bad_inputs`: missing path, invalid JSON, missing notebook fields, invalid cell, and invalid output |
| R3 | Require review fields, three scores from 0 to 2, explicit decision | PASS with limited automated coverage | `test_review_validation` covers empty explanation, out-of-range scores, wrong score count, and unsupported decision. Required CLI arguments are enforced by argparse; blank reviewer/feedback are rejected by the shared validation function. |
| R4 | Export report data and escape HTML | PASS for automated assertions | `test_end_to_end` checks both files, decision, score, and matching fingerprint; `test_escape` checks escaped script text. Browser visual inspection has not been performed. |
| R5 | Sample completes inspection and review without extra dependencies | PASS | `test_end_to_end`; direct inspection stored in `evidence/inspection.json`; implementation imports only standard-library modules |
| R6 | Report explicitly limits interpretation | PASS | `test_sample_evidence` checks warning; report renderer includes the warning and full evidence record |
| R7 | AI suggest returns scores, quotes, reasons, flags, questions; free local model by default | PASS | Real run with the free local model Qwen2.5-1.5B-Instruct on CPU: `evidence/ai-suggestions-local-run.json`. Automated: `test_no_key_uses_free_local_model`; `test_end_to_end_with_simulated_openai_server` (hosted path via a local OpenAI-style test server); `test_prompt_contains_evidence_and_explanation`. |
| R8 | Reject malformed AI output; quotes come from numbered learner sentences | PASS | `test_invalid_ai_scores_rejected` (score 3, non-JSON); `test_valid_suggestions_and_quote_check`; `test_sentence_numbers_become_exact_quotes` |
| R9 | Human enters scores and decision; AI and human shown side by side | PASS | `test_human_decides_and_agreement_recorded` checks `decision_made_by` and agreement count; `test_end_to_end_with_simulated_openai_server` checks the HTML section |
| R10 | Refuse mismatched suggestions; escape AI text; show prompt option | PASS for automated assertions | `test_human_decides_and_agreement_recorded` rejects a changed explanation; `test_ai_text_is_escaped`. `--show-prompt` checked manually during development. |

## Not verified
- AI suggestion quality. One real run with a small free model shows the feature works end to end, but its chosen quotes were often weak and all 3 flags were incorrect (see `evidence/ai-suggestions-local-run.json`). It does not show the suggestions are accurate or useful to reviewers. Hosted OpenAI and Anthropic paths have not been run against the real services.
- Full independent numerical audit or quantum hardware behavior. The sample was executed sequentially; see the rerun record below.
- Real learner understanding, reviewer usefulness, time savings, or employer trust.
- Browser layout and usability with an actual participant.

## User test status
Pending. Follow `docs/user-test.md`. No participant feedback or PRD changes from a participant are claimed.

## Fresh notebook execution
PASS: all 10 code cells executed sequentially in one IPython process with the original assertions enabled and optional extensions disabled. The original notebook was preserved unchanged. The executed copy is `evidence/rerun/quantum_bloom.executed.ipynb`. Details and environment are in `docs/notebook-rerun.md`. This is developer verification, not a human user test.
