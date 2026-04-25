# Building Integrated AI Agents with OpenClaw

Course materials for the O'Reilly live course on building, deploying, customizing, and securing self-hosted AI agents with OpenClaw.

## Repository layout

```
openclaw_course_code/
  workspaces/           Pre-built agent personas (one folder per archetype)
    personal-assistant/   Alfred — butler persona with full PKM + bundled skills
    coding-agent/         Coder — minimal engineer persona (Demo 7)
  deployment/          Take-home VPS deployment guide
  multi-agent/         Multi-agent config variant (Demo 7)
  demo_runbooks/       Step-by-step runbook for each live demo
  README.md            (this file)
```

The repo is organized **by asset type**, not by course module. Most assets show up across multiple modules — a workspace is used in the Module 1 opener, the Module 3 customization demo, and the Module 4 multi-agent demo — so asset-type layout avoids duplication.

The default topology is **one agent, one channel, one workspace**. That is what Demos 1 through 6 use, and it is what the `deployment/` guide sets up. The `multi-agent/` folder is an explicit variant for the Demo 7 use case where you want multiple agents on one gateway.

## Demo Index

Each demo has a runbook in `demo_runbooks/` and may pull assets from other folders. The live demos run against a VPS prepared before the course; the artifacts below are what you can take home and reproduce yourself.

| # | Demo | Module | Runbook | Key Files |
|---|---|---|---|---|
| 1 | OpenClaw in Action | M1 | [`demo_1_personal_assistant.md`](demo_runbooks/demo_1_personal_assistant.md) | [`workspaces/personal-assistant/`](workspaces/personal-assistant/) |
| 2 | VPS Deployment + Dashboard | M2 | [`demo_2_vps_and_dashboard.md`](demo_runbooks/demo_2_vps_and_dashboard.md) | [`deployment/hostinger-vps-guide.md`](deployment/hostinger-vps-guide.md) |
| 3 | Context Files Walkthrough | M3 | [`demo_3_context_files.md`](demo_runbooks/demo_3_context_files.md) | [`workspaces/personal-assistant/SOUL.md`](workspaces/personal-assistant/SOUL.md), [`IDENTITY.md`](workspaces/personal-assistant/IDENTITY.md), [`USER.md`](workspaces/personal-assistant/USER.md), [`AGENTS.md`](workspaces/personal-assistant/AGENTS.md), [`TOOLS.md`](workspaces/personal-assistant/TOOLS.md) |
| 4 | Adding a Custom Skill | M3 | [`demo_4_bring_over_skill.md`](demo_runbooks/demo_4_bring_over_skill.md) | [`workspaces/personal-assistant/skills/rental-search/`](workspaces/personal-assistant/skills/rental-search/) |
| 5 | Security Pitfalls + Guardrails | M4 | [`demo_5_security_pitfalls_and_guardrails.md`](demo_runbooks/demo_5_security_pitfalls_and_guardrails.md) | Live VPS demo (no repo artifact) |
| 6 | Proactive Automation (Cron + Heartbeat) | M4 | [`demo_6_proactive_automation.md`](demo_runbooks/demo_6_proactive_automation.md) | Live VPS config walk (no repo artifact) |
| 7 | Multi-Agent Personas | M4 | [`demo_7_multi_agent_personas.md`](demo_runbooks/demo_7_multi_agent_personas.md) | [`multi-agent/openclaw.json.example`](multi-agent/openclaw.json.example), [`workspaces/personal-assistant/`](workspaces/personal-assistant/), [`workspaces/coding-agent/`](workspaces/coding-agent/) |

## Folder reference

### `workspaces/`

Each subfolder is a complete, runnable OpenClaw workspace. Drop one into `~/.openclaw/workspace/` (single-agent) or wire it as an `agentId` under `agents.list[]` (multi-agent) and the agent boots with that persona, those skills, and that PKM scaffolding.

- **`personal-assistant/`** — Butler-style daily-driver ("Alfred"). File-based PKM (tasks, daily notes, weekly reviews, projects, freeform notes, reading tracker). Bundled skills: `notes-tasks`, `daily-briefing`, `nightly-review`, `weekly-review`, `books-tracker`, `rental-search`. Used as the running example throughout Modules 1 through 6.
- **`coding-agent/`** — Minimal engineer persona ("Coder"). Direct, terse, code-focused. Workspace holds one or more cloned git repos and the agent operates inside them. Bundled skills: `create-pr` (drafts title + summary/changes/test-plan body from the branch diff and runs `gh pr create`), `review-code` (structured review with Blockers / Suggestions / Nits / What's good sections, file-line references, review-only by default). Used as the second agent in the Module 4 multi-agent demo.

### `deployment/`

Take-home resources for deploying OpenClaw on a VPS. The Dockerfile and docker-compose.yml live in the OpenClaw repo itself; this folder provides the guide and environment template.

- `hostinger-vps-guide.md` — Step-by-step take-home VPS deployment guide
- `.env.template` — Required environment variables (placeholder values)

Other deployment paths mentioned in the course:

- **Hostinger one-click:** [OpenClaw VPS template](https://www.hostinger.com/vps/docker/openclaw) provisions a ready-to-go instance with no SSH or Docker knowledge needed.
- **Fast-path script:** The OpenClaw repo ships `docker-setup.sh`, which automates image build, token generation, onboarding, and gateway start.

### `multi-agent/`

Configuration variant for hosting multiple agents on one gateway. Used in the Module 4 multi-agent demo. Ships as a reference config plus a setup README — you bring your own workspaces (from `../workspaces/`) and two Telegram bot tokens.

- `openclaw.json.example` — Full annotated gateway config (two agents, two bindings, two Telegram accounts)
- `README.md` — What this is, how it differs from the default single-agent setup, and step-by-step instructions to run it yourself. Env vars are shared with the single-agent setup; see `deployment/.env.template` and add a second Telegram bot token alongside the first.

### `demo_runbooks/`

One runbook per live demo. Each runbook follows the same structure: Goals, Pre-flight Checklist, Demo Flow (step-by-step with narration), Timing, Failure Modes, and Post-Demo Notes. These are primarily for the instructor's delivery, but students can read them after the course to see exactly what was demonstrated and how to reproduce it.

## A note on skill scopes

OpenClaw supports two scopes for skills:

- **Workspace-bundled** (used throughout this repo). Skills live inside a workspace's `skills/` folder and ship with it. Use this when the skill is tightly coupled to the workspace's conventions (e.g., the personal-assistant's `daily-briefing` skill reads `notes/dailies/_template.md`, which only exists in that workspace).
- **System-installed** (not used in this repo's demos). Generic, reusable skills installed at the gateway level via `openclaw skills install <slug>` or pulled from ClawHub. Available to every agent on the gateway.

Every demo in this course is anchored to a specific workspace use case, so all the skills here are workspace-bundled. The system-installed pattern is taught conceptually in M3 but not exercised by these demos.

## Getting started

### Prerequisites

- A Linux VPS (Ubuntu / Debian) or local machine with Docker
- An LLM API key (Anthropic, OpenAI, or OpenRouter)
- Basic comfort with SSH and the command line

### Quick setup (single-agent default)

1. Clone this repository
2. Copy `deployment/.env.template` to `.env` and fill in your values
3. Follow the deployment guide in `deployment/hostinger-vps-guide.md`
4. Copy your chosen workspace template from `workspaces/` into `~/.openclaw/workspace/`

### Multi-agent setup

See `multi-agent/README.md` for the multi-agent variant (two agents, two Telegram bots, one gateway).

## Course modules

The 5-hour live course is structured into four modules. The repository is organized by asset type rather than by module, but here is the mapping:

- **Module 1:** The Integrated AI Agent and OpenClaw Architecture
- **Module 2:** Deployment Options and Going Live
- **Module 3:** The OpenClaw Workspace — Tailoring Your Agent
- **Module 4:** Security, Automation, and Real-World Workflows

See the Demo Index above for which runbooks and artifacts each module uses.

## Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [ClawHub Skills Registry](https://clawhub.ai)
