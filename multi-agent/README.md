# Multi-Agent Setup (Demo 6)

Two agents share one OpenClaw 2026.9.5 gateway, with a separate Telegram bot and workspace for each. Alfred is the personal assistant; Coder works in cloned repositories. Separate agent IDs partition persona and runtime state. **They do not create an operating-system security boundary.**

## Architecture and configuration

- `agents.entries` is a map keyed by agent ID. The old `agents.list` array needs Doctor migration.
- `agents.ownership: "explicit"` names the current ownership model. Each Telegram account has a binding, and Alfred owns system-agent operations. Add bindings for any new channels; an unbound multi-agent route can require an explicit agent selection.
- Each agent has a workspace and canonical state at `~/.openclaw/agents/<agentId>/agent/openclaw-agent.sqlite`.
- `bindings` route incoming messages by channel/account. More specific matches take precedence; the sample's two account matches are disjoint.
- The reference keeps session-tool visibility within each agent and disables ordinary cross-agent session access. Files, environment credentials, and mounts remain shared within the container.
- `tools.exec.mode: "ask"` is the sample's guarded default. Session Execution permissions, host approval policy, tool availability, and sandbox policy also affect a command. Switching to Full Access requires an explicit administrator choice.
- The outer Docker container hosts both agents. A real boundary between mutually untrusted agents needs separate restricted execution environments or gateways. `tools.fs.workspaceOnly` scopes managed file tools and does not contain unrestricted shell commands.

Alfred uses OpenRouter Sonnet 4.6, and Coder uses direct Anthropic Sonnet 5 with OpenRouter fallback. Model choice is independent of the 2026.9.5 config migration; verify that your accounts can access the selected models.

## Prerequisites

Complete the [deployment guide](../deployment/linux-vps-guide.md), create two bots with `@BotFather`, and obtain the provider keys used by the sample. Commands below run on the VPS from `~/openclaw-course/deployment`.

## 1. Copy the workspace contents

For new destination directories:

```bash
cd ~/openclaw-course/deployment
mkdir -p /root/.openclaw/workspace-alfred /root/.openclaw/workspace-coder
cp -a ../workspaces/personal-assistant/. /root/.openclaw/workspace-alfred/
cp -a ../workspaces/coding-agent/. /root/.openclaw/workspace-coder/
chown -R 1000:1000 /root/.openclaw/workspace-alfred /root/.openclaw/workspace-coder
```

Merge carefully if those directories already contain work. These locations sit under the existing state mount, so both are visible in the gateway. Customize the Tools section of each `AGENTS.md`; Alfred's account ID is `alfred` in this variant, rather than `default` in the single-bot setup.

## 2. Add secrets to the active environment

Edit the existing `deployment/.env`. Merge the values from [the multi-agent env template](.env.template): `ALFRED_BOT_TOKEN`, `CODER_BOT_TOKEN`, `OPENROUTER_API_KEY`, and `ANTHROPIC_API_KEY`. Preserve the gateway token, image, and mount paths. Avoid keeping an old single-bot token/account enabled alongside the same named bot.

## 3. Merge the reference config

Merge [openclaw.example.json5](openclaw.example.json5) into `/root/.openclaw/openclaw.json`. Preserve gateway auth/network settings and provider credentials. For the fresh take-home setup, deliberately replace the old `main` roster entry with `alfred` and `coder`, and set the two bindings and Telegram accounts. Remove obsolete single-agent routing after checking it.

For an existing installation with history, keep its agent IDs and explicit workspace paths instead of renaming them. Renaming `main` to `alfred` does not move canonical sessions or credentials. Adapt this sample to the existing IDs and run Doctor on a backed-up migration when required.

The configuration fragment is not a standalone replacement for all onboarding output. In particular, copying it over the entire config can discard gateway auth or provider settings.

## 4. Validate and recreate

After editing `.env`, recreate the gateway to pick up the new variables:

```bash
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config validate
docker compose up -d --no-build --force-recreate openclaw-gateway
docker compose exec openclaw-gateway openclaw agents list --bindings
docker compose exec openclaw-gateway openclaw models status --agent alfred
docker compose exec openclaw-gateway openclaw models status --agent coder
docker compose exec openclaw-gateway openclaw channels status --probe
```

`docker compose restart` retains the old container environment. For a native installation, use its native lifecycle commands; Docker owns the process in this guide.

## 5. Pair each bot

DM Alfred's bot and approve its pending code after checking your sender identity:

```bash
docker compose exec openclaw-gateway openclaw pairing list telegram --account alfred
docker compose exec openclaw-gateway openclaw pairing approve telegram <ALFRED_CODE> --account alfred
```

Repeat for Coder using `--account coder` and its code. If `commands.ownerAllowFrom` is empty, the first CLI pairing approval also establishes the command owner. Pairing grants channel access; it does not provide filesystem containment.

DM each bot again and confirm the expected persona. Verify the resolved model, workspace, and session permissions in the Control UI before asking Coder to edit a repository.

## Git push and PR creation

The course image already includes `git` and `gh`. PR creation additionally needs credentials and a repository:

1. Use a dedicated GitHub identity/token scoped to the intended repository. Grant Contents and Pull requests write access. Keep it out of workspace Markdown and version control.
2. Set `GH_TOKEN` in the active `.env`, recreate the container, and verify `gh auth status` privately. A shared env token is available to both agents. Separate workspace names do not protect it.
3. Use an HTTPS Git remote and configure Git to use the token-aware `gh` credential helper. Persist that helper in the repository's `.git/config`, which lives under the mounted workspace:

   ```bash
   docker compose exec -w /home/node/.openclaw/workspace-coder openclaw-gateway bash
   # Replace OWNER/REPO and example-repo before running.
   gh repo clone OWNER/REPO example-repo
   cd example-repo
   git config --local credential.https://github.com.helper ''
   git config --local --add credential.https://github.com.helper '!gh auth git-credential'
   git config --local user.name 'Your Bot Name'
   git config --local user.email 'YOUR_BOT_EMAIL'
   git ls-remote origin HEAD
   exit
   ```

The helper contains a command, not the token. Do not put a token in a remote URL. This setup survives container recreation because the repo configuration persists; an unmounted home-directory Git config may not. SSH transport is also possible with separately managed keys, verified host keys, permissions, and mounts, but `GH_TOKEN` alone does not authenticate an SSH remote.

When the user asks for a PR, the bundled `create-pr` skill pushes the current feature branch and opens the PR. It leaves merging, force pushes, branch deletion, and direct pushes to `main` or `master` for separate explicit decisions. Coder may still need an exec approval under the active session policy.

Try the workflow with a disposable repository. Confirm the diff and tests before pushing, then review the returned PR. Verify that the branch and PR appear in the intended GitHub repository.

## Further patterns

This example covers channel/account routing. Peer/group bindings, specialist teams, and agent-to-agent delegation are additional designs. Enable them deliberately; the sample preserves independently routed course personas.

- [Multi-agent routing](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/multi-agent.md)
- [Session permissions](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/permission-modes.md)
- [Security boundaries](../security/README.md)
- [Automation and delivery](../automation/README.md)
