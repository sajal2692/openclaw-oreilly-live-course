# Operating Instructions

## Working in a Repo

- Code lives in subdirectories of this workspace. Each subdirectory is typically a separate repo.
- **When the user references a project, app, or repo, `ls` the workspace first to see what exists.** Do not rely on `memory_search` or prior session memory to determine whether a repo is present. The filesystem is the source of truth for what is in the workspace.
- When the user names a repo that matches a subdirectory, `cd` into it. Then read `CLAUDE.md`, `AGENTS.md`, or `README.md` at the repo root before doing anything else. Repo-level instructions take priority over these workspace defaults.
- Run commands from the repo root, not the workspace root. Use `workdir` on `exec` if needed.
- If the user names a repo that does not exist as a subdirectory, stop and ask.

## Code Changes

- Read the relevant code before suggesting changes. Understand context first.
- Make the smallest change that solves the problem. Do not refactor adjacent code.
- When fixing a bug, explain the root cause before the fix.
- When writing new code, follow existing patterns in the codebase.
- Prefer editing existing files over creating new ones.

## Feature Requests

- Restate the ask in one sentence. If it is ambiguous, ask a clarifying question before writing code.
- Propose an approach (1-3 bullets) before making edits on anything non-trivial. Wait for confirmation.
- Implement in a feature branch, not on `main`.
- When done, summarize what changed, show `git diff --stat`, and wait for review.

## Git Workflow

- Never commit directly to `main` or `master`. Always branch: `feat/<short-name>`, `fix/<short-name>`, `chore/<short-name>`.
- Write clear, concise commit messages that explain the "why" not the "what".
- One logical change per commit. Do not bundle unrelated changes.
- Always check `git status` and `git diff` before committing.
- **Ask before pushing or opening a PR.** Push, PR, branch delete, and force-push are actions with blast radius. Confirm first.

## Verification Before "Done"

- Run the project's lint, typecheck, test, and build commands (look in the README or `package.json` / `Makefile` / equivalent) before declaring a task complete.
- If changes touch new logic, add a test.
- If anything fails, investigate the failure. Do not paper over it.

## Code Review

When asked to review code:
1. Focus on correctness and edge cases first.
2. Note security issues (injection, auth, data exposure).
3. Flag only style issues that affect readability or maintainability.
4. Be specific: reference file paths and line numbers.

## Scope Discipline

- Stay inside the task asked. If you spot an unrelated issue, note it briefly at the end. Do not fix it unilaterally.
- Do not add features, logging, or abstractions that were not requested.

## Security

- Never commit secrets, API keys, or `.env` files. Check `.gitignore` covers them.
- Treat credentials in the workspace as private. Do not echo them back in replies or put them in commits.

## Memory

- After completing a significant task, write a brief note to `memory/` with the date, what was done, and any context that would help future sessions.
- Check `memory/` at the start of a session for relevant context.
- `memory_search` is for recalling prior work and notes. It is **not** authoritative for "does X exist in the workspace" — use `ls` for that.
