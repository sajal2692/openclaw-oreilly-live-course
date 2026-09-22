# Deploying OpenClaw 2026.9.5 on a Linux VPS

This guide uses Docker Compose and the official **2026.9.5** release image, with Python and GitHub CLI added for the course skills. It targets a fresh Ubuntu/Debian VPS. The course Hostinger deployment was upgraded from 2026.7.1 separately; follow [Upgrading an existing installation](#upgrading-an-existing-installation) before changing an existing gateway.

The base recipe runs one gateway container and provides an optional one-shot CLI service. It publishes only `127.0.0.1:18789`. The live instructor deployment has a persistent CLI companion as well; that is an operational choice, not one container per agent.

## Prerequisites

- A Linux VPS with 4 GB or more RAM and room for images, state, and backups
- Docker Engine and Docker Compose v2
- SSH access and an LLM provider account/API key
- A Telegram bot token if you want messaging

This recipe layers dependencies onto a pre-built image. Upstream documents **at least 6 GB RAM for a full source image build**. The image supplies a compatible Node runtime; native installs need Node `>=24.16.0 <25 || >=26.1.0` for this release.

A Hostinger one-click template is an alternative installation with its own image, paths, ports, and update procedure. Verify those details before applying any commands from this guide. Do not assume it has the same layout.

## 1. Prepare the VPS

Provision Ubuntu 24.04 or a supported Debian release, add your SSH key, then connect:

```bash
ssh root@YOUR_VPS_IP
apt-get update
apt-get install -y git curl ca-certificates openssl
curl -fsSL https://get.docker.com | sh
docker --version
docker compose version
```

The rest of the guide runs on the VPS as root, except for the laptop SSH tunnel. OpenClaw itself runs as the image's non-root `node` user, uid 1000.

## 2. Get the course recipe and create state directories

```bash
git clone https://github.com/sajal2692/openclaw-oreilly-live-course.git ~/openclaw-course
cd ~/openclaw-course/deployment
mkdir -p /root/.openclaw/workspace /root/.openclaw-auth-profile-secrets
chown -R 1000:1000 /root/.openclaw /root/.openclaw-auth-profile-secrets
chmod 700 /root/.openclaw /root/.openclaw-auth-profile-secrets
cp .env.template .env
chmod 600 .env
openssl rand -hex 32
nano .env
```

Paste the generated value into `OPENCLAW_GATEWAY_TOKEN`. Fill the provider keys you use and optionally `TELEGRAM_BOT_TOKEN`. Keep `.env` private. The [template](.env.template), [Compose file](docker-compose.yml), and [Dockerfile](Dockerfile.course) are in this directory; no edits to an upstream OpenClaw checkout are needed.

`OPENCLAW_GATEWAY_BIND=lan` makes the listener reachable from Docker's port forwarding **inside the container**. The `127.0.0.1:` host mapping keeps it private on the VPS. The recipe does not publish bridge or Teams ports, and does not mount the Docker socket.

## 3. Build the course image

```bash
docker compose config --quiet
docker compose build openclaw-gateway
```

The Dockerfile pins the upstream release by tag and digest. It adds Python packages in `/opt/course-python` and Debian's `gh` package. Direct Python dependency versions match the upgraded instructor environment; Debian package versions and transitive Python dependencies can vary. This is a student recipe, not a byte-for-byte copy of the instructor image.

If GHCR is unavailable, the official Docker Hub mirror is `openclaw/openclaw`. Verify the matching release digest before overriding `OPENCLAW_BASE_IMAGE` through `docker compose build --build-arg`. Avoid floating `latest` tags for a rehearsal.

## 4. Onboard before starting the gateway

Use a one-shot gateway container for pre-start commands. The CLI service shares the gateway network and needs a running gateway.

```bash
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon --skip-health
```

Choose the model/provider, token authentication, and workspace `/home/node/.openclaw/workspace`. The host path `/root/.openclaw` is mounted at `/home/node/.openclaw` in the container. Keep the configured gateway token consistent with `.env`; direct config values and environment fallbacks are resolved separately.

Merge the fields from [openclaw.example.json5](openclaw.example.json5) into `/root/.openclaw/openclaw.json`, preserving onboarding's model, auth, and channel settings. This sets the current `agents.entries` roster, explicit workspace, timezone, and a guarded starting exec policy. It disables recurring heartbeats, autonomous Workshop edits, and dreaming for a predictable course starting state.

For Telegram, either configure it during onboarding or use the token from `.env`:

```bash
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js channels add --channel telegram --use-env
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config validate
```

## 5. Install the personal-assistant workspace

For a fresh workspace, copy the **contents**, including hidden files, into the configured directory:

```bash
cp -a ../workspaces/personal-assistant/. /root/.openclaw/workspace/
chown -R 1000:1000 /root/.openclaw/workspace
```

Review any onboarding-created `BOOTSTRAP.md`. Remove it only after completing that first-run setup if you intend to keep the supplied persona. For an existing workspace, back up and merge the files you want instead of copying over it.

Customize `USER.md`, `SOUL.md`, `IDENTITY.md`, and `AGENTS.md`. Local tool notes belong in `AGENTS.md` under Tools. Set your timezone and Telegram destination there. The dated notes and memory exports are **historical April 2026 fixtures**; prepare current daily/weekly notes before asking for a live briefing. Copying these Markdown files does not import canonical session history or create schedules.

## 6. Start and verify

```bash
docker compose up -d --no-build openclaw-gateway
docker compose ps
docker compose exec openclaw-gateway openclaw --version
docker compose exec openclaw-gateway openclaw config validate
docker compose exec openclaw-gateway openclaw health
docker compose exec openclaw-gateway openclaw skills check
docker compose exec openclaw-gateway python3 -c 'import requests, bs4; print(requests.__version__, bs4.__version__)'
docker compose exec openclaw-gateway gh --version
```

The reported OpenClaw version should be `2026.9.5`. `skills check` checks eligibility; a successful skill/model invocation is a separate check. To inspect startup, run `docker compose logs --tail=100 openclaw-gateway` privately.

For Telegram, DM your bot, inspect the request, and approve its code:

```bash
docker compose exec openclaw-gateway openclaw pairing list telegram
docker compose exec openclaw-gateway openclaw pairing approve telegram <CODE>
docker compose exec openclaw-gateway openclaw channels status --probe
```

Verify the sender before approval. When no command owner exists, the CLI's first approval also bootstraps that sender as the command owner. Channel pairing and browser device pairing are separate controls.

## 7. Access the Control UI through SSH

On your laptop, keep this tunnel running:

```bash
ssh -N -L 18789:127.0.0.1:18789 root@YOUR_VPS_IP
```

Open `http://localhost:18789/`, enter the gateway token in the connection settings, and retain browser device identity. If a pairing request appears:

```bash
docker compose exec openclaw-gateway openclaw devices list
docker compose exec openclaw-gateway openclaw devices approve <REQUEST_ID>
```

Approve the exact request after checking it. The 2026.9.5 UI opens with Home chat and the Sessions sidebar. Profile menu → Settings contains Gateway, Channels, Agents, and Automations. Agent files are under Settings → Agents → Files. Send a simple message, verify the response, and check the session's Execution permissions before testing writes or shell commands.

## Optional: OpenClaw-managed Tailscale Serve

This Linux-only variant provides private HTTPS and verified Tailscale identity for browser authentication. Keep the SSH tunnel path available while setting it up.

1. Install Tailscale on the VPS and laptop, join the same tailnet, and enable tailnet HTTPS certificates. On the VPS:

   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   tailscale up
   tailscale status
   ```

2. In `docker-compose.yml`, remove the gateway's entire `ports` block and add `network_mode: host`. Change the CLI service's `network_mode` to `host` too. In the shared `runtime-volumes` list, add:

   ```yaml
   - /var/run/tailscale:/var/run/tailscale
   - /usr/bin/tailscale:/usr/bin/tailscale:ro
   ```

   Verify that the binary exists at this path and is compatible with the container. These mounts give the gateway access to the host Tailscale daemon. They are part of the deployment's trust boundary.

3. Set `OPENCLAW_GATEWAY_BIND=loopback` in `.env`. Merge these fields into the existing `gateway` block in `/root/.openclaw/openclaw.json`, retaining its token and other settings:

   ```json5
   {
     gateway: {
       bind: "loopback",
       auth: { mode: "token", allowTailscale: true },
       tailscale: { mode: "serve" },
       controlUi: { allowedOrigins: ["https://YOUR-HOST.YOUR-TAILNET.ts.net"] },
     },
   }
   ```

4. Managed Serve needs operator permission on the Tailscale daemon for the gateway's host-mapped uid (1000 in this recipe). Inspect `getent passwd 1000`, assign operator rights to that account with `tailscale set --operator=<HOST_ACCOUNT>`, and verify the container can manage Serve. Granting these rights lets that account administer Tailscale on the host. If you cannot grant them, keep the SSH tunnel or use an externally managed proxy with token authentication.

5. Validate and recreate the container:

   ```bash
   docker compose config --quiet
   docker compose run --rm --no-deps --entrypoint node openclaw-gateway dist/index.js config validate
   docker compose up -d --no-build --force-recreate openclaw-gateway
   docker compose logs --tail=100 openclaw-gateway
   tailscale serve status
   ```

Open the private HTTPS URL from your tailnet-connected laptop. **Do not manually run `tailscale serve --bg ...18789` for this flow.** OpenClaw owns a foreground Serve claim pointing to a dedicated listener and verifies identity through `tailscale whois`. The ordinary gateway listener still requires gateway authentication. Verified managed Serve can skip the browser's bootstrap pairing round trip, but still requires browser device identity.

An existing route may conflict with managed Serve. Inspect the reported hostname, handler, and owner before changing it. A manually managed route to port 18789 is generic proxy ingress, requires narrow `trustedProxies` configuration and normal token/password auth, and does not become tokenless by setting `allowTailscale`.

If you restrict public SSH later, first verify a second SSH connection over the tailnet and a provider-console recovery path. Use your actual network interface and firewall rules. Ordinary `ssh root@<tailnet-host>` is SSH over Tailscale; it does not by itself enable the separate Tailscale SSH feature.

## Persistent state and backups

| Data | Default container location |
|---|---|
| Gateway config | `/home/node/.openclaw/openclaw.json` |
| Shared runtime state | `/home/node/.openclaw/state/openclaw.sqlite` |
| Per-agent sessions, transcripts, model auth, memory index | `/home/node/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite` |
| Persona, skills, Markdown notes | The configured workspace |
| Compatibility auth key material | `/home/node/.config/openclaw` (separate mount) |

Legacy JSON/JSONL artifacts can remain after migration. Their presence does not make them the active store. A workspace backup alone does not capture the runtime databases, credentials, devices, or automation state.

For a complete cold backup, stop every container/service writing these mounts, archive the full host state and external mounts, then restart. Include the Compose files, `.env`, Dockerfile, dependency pins, image digest or image export, and any added SSH/GitHub/Tailscale configuration. Keep the backup private, verify its checksum and extraction, and keep an off-VPS copy. Do not copy only live SQLite main files while WAL writes are active.

## Upgrading an existing installation

1. Record the **running** image digest and `openclaw --version`, mounts, config, and enabled jobs. The instructor's old `/root/openclaw` checkout stayed on 2026.7.1 after its image upgrade; its Git version does not identify the running runtime.
2. Make and verify a complete cold backup of the old image, state, external mounts, and deployment files. Preserve a matching image/state recovery point.
3. Build or pull the chosen pinned candidate. Rehearse against a restored copy with outbound channels, schedules, and hooks disabled and network isolated. Review Doctor's changes before cutover.
4. The 2026.7.1 → 2026.9.5 transition needs migration of legacy configuration/session policy and state. With all writers stopped, run the **candidate image** against the intended state copy:

   ```bash
   docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
     dist/index.js doctor --fix --non-interactive
   docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
     dist/index.js config validate
   ```

   Doctor mutates state. Expect `agents.list` → `agents.entries`, SQLite imports, exec-policy migration, and Tools notes merged into `AGENTS.md`. Inspect unreadable legacy auth sources rather than deleting them.
5. Recreate the gateway with the candidate, then verify version, readiness, model auth discovery, a model response, channels, skills, and intended scheduling. Confirm enabled jobs and delivery destinations before restoring unattended work.
6. If recovery is needed, stop the candidate and restore the **old image and its matching state together**. Swapping only the image after a database migration is not a complete rollback.

Routine later image replacements can run startup-safe migrations; do not assume every upgrade needs Doctor repair. Review that release's migration notes. Do not use `git pull`, an in-container package update, or an Atomic Update's private validation copy as a substitute for this Docker image and backup process.

## Operations and troubleshooting

Run these from this deployment directory:

```bash
# A shell in the existing gateway
docker compose exec openclaw-gateway bash

# CLI service, when the gateway is already running
docker compose run --rm openclaw-cli health

# Read-only diagnostics; review output privately
docker compose exec openclaw-gateway openclaw models status
docker compose exec openclaw-gateway openclaw security audit

# Apply env, image, mounts, or networking changes
docker compose up -d --no-build --force-recreate openclaw-gateway
```

A one-shot `compose run` **shares the configured bind mounts**. It is a separate process, not an isolated state copy. Never run destructive repair concurrently with the gateway.

- For config changes, validate first and follow restart requirements; `compose restart` does not reload `.env`.
- For missing model auth, inspect `models status` and use onboarding/auth commands. Do not grep credentials onto a teaching screen.
- For dashboard connection failures, check the SSH tunnel or managed Serve claim, exact allowed origin, auth, and browser identity.
- For skill eligibility failures, inspect `skills check` and verify dependencies in the actual execution environment. A separate agent sandbox needs its own Python/CLI dependencies.
- For Telegram reminders, verify job execution **and** delivery separately. See [automation examples](../automation/README.md).

## Release-pinned references

- [Docker installation](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/install/docker.md)
- [Managed Tailscale authentication](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/tailscale.md)
- [Workspace contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/agent-workspace.md)
- [Doctor migrations](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/cli/doctor/state-migrations.md)
- [Session permissions](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/permission-modes.md)
