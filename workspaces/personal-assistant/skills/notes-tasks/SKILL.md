---
name: notes-tasks
description: Manage tasks in the file-based PKM at notes/tasks.md. Add, complete, move, list, and search tasks across sections (Today, This Week, Inbox, Someday). Use when the user asks to add a task, check today's tasks, list inbox, mark something done, move a task, or any task management operation.
---

# Notes Tasks

Manage tasks in `notes/tasks.md`, the file-based task list at the root of the workspace.

## File Structure

`notes/tasks.md` is a single markdown file with four sections:

```markdown
# Tasks

## Today
- [ ] Task one
- [ ] Task two
- [x] Completed task

## This Week
- [ ] Task three
- [ ] Task four

## Inbox
- [ ] Untriaged item

## Someday
- [ ] Long-term aspiration
```

Each task is a GFM checkbox: `- [ ]` for open, `- [x]` for done.

Tasks may include lightweight metadata as inline tags or trailing context:
- `#work`, `#study`, `#side-project`, `#fitness`, `#life` — area tags
- `(due: 2026-04-15)` — deadline
- `[project: personal-agent]` — project pointer

## Available Actions

### 1. List tasks

When the user asks to see tasks ("show today", "what's in my inbox", "this week's tasks"):

1. Read `notes/tasks.md`
2. Parse the relevant section
3. Format as a clean list, grouped if helpful

### 2. Add a task

When the user asks to add a task:

1. Determine target section (default: `## Today` if nothing specified, `## Inbox` for "capture this" or "add to inbox")
2. Append `- [ ] <task description>` to that section in `notes/tasks.md`
3. Add inline metadata if the user provided it (tags, deadlines, project)
4. Confirm: "Added to [section]: [task]"

### 3. Complete a task

When the user asks to mark a task done:

1. Read `notes/tasks.md`
2. Find the matching `- [ ]` line (fuzzy match on description)
3. Change `- [ ]` to `- [x]`
4. Confirm: "Marked done: [task]"

### 4. Move a task between sections

When the user asks to move a task ("push that to next week", "move X to Today"):

1. Find the task line in its current section
2. Remove it from there
3. Append to the target section
4. Confirm: "Moved to [target]: [task]"

### 5. Search tasks

When the user asks to find tasks ("find anything about the agent project", "what's tagged #fitness"):

1. Read `notes/tasks.md`
2. Grep across all sections for the query (or tag)
3. Return matches with their section context

### 6. Triage inbox

When the user asks to triage the inbox ("clean up inbox", "process inbox"):

1. Read the `## Inbox` section
2. For each item, ask the user: discard, defer (move to Someday), schedule (move to This Week), or do today (move to Today)?
3. Apply the chosen action
4. Confirm summary

## Conventions

- Keep `## Today` realistic: 3-7 tasks max
- Move stale Today items back to This Week or Someday during nightly review
- The Inbox is a buffer, not a graveyard. Process it during weekly review.

## Notes

- Always read the file before writing. Sections may have been edited externally.
- Preserve formatting (blank lines between sections, header levels) when writing
- If a section is missing, recreate it in the standard order: Today, This Week, Inbox, Someday
