# Converge plugin

Converge is a small workflow for front-loading software change reasoning and
bounding post-implementation review.

## Skills

- `plan` — Scope, Map, Challenge, lane selection, and split decision
- `build` — implement the sealed Change Brief
- `verify` — verify the exact candidate
- `review` — the single broad, batch-complete review
- `close` — the single delta-only closure review
- `status` — show workflow state and next action

Installed skill names are namespaced by the host where applicable, for example
`/converge:plan` in Claude Code.

## Core policy

```text
One broad review → one remediation batch → one closure review
→ CLOSED, REPLAN, SPLIT, or BLOCKED
```

Converge is intentionally skill-only. It does not install hooks, MCP servers,
agents, background tasks, or credentialed integrations.
