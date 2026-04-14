---
name: daily-briefing
description: Generate and deliver a morning briefing with today's schedule, exercise plan, and task priorities. Use when triggered by the daily briefing cron or when manually requested to prepare the morning briefing.
---

# Daily Briefing

Automated morning briefing system that prepares the day ahead by creating today's daily note, gathering relevant information, and delivering a formatted briefing via Telegram.

## Workflow

Execute the following steps in sequence. Do not ask for confirmation. This workflow runs automatically.

### 1. Create Today's Daily Note

**Path:** `notes/dailies/YYYY-MM-DD.md`

Steps:
1. Resolve today's date in the principal's timezone (see USER.md)
2. Check if `notes/dailies/YYYY-MM-DD.md` exists
3. If it exists, skip creation. Do not overwrite.
4. If it doesn't exist:
   - Read template: `notes/dailies/_template.md`
   - Replace placeholders:
     - `{{date}}` -> ISO date (e.g., `2026-04-13`)
     - `{{day}}` -> Day name (e.g., `Monday`)
     - `{{date_long}}` -> Long date (e.g., `April 13, 2026`)
     - `{{yesterday}}` -> Yesterday's ISO date
     - `{{tomorrow}}` -> Tomorrow's ISO date
   - Write the file

### 2. Populate Yesterday's Wins

Steps:
1. Read yesterday's daily note: `notes/dailies/YYYY-MM-DD.md` (yesterday's date)
2. Find the `## Completed Today` section (populated by nightly review)
3. Extract the bullet items
4. Write 3-5 items into today's note under `## Yesterday's Wins`
5. If yesterday's note doesn't exist or has no wins data: write "Rest day / No tracked wins from yesterday"

### 3. Gather Briefing Data

#### Yesterday's Summary
- Reuse yesterday's daily note (already read in Step 2)
- Primary source: `## Completed Today`. Curated record of what actually happened.
- Generate a concise 1-2 line summary capturing the essence of yesterday
- Tone: reflective but forward-looking
- Example: "Wrapped a deploy and tackled three DSA problems. Busier than expected but on track."
- If yesterday's note doesn't exist: "No record from yesterday."

#### Weather
No weather skill is configured. Skip this section entirely. Do not attempt to read `skills/weather/SKILL.md`.

#### Today's Schedule
This workspace does not connect to an external calendar. The schedule lives inside the daily note.

- Look for a `## Schedule` section in today's daily note (just created from template)
- If it's empty, also check yesterday's daily note for a `## Tomorrow` section that may have planned today's schedule
- Include any items found
- If nothing is scheduled, say "No fixed schedule today. Open day."

#### Exercise Plan
- Look for an exercise mention in today's `## Schedule` (e.g., "Push Day", "5k run", "swim")
- If exercise is planned: include a short personality-laden note about the session
  - Example: "Push day. Chest and shoulders are on the clock."
  - Example: "5k easy. Build the base."
- If no exercise: "Rest day. Recovery is training too."

#### Tasks
- Read `notes/tasks.md` via the `notes-tasks` skill (or directly)
- Pull the `## Today` section
- **Group by area tag** (e.g., #side-project, #work, #study, #fitness, #life). Use 2-4 groups; don't over-fragment.
- **Mark one priority per group with a star** (`⭐`). The "if you do nothing else, do this" task per area.
- Priority logic: deadlines first, then streak items (study, fitness), then importance
- Filter out trivial routine items
- Count substantial tasks and add brief commentary on the load (see Personality)

#### Capacity Analysis
- Estimate the day's capacity from the `## Schedule` section in today's daily note
- Compare to the count of substantial tasks
- Light load (<=3 substantial tasks): "Light slate today. Use the time well."
- Normal (4-6): no special comment
- Heavy (7+): "Ambitious list. The starred items are your anchors. Everything else is bonus."
- If schedule is full and tasks are heavy too, flag the tension honestly

### 4. Format Briefing

Generate the Telegram-formatted briefing.

```
[Variable opening line. See Personality.]

📝 *Yesterday*
[1-2 line summary]

📅 *Today*
[schedule items, or "No fixed schedule today"]

🏋️ *Exercise*
[short note with personality]

✅ *Tasks*
[task load commentary if warranted]

🛠️ *<Group 1>*
• ⭐ [priority task]
• [other tasks]

💼 *<Group 2>*
• ⭐ [priority task]
• [other tasks]

[Additional groups as needed]

🎯 *Top 3 for today?*
[Only include if today's `## Top 3 Priorities` section in the daily note is empty]
Reply with up to 3 priorities and I'll log them.

😴 How'd you sleep? Drop your bedtime, wake time, and a rating (or just a quick word) and I'll log it.
```

**Personality Guidelines:**

The briefing should feel like it's from *you*, Alfred. Not a report generator.

1. **Variable opening line.** Never the same opener two days in a row. Rotate based on:
   - Weather: "Overcast and 55°F. The kind of day that rewards indoor focus."
   - Day of week: "Wednesday. The week's false summit." / "Friday. The finish line is in sight."
   - Yesterday callback: "You crushed yesterday's list. Let's keep that energy." / "Yesterday was scattered. Clean slate."
   - Occasional dry wit: "Another Tuesday. They keep making these."

2. **Task load commentary.** Brief, honest:
   - Light (<=3): "Light slate. Rare. Use it well."
   - Normal (4-6): no comment
   - Heavy (7+): "Ambitious list. The starred items are your anchors."

3. **Exercise flavour.** Inject personality:
   - "Push day. Chest and shoulders are on the clock."
   - "Long run. Time on feet. Keep it conversational."
   - "Rest day. Recovery is training too."

4. **Keep it tight.** Personality lives in word choice, not word count.

### 5. Deliver Briefing

**If the conversation is already happening on Telegram (or any messaging channel):** just reply with the briefing directly. Do not use the `message` tool. Do not mention how or where you are delivering it. Just send the content.

**If triggered by a cron job or automation (no active conversation):** use the `message` tool:
- `action`: `send`
- `target`: <Telegram chat ID from TOOLS.md>
- `channel`: `telegram`
- `message`: the formatted briefing

If the message tool fails or the channel isn't configured, save the briefing to `notes/dailies/YYYY-MM-DD.md` under a `## Briefing` section and report what happened.

### 6. Handle Priority-Setting (Interactive)

After delivering the briefing, if the principal replies with their Top 3:

**Expected formats:**
- "1. Ship project update 2. DSA practice 3. 5k run"
- "priorities: code review, study block, evening run"

**Steps:**
1. Parse 1-3 priorities
2. Update today's daily note: fill in the `## Top 3 Priorities` section
3. Confirm: "Logged your priorities for today."

### 7. Sleep Check-In (Interactive)

When the principal replies with sleep info ("slept at 11:30, woke 7, decent" / "6 hours, groggy"):

**Steps:**
1. Parse what's available: bedtime, wake time, duration, quality, energy
2. Update today's daily note section `## Sleep & Energy`:
   - `Bedtime:`, `Wake time:`, `Duration:`, `Quality:`, `Notes:`
3. Confirm: "Logged your sleep."

## Troubleshooting

- **Daily note creation fails:** check that `notes/dailies/_template.md` exists
- **Yesterday's wins empty:** normal if yesterday's note doesn't exist or had no completed tasks
- **Tasks not loading:** check `notes/tasks.md` exists and is well-formed
- **Telegram delivery fails:** save the briefing to today's daily note as fallback
