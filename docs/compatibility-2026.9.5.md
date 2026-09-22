# OpenClaw 2026.9.5 compatibility audit

Audited September 22, 2026. Target release: **2026.9.5**, revision `ec9c1a13db8938e5a3eaa51fca2e981cde2395a9`. The course deployment was upgraded from 2026.7.1 separately. This audit updates the student repository and does not certify completion of the live demos.

## Findings and changes

| Area | Finding | Repository update |
|---|---|---|
| Multi-agent config | The old example used `agents.list` and lacked valid multi-agent ownership. The actual 2026.9.5 CLI rejected it. | `agents.entries`, explicit ownership, system-agent selection, and account-specific bindings. |
| Deployment | Floating image/source updates, a source build on a 4 GB VPS, and a template URL with an extra repository path were unreliable. | A complete local Compose recipe, release/digest-pinned base image, small course dependency layer, and correct repository paths. |
| Container environment | Host mount paths could leak into runtime path resolution; restarting retained old env values. | Explicit container paths, separate auth-key mount, and recreation after env changes. |
| Networking | The older manual Tailscale proxy instructions claimed tokenless access to the ordinary gateway port. | Managed Serve, dedicated-listener identity checks, operator-permission prerequisites, and normal auth for external proxy routes. |
| State and recovery | The guide treated sessions/auth as generic files and described a temporary container as separate state. | Canonical SQLite locations, shared bind-mount semantics, cold backups, and matching image/state recovery. |
| Workspace bootstrap | `TOOLS.md` and root `HEARTBEAT.md` were presented as active inputs. | Tools merged into `AGENTS.md`; retired files removed from the starter; monitor scratch documented. |
| Memory privacy | Workspace instructions read curated memory in every session. | Main-private-session scope for curated and daily memory; task-specific reads in shared/scheduled contexts. |
| Automation | Main-session system events were combined with isolated-delivery flags; removal used `rm --id`. | Current CLI examples, positional job IDs, explicit account/recipient, timezone checks, and separate execution/delivery verification. |
| Boundaries | The multi-agent guide claimed fully isolated personas and used full/off exec by default. | Guarded sample exec, explicit session-tool limits, and explanation of the shared filesystem and credential boundary. |
| Skills | Scheduled skills hard-coded independent sends, weekly review named an unavailable question tool, and dependency requirements were implicit. | Scheduler-owned delivery, ordinary clarification, corrected Sunday/ISO-week handling, dependency gates, and rental script base-directory resolution. |
| Demo fixtures | April notes, old timezone, and static reading-pace summaries could be mistaken for current data. | Historical-fixture labels, Vancouver timezone defaults, and date-based reading-pace instructions. Dated records are preserved. |
| Architecture/UI | An example note conflated current OpenClaw with PI; dashboard and device commands were stale. | OpenClaw-owned runtime and SQLite wording, Sessions-first UI guidance, and `devices list`. |

The repository previously had no student-facing `security/` or `automation/` directory. Their new reference guides accompany the six-demo sequence. Instructor-only attack/preparation skills and runbooks remain outside this repository.

## Deliberate differences from the live deployment

- The student Compose recipe starts one gateway and offers a one-shot CLI service. The live deployment has a persistent CLI companion.
- The student image installs Debian's `gh` package. The verified local build has `gh 2.23.0`; the instructor image carries `gh 2.97.0` and private Git credential configuration. The guide supplies an explicit persistent HTTPS helper for student repositories.
- Python direct dependencies match the instructor environment: requests 2.34.2 and Beautiful Soup 4.15.0. Apt versions and Python transitive dependencies are not fully locked.
- The student sample uses guarded exec. The live Coder's full-access policy remains an instructor choice.
- The multi-agent sample uses agent/account IDs `alfred` and `coder`. The live deployment retains agent `main`, Telegram account `default`, and `coder`. Existing installations should keep their IDs and state instead of renaming them by copying this sample.
- Alfred's sample model remains OpenRouter Sonnet 4.6; Coder uses direct Anthropic Sonnet 5 with OpenRouter fallback. The live deployment currently uses Sonnet 5 for both. Verify provider access before reproducing model calls.

## Validation performed

| Check | Result |
|---|---|
| Original multi-agent example with 2026.9.5 CLI | Rejected as expected: missing valid multi-agent ownership |
| New single-agent, multi-agent, and merged examples | Valid with the released CLI; no legacy ownership warnings in the final examples |
| Webhook fragment merged into the single-agent config | Valid |
| Documented automation, model-status, device, and approval CLI flags | Verified against released CLI help and release source |
| Compose configuration | Parses; loopback-only publishing, three persistent mounts, fixed internal paths, optional CLI profile, no Docker socket |
| Course Docker image | Built locally from the pinned official digest |
| Network-disabled container smoke | uid 1000; OpenClaw 2026.9.5 (`ec9c1a1`); Node 24.19.0; Python imports and `gh` available; multi-agent config valid; rental CLI help works |
| Workspace skill discovery | All six Alfred skills and both Coder skills eligible via isolated CLI local-inventory fallback |
| Rental script | Python syntax plus offline search/detail/dedup fixtures pass |
| Repository hygiene | Local documentation links and `git diff --check` checked; original checkout's existing diff preserved byte-for-byte |

Tests used temporary local state and placeholder tokens. They did not send model prompts, Telegram messages, webhook requests, Git pushes, or PRs. A further network-disabled gateway readiness/skill RPC test could not run because the local Docker daemon was stopped after the interruption; it is not counted as a passing test. Skill eligibility was subsequently checked through the CLI's local fallback.

## Remaining rehearsal and operational risks

1. A fresh VPS onboarding and managed Tailscale Serve setup still needs end-to-end rehearsal on the intended host. Docker image/config checks do not verify host operator rights, firewall policy, browser identity, or HTTPS routing.
2. Real model/provider access, Telegram pairing and reminder delivery, webhook completion, exec-review enforcement, and GitHub PR creation remain live integration checks. Schema validity and skill eligibility do not prove those workflows.
3. Dated workspace fixtures are intentionally historical. Prepare a current daily note and a complete prior ISO week, recompute tracker statistics, and verify the new reminder's destination separately. The existing Demo 1 preparation task owns that live work.
4. Rental scraping depends on external HTML and availability. The unchanged scraper can emit an empty array after fetch/parsing failures; inspect stderr and do not present that as evidence of no available rentals. Fractional bathroom counts are also reduced to integers by the current scraper.
5. Guarded exec and separate IDs do not isolate shared credentials or sibling workspaces from an approved broad command. Use separate environments when the trust boundary requires it.
6. The Docker baseline is pinned; Debian packages and Python transitive dependencies can still change. Record the resulting image digest for each rehearsal and keep a verified off-host backup before migration.

## Release-pinned evidence

- [Release and revision](https://github.com/openclaw/openclaw/releases/tag/v2026.9.5)
- [Docker installation](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/install/docker.md) and [upstream Compose](https://github.com/openclaw/openclaw/blob/v2026.9.5/docker-compose.yml)
- [Agent bindings and ownership](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/agent-bindings.md)
- [Workspace contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/concepts/agent-workspace.md)
- [Tailscale ingress and auth](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/tailscale.md)
- [Session permission modes](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/permission-modes.md)
- [Automation CLI](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/cli/cron.md) and [heartbeat contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/heartbeat.md)
- [Skills contract](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/tools/skills.md)

The live comparison used the course's saved September 21 deployment-upgrade report and September 22 Demo 1 preflight. This audit performed no live Hostinger access or changes.
