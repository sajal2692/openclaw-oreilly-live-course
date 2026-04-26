# Multi-Agent Setup (Demo 7)

Two agents on one gateway, each bound to its own Telegram bot. This is the config variant shown in Module 4's multi-agent demo. The default single-agent setup covered in Modules 1 through 3 is still the recommended starting point. This folder is for when you want to host multiple, fully-isolated personas on one gateway.

## What this setup looks like

```
Telegram @alfred_*_bot  ─┐
                         ├──>  OpenClaw Gateway  ──┬── agent: alfred (personal assistant persona)
Telegram @coder_*_bot   ─┘                         └── agent: coder (engineer persona)
```

- **One gateway**, one Docker container, one process.
- **Two independent agents**, each with its own workspace, auth, sessions, and memory.
- **Two Telegram bots**, routed to the correct agent by the `bindings` rules in `openclaw.json`.
- **Deterministic routing**: no ML inference. Which agent replies is pure config.

## How this differs from the default single-agent setup

| Aspect | Single-agent (default) | Multi-agent (this folder) |
|---|---|---|
| `agents.list` | One entry (or omitted; defaults to `main`) | Two entries, one per persona |
| `bindings` | Not needed (all messages go to the default agent) | Explicit rules, one per agent/channel |
| Telegram `accounts` | One `botToken` | `accounts.<id>.botToken` per bot |
| Workspace location | `~/.openclaw/workspace` | `~/.openclaw/workspace-<agentId>` per agent |
| DM pairing | Pair once | Pair each bot separately |

## Prerequisites

- OpenClaw gateway running (see `../deployment/linux-vps-guide.md` if you do not have one yet)
- Two Telegram bots created via `@BotFather` (the flow is `/newbot` → pick names → copy tokens)
- An LLM provider key (OpenRouter is the example; swap if you use Anthropic or OpenAI directly)
- Your numeric Telegram user ID (DM `@userinfobot` to get it)

## Setup

### 1. Copy workspaces into place

```bash
cp -r ../workspaces/personal-assistant ~/.openclaw/workspace-alfred
cp -r ../workspaces/coding-agent       ~/.openclaw/workspace-coder
```

### 2. Fill in the env file

The multi-agent setup reuses the single-agent `.env` from `deployment/.env.template`. Copy it if you have not already, then uncomment and fill in the two multi-agent bot tokens (already pre-staged as commented-out placeholders in the template):

```bash
cp ../deployment/.env.template .env
# In .env, uncomment and fill:
#   ALFRED_BOT_TOKEN=<Alfred's BotFather token>
#   CODER_BOT_TOKEN=<Coder's BotFather token>
# Also fill in OPENROUTER_API_KEY (or your provider key of choice) and the Telegram user ID
# placeholders. The single-agent TELEGRAM_BOT_TOKEN line above can stay commented out; the
# multi-agent variant uses the two named tokens instead.
```

These two var names match the `${ALFRED_BOT_TOKEN}` / `${CODER_BOT_TOKEN}` substitutions in `openclaw.example.json5`.

### 3. Apply the config

Point your gateway at `openclaw.example.json5` (either copy it to `~/.openclaw/openclaw.json` or merge its contents into your existing config). Make sure env substitutions are available when the gateway starts: in Docker this means exporting the env vars into the container; with a local gateway, source the `.env` before starting.

### 4. Restart the gateway

If you followed the [deployment guide](../deployment/linux-vps-guide.md), the gateway is running in Docker:

```bash
docker compose restart openclaw-gateway
```

For a native (non-Docker) install, use `openclaw gateway restart` instead. The two are not interchangeable: `docker compose restart` only acts on the container, and `openclaw gateway restart` only acts on a host-installed gateway process.

### 5. Pair both bots

With `dmPolicy: "pairing"`, the gateway will not respond to a bot until you approve a one-time pairing handshake. For each of the two bots:

1. **DM the bot** from your Telegram account (any message; `/start` is conventional). The bot replies with a pairing code:

   ```
   OpenClaw: access not configured.
   Your Telegram user id: 6291011783
   Pairing code: YWTEMLUY
   Ask the bot owner to approve with:
     openclaw pairing approve telegram YWTEMLUY
   ```

2. **Approve the code from the gateway host:**

   ```bash
   docker compose exec openclaw-gateway openclaw pairing approve telegram <CODE>
   ```

   (For a native non-Docker install, drop the `docker compose exec openclaw-gateway` prefix.)

3. **DM the bot again.** It should now respond as the configured agent.

Repeat for the second bot. Each bot needs its own pairing approval.

Verify routing is live:

```bash
docker compose exec openclaw-gateway openclaw agents list --bindings
```

You should see both `alfred` and `coder` agents, each with its Telegram binding.

## Try it out

- DM `@alfred_*_bot` → personal assistant replies in measured, formal tone.
- DM `@coder_*_bot` → terse engineer replies focused on code.

The two agents share only a gateway process and an LLM provider configuration; memory, sessions, and personas are isolated per agent.

If you also want the coder to push branches and open PRs against a real GitHub repo, see the optional section below.

## Beyond chat: git push and PR creation (optional)

The setup above gets you two agents chatting on Telegram, each with their own workspace. The coder agent will be able to read code, write code, and explain code inside its workspace. It will **not** be able to push a branch to GitHub or open a PR, because that requires extra infrastructure outside OpenClaw itself.

To reproduce Demo 7's live-fire (coder branches, commits, pushes, and opens a PR via `gh pr create`), three pieces are needed beyond the multi-agent config.

### 1. `gh` CLI inside the container

The `create-pr` skill shells out to `gh pr create`, which is not present in the base OpenClaw image. Edit the OpenClaw `Dockerfile` (the one in your cloned OpenClaw repo that `docker compose build` consumes per the [deployment guide](../deployment/linux-vps-guide.md)) and add this block before the `USER node` line:

```Dockerfile
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
  && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
  && apt-get update && apt-get install -y gh
```

Rebuild: `docker compose build`.

### 2. SSH key mounted into the container

So `git push` works over SSH. Generate a dedicated deploy key on the host, add it to the target repo (or a bot account with collaborator access), then mount it read-only via `docker-compose.yml`:

```yaml
services:
  openclaw-gateway:
    volumes:
      # ... existing mounts ...
      - ~/.openclaw-ssh:/home/node/.ssh:ro
```

Host side, populate `~/.openclaw-ssh/` with:

- `id_<keyname>` (mode `600`)
- `config` containing `Host github.com` / `User git` / `IdentityFile ~/.ssh/id_<keyname>`
- `known_hosts` (run `ssh-keyscan github.com` to populate)

All files owned by `1000:1000` (matches the OpenClaw image's `node` user; verify with `docker compose exec openclaw-gateway id node` if you built a custom image with a different UID) with directory mode `700`.

### 3. `GH_TOKEN` for `gh` CLI auth

`gh` authenticates via an env var inside the container. Create a bot GitHub account (keeps the demo distinct from your personal identity), add it as a collaborator on the target repo, generate a **classic** PAT with `repo` scope, and put it in `.env` as:

```bash
GH_TOKEN=ghp_...
```

**Why classic and not fine-grained?** Cross-account fine-grained PATs need resource-owner approval on the target repo, which is an extra friction step for a bot account setup. Classic PATs with narrow scope are simpler for single-repo bot agents.

### What this enables

With all three in place, the coder's `create-pr` skill can run end-to-end:

```
User (Telegram): "add a delete button to the habit-tracker app, open a PR when done"

Coder:
  ls ~/.openclaw/workspace-coder
  cd habit-tracker
  cat CLAUDE.md
  git checkout -b feat/delete-habit
  <edits src/App.tsx>
  git add . && git commit -m "add delete button for habits"
  git push -u origin feat/delete-habit
  gh pr create --title "..." --body "..."
  -> PR URL returned to user
```

None of this is multi-agent specific. It is "how to make any OpenClaw agent capable of pushing to GitHub". It lives here because Demo 7's payoff moment is a real PR.

## What about the other routing patterns?

The slides cover three patterns: per-channel, per-person, and group routing. This folder demos the per-channel pattern because it is the clearest live demo. The other two use the same `bindings` mechanism with different `match` fields:

- **Per-person routing** (same bot, different DMs → different agents): add `peer: { kind: "direct", id: "<sender_id>" }` to the match rule.
- **Group routing** (specific Telegram group → specific agent): add `peer: { kind: "group", id: "<group_chat_id>" }` to the match rule.

See the OpenClaw [Multi-Agent Routing docs](https://docs.openclaw.ai/concepts/multi-agent) for the full binding match-order reference.

## Files in this folder

- `openclaw.example.json5`: full gateway config (annotated). Two agents, two bindings, two Telegram accounts.
- `README.md`: this file. Env vars come from `../deployment/.env.template` (see Setup step 2).
