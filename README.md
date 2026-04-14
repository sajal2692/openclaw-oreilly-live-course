# Building Integrated AI Agents with OpenClaw

Course materials for the O'Reilly live course on building, deploying, customizing, and securing self-hosted AI agents with OpenClaw.

## How This Repository is Organized

The repository is organized **by asset type**, not by course module. Most assets are used across multiple modules (a workspace shows up in the M1 opener, the M3 customization demo, and the M4 closing showcase), so a module-based layout would force duplication or cross-references. Asset-type layout keeps each thing in one place and makes it obvious what to clone or copy when you want to use it.

```
openclaw_course_code/
  workspaces/          Pre-built agent workspace templates (one folder per archetype)
    personal-assistant/
      skills/          Workspace-bundled skills (PKM-coupled)
    coding-agent/
      (skills/ added when dev-coupled skills are built)
    data-analyst/
      (skills/ added when analytics-coupled skills are built)
  deployment/          VPS deployment templates (Dockerfile, compose, .env, configs)
  security/            Insecure vs hardened config comparison
  automation/          Cron and webhook examples
    cron/
  README.md
```

### A note on skill scopes

OpenClaw supports two scopes for skills:

- **Workspace-bundled** (used throughout this repo). Skills live inside a workspace's `skills/` folder and ship with it. Use this when the skill is tightly coupled to the workspace's conventions (e.g., the personal-assistant's `daily-briefing` skill reads `notes/dailies/_template.md`, which only exists in that workspace).
- **System-installed** (not used in this repo's demos). Generic, reusable skills installed at the gateway level via `openclaw skills install <slug>` or pulled from ClawHub. Available to every agent on the gateway.

Every demo in this course is anchored to a specific workspace use case, so all the skills here are workspace-bundled. The system-installed pattern is taught conceptually in M3 but not exercised by these demos.

## Demo Index

Each demo in the live course pulls from one or more of the folders above. This table maps demos to the assets they use.

| # | Demo | Module | Uses |
|---|---|---|---|
| 1 | OpenClaw in Action | M1 | `workspaces/personal-assistant` |
| 2 | VPS Setup Retrospective | M2 | `deployment/` |
| 3 | Control UI / Dashboard Walkthrough | M2 | (live, no shared assets) |
| 4 | Connect a Messaging Channel | M2 | (live, no shared assets) |
| 5 | Customize a Workspace | M3 | `workspaces/personal-assistant` |
| 6 | Build a Custom Skill | M3 | TBD (skill to be decided; will live under the relevant workspace's `skills/`) |
| 7 | Workspace Archetypes Showcase | M3 | `workspaces/*` |
| 8 | Security Pitfalls (Live Attack) | M4 | `security/openclaw-insecure.json` + `workspaces/personal-assistant` |
| 9 | Configure Guardrails | M4 | `security/openclaw-hardened.json` |
| 10 | Cron-Driven Daily Briefing | M4 | `automation/cron/` + `workspaces/personal-assistant` |
| 11 | Closing Archetypes Recap | M4 | `workspaces/*` |

## Folder Reference

### `workspaces/`

Each subfolder is a complete, runnable OpenClaw agent workspace. Drop one into `~/.openclaw/workspace/` (or wire as a multi-agent binding) and the agent boots with that persona, those skills, and that PKM scaffolding.

- **`personal-assistant/`** — Butler-style daily-driver. File-based PKM (tasks, daily notes, weekly reviews, projects, freeform notes, reading tracker). Bundled skills: `notes-tasks`, `daily-briefing`, `nightly-review`, `weekly-review`, `books-tracker`. Used as the running example throughout the course.
- **`coding-agent/`** — Developer-focused assistant. Code review, git workflow, testing patterns.
- **`data-analyst/`** — Analytical, data-focused. Pandas, SQL, charting workflows.

### `deployment/`

Everything you need to deploy OpenClaw on a VPS.

- **`Dockerfile`** — Container image with baked binaries
- **`docker-compose.yml`** — Gateway service definition
- **`.env.template`** — Required environment variables (placeholder values)
- **`openclaw-hardened.json`** — Security-baseline gateway config
- **`openclaw-multi-agent.json`** — Multi-agent routing example
- **`hostinger-vps-guide.md`** — Step-by-step take-home VPS deployment guide

### `security/`

Side-by-side security configurations for the M4 security demo.

- **`openclaw-insecure.json`** — Deliberately weak config used in the live attack demo
- **`openclaw-hardened.json`** — Locked-down version (annotated to show what changed)
- **`README.md`** — Explains the diff, what each setting does, and how the attack works

### `automation/`

Automation patterns: cron, webhooks, hooks.

- **`cron/`** — CLI examples for daily briefings, weekly reports, one-shot reminders

## Getting Started

### Prerequisites

- A Linux VPS (Ubuntu / Debian) or local machine with Docker
- An LLM API key (Anthropic, OpenAI, or Google)
- Basic comfort with SSH and the command line

### Quick Setup

1. Clone this repository
2. Copy `deployment/.env.template` to `.env` and fill in your values
3. Follow the deployment guide in `deployment/hostinger-vps-guide.md`
4. Customize your agent using a workspace template from `workspaces/`

## Course Modules

The 5-hour live course is structured into four modules. The repository is organized by asset type rather than by module, but here's the module mapping for reference:

- **Module 1**: The Integrated AI Agent and OpenClaw Architecture
- **Module 2**: Deployment Options and Going Live
- **Module 3**: The OpenClaw Workspace: Tailoring Your Agent
- **Module 4**: Security, Automation, and Real-World Workflows

See the Demo Index above for which folders each module's demos pull from.

## Resources

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [ClawHub Skills Registry](https://clawhub.ai)