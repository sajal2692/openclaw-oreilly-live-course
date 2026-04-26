# Deploying OpenClaw on a Linux VPS

A step-by-step guide to getting OpenClaw running 24/7 on a Linux VPS with Docker.

**Works on other VPS providers too.** The setup is Docker-based, so any Linux VPS with Docker runs it. Hostinger is just the example provider — DigitalOcean, Linode, Hetzner, AWS Lightsail, and others all work the same way. Only Step 1 (provisioning) is provider-specific, and the public interface name in Step T7 (`eth0` vs `ens3`, etc.) may differ.

## What You Will Have at the End

- A persistent OpenClaw Gateway running on your own VPS
- Docker-based deployment that survives reboots
- Secure remote access via SSH tunnel
- Optional: HTTPS through Tailscale Serve with tokenless tailnet auth (recommended)

## Prerequisites

- A VPS with 4GB+ RAM (Hostinger, DigitalOcean, Hetzner, Linode, etc.)
- An LLM API key (Anthropic, OpenAI, OpenRouter, Gemini, or any other [supported provider](https://docs.openclaw.ai/providers))
- Basic comfort with SSH and the command line

## Fast Path (Optional)

Two faster alternatives to the manual walkthrough below.

**Hostinger one-click (Hostinger only).** The [OpenClaw VPS template](https://www.hostinger.com/vps/docker/openclaw) provisions a ready-to-go instance with OpenClaw pre-installed — no SSH or Docker knowledge needed. After provisioning, follow Step 9 to access the Control UI. If the template uses a different port or bind, follow its own documentation for accessing the Control UI.

**Setup script (any Docker-capable VPS).** OpenClaw ships a one-shot setup script that handles most of what's below automatically. After Step 3 (clone the repo), run:

```bash
cd ~/openclaw
./docker-setup.sh
```

The script builds the image, generates a gateway token, writes `.env`, runs `openclaw onboard` (model and channel setup), and starts the gateway via Docker Compose. After it finishes, run Steps T1–T7 to put the gateway behind Tailscale (recommended), or use the SSH tunnel from Step 9 for quick access.

The rest of this guide is the manual walkthrough. The fast paths above hide Docker, env, networking, and config behind one command — fine for getting started, but worth understanding before you reach for them, especially if you hit a misconfiguration later or move to a different provider.

## Step 1: Create Your VPS

1. Log in to Hostinger and go to the VPS section
2. Choose **Plain OS** and select **Ubuntu 24.04**
3. Set a strong **root password** and add your **SSH key** (recommended for smoother access)
4. Complete the setup and note your VPS **IP address** from the dashboard

## Step 2: Initial Server Setup

SSH into your VPS as root:

```bash
ssh root@YOUR_VPS_IP
```

Install Docker and essential packages:

```bash
apt-get update && apt-get install -y git curl ca-certificates
curl -fsSL https://get.docker.com | sh
```

Verify Docker is working:

```bash
docker --version
docker compose version
```

## Step 3: Clone OpenClaw and Create Directories

```bash
git clone https://github.com/openclaw/openclaw.git ~/openclaw
mkdir -p /root/.openclaw/workspace
chown -R 1000:1000 /root/.openclaw
```

The `chown` sets ownership to uid 1000, which matches the container's internal user (`node`).

## Step 4: Configure Environment Variables

```bash
cd ~/openclaw
```

Create a `.env` file in the repository root. The course repo provides a fully commented starter at [`deployment/.env.template`](https://github.com/sajal2692/openclaw-oreilly-live-course/blob/main/openclaw_course_code/deployment/.env.template) you can pull onto the VPS:

```bash
curl -fsSL https://raw.githubusercontent.com/sajal2692/openclaw-oreilly-live-course/main/openclaw_course_code/deployment/.env.template -o .env
nano .env
```

Or skip the template and create `.env` from scratch:

```bash
nano .env
```

Required variables:

```
OPENCLAW_IMAGE=openclaw:latest
OPENCLAW_GATEWAY_TOKEN=<generate with: openssl rand -hex 32>
OPENCLAW_GATEWAY_BIND=lan
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_CONFIG_DIR=/root/.openclaw
OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace
```

Optional, only if you plan to install the `gog` companion CLI (Gmail / Google Calendar skills, not covered in this course):

```
GOG_KEYRING_PASSWORD=<generate with: openssl rand -hex 32>
```

The template additionally has commented-out sections for model provider API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.) and channel tokens (`TELEGRAM_BOT_TOKEN`, `DISCORD_BOT_TOKEN`, etc.). Uncomment whatever you use.

Do not commit this file.

## Step 5: Update docker-compose.yml

The repository includes a Dockerfile but the `docker-compose.yml` needs a few edits.

```bash
nano docker-compose.yml
```

**Add** `build: .` and `env_file` to the `openclaw-gateway` service (right after the `image:` line):

```yaml
services:
  openclaw-gateway:
    image: ${OPENCLAW_IMAGE:-openclaw:local}
    build: .          # add this line
    env_file:         # add this line
      - .env          # add this line
    environment:
      ...
```

**Update** the `ports` section to bind to loopback only, so the gateway is not exposed to the public internet:

```yaml
    ports:
      - "127.0.0.1:${OPENCLAW_GATEWAY_PORT:-18789}:18789"
      - "127.0.0.1:${OPENCLAW_BRIDGE_PORT:-18790}:18790"
```

Both ports are bound to loopback to keep them off the public internet. Port `18789` is the gateway's main WebSocket and Control UI endpoint.

Leave everything else in the file unchanged.

**Why two layers?** `OPENCLAW_GATEWAY_BIND=lan` tells the gateway to listen on all interfaces *inside the container* — this is required so Docker's port-forwarding can reach it (setting it to `loopback` inside Docker breaks host-published access, per the [OpenClaw Docker docs](https://docs.openclaw.ai/install/docker#lan-vs-loopback-docker-compose)). The `127.0.0.1:` prefix on the host-side port mapping is what actually keeps the port off the public internet. Both layers matter: without the prefix, Docker publishes the port on `0.0.0.0` regardless of the internal bind.

## Step 6: Build the Image

```bash
docker compose build
```

## Step 7: Run Onboarding

Before starting the gateway, run `openclaw onboard` to configure your model provider, channels, workspace, and skills in one guided flow. We do this in a one-shot temp container (`docker compose run --rm`) so the config is fully written to `~/.openclaw/` before the long-lived gateway boots in Step 8. That way the gateway starts cleanly with everything in place: channels active, agents defined, model auth wired.

```bash
docker compose run --rm openclaw-gateway bash
openclaw onboard --skip-daemon --skip-health
exit
```

The onboarding wizard walks you through:

- **Model and auth** — pick a provider (Anthropic, OpenAI, OpenRouter, Gemini, etc.) and paste your API key. This replaces having to run `openclaw models auth add` separately later.
- **Workspace** — defaults to `~/.openclaw/workspace`. Accept the default or point at a custom workspace (e.g., one of the templates from `workspaces/` in this repo).
- **Gateway** — confirm port, bind, and auth settings (these are already set via `.env`, so just accept).
- **Channels** — optionally add Telegram, Discord, Slack, etc. Bot tokens go in here.
- **Skills** — install any optional dependencies for skills you want active.

The two flags above are specific to this Docker-on-VPS setup:

- `--skip-daemon` — skip the systemd / launchd service install. We use Docker Compose for the gateway lifecycle.
- `--skip-health` — skip the gateway-start and health-check step. We start the gateway in Step 8 via Docker Compose.

**Where are my files?** The container's working directory is `/app` (the OpenClaw source code). Your configuration and workspace are at `/home/node/.openclaw/` inside the container, which maps to `/root/.openclaw/` on the host. You can edit files from either side; they are the same files.

## Step 8: Launch and Verify

```bash
docker compose up -d
docker compose logs -f openclaw-gateway
```

You should see:

```
[gateway] listening on ws://0.0.0.0:18789
```

Press `Ctrl+C` to stop following the logs. The gateway continues running in the background.

## Step 9: Access the Control UI

The gateway is bound to loopback and not exposed to the public internet. To access it from your laptop, open an SSH tunnel in a new terminal:

```bash
ssh -N -L 18789:127.0.0.1:18789 root@YOUR_VPS_IP
```

Then open in your browser:

```
http://localhost:18789/
```

Paste your gateway token when prompted. This is the value of `OPENCLAW_GATEWAY_TOKEN` from `.env`. You should see the OpenClaw Control UI with WebChat.

Send a message via WebChat. If the agent responds, your deployment is working end-to-end (model auth from Step 7 + gateway from Step 8 + Control UI access from Step 9).

## Recommended: Tailscale Serve for HTTPS and Tokenless Auth

The SSH tunnel approach in Step 9 works, but Tailscale Serve gives you HTTPS, tokenless dashboard auth via tailnet identity, and removes the need to keep an SSH tunnel running. This is also the configuration used on the demo VPS for the live course.

[Tailscale](https://tailscale.com) (free tier) creates a private WireGuard mesh between your devices. **Tailscale Serve** proxies HTTPS traffic from your tailnet hostname to a loopback port on the VPS — so the gateway stays bound to loopback, and Tailscale handles encryption, identity, and routing.

### Step T1: Install Tailscale and enable HTTPS

On the VPS (as root):

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

Follow the printed URL to authenticate the device. Install Tailscale on your laptop as well and join the same tailnet. Note the VPS's **MagicDNS hostname** (e.g., `my-vps.tail-xxxx.ts.net`); you can find it in the Tailscale admin console or by running `tailscale status` on the VPS.

In the [Tailscale admin console](https://login.tailscale.com/admin/dns), enable **HTTPS Certificates** for your tailnet (DNS settings, "Enable HTTPS" toggle). Tailscale will provision a Let's Encrypt cert for your MagicDNS hostname.

### Step T2: Switch the gateway to host networking

In `docker-compose.yml`, the `openclaw-gateway` service needs three changes from the Step 5 layout:

1. Replace the `ports:` block with `network_mode: host` (so the container shares the host's network namespace and "loopback inside the container" is the same as `127.0.0.1` on the host).
2. Bind-mount the Tailscale CLI and socket so the gateway can call `tailscale whois` to verify the tailnet identity of incoming requests.
3. Change the `openclaw-cli` service from `network_mode: "service:openclaw-gateway"` to `network_mode: host` so it joins the same host namespace.

```yaml
  openclaw-gateway:
    image: ${OPENCLAW_IMAGE:-openclaw:local}
    build: .
    env_file:
      - .env
    network_mode: host    # replaces the `ports:` block from Step 5
    volumes:
      - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
      - /var/run/tailscale:/var/run/tailscale       # add
      - /usr/bin/tailscale:/usr/bin/tailscale:ro    # add
    # ... rest of service unchanged; remove the `ports:` block entirely
```

Apply change #3 to the `openclaw-cli` block as well:

```yaml
  openclaw-cli:
    image: ${OPENCLAW_IMAGE:-openclaw:local}
    network_mode: host    # was: network_mode: "service:openclaw-gateway"
    # ... rest of service unchanged
```

Both Tailscale bind-mounts are safe to add: the Tailscale socket is `0666` and the binary is a statically linked Go executable.

### Step T3: Switch the gateway bind mode to loopback

In `.env`, change:

```
OPENCLAW_GATEWAY_BIND=loopback
```

With host networking, `loopback` means the host's `127.0.0.1`. The gateway is no longer reachable from any non-loopback interface — only Tailscale Serve can proxy to it.

### Step T4: Enable tokenless tailnet auth

Edit `/root/.openclaw/openclaw.json` and merge the fields below into the existing `gateway` block. Do not paste over the whole file: `openclaw.json` already has many other keys (model auth, agents, channels) that must stay intact. If you have a coding agent like Claude Code or Cursor handy, ask it to merge these fields into the existing file. Otherwise, edit by hand and add only the new keys (`auth.allowTailscale`, `controlUi.allowedOrigins`, `trustedProxies`) without disturbing what is already there.

Replace the hostname in `allowedOrigins` with your own MagicDNS hostname (with `https://` and no trailing slash). For example, if `tailscale status` shows `my-vps.tail-a1b2.ts.net`, the origin is `https://my-vps.tail-a1b2.ts.net`.

```json
{
  "gateway": {
    "auth": {
      "mode": "token",
      "token": "<your existing token>",
      "allowTailscale": true
    },
    "controlUi": {
      "allowedOrigins": [
        "https://<hostname>.<tailnet>.ts.net"
      ]
    },
    "trustedProxies": ["127.0.0.1/32", "::1/128"]
  }
}
```

What each piece does:

- `auth.allowTailscale: true` lets the gateway accept Tailscale identity headers (`tailscale-user-login`) instead of a token, but only when the request arrived via Tailscale Serve (loopback socket plus Tailscale's forwarded headers, verified against `tailscale whois`). The gateway token is still kept for non-browser clients (CLI, channels).
- `controlUi.allowedOrigins` is a strict allowlist; the dashboard refuses WebSocket upgrades whose `Origin` header is not on the list. Add your tailnet HTTPS URL.
- `trustedProxies` tells the gateway that 127.0.0.1 is a trusted proxy (Tailscale Serve, running on the same host). Without this, the gateway logs a "proxy headers from untrusted address" warning on every Serve request.

### Step T5: Restart the gateway and start Tailscale Serve

```bash
cd ~/openclaw
docker compose up -d --force-recreate openclaw-gateway
tailscale serve --bg --https=443 http://127.0.0.1:18789
tailscale serve status
```

`--force-recreate` ensures the gateway container is rebuilt with the new `network_mode: host` and the Tailscale bind-mounts. Without it, compose sometimes keeps the old container if it thinks the service definition has not changed.

The status output should look like:

```
https://<hostname>.<tailnet>.ts.net (tailnet only)
|-- / proxy http://127.0.0.1:18789
```

> Tailscale Serve persists across reboots once configured this way. As an alternative, OpenClaw can manage Serve itself by setting `gateway.tailscale.mode: "serve"` in `openclaw.json`; the manual command above is shown here because it makes the proxy chain visible and easy to inspect with `tailscale serve status`.

### Step T6: Approve the first device pairing

Open `https://<hostname>.<tailnet>.ts.net/` in your browser. You will see a "pairing required" prompt — this is expected on the first connection from any new browser.

Approve it once from inside the gateway container:

```bash
docker compose exec openclaw-gateway openclaw devices pending
docker compose exec openclaw-gateway openclaw devices approve <requestId>
```

Reload the browser tab. You should land in the Control UI directly, no token prompt — your tailnet identity authenticates the connection, and the device is now paired.

**Why pairing is required:** OpenClaw's dashboard binds to the browser's persistent device identity (a key pair stored in IndexedDB). Tokenless tailnet auth replaces only the *shared-secret* layer; device pairing is a separate layer that always applies. The first browser hit creates a pending request, and one CLI approval is all you need per browser. Pairing survives reloads, restarts, and reboots.

### Step T7: Lock SSH down to Tailscale only

A public SSH port on the open internet is constantly scanned. Bots sweep the IPv4 space looking for port 22, then attempt credential stuffing, brute force against weak passwords, and exploits against unpatched `sshd` versions. Even with key-only auth, the surface is constant noise in your logs and a single misconfigured password (or a future `sshd` CVE) is all it takes to lose the box.

Putting SSH behind Tailscale removes that surface entirely. With UFW dropping all non-`tailscale0` traffic, port 22 simply does not respond to the public internet — there is nothing for bots to attack. Only devices that have authenticated to your tailnet (with WireGuard keys tied to your identity provider) can even reach the port. Tailscale's own auth runs underneath SSH, so an attacker would have to compromise your tailnet identity *and* your SSH credentials to get a shell.

This matters especially if SSH password auth is enabled on the VPS. With public SSH, a weak password is a brute-force target around the clock. Behind Tailscale, the password never sees the public internet at all.

To restrict SSH to your tailnet:

```bash
apt-get install -y ufw

# Allow all traffic over Tailscale
ufw allow in on tailscale0

# Keep public SSH as a fallback until you verify Tailscale SSH works
ufw allow in on eth0 to any port 22

ufw default deny incoming
ufw default allow outgoing
ufw enable
```

Verify Tailscale SSH from your laptop (MagicDNS resolves the hostname automatically — no IP needed):

```bash
ssh root@<hostname>
```

Once confirmed, drop the public-SSH fallback rule:

```bash
ufw delete allow in on eth0 to any port 22
```

The VPS is now reachable only through your tailnet. Both SSH and the dashboard are gated by tailnet identity, and the gateway never exposes a port on a public interface.

## What Persists Where

| Component | Location | Notes |
|-----------|----------|-------|
| Gateway config | `/root/.openclaw/` | Includes `openclaw.json`, tokens |
| Model auth | `/root/.openclaw/` | OAuth tokens, API keys |
| Agent workspace | `/root/.openclaw/workspace/` | SOUL.md, AGENTS.md, memory, skills |
| Sessions | `/root/.openclaw/` | Chat history |
| Docker image | Container filesystem | Rebuilt on `docker compose build` |

**Back up `~/.openclaw/`.** Everything important — workspace, sessions, model credentials, gateway tokens, paired devices — lives there. Periodically copy it off the VPS (rsync to another host, or scp to your laptop) so you can rebuild from scratch without losing state. The Docker image is reproducible from `docker compose build`; `~/.openclaw/` is not.

## Updating OpenClaw

```bash
cd ~/openclaw
git pull
docker compose build
docker compose up -d
```

If `git pull` reports a conflict on `docker-compose.yml`, that is your local edits from Step 5 (and Step T2 if you took the Tailscale path) clashing with upstream changes. `git stash`, pull, then reapply your edits, or resolve the conflict by hand.

## Troubleshooting

- **Build fails with OOM**: Add swap or upgrade VPS plan
- **Cannot access Control UI (SSH-tunnel path)**: Check your SSH tunnel is running and the gateway token is correct
- **Cannot access Control UI (Tailscale Serve path)**: Check Tailscale is connected on both sides (`tailscale status`), `tailscale serve status` shows the proxy entry, and your tailnet HTTPS hostname is listed in `gateway.controlUi.allowedOrigins`
- **`tailscale serve` fails with a certificate error**: HTTPS Certificates were just enabled in the admin console and Let's Encrypt has not finished provisioning the cert yet. Wait a minute and rerun the command.
- **Dashboard loads but the WebSocket immediately closes**: The tailnet hostname is missing from `gateway.controlUi.allowedOrigins`, or the entry has a trailing slash or the wrong scheme (`http://` instead of `https://`). The check is exact-match.
- **"pairing required" on the dashboard**: Expected on the first browser connection per device. Approve once: `docker compose exec openclaw-gateway openclaw devices pending` then `... openclaw devices approve <requestId>`
- **Gateway not starting**: Check logs with `docker compose logs -f openclaw-gateway`
- **Model auth fails**: Re-run `openclaw models auth add` inside the container (or re-run `openclaw onboard` to step through everything again)

## Quick Notes and Handy Commands

### Enter a shell inside the running container

```bash
cd ~/openclaw
docker compose exec openclaw-gateway bash
```

Use `exec` when the gateway is already running (it attaches to the live container). Use `docker compose run --rm openclaw-gateway bash` only when the gateway is stopped; `run` creates a new temporary container that will not share state with a running gateway.

### Find where a credential or config value is stored

`openclaw onboard` and `openclaw models auth add` write credentials to different files depending on the provider and flow. If you cannot find a value in `openclaw.json`, grep the whole `.openclaw` directory:

```bash
# Search for a specific key prefix (e.g., OpenRouter keys start with sk-or-)
grep -r "sk-or-" ~/.openclaw/ 2>/dev/null

# Search case-insensitively for a provider name
grep -ri "openrouter" ~/.openclaw/ 2>/dev/null
```

Auth profiles created by `onboard` typically live in `~/.openclaw/agents/<agent-id>/auth-profiles.json`. The main config is in `~/.openclaw/openclaw.json`, and environment variables can be added to `~/.openclaw/.env`.

### View live gateway logs

```bash
docker compose logs -f openclaw-gateway
```

### Restart the gateway

```bash
docker compose restart openclaw-gateway
```

### Add a messaging channel

OpenClaw ships an interactive wizard for adding messaging channel accounts (Telegram, Discord, Slack, Signal, iMessage, etc.). Run it from inside the container:

```bash
docker compose exec openclaw-gateway bash
openclaw channels add
```

The wizard prompts for the channel, credentials (bot token, private key, etc.), an optional display name, and can bind the account to a specific agent in one step.

Non-interactive form (useful for scripts):

```bash
openclaw channels add --channel telegram --token <bot-token>
```

Check status and tail logs:

```bash
openclaw channels list
openclaw channels status
openclaw channels logs --channel all
```

See per-channel setup notes in the [OpenClaw channel docs](https://docs.openclaw.ai/channels).
