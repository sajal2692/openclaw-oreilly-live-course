# OpenClaw 2026.9.5 compatibility notes

The course examples target **OpenClaw 2026.9.5**, revision `ec9c1a13db8938e5a3eaa51fca2e981cde2395a9`. Start with the [deployment guide](../deployment/linux-vps-guide.md) for a fresh installation. For an existing gateway, follow its [upgrade procedure](../deployment/linux-vps-guide.md#upgrading-an-existing-installation) with a complete backup.

## Migrating from an older release

- **Agent configuration:** `agents.entries` replaces the old `agents.list` array. Multi-agent configurations need explicit ownership and channel/account bindings. Preserve existing agent IDs and workspace paths when they contain history. See the [multi-agent guide](../multi-agent/README.md).
- **Workspace instructions:** Tool notes belong in the Tools section of `AGENTS.md`. The starter no longer uses `TOOLS.md` or a root `HEARTBEAT.md`; see the [automation guide](../automation/README.md) for heartbeat scratch and scheduled jobs.
- **Runtime state:** Shared state and per-agent sessions, transcripts, model auth, and memory indexes use SQLite stores. Back up the full state directory and external mounts with all writers stopped. Keep a matching image and state snapshot for recovery.
- **Permissions:** Use current `tools.exec.mode` settings and inspect each session's Execution permissions. Doctor migrates legacy session policy. Separate agent IDs and workspace-scoped file tools still share the container's filesystem and credentials; see [security boundaries](../security/README.md).
- **Container configuration:** Use container paths in runtime settings. Recreate containers after changing `.env`; `docker compose restart` keeps the previous environment.
- **Remote access:** The deployment guide starts with a private SSH tunnel. Its optional managed Tailscale Serve setup uses a dedicated listener and verified identity. A manual proxy to the ordinary gateway port requires normal gateway authentication.
- **Automation:** Use the current CLI examples, explicit account and recipient IDs, and your timezone. Check execution and delivery separately. Main-session system events and isolated jobs use different delivery options.

Review Doctor's changes on a restored state copy before applying the upgrade to your active gateway.

## Example defaults

The Docker recipe runs one gateway with an optional one-shot CLI service. It pins the upstream image by release and digest, then adds Python dependencies and GitHub CLI. Direct Python dependencies are pinned; Debian packages and transitive Python dependencies can vary. Record the resulting image digest alongside your backup.

The single-agent example uses agent `main`. The multi-agent example uses `alfred` and `coder`, each bound to its own Telegram account. Alfred uses OpenRouter Sonnet 4.6; Coder uses direct Anthropic Sonnet 5 with OpenRouter fallback. Select models your provider accounts can access and keep credentials in the environment or the configured auth store.

The examples start with guarded exec, workspace-scoped file tools, and agent-scoped session visibility. Automatic skill editing, memory dreaming, and periodic heartbeat work start disabled. Enable additional behavior deliberately and verify the active session's permissions.

## Check your installation

After setup or migration:

1. Verify the running version, validate the configuration, and check model authentication and skill eligibility using the deployment guide's commands.
2. Send a simple message and confirm the expected agent, model, workspace, and response. For the multi-agent setup, check both bots separately.
3. Test permitted and approval-required operations using a disposable workspace and synthetic data.
4. If enabling reminders or webhooks, check that the job runs and reaches the intended destination. For Coder, try a disposable repository and inspect the resulting branch and PR.
5. If enabling managed Tailscale Serve, verify the host's operator permissions, HTTPS route, and browser access before changing SSH access.

## Sample data and rental search

The personal-assistant notes and memory exports contain historical April 2026 fixtures. Customize the persona, timezone, and recipient IDs. Create current daily notes and a complete prior ISO week before trying daily or weekly summaries, and recompute reading statistics from the dated records. Copying these files does not install schedules or import active session history.

Rental search depends on external HTML and site availability. The scraper can return an empty array after a fetch or parsing failure, so inspect stderr before treating an empty result as evidence that no rentals are available. The current scraper also reduces fractional bathroom counts to integers.

## Release-pinned references

- [Release and revision](https://github.com/openclaw/openclaw/releases/tag/v2026.9.5)
- [Docker installation](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/install/docker.md) and [upstream Compose](https://github.com/openclaw/openclaw/blob/v2026.9.5/docker-compose.yml)
- [Agent bindings and ownership](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/agent-bindings.md)
- [Workspace contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/agent-workspace.md)
- [Tailscale ingress and auth](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/tailscale.md)
- [Session permission modes](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/permission-modes.md)
- [Automation CLI](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/cli/cron.md) and [heartbeat contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/heartbeat.md)
- [Skills contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/tools/skills.md)
