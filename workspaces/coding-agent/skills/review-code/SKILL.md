---
name: review-code
description: Perform a focused code review of a branch, PR, or set of recent changes. Use when the user asks to review code, review a PR, review a branch, do a code review, look over recent work, or give a second opinion on changes. Returns structured findings grouped by severity with file:line references.
---

# Review Code

Review a bounded set of code changes and return structured, actionable findings. Compare **what the code does** against **what the code claims to do**. Assume the author knows the project better than you. Flag what matters; stay out of preference wars.

## Scope Resolution

Before reviewing, resolve what to actually read:

- **"Review PR #N" / "review <GitHub PR URL>"** — use `gh pr view <N> --json title,body,files,commits` and `gh pr diff <N>`.
- **"Review the `<branch>` branch"** — use `git diff <base>...<branch>` and `git log <base>..<branch>`.
- **"Review my changes" / "review what I just did"** — current branch vs the default base. If already on the default branch, use uncommitted/staged work: `git diff HEAD` and `git status`.

Determine the default base with:

```
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

Fall back to `main` if the command fails. If the scope is ambiguous, stop and ask which changes to review.

## What to Check

In priority order. Spend time on 1-3; skim 4-7; only surface 8 if egregious.

1. **Correctness** — does the code do what it claims? Off-by-one, wrong conditionals, missed branches, unhandled cases.
2. **Edge cases** — empty / null / very large inputs, concurrent access, malformed or adversarial input.
3. **Security** — injection (SQL, shell, HTML), auth bypasses, PII/secret exposure, unsafe defaults, dangerous deserialization, path traversal.
4. **Error handling** — handled at the right boundary? No silent swallows? No overly broad catches?
5. **Tests** — new logic covered? Tests actually assert the behavior or do they pass tautologically?
6. **Readability** — names, structure, comments that add value.
7. **Consistency** — does it match existing patterns in the codebase? If it deviates, is that intentional?
8. **Performance** — only flag egregious issues (N+1 queries, quadratic loops on likely-large inputs).

Do NOT flag:

- Style a linter already enforces.
- Personal-preference rewrites.
- Missing features the change did not claim to add.
- Things you are not confident about after reading the code.

## Steps

### 1. Understand the claim

Read the PR title + body (or the branch's commit messages) first. The review hinges on the delta between what is claimed and what the code does.

### 2. Map the diff shape

```
git diff <base>...<head> --stat
```

If the diff is very large (100+ files or 5000+ lines), mention it upfront so the reader knows the review is a skim, not a full audit.

### 3. Read the changed files in context

For each file touched, read enough of the full file to understand the hunk in context. Read callers/callees of modified functions when the change is not self-contained.

### 4. Write the review

Use this output structure. **Skip empty sections** (no "Blockers" header if there are no blockers).

```markdown
## Review: <PR title or branch name>

**Take:** <1-2 sentences. Merge-ready / needs changes / has questions.>

### Blockers

- `path/file.ts:LINE` — <what is broken and why it blocks>

### Suggestions

- `path/file.ts:LINE` — <issue and brief rationale>

### Nits

- `path/file.ts:LINE` — <minor issue>

### What's good

- <1-3 brief callouts>

### Open questions

- <anything that needs author clarification>
```

Rules for findings:

- **Always include `file:line`** (or `file:line-range`).
- **Lead with the issue, not the fix.** "`delete()` does not guard against deleting the last habit" beats "you could add a guard for the last habit".
- **Be specific.** "Timezone is hardcoded" is weak; "Timezone hardcoded to `Asia/Singapore` in `src/App.tsx:42` — will break for users in other zones" is useful.
- **One issue per bullet.** Do not bundle.

### 5. Deliver

Return the review markdown in the chat. That is the primary output.

If the user explicitly asks to post the review as a comment on a GitHub PR, **ask for confirmation first** (per workspace AGENTS.md rule on actions with blast radius), then:

```
gh pr comment <N> --body-file /tmp/review.md
```

Do not `gh pr review --approve` or `--request-changes` unless the user explicitly asks.

## Constraints

- **Review only.** Do not modify files, do not open commits, do not suggest a patch unless asked.
- **Do not rewrite the code for the author.** Describe the issue and a direction; let them write the fix.
- **Do not fabricate findings.** If you could not read a file (too large, binary, not in the diff), say so.
- **Do not approve or request changes on the PR** unless the user explicitly asks.
