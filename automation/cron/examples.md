# Cron Job Examples

Common cron job patterns for OpenClaw. Run these via the CLI.

## Daily Morning Briefing

Runs at 7am Pacific in an isolated session. Delivers summary to Telegram.

```bash
openclaw cron add \
  --name "Morning briefing" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Generate today's briefing: weather forecast, calendar events, top 3 emails, and any pending tasks." \
  --model "anthropic/claude-sonnet-4-5" \
  --announce \
  --channel telegram
```

## Weekly Analysis Report

Runs every Monday at 9am. Uses a stronger model for deeper analysis.

```bash
openclaw cron add \
  --name "Weekly report" \
  --cron "0 9 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Generate a weekly summary: key accomplishments from git log, open issues, metrics from the dashboard, and priorities for the coming week." \
  --model "anthropic/claude-opus-4-6" \
  --announce \
  --channel telegram
```

## One-Shot Reminder

Fires once at a specific time and deletes itself.

```bash
openclaw cron add \
  --name "Standup reminder" \
  --at "2026-04-10T14:45:00-07:00" \
  --session main \
  --system-event "Reminder: daily standup starts in 15 minutes." \
  --wake now \
  --delete-after-run
```

## Recurring Check-In (Every 4 Hours)

Uses a fixed interval instead of a cron expression.

```bash
openclaw cron add \
  --name "Status check" \
  --every "4h" \
  --session isolated \
  --message "Quick status check: any alerts in monitoring? Any pending PRs that need review?" \
  --announce \
  --channel telegram
```

## Managing Cron Jobs

```bash
# List all jobs
openclaw cron list

# Show details for a specific job
openclaw cron show "Morning briefing"

# Pause a job
openclaw cron disable "Morning briefing"

# Resume a job
openclaw cron enable "Morning briefing"

# Delete a job
openclaw cron remove "Morning briefing"
```
