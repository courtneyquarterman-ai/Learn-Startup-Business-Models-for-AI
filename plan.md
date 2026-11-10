# Implementation plan

1. Write requirements and acceptance criteria before implementation.
2. Preserve the supplied notebook as the sample assessment.
3. Implement notebook inspection without executing submitted code.
4. Add reviewer input validation and JSON/HTML evidence export.
5. Test the sample journey, invalid files, invalid review inputs, and HTML escaping.
6. Have a real reviewer follow docs/user-test.md; record their feedback and revise the PRD.

The initial plan deliberately uses a local command-line interface so the prototype has no account setup, hosting, or extra dependencies. A later interface change should follow observed user feedback.

## AI assistance
An AI coding agent drafted the requirements, implementation, and automated tests. The student must review the code, run it, explain its limitations, and conduct the real user test. Git commits record actual development stages from this session, not earlier work.
