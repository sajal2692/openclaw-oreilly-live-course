# Automations on OpenClaw 2026.9.5

The scheduler owns timed jobs, heartbeat monitors, and delivery. Use `openclaw automations`; `openclaw cron` remains an alias. These examples are opt-in take-home exercises, not a seventh live demo.

Run CLI commands in the running gateway container from the deployment directory, for example:

```bash
docker compose exec openclaw-gateway bash
openclaw automations list --all
```

Replace agent/account/recipient placeholders with your configured values. The single-agent guide uses agent `main` and Telegram account `default`; the multi-agent reference uses `alfred`/`alfred` and `coder`/`coder`. No job below exists until you create it.

## One-shot reminder with explicit delivery

This starts an isolated agent turn in 20 minutes and sends its final result through a specific Telegram account:

```bash
openclaw automations create --name "Grocery reminder" \
  --at 20m --agent main --session isolated \
  --message "Remind me to buy groceries. Return only the reminder text; do not use the message tool." \
  --announce --channel telegram --account default --to <YOUR_CHAT_ID> \
  --delete-after-run
```

For an absolute time, use an ISO timestamp with an explicit offset, or an offset-less timestamp with `--tz America/Vancouver`. Verify the actual future date and timezone before creating it. Pairing approval alone is not a fallback automation recipient; the explicit `--to` matters.

A **main-session wake** uses a different payload:

```bash
openclaw automations create --name "Review prompt" \
  --at 20m --agent main --session main \
  --system-event "Reminder: review today's tasks." --wake now --delete-after-run
```

Do not add `--announce`, `--channel`, `--account`, or `--to` to that main-session system event. It wakes the agent; it does not establish the isolated job's explicit delivery contract.

## Recurring morning briefing

Create the job disabled, inspect it, then enable it when its recipient and schedule are correct:

```bash
openclaw automations create --name "Morning briefing" \
  --cron "0 8 * * 1-5" --tz America/Vancouver \
  --agent main --session isolated --disabled \
  --message "Use the daily-briefing skill. Read current notes and tasks, create today's note if missing, and return the briefing for scheduler delivery. Do not use the message tool." \
  --announce --channel telegram --account default --to <YOUR_CHAT_ID>
openclaw automations get <JOB_ID>
openclaw automations enable <JOB_ID>
```

Check `USER.md`, `agents.defaults.userTimezone`, and the job timezone together. These sample skills need writable notes and a configured model. Unattended jobs cannot rely on a user answering clarification questions during the run.

After an execution, inspect the result and destination:

```bash
openclaw automations runs <JOB_ID>
openclaw automations disable <JOB_ID>
openclaw automations rm <JOB_ID>
```

A successful model run and successful delivery are separate facts. The `announce` mode fallback-delivers final text when the agent has not already sent to the target. `--no-deliver` disables scheduler fallback; it is not a blanket prohibition on an agent's message tool.

## Heartbeat monitor scratch

Recurring heartbeats are system-owned automation jobs. Root `HEARTBEAT.md` is retired in this release. The course samples set `heartbeat.every: "0m"` so no recurring monitor is started unintentionally; targeted event wakes can still run.

To opt in, configure the intended agent's `heartbeat` fields, cadence, timezone/active hours, and a concrete delivery route. For a multi-agent roster, use `agents.entries.<id>.heartbeat`. Inspect the generated monitor:

```bash
openclaw automations list --all
openclaw cron scratch <HEARTBEAT_JOB_ID> --set "Check for a meaningful change in the current task. If nothing needs attention, reply NO_REPLY."
```

Edit cadence through the agent's heartbeat configuration, rather than editing the system-owned job schedule. Recurring tasks such as daily briefings belong in their own jobs. `cron.enabled: false` disables scheduled heartbeats as well as other schedules. Scratch is bounded context for the monitor; it is not a replacement task queue.

## Inbound webhooks

Webhooks are disabled by default. To opt in, merge a separate hook token and an explicit agent allowlist into the existing config:

```json5
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOK_TOKEN}",
    path: "/hooks",
    allowedAgentIds: ["main"],
    allowRequestSessionKey: false,
  },
}
```

Add `OPENCLAW_HOOK_TOKEN` to the active `.env`, validate, and recreate the container. Use a dedicated random hook token, separate from the gateway token. Start with a synthetic event on the gateway host:

```bash
curl --include http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer <YOUR_HOOK_TOKEN>' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: course-webhook-smoke-001' \
  --data '{"agentId":"main","name":"Course smoke test","message":"Reply with: synthetic import received. Do not use tools.","deliver":false}'
```

HTTP 200 with `runId` confirms admission, not model completion or delivery. Inspect that run's logs/result. Treat event text as untrusted input and keep the same execution boundaries as other agent requests. The test can incur a model call; it is not executed by installing these files. External callers need an intentional authenticated ingress route; the base Compose port is private.

- [Automation CLI](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/cli/cron.md)
- [Delivery contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/automation/cron-jobs/delivery.md)
- [Heartbeat](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/heartbeat.md)
- [Inbound webhooks](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/automation/cron-jobs/webhooks.md)
