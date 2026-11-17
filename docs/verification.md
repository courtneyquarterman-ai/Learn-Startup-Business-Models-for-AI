# Verification record

Executed during prototype development on November 10, 2026. This records software verification, not a participant session or a fresh quantum experiment.

Command: `python -m unittest discover -s tests -v`
Result: 5 tests passed. Full captured output: `evidence/automated-tests.txt`.

| Requirement ID | Acceptance criterion | Result | Evidence |
|---|---|---|---|
| R1 | Extract counts, saved errors, comparison, and fingerprint | PASS | `test_sample_evidence`; `evidence/inspection.json`: 10 code cells, zero saved errors, one comparison, 64-character SHA-256 |
| R2 | Reject missing and malformed files with nonzero exit | PASS | `test_bad_inputs`: missing path, invalid JSON, missing notebook fields, invalid cell, and invalid output |
| R3 | Require review fields, three scores from 0 to 2, explicit decision | PASS with limited automated coverage | `test_review_validation` covers empty explanation, out-of-range scores, wrong score count, and unsupported decision. Required CLI arguments are enforced by argparse; blank reviewer/feedback are rejected by the shared validation function. |
| R4 | Export report data and escape HTML | PASS for automated assertions | `test_end_to_end` checks both files, decision, score, and matching fingerprint; `test_escape` checks escaped script text. Browser visual inspection has not been performed. |
| R5 | Sample completes inspection and review without extra dependencies | PASS | `test_end_to_end`; direct inspection stored in `evidence/inspection.json`; implementation imports only standard-library modules |
| R6 | Report explicitly limits interpretation | PASS | `test_sample_evidence` checks warning; report renderer includes the warning and full evidence record |

## Not verified
- Full independent numerical audit or quantum hardware behavior. The sample was executed sequentially; see the rerun record below.
- Real learner understanding, reviewer usefulness, time savings, or employer trust.
- Browser layout and usability with an actual participant.

## User test status
Pending. Follow `docs/user-test.md`. No participant feedback or PRD changes from a participant are claimed.

## Fresh notebook execution
PASS: all 10 code cells executed sequentially in one IPython process with the original assertions enabled and optional extensions disabled. The original notebook was preserved unchanged. The executed copy is `evidence/rerun/quantum_bloom.executed.ipynb`. Details and environment are in `docs/notebook-rerun.md`. This is developer verification, not a human user test.
