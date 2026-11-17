# Hybrid Skills Verifier: second version

Status: implemented prototype with AI review assistant; real AI run and external user test pending.

## Problem and user
An instructor needs a clear record of a learner's hybrid quantum-classical work. A notebook contains code and outputs, but the reviewer still needs to inspect the evidence and assess the explanation.

## Scope and journey
This version is a local Python command-line tool. The reviewer inspects the supplied Quantum BLOOM notebook, optionally asks an AI assistant for suggested rubric scores, flagged claims and follow-up questions, reads the learner explanation, enters their own rubric scores and feedback, and exports JSON and HTML reports that show AI suggestions beside the human scores. Saved notebook evidence is explicitly distinguished from a fresh execution. It does not issue credentials or execute uploaded code.

## Riskiest assumption
A structured evidence report helps an instructor judge the learner's skills. Test with one instructor or advanced quantum student. Initial success threshold: they can locate the classical comparison and explain the evidence limitations within five minutes, and rate the report's usefulness at least 4/5. This threshold is a hypothesis, not a result.

Second assumption (AI): AI suggestions with exact learner quotes save the reviewer time and point to the right evidence, without the reviewer simply copying them. Test by recording reviewer agreement with each AI score, whether the reviewer changed any score after reading the AI reason, and whether the follow-up questions were useful (1 to 5). These are hypotheses, not results.

## Role of AI
The AI reads unstructured learner writing alongside the saved notebook evidence, which fixed rules cannot do well. It suggests a score for each rubric area with an exact supporting quote, flags claims that may not match the evidence, and drafts follow-up questions specific to this learner's results. It never chooses the final scores or decision.

## Requirements
| ID | Acceptance criterion |
|---|---|
| R1 | Inspect a valid notebook and list its code-cell count, saved execution errors, saved model comparison text, and SHA-256 fingerprint. |
| R2 | Reject malformed JSON, invalid notebook cells, and missing input files with a readable error and nonzero exit. |
| R3 | Require a learner explanation, reviewer name, feedback, three integer scores from 0 to 2, and an explicit reviewer decision. |
| R4 | Export HTML and JSON containing the checks, notebook fingerprint, explanation, rubric scores, reviewer feedback, decision, and evidence limitation. Escape user text in HTML. |
| R5 | The included sample can complete inspection and review using only Python's standard library. |
| R6 | Every report states that notebook code was not executed and saved outputs do not prove correctness or learner understanding. |
| R7 | The suggest command runs a free open-source model locally by default (no key or payment), or a hosted service if a key is set, and returns a suggested 0-2 score, quote and reason per rubric area, flagged claims, and up to five follow-up questions. Missing AI packages give a readable install message. |
| R8 | Reject AI output that is not JSON or has missing or out-of-range scores. Number learner sentences so the AI cites a sentence; the tool pulls the quote from the learner text and marks any citation it cannot match. |
| R9 | The reviewer always enters their own scores and decision. Reports record the decision as made by the human reviewer and show AI and reviewer scores side by side with agreement counts. |
| R10 | Refuse AI suggestions made for a different notebook fingerprint or a different explanation. Escape all AI text in HTML. Offer --show-prompt so the reviewer can see what would be sent. |

## Rubric
Each dimension receives 0 (missing), 1 (partial), or 2 (clear): workflow explanation; classical comparison; limitations and errors. Scores support human judgment. They never automatically award a credential. Decisions: needs-revision or meets-prototype-rubric.

## Outside this version
AI-made decisions or credentials, AI checking of code correctness, arbitrary code execution, identity checks, unseen assessment tasks, credentials, multi-user accounts, quantum hardware, and clinical use. The sample is an educational classifier experiment, not a diagnostic product.

## Changes from development testing
- First real run with the free local model (Qwen2.5-1.5B-Instruct): the model reworded the rubric instead of quoting the learner, and the quote check marked all three quotes as not found. Change: learner sentences are now numbered and the AI cites a sentence number; the tool inserts the exact sentence. See evidence/ai-suggestions-local-run.json for the rerun.
- Second run: the small model copied a worked example from the prompt instead of judging the learner. Change: one short task per rubric area, plus separate requests for flags and questions; unreadable flags or questions are skipped with a note instead of stopping the run.
- Third run (evidence/ai-suggestions-local-run.json, 449 seconds on 2 CPU cores): completed end to end. Scores and follow-up questions usable; chosen supporting sentences often weak; all 3 flags incorrect. Change: report labels AI flags as unverified. Planned: test a larger free model on a Colab GPU and replace AI flags with a rule-based number check.
- Decision to use a free local model by default, so the AI step costs nothing and the explanation never leaves the reviewer's computer.

## Changes from user testing
None yet. Complete docs/user-test.md after a real session, then update this section with the observation, requirement change, and reason.
