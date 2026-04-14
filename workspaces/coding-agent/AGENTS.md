# Operating Instructions

## Code Changes

- Read the relevant code before suggesting changes. Understand context first.
- Make the smallest change that solves the problem. Do not refactor adjacent code.
- When fixing a bug, explain the root cause before the fix.
- When writing new code, follow existing patterns in the codebase.
- Prefer editing existing files over creating new ones.

## Git Workflow

- Write clear, concise commit messages that explain the "why" not the "what".
- One logical change per commit. Do not bundle unrelated changes.
- Always check `git status` and `git diff` before committing.

## Code Review

When asked to review code:
1. Focus on correctness and edge cases first.
2. Note security issues (injection, auth, data exposure).
3. Flag only style issues that affect readability or maintainability.
4. Be specific: reference file paths and line numbers.

## Testing

- Run existing tests after making changes.
- If the project has a test framework, write tests for new logic.
- If tests fail, investigate the failure before suggesting fixes.

## Memory

- After completing a significant task, write a brief note to `memory/` with the date, what was done, and any context that would help future sessions.
- Check `memory/` at the start of a session for relevant context.
