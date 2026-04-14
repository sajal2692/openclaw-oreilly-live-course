---
name: weekly-review
description: Performs weekly reviews by analyzing the week's daily notes, project files, and task list. Use when the user asks to create, generate, or perform a weekly review.
---

# Weekly Review

Generate a comprehensive weekly review from the week's daily notes, active projects, and task list.

## Sources

- **Daily notes:** `notes/dailies/YYYY-MM-DD.md` for the review week (Monday-Sunday)
- **Tasks:** `notes/tasks.md`
- **Projects:** `notes/projects/*.md` (each represents an active project)
- **Last week's review:** `notes/weekly/YYYY-Www.md` for continuity

## When to Use

- "Do my weekly review"
- "Generate this week's review"
- "Wrap up the week"

## Week Boundaries

- Weeks run Monday-Sunday (ISO 8601)
- Reviews are typically run Sunday evening
- Use ISO week numbering: `YYYY-Www` (e.g., `2026-W15`)

## Workflow

### 1. Determine the Review Period

- Resolve current date and ISO week number
- If running on Sunday evening or early Monday, review the previous week (Monday-Sunday just completed)
- Compute the date range (e.g., `2026-04-06` to `2026-04-12`)

### 2. Gather Data

**A. Daily notes**

Read each daily note from the review period (Mon-Sun). Look for:
- `## Completed Today` (definitive proof of what got done)
- `## Top 3 Priorities` (intent, compare to completed)
- `## Sleep & Energy` (wellbeing trend)
- `## Evening Reflection` (qualitative notes)
- `## Field Notes` (if present, see step 5)

**B. Tasks**

Read `notes/tasks.md`:
- `## Today` and `## This Week`: rollover load. What didn't get done?
- `## Inbox`: count items (target: <20). Has it grown all week?
- `## Someday`: any candidates to promote?

**C. Projects**

Read each file in `notes/projects/*.md`. For each:
- Current status / phase
- What progress was logged this week (look at modification dates and check the daily notes for project mentions)
- Next actions

**D. Last week's review**

Read `notes/weekly/YYYY-Www.md` for last week (if it exists) to:
- Compare planned vs actual outcomes
- See last week's "Next Week" priorities. Were they met?

### 3. Assess Data Completeness

If you have at least 4-5 substantive daily notes, proceed.

If data is sparse (fewer than 3 daily notes with content), use AskUserQuestion to fill gaps. Ask 3-5 questions covering:
- Proud moments (always ask, regardless)
- Accomplishments and milestones
- Stalled projects and blockers
- Learnings and insights
- Energy and wellbeing
- Next week's outcomes

### 4. Analyze for Insights

**Big wins** to surface:
- Completed projects or major milestones
- Breakthroughs in learning
- Productivity patterns that worked
- Difficult tasks completed despite resistance
- Habits established or maintained
- Significant project progress

**Areas for optimization** to surface:
- Stalled projects (identify blockers)
- Time drains or inefficiencies
- Tasks that rolled over multiple days
- Energy or productivity slumps
- Misalignment between planned vs actual

Be specific and evidence-based. Identify the *why*, not just the *what*.

### 5. Field Notes Analysis (if present)

If daily notes contain `## Field Notes` sections:
- If fewer than 3 days have field notes, skip with "Not enough field notes this week"
- Otherwise: surface recurring themes, emotions, or triggers across the week

For each pattern, complete an Observation -> Question -> Hypothesis row:

| Observation | Question | Hypothesis |
|---|---|---|
| (what you noticed) | (what it makes you curious about) | (possible explanation) |

Plus: what's working / what's not working.

### 6. Generate the Review

Read the template at `notes/weekly/_template.md`. Replace placeholders:

- `{{week}}` -> ISO week (e.g., `2026-W15`)
- `{{start_date}}` -> Monday (e.g., `2026-04-06`)
- `{{end_date}}` -> Sunday (e.g., `2026-04-12`)
- `{{prev_week}}` -> previous week (e.g., `2026-W14`)
- `{{next_week}}` -> next week (e.g., `2026-W16`)
- `{{year_month}}` -> year-month tag (e.g., `2026-04`)

**Tone:**
- Trusted advisor reviewing the week together, not a report generator
- Direct and honest. Celebrate wins, call out issues respectfully.
- Subtle wit where it fits
- Avoid corporate platitudes ("solid progress" beats "synergistic advancement")
- Constructive but candid on optimization areas

**Section content:**

- **This Week's Wins:** 3 biggest wins. Focus on themes and significant outcomes; don't enumerate granular task completions.
- **Active Projects Health:** For each project file: status (On track / Ahead / Behind / Stalled / Complete), summary, next actions. Be honest about stalls.
- **Insights & Patterns:** What's working, what's not. Pattern alerts. Specific and evidence-based.
- **System Maintenance:** Inbox count vs target (<20). If overflowing, say so.
- **Energy & Wellbeing:** Overall energy trend, sleep, exercise, social connections (from sleep logs and reflections).
- **Field Notes Analysis:** Output from step 5.
- **Next Week Planning:** **Do not plan the principal's week for them.** After the rest of the review is generated, ask what they're thinking. Guide them to articulate 3 key outcomes (offer suggestions based on project health if helpful).
- **Links:** Wikilinks to previous and next weekly notes.

### 7. Save

Save the review to `notes/weekly/YYYY-Www.md`.

### 8. Offer Summary (Optional)

Offer to send a short Telegram summary with:
- Top 3 wins
- Top 3 areas worth noting
- Project health one-liner
- "What are your 3 outcomes for next week?"

## Best Practices

1. **Be specific.** Use concrete examples from the data, not generic statements
2. **Be honest.** Reflect actual progress and challenges
3. **Be actionable.** Next actions should be clear and immediately doable
4. **Be balanced.** Include successes and improvement areas
5. **Be realistic.** Consider actual energy and capacity when planning

## Examples

### Good
```
### Completed
- Shipped admin panel auth (3 weeks of work)
- Finished 2 chapters of Designing Data-Intensive Applications
- 3 runs (one 5k PR)
- Cleared 47 items from Inbox
```

### Poor
```
### Completed
- Did some work
- Made progress on things
```
