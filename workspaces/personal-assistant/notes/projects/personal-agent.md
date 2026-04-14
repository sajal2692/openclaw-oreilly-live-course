# Personal Agent

**Status:** On track. v1 plumbing milestone hit (Telegram round-trip working).
**Started:** 2026-02-15
**Target v1:** End of Q2 2026 (June 30)

## Goal

A self-hosted personal AI agent that:
- Runs on a small VPS
- Handles daily briefings and nightly reviews
- Manages tasks and notes via a file-based PKM
- Talks via Telegram (and eventually Discord)
- Acts as a real daily-driver, not a toy

## Why

Two reasons:
1. **Reduce friction in personal operations.** Tasks, planning, fitness logs, reading list. All of it currently lives across too many apps. One file-based system plus one agent feels right.
2. **Learn agent patterns end-to-end.** Reading about agents is one thing; running one in production for myself is another. Best way to internalize the patterns is to ship something and use it daily.

## Current Status (as of 2026-04-12)

- [x] Workspace structure designed (file-based PKM)
- [x] Skills scaffolded (notes-tasks, daily-briefing, nightly-review, weekly-review, books-tracker)
- [x] Telegram channel wired (round-trip "hello" works)
- [ ] Daily briefing skill: partial. Reads daily note template. Doesn't yet pull tasks correctly.
- [ ] Nightly review skill: scaffolded, not yet wired
- [ ] Weekly review skill: scaffolded, not yet wired
- [ ] Books tracker: scaffolded
- [ ] Production deploy to VPS

## Next Actions

1. Finish wiring `notes-tasks` skill against `notes/tasks.md` (in progress)
2. Test full daily-briefing flow in WebChat
3. Deliver first real briefing via Telegram (target: end of next week)
4. Wire nightly-review and run for a week
5. Wire weekly-review and use for next week's review

## Open Questions

- Where to host: small VPS (Hetzner CX22 looks fine) or Pi at home?
- How to handle secrets long-term (env vars in compose are fine for v1 but not ideal)
- When to introduce a second channel (Discord). After Telegram has been stable for 2 weeks?

## Notes

- Course is providing the right structural patterns at the right time. The architecture diagram from module 1 is now the mental model.
- The "obfuscated personal workspace" example from module 3 is essentially what this project is trying to be: file-based, self-contained, portable.
