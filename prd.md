# Hybrid Skills Verifier: first version

Status: implemented prototype; external user test pending.

## Problem and user
An instructor needs a clear record of a learner's hybrid quantum-classical work. A notebook contains code and outputs, but the reviewer still needs to inspect the evidence and assess the explanation.

## Scope and journey
This version is a local Python command-line tool. The reviewer inspects the supplied Quantum BLOOM notebook, reads a learner explanation, enters rubric scores and feedback, and exports JSON and HTML reports. Saved notebook evidence is explicitly distinguished from a fresh execution. It does not issue credentials or execute uploaded code.

## Riskiest assumption
A structured evidence report helps an instructor judge the learner's skills. Test with one instructor or advanced quantum student. Initial success threshold: they can locate the classical comparison and explain the evidence limitations within five minutes, and rate the report's usefulness at least 4/5. This threshold is a hypothesis, not a result.

## Requirements
| ID | Acceptance criterion |
|---|---|
| R1 | Inspect a valid notebook and list its code-cell count, saved execution errors, saved model comparison text, and SHA-256 fingerprint. |
| R2 | Reject malformed JSON, invalid notebook cells, and missing input files with a readable error and nonzero exit. |
| R3 | Require a learner explanation, reviewer name, feedback, three integer scores from 0 to 2, and an explicit reviewer decision. |
| R4 | Export HTML and JSON containing the checks, notebook fingerprint, explanation, rubric scores, reviewer feedback, decision, and evidence limitation. Escape user text in HTML. |
| R5 | The included sample can complete inspection and review using only Python's standard library. |
| R6 | Every report states that notebook code was not executed and saved outputs do not prove correctness or learner understanding. |

## Rubric
Each dimension receives 0 (missing), 1 (partial), or 2 (clear): workflow explanation; classical comparison; limitations and errors. Scores support human judgment. They never automatically award a credential. Decisions: needs-revision or meets-prototype-rubric.

## Outside this version
Arbitrary code execution, identity checks, unseen assessment tasks, credentials, multi-user accounts, quantum hardware, and clinical use. The sample is an educational classifier experiment, not a diagnostic product.

## Changes from user testing
None yet. Complete docs/user-test.md after a real session, then update this section with the observation, requirement change, and reason.
