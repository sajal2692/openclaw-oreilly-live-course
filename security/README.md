# Security boundaries on OpenClaw 2026.9.5

Use this alongside Demo 5 and the deployment/multi-agent examples. The instructor's deliberately permissive Coder configuration is a demo choice. The take-home examples start with `tools.exec.mode: "ask"`, workspace-scoped file tools, agent-scoped session visibility, and cross-agent session access disabled.

## Controls and what they cover

| Control | Scope |
|---|---|
| Telegram pairing / allowlists | Who can talk to a bot |
| Gateway token and browser device identity | Who can connect as an operator |
| Session Execution permissions | Effective filesystem boundary and exec reviewer for that session |
| Exec mode / approval policy | Whether and how shell commands are admitted |
| File-tool workspace restriction | Paths available to OpenClaw-managed file tools |
| Agent sandbox or separate gateway | Execution environment and mounted resources |
| Outer course Docker container | A shared environment containing both agents and mounted credentials |

Separate workspaces and `tools.fs.workspaceOnly` do not prevent unrestricted shell commands from reading sibling workspaces or gateway credentials. Tools notes, SOUL.md, and skill text are behavioral instructions; they do not enforce an OS boundary. Approving a command does not retroactively restrict already-running processes.

## Session permissions

For OpenClaw-managed tools:

| Mode | Filesystem / exec behavior |
|---|---|
| `read-only` | Reads inside the session root; managed mutation tools omitted; exec denied |
| `guarded` | Workspace writes; human review after the exec allowlist fast path |
| `workspace` | Workspace writes; LLM reviewer can allow, deny, or request human review |
| `full` | Unrestricted filesystem access and exec without review, subject to independent tool/sandbox constraints |

A session's explicit mode matters even after global config is changed. Inspect the active session in the composer, plus any stored host approval policy. Full Access requires administrator authority. Native harnesses can have their own tool surface and additional constraints.

Legacy `security`/`ask` pairs may still appear in imported policy. Prefer current `tools.exec.mode` in new examples. Doctor migrates legacy session policy; the retired `execSecurity` / `execAsk` session patch fields are rejected by the current API.

## Rehearse guardrails with synthetic data

1. Use a disposable workspace containing a clearly fake profile. Select the exact session and record its permission mode.
2. Present an untrusted skill/document that asks for an unrelated file read or command. Inspect what the agent attempts and what the runtime admits.
3. Start in Read Only or Guarded, inspect a denied or approval-required operation, and confirm that no mutation occurred. Any network receiver used in the exercise should be under your control and receive only synthetic text.
4. If comparing Full Access, choose it explicitly in the intended session, run only the bounded demonstration, then restore the prior mode. Verify the final files and any outgoing activity.

Do not infer safety from an allowlisted interpreter such as `python3`, `bash`, or `node`: it can run arbitrary code. Do not demonstrate exfiltration using a real USER.md, token, private profile, or paid webhook.

## Diagnostics

From the deployment directory:

```bash
docker compose exec openclaw-gateway openclaw config validate
docker compose exec openclaw-gateway openclaw security audit
docker compose exec openclaw-gateway openclaw approvals get
```

Read audit/approval output privately before showing it in class. Config validity does not prove isolation or successful enforcement. Docker hosting does not enable OpenClaw agent sandboxing; a sandbox also needs its backend, images, dependencies, and restricted mounts. Mounting the host Docker socket grants powerful host control and is not part of the take-home recipe.

For separate operators or mutually untrusted agents, use separate gateways/environments and credentials, then verify the actual boundary. The independent course personas share one operator's trust boundary.

- [Session permissions](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/permission-modes.md)
- [Tool permissions](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/gateway/security/tool-permissions.md)
- [Exec approvals](https://github.com/openclaw/openclaw/blob/v2026.9.5/docs/tools/exec-approvals.md)
