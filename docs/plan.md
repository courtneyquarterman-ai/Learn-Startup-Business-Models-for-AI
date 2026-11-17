# Implementation plan

1. Write requirements and acceptance criteria before implementation.
2. Preserve the supplied notebook as the sample assessment.
3. Implement notebook inspection without executing submitted code.
4. Add reviewer input validation and JSON/HTML evidence export.
5. Test the sample journey, invalid files, invalid review inputs, and HTML escaping.
6. Add the AI review assistant (R7-R10): prompt, AI service connection, output validation, quote check, side-by-side report.
7. Test the AI path with a simulated AI service, then run once with a real API key.
8. Have a real reviewer follow docs/user-test.md; record their feedback and revise the PRD.

The initial plan deliberately uses a local command-line interface so the prototype has no account setup, hosting, or extra dependencies. A later interface change should follow observed user feedback.

## AI assistance
An AI coding agent drafted the requirements, implementation, and automated tests. See docs/ai-use-log.md. The student must review the code, run it, explain its limitations, and conduct the real user test. Git commits record actual development stages from this session, not earlier work.
