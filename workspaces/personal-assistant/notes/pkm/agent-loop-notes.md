# Agent Loop, Course Notes

Notes from the Module 1 agent loop section. Captured 2026-04-10.

## The Core Loop

The agent loop is deceptively simple:

```
Loop:
  1. Assemble context (system prompt + history + new message)
  2. Send to LLM
  3. If response is text only -> return to user
  4. If response includes tool calls -> execute, feed results back, loop
  5. (Optional) compaction when context grows too large
```

That's the whole pattern. Most agent frameworks are some flavor of this with different ergonomics on top.

## Why It Works

The model decides when to call tools, when to think more, and when to stop. The framework's job is to:
- Provide tools the model can call
- Execute them safely
- Feed results back in a form the model understands
- Detect when to terminate

It's not the framework that's "intelligent". It's the model. The framework is plumbing.

## Where Frameworks Differ

- **Tool definition format:** OpenAI function-calling vs Anthropic tool-use vs MCP. Same underlying idea, different schemas.
- **Memory:** Some frameworks (LangChain, etc.) impose structured memory abstractions. Others (PI / OpenClaw) keep it minimal. The agent reads and writes files directly.
- **Compaction:** When context fills up, you have to compress prior turns. Strategies vary.
- **Multi-agent orchestration:** Some frameworks build hierarchies; others stay flat.

## OpenClaw Specifics

OpenClaw layers on top of PI:
- Channel adapters (Telegram, Discord, Slack, etc.)
- Workspace plus memory model
- Multi-agent routing
- Security guardrails

Under the hood the loop is still PI's. OpenClaw is the integration plus ops layer.

## Key Takeaway

For my side project: the loop is not the part to spend time on. The leverage is in:
1. Workspace design (what files? what conventions?)
2. Skills (what tools does the agent have?)
3. Channel integrations (where does the agent live?)

The model plus loop is a commodity. The agent's behavior comes from the workspace and skills.
