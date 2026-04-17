# Deploying OpenClaw on a Hostinger VPS

A step-by-step guide to getting OpenClaw running 24/7 on a Hostinger VPS with Docker.

## What You Will Have at the End

- A persistent OpenClaw Gateway running on your own VPS
- Docker-based deployment that survives reboots
- Secure remote access via SSH tunnel

## Prerequisites

- A Hostinger account with a VPS plan (4GB+ RAM recommended)
- An LLM API key (Anthropic, OpenAI, or Google)
- Basic comfort with SSH and the command line

## Fast Path (Optional)

OpenClaw ships a one-shot setup script that handles most of what's below automatically. After Step 3 (clone the repo), you can run:

```bash
cd ~/openclaw
./docker-setup.sh
```

The script builds the image, generates a gateway token, writes `.env`, runs `openclaw onboard` (model and channel setup), and starts the gateway via Docker Compose. After it finishes, follow Step 9 to access the Control UI and verify everything works.

The rest of this guide is the manual walkthrough. Slower, but useful if you want to understand each piece or customize the setup.

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

Create a `.env` file in the repository root. The course repo provides a fully commented starter at `deployment/.env.template` you can copy from (or use the snippet below directly):

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

After the gateway is running (Step 8), use `docker compose exec` instead to open a shell in the running container:

```bash
docker compose exec openclaw-gateway bash
```

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

Paste your gateway token when prompted. You should see the OpenClaw Control UI with WebChat.

Send a message via WebChat. If the agent responds, your deployment is working end-to-end (model auth from Step 7 + gateway from Step 8 + Control UI access from Step 9).

## What Persists Where

| Component | Location | Notes |
|-----------|----------|-------|
| Gateway config | `/root/.openclaw/` | Includes `openclaw.json`, tokens |
| Model auth | `/root/.openclaw/` | OAuth tokens, API keys |
| Agent workspace | `/root/.openclaw/workspace/` | SOUL.md, AGENTS.md, memory, skills |
| Sessions | `/root/.openclaw/` | Chat history |
| Docker image | Container filesystem | Rebuilt on `docker compose build` |

## Updating OpenClaw

```bash
cd ~/openclaw
git pull
docker compose build
docker compose up -d
```

## Highly Recommended: Use Tailscale Instead of SSH Tunnels

The SSH tunnel approach works, but it has downsides: the tunnel only stays active while the terminal running it is open, and you need to re-run the command each time your laptop sleeps or the terminal closes.

[Tailscale](https://tailscale.com) (free tier) creates a private network between your devices. Once set up, you can access the Control UI directly from your browser without managing tunnels. It also works from your phone, which is useful for testing messaging channels.

### Setup

Install Tailscale on your VPS (as root):

```bash
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
```

Follow the printed URL to authenticate the device. Install Tailscale on your laptop as well and join the same network. Note the VPS **Tailscale IP** (e.g., `100.x.y.z`).

Remove the `127.0.0.1:` prefix from both `ports` lines in `docker-compose.yml` and restart with `docker compose up -d`. That prefix restricts Docker's port forwarding to the host's loopback interface, which blocks Tailscale traffic too, so it needs to go. With UFW (below), only your Tailscale network can reach the port.

Access the Control UI directly, no tunnel needed:

```
http://TAILSCALE_IP:18789/
```

### Lock Down SSH to Tailscale Only

With Tailscale working, you can restrict SSH so only devices on your Tailscale network can connect:

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

Verify you can SSH via your Tailscale IP (`ssh root@TAILSCALE_IP`). Once confirmed, drop public SSH:

```bash
ufw delete allow in on eth0 to any port 22
```

Now the only way to reach the VPS is through your Tailscale network.

## Troubleshooting

- **Build fails with OOM**: Add swap or upgrade VPS plan
- **Cannot access Control UI**: Check your SSH tunnel is running (or Tailscale is connected on both sides), and that the gateway token is correct
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
