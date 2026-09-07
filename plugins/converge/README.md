# Converge plugin

Converge is a small workflow for front-loading software change reasoning and
bounding post-implementation review.

## Skills

- `plan` — Scope, Map, Challenge, lane selection, and split decision
- `build` — implement the sealed Change Brief
- `verify` — verify the exact candidate
- `review` — the single broad, batch-complete review
- `remediate` — fix the complete Round 1 batch by root-cause family
- `close` — the single delta-only closure review
- `status` — show workflow state and next action

Shared policy lives in `skills/_shared/`: `workflow.md` (flow, sealing,
delegation), `lanes.md`, `scope-policy.md` (Plan), `candidate-checks.md`
(Build, Verify, Remediate), `review-policy.md` (Review, Remediate, Close),
`artifact-protocol.md` (gate and candidate identity), `doctrine-cards.md`
(Challenge alternatives only), and the templates. Each rule lives in exactly
one file.

Installed skill names are namespaced by the host where applicable, for example
`/converge:plan` in Claude Code.

## Core policy

```text
One broad review → one remediation batch → one closure review
→ optional one-time targeted correction for a remediation-caused defect or
  incomplete prior finding family
→ CLOSED, REPLAN, SPLIT, or BLOCKED
```

Converge is intentionally skill-only. It does not install hooks, MCP servers,
agents, background tasks, or credentialed integrations. It bundles one
standard-library script, `scripts/state_gate.py`. Skills invoke it to check
legal transitions, couple Review and Close outcomes to budget use, capture or
check exact candidate identity, and start a new contract after `CLOSED`,
`REPLAN`, or `SPLIT`. Nothing runs outside a skill invocation.
