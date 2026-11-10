# Hybrid Skills Verifier

A small local Python prototype for inspecting a quantum-classical notebook and recording a human assessment. It uses only Python 3's standard library. No installation packages or API keys are needed. This version is a command-line application, not a hosted website.

## Start here
Unzip the folder, open a terminal in `hybrid-skills-verifier`, and run:

```sh
python verifier.py inspect samples/quantum_bloom.ipynb
```

Use `python3` if that is your Python command. The output lists code cells, saved execution errors, the saved quantum/classical comparison, and a fingerprint of the notebook. An empty error list means no errors were saved; it does not mean every cell was executed successfully.

Write your own explanation in a file called `explanation.txt`. Explain the preprocessing, quantum kernel, classical baseline, and what the results do and do not show. Then have a reviewer read it and choose the scores, feedback, and decision below. Replace the example values with their actual judgment:

```sh
python verifier.py review samples/quantum_bloom.ipynb --explanation explanation.txt --reviewer "Reviewer name" --feedback "Replace with actual reviewer feedback" --scores 1 1 1 --decision needs-revision --output reports/my-assessment
```

Open `reports/my-assessment.html` in your browser. The JSON beside it contains the same assessment data. Reports stay on your computer. Running the same output prefix replaces the previous report, so use a different prefix for each review.

Scores are ordered: workflow explanation, classical comparison, limitations. Each is 0 (missing), 1 (partial), or 2 (clear). The reviewer explicitly selects `needs-revision` or `meets-prototype-rubric`. The tool does not automatically certify a learner.

## Verify the application

```sh
python -m unittest discover -s tests -v
```

See `docs/verification.md` for requirement mapping and limits. `evidence/inspection.json` is an actual inspection of the attached sample. Automated checks do not replace a participant session.

## Rerunning the quantum experiment
This prototype does not execute notebooks. To verify the experiment separately, open the sample in Jupyter or Colab and run all cells in order; its setup cell installs missing dependencies. Review that cell first. Save the rerun notebook and inspect that saved copy. Record the execution environment, any failures, and changed outputs. The experiment was rerun sequentially during development; all 10 code cells completed. See `docs/notebook-rerun.md` for the exact execution method and limits.

## Prepared materials

`docs/learner-explanation-draft.md` provides an AI-assisted explanation to review and adapt. `docs/reviewer-session-guide.md` provides a real participant session script. Neither is a record of demonstrated learner understanding or completed participant testing.

## What remains before submission
1. Run this tool yourself and make sure you can explain its code and scope.
2. Write your own learner explanation.
3. Conduct the real session in `docs/user-test.md` and record actual observations.
4. Update the PRD based on that feedback, implement any necessary changes, and rerun tests.
5. Commit the changes, including the test notes. Submit a repository link or zip including `.git`.

The detailed Hands-On assignment document was not supplied. Check its Part D and other instructions against this project before submitting. This package follows the submission requirements pasted in the conversation.

## Development record
AI assistance was used to draft the documents, code, and automated tests, as the assignment permits. The attached notebook was supplied by the student; this package does not establish its authorship. Review and adapt the work before submission. Git history records actual development stages from this session and is attributed to the AI coding assistant. This is a prototype, not a completed user-tested submission.
