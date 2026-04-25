---
name: create-pr
description: Open an informative pull request from the current feature branch. Use when the user asks to open a PR, raise a PR, create a pull request, or ship the feature. Generates a clear title + structured body (summary, changes, test plan) from the branch diff, then runs gh pr create and returns the PR URL.
---

# Create PR

Open a pull request from the current feature branch with a clear title and structured body. The goal is a PR a human reviewer can skim in 60 seconds and know what changed, why, and how to verify it.

## Preconditions

Before running this skill, verify each of these. If any fails, stop and tell the user what is missing.

1. You are inside the target repo (cwd ends in the repo directory, not the workspace root).
2. Current branch is **not** `main` or `master`. Check with `git rev-parse --abbrev-ref HEAD`.
3. The branch has been pushed to `origin`. Check with `git rev-parse --abbrev-ref --symbolic-full-name @{u}` (non-zero exit means not pushed). Per workspace `AGENTS.md`, ask before pushing if it is not.
4. `gh auth status` shows an authenticated session.

## Steps

### 1. Determine the base branch

```
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

Use this as the base. Default `main` if the command fails.

### 2. Gather context from the diff

- `git log <base>..HEAD --oneline` — commits on this branch
- `git diff <base>...HEAD --stat` — file-level change summary
- `git diff <base>...HEAD -- <file>` — drill into specific files for the "why" if needed

Focus on understanding *why* the change exists, not just what it does. The diff shows what; the PR body should explain why.

### 3. Draft the title

- **Imperative mood, present tense**: "Add delete button" not "Added" or "Adding".
- **Under 70 characters**.
- **Conventional prefix if the repo uses them**: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`. Check recent commits or PRs for the convention before applying one.
- **No trailing period**.

### 4. Draft the body

Use this structure. Skip sections that do not apply.

```markdown
## Summary

<1-3 sentences: what this PR does and why. Focus on the why.>

## Changes

- `<file>`: <what changed and why>
- `<file>`: <what changed and why>

## Test Plan

- [ ] <how to verify the change works>
- [ ] <edge case to check>
- [ ] <lint / typecheck / build / tests run locally>

## Notes

<Optional: breaking changes, open questions, follow-ups for later PRs.>
```

Guidelines for the body:

- Be specific. `Added delete feature` is weak; `Added deleteHabit(id) in src/App.tsx and a trash-icon button rendered per row in the habit list` is useful.
- Match tone: neutral, factual. No marketing language, no emoji, no "I" or "we" unless the project clearly uses them.
- If the diff is large (100+ files or 5000+ lines), note it so reviewers can plan review time.

### 5. Create the PR

```
gh pr create \
  --base <base-branch> \
  --head <current-branch> \
  --title "<drafted title>" \
  --body "<drafted body>"
```

Pass the body via a heredoc if it contains characters that might need escaping.

### 6. Report back

Return the PR URL and a one-line summary. Nothing else.

Example:

> Opened PR: https://github.com/sajal2692/my-app/pull/42
> Title: feat: add delete button for habits

## Constraints

- Do not push the branch as part of this skill. If it is not pushed, stop and surface that to the user.
- Do not merge the PR. PR creation only.
- Do not add labels, reviewers, or milestones unless the user asks.
- Stick to facts from the diff; do not speculate about intent or impact.
