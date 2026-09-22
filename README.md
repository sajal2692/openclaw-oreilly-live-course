# Building Integrated AI Agents with OpenClaw

Course materials for the O'Reilly live course on building, deploying, customizing, and securing self-hosted AI agents with OpenClaw.

**Course baseline: OpenClaw 2026.9.5.** The repository examples target this exact release. See the [compatibility notes](docs/compatibility-2026.9.5.md) for migration guidance and setup checks.

## Repository layout

```
openclaw_course_code/
  workspaces/           Pre-built agent personas (one folder per archetype)
    personal-assistant/   Alfred, personal assistant with PKM and bundled skills
    coding-agent/         Coder, minimal engineer persona (Demo 6)
  deployment/          Pinned Docker recipe and take-home VPS guide
  multi-agent/         Multi-agent config variant (Demo 6)
  automation/          Opt-in reminders, heartbeat scratch, and webhook examples
  security/            Current permission and isolation guidance
  README.md            (this file)
```

The repo is organized **by asset type**. A workspace appears in the Module 1 opener, Module 3 customization, and Module 4 multi-agent demo.

The default topology is **one agent, one channel, one workspace**. That is what Demos 1 through 5 use, and it is what the `deployment/` guide sets up. The `multi-agent/` folder is an explicit variant for the Demo 6 use case where you want multiple agents on one gateway.

## Demo Index

The live demos run against a VPS prepared before the course. The artifacts below are what you can take home and reproduce yourself.

| # | Demo | Module | Key Files |
|---|---|---|---|
| 1 | OpenClaw in Action | M1 | [`workspaces/personal-assistant/`](workspaces/personal-assistant/) |
| 2 | VPS Deployment + Dashboard | M2 | [`deployment/linux-vps-guide.md`](deployment/linux-vps-guide.md) |
| 3 | Context Files Walkthrough | M3 | [`workspaces/personal-assistant/SOUL.md`](workspaces/personal-assistant/SOUL.md), [`IDENTITY.md`](workspaces/personal-assistant/IDENTITY.md), [`USER.md`](workspaces/personal-assistant/USER.md), [`AGENTS.md`](workspaces/personal-assistant/AGENTS.md) |
| 4 | Adding a Custom Skill | M3 | [`workspaces/personal-assistant/skills/rental-search/`](workspaces/personal-assistant/skills/rental-search/) |
| 5 | Security Pitfalls + Guardrails | M4 | Live VPS demo; [permission and isolation notes](security/README.md) |
| 6 | Multi-Agent Personas | M4 | [`multi-agent/openclaw.example.json5`](multi-agent/openclaw.example.json5), [`workspaces/personal-assistant/`](workspaces/personal-assistant/), [`workspaces/coding-agent/`](workspaces/coding-agent/) |

## How to use this repo

This repo is a take-home companion to the live course. It bundles the deployment guide, the agent personas, and the demo artifacts so you can stand up your own OpenClaw gateway and reproduce what was demonstrated.

### Prerequisites

- A Linux VPS (Ubuntu / Debian) or a local machine with Docker
- An LLM API key (Anthropic, OpenAI, or OpenRouter)
- Basic comfort with SSH and the command line

### Default flow (single-agent)

1. **Deploy a gateway.** Follow [the VPS guide](deployment/linux-vps-guide.md). It uses the pinned official image with Python and GitHub CLI added for course skills, private SSH-tunnel access, and an optional OpenClaw-managed Tailscale Serve path.
2. **Copy a workspace's contents** to the configured mounted directory using the guide's commands. Customize `SOUL.md`, `IDENTITY.md`, `USER.md`, and `AGENTS.md`. Tool notes now live in the Tools section of `AGENTS.md`.
3. **Verify the environment.** Check config, model auth, channel pairing, skill eligibility, and the active session permissions. Copying a skill does not install its dependencies or grant access to tools.
4. **Prepare your data.** Personal-assistant notes and memory exports are historical April 2026 fixtures. Customize the persona and recipient IDs, then create current daily/weekly data. These files do not install schedules or import active SQLite session history.

The personal-assistant workspace includes `notes-tasks`, `daily-briefing`, `nightly-review`, `weekly-review`, `books-tracker`, and `rental-search`. The coding-agent workspace includes `review-code` and `create-pr`. When requested, `create-pr` pushes the feature branch and creates the PR; merging remains a separate action.

### Multi-agent variant

For Demo 6 (two agents on one gateway, each bound to a different Telegram bot), see [`multi-agent/README.md`](multi-agent/README.md). It walks through copying both workspaces into separate paths, generating two bot tokens, and merging the reference `openclaw.example.json5` into your gateway config. Stick with the single-agent default unless you want multiple agents on one gateway.

## Folder reference

- **[`workspaces/`](workspaces/)**: Pre-built agent personas (`personal-assistant/`, `coding-agent/`)
- **[`deployment/`](deployment/)**: VPS guide, Compose recipe, course Dockerfile, env template, and single-agent config.
- **[`multi-agent/`](multi-agent/)**: Current `agents.entries` config and setup for two agents on one gateway (Demo 6).
- **[`automation/`](automation/)**: Opt-in scheduled reminders, heartbeat scratch, and inbound webhook examples.
- **[`security/`](security/)**: Session permissions, shared-container boundaries, and exercises using synthetic data.

## Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [ClawHub Skills Registry](https://clawhub.ai)
