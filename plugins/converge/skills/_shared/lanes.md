# Workflow lanes

Choose the lightest lane that matches the actual failure impact and complexity.

## Fast

Use for a localized, well-understood change that introduces no new state,
authorization, external side-effect, retry, rollout, or compatibility boundary.

Default process:

```text
Short acceptance list → Build → Verify → one Review
```

Plan Attack and Close are optional unless evidence requires them.

## Standard

Use for most meaningful backend or product changes that span several paths but
still have one coherent proof story.

Default budgets:

- Important invariants: at most 4
- Acceptance criteria: at most 6
- Independent plan attackers: 1
- Coverage matrices: 0 unless behavior is genuinely combinatorial
- Broad implementation reviews: 1
- Closure reviews: 0 or 1
- Primary planning artifacts: 1 evolving Change Brief

## Critical

Use when false success could materially affect money, authorization, tenant
isolation, destructive remote state, irreversible data, difficult concurrency,
representation cutover, or mixed-version safety.

Critical is not triggered merely because a change uses a transaction, migration,
queue, or database. Escalate when impact and failure complexity are both high,
or when impact is independently catastrophic.

Critical additions may include:

- Two independent plan attacks using different models or contexts
- One or two explicit coverage matrices
- Same-head parallel implementation reviews synthesized into one finding batch
- Blind code-first review when contract anchoring is a material concern

These additions still count as one broad review round because all reviewers
inspect the same candidate before remediation.
