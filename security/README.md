# Security Configuration: Insecure vs Hardened

This directory contains two OpenClaw configurations that demonstrate the difference between an unguarded agent and a properly secured one.

## Files

- `openclaw-insecure.json` - Deliberately insecure. Open DMs, unrestricted exec, no sandbox, no filesystem boundaries. Used in the Module 4 security pitfalls demo to show what can go wrong.
- `openclaw-hardened.json` - Locked down. Pairing-based DM access, exec denied by default, sandboxed non-main sessions, workspace-only filesystem. The "after" state that fixes the vulnerabilities.

## What Changed (insecure to hardened)

| Setting | Insecure | Hardened | Why |
|---------|----------|----------|-----|
| `gateway.bind` | `lan` | `loopback` | Prevent direct network access |
| `gateway.auth.token` | Weak demo token | Strong random token | Prevent unauthorized gateway access |
| `session.dmScope` | (default) | `per-channel-peer` | Isolate conversations between senders |
| `sandbox.mode` | `off` | `non-main` | Contain tool execution in non-main sessions |
| `tools.exec.security` | `allow` | `deny` | Block arbitrary command execution |
| `tools.elevated.enabled` | `true` | `false` | Prevent host-level escape |
| `tools.fs.workspaceOnly` | `false` | `true` | Restrict file access to workspace |
| `channels.telegram.dmPolicy` | `open` | `pairing` | Require explicit approval for new senders |
| `groups.*.requireMention` | `false` | `true` | Prevent agent responding to every group message |

## Demo Flow

1. Start the insecure gateway and show a prompt injection attack that reads sensitive files.
2. Apply the hardened config and restart.
3. Show the same attack now blocked.
4. Run `openclaw doctor` and `openclaw security audit` to validate.
