---
name: nightly-review
description: Nightly review at end of day that summarizes the day, surfaces unclosed tasks, and previews tomorrow. Sends a conversational Telegram summary asking for thoughts.
---

# Nightly Review

A conversational end-of-day check. Summarize what happened, surface unclosed tasks, prep for tomorrow, and ask for thoughts.

## Workflow

Execute all steps. No confirmation needed. Runs automatically.

### 1. Gather State

#### Today's Plan (from daily note)
- Read today's daily note: `notes/dailies/YYYY-MM-DD.md`
- Note: what was on `## Schedule`, `## Top 3 Priorities`, and what's already in the `## Completed Today` section (if anything)

#### Open Tasks
- Read `notes/tasks.md` via the `notes-tasks` skill
- Pull the `## Today` section
- Identify any items still open (`- [ ]`)

### 2. Reconcile and Update Daily Note

Build a combined list of what actually got done today, drawing from:
- Items already noted in `## Completed Today` (if anything)
- Items checked off in `notes/tasks.md` `## Today` (any `- [x]` lines)
- Schedule items the principal explicitly confirmed

Replace the content of `## Completed Today` in today's daily note with this combined list. Format each item as `- [description]`. Aim for 3-6 meaningful items.

For schedule items where completion isn't verified (e.g., a study block on the schedule but no matching done task), note them in the message below as "Did you get to these?" Don't assume completion.

### 3. Build the Message

Format a conversational Telegram message:

```
🌙 *Nightly Review*

📅 *Today*
[2-3 line summary of what happened. Confirmed completions only.]

❓ *Did you get to these?*
[Only include if there are unverified schedule items]
• [item 1]
• [item 2]

📋 *Open tasks on Today*
[Only include if there are open tasks]
• [task]
• [task]
Mark done or roll over?

🗓️ *Tomorrow*
[Brief preview from `notes/dailies/YYYY-MM-DD.md` (tomorrow's date) if it exists, or from any planning notes in today's `## Tomorrow` section]
[If nothing planned: "Open day"]

---
How did the day go?
```

### 4. Deliver

**If the conversation is already happening on Telegram (or any messaging channel):** just reply with the review directly. Do not use the `message` tool. Do not mention how or where you are delivering it. Just send the content.

**If triggered by a cron job or automation (no active conversation):** use the `message` tool:
- `action`: `send`
- `target`: <Telegram chat ID from TOOLS.md>
- `channel`: `telegram`
- `message`: the formatted review

### 5. Reconcile After Response

When the principal responds:

1. If they confirm completion of any unverified items, append those to `## Completed Today`
2. If they want open tasks rolled over: move them from `## Today` to `## This Week` in `notes/tasks.md`
3. If they share an evening reflection ("rough day", "great session"), add it to today's daily note `## Evening Reflection` section
4. Confirm what you logged

## Edge Cases

- **No scheduled items today:** keep the message short. Just summary plus "How did the day go?"
- **No completed tasks at all:** ask gently rather than reporting nothing happened
- **Daily note doesn't exist:** create a minimal one with `## Completed Today` if there are any completions to log
- **Tasks file missing:** skip the open-tasks section. Mention the file is missing in the summary.
