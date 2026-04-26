# Building Integrated AI Agents with OpenClaw

Course materials for the O'Reilly live course on building, deploying, customizing, and securing self-hosted AI agents with OpenClaw.

## Repository layout

```
openclaw_course_code/
  workspaces/           Pre-built agent personas (one folder per archetype)
    personal-assistant/   Alfred — personal assistant persona with full PKM + bundled skills
    coding-agent/         Coder — minimal engineer persona (Demo 7)
  deployment/          Take-home VPS deployment guide
  multi-agent/         Multi-agent config variant (Demo 7)
  README.md            (this file)
```

The repo is organized **by asset type**. Most assets show up across multiple modules — a workspace is used in the Module 1 opener, the Module 3 customization demo, and the Module 4 multi-agent demo — so an asset-type layout avoids duplication.

The default topology is **one agent, one channel, one workspace**. That is what Demos 1 through 6 use, and it is what the `deployment/` guide sets up. The `multi-agent/` folder is an explicit variant for the Demo 7 use case where you want multiple agents on one gateway.

## Demo Index

The live demos run against a VPS prepared before the course. The artifacts below are what you can take home and reproduce yourself.

| # | Demo | Module | Key Files |
|---|---|---|---|
| 1 | OpenClaw in Action | M1 | [`workspaces/personal-assistant/`](workspaces/personal-assistant/) |
| 2 | VPS Deployment + Dashboard | M2 | [`deployment/linux-vps-guide.md`](deployment/linux-vps-guide.md) |
| 3 | Context Files Walkthrough | M3 | [`workspaces/personal-assistant/SOUL.md`](workspaces/personal-assistant/SOUL.md), [`IDENTITY.md`](workspaces/personal-assistant/IDENTITY.md), [`USER.md`](workspaces/personal-assistant/USER.md), [`AGENTS.md`](workspaces/personal-assistant/AGENTS.md), [`TOOLS.md`](workspaces/personal-assistant/TOOLS.md) |
| 4 | Adding a Custom Skill | M3 | [`workspaces/personal-assistant/skills/rental-search/`](workspaces/personal-assistant/skills/rental-search/) |
| 5 | Security Pitfalls + Guardrails | M4 | Live VPS demo (no repo artifact) |
| 6 | Proactive Automation (Cron + Heartbeat) | M4 | Live VPS config walk (no repo artifact) |
| 7 | Multi-Agent Personas | M4 | [`multi-agent/openclaw.example.json5`](multi-agent/openclaw.example.json5), [`workspaces/personal-assistant/`](workspaces/personal-assistant/), [`workspaces/coding-agent/`](workspaces/coding-agent/) |

## How to use this repo

This repo is a take-home companion to the live course. It bundles the deployment guide, the agent personas, and the demo artifacts so you can stand up your own OpenClaw gateway and reproduce what was demonstrated.

### Prerequisites

- A Linux VPS (Ubuntu / Debian) or a local machine with Docker
- An LLM API key (Anthropic, OpenAI, or OpenRouter)
- Basic comfort with SSH and the command line

### Default flow (single-agent)

1. **Deploy a gateway.** Follow [`deployment/linux-vps-guide.md`](deployment/linux-vps-guide.md) end-to-end. The base path uses an SSH tunnel; the optional Tailscale Serve section at the end is what was used on the demo VPS for the live course.

   Faster alternatives covered in the guide:
   - **Hostinger one-click** — [OpenClaw VPS template](https://www.hostinger.com/vps/docker/openclaw) provisions a ready-to-go instance with no SSH or Docker knowledge needed.
   - **Fast-path script** — the OpenClaw repo ships `docker-setup.sh`, which automates image build, token generation, onboarding, and gateway start.

2. **Pick a workspace.** Clone this course repo locally, then copy a `workspaces/` subfolder onto the VPS at `~/.openclaw/workspace/` (e.g. `scp -r workspaces/personal-assistant root@<vps>:/root/.openclaw/workspace`). Each subfolder is a complete, runnable OpenClaw workspace — drop it in and the agent boots with that persona, those skills, and that PKM scaffolding.

   - **[`personal-assistant/`](workspaces/personal-assistant/)** — Daily-driver personal assistant ("Alfred"). File-based PKM (tasks, daily notes, weekly reviews, projects, freeform notes, reading tracker). Bundled skills: `notes-tasks`, `daily-briefing`, `nightly-review`, `weekly-review`, `books-tracker`, `rental-search`. The running example throughout the course.
   - **[`coding-agent/`](workspaces/coding-agent/)** — Minimal engineer persona ("Coder"). Direct, terse, code-focused. Workspace holds one or more cloned git repos and the agent operates inside them. Bundled skills: `create-pr` (drafts title + summary/changes/test-plan body from the branch diff and runs `gh pr create`) and `review-code` (structured review with Blockers / Suggestions / Nits / What's good sections, file-line references, review-only by default). Used as the second agent in the Module 4 multi-agent demo.

3. **Customize.** Edit `SOUL.md`, `IDENTITY.md`, `USER.md`, `AGENTS.md`, and `TOOLS.md` inside your chosen workspace to fit your own context. The personal-assistant's `notes/` folder is plain markdown — re-use, replace, or wire your own PKM in. Bundled skills (e.g. `skills/rental-search/`) are self-contained, so copy and adapt them as templates for your own.

### Multi-agent variant

For Demo 7 (two agents on one gateway, each bound to a different Telegram bot), see [`multi-agent/README.md`](multi-agent/README.md). It walks through copying both workspaces into separate paths, generating two bot tokens, and merging the reference `openclaw.example.json5` into your gateway config. Stick with the single-agent default unless you want multiple agents on one gateway.

## Folder reference

- **[`workspaces/`](workspaces/)** — Pre-built agent personas (`personal-assistant/`, `coding-agent/`)
- **[`deployment/`](deployment/)** — VPS deployment guide and `.env.template`. The Dockerfile and `docker-compose.yml` live in the [OpenClaw repo](https://github.com/openclaw/openclaw) itself.
- **[`multi-agent/`](multi-agent/)** — Reference `openclaw.json` and setup README for hosting two agents on one gateway (Demo 7)

## Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [ClawHub Skills Registry](https://clawhub.ai)
