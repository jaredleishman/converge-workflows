# Workflow lanes

Choose the lightest lane that matches the actual failure impact and complexity.

## Fast

Use for a localized, well-understood change that introduces no new state,
authorization, external side-effect, retry, rollout, or compatibility boundary.

Default process:

```text
Short acceptance list → Build → Verify → one Review
```

Challenge and Close are optional unless evidence requires them.

Bias toward Fast when all Fast conditions are supported by repository evidence.
Keep its Direction Summary to one concise confirmation unless a real product
decision remains. Use at most two important invariants and three acceptance
criteria; write `Not applicable` for irrelevant map boundaries instead of
expanding the brief with speculative analysis.

If Round 1 finds a P1 after Fast skipped Challenge, record a lane-misjudgment
signal in `findings.md` and the evaluation log. This is evidence for future lane
selection, not permission to restart review.

## Standard

Use for most meaningful backend or product changes that span several paths but
still have one coherent proof story.

Default budgets:

- Important invariants: at most 4
- Acceptance criteria: at most 6
- Independent Challenge passes: 1
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

### Compound-boundary screen

Treat these as boundary types rather than implementation keywords:

- Hard deadline or late-completion cutoff
- External I/O or externally visible effect
- Async handoff through a task, thread, queue, callback, or signal
- Retry, cancellation, recovery, or next-attempt behavior
- Persistent identity, collision, or deduplication rule
- Transaction or commit-order boundary
- Shared physical resource such as a connection, permit, worker, or pool slot
- Asynchronous approval, promotion, activation, or multiple partitioned streams

Select Critical when three or more boundary types are causally coupled and at
least one has a persistent-data, external-effect, or physical-resource
consequence. “Causally coupled” means correctness depends on their ordering or
on ownership transferring between contexts or attempts. This screen makes a
deadline plus external HTTP plus persistent identity plus detached work
Critical; it does not make one ordinary transaction, queue, or external call
Critical by itself.

Standard is allowed only with a sealed, falsifiable exception that:

- Enumerates the coupled boundaries and the defeating failure sequence
- Shows that failure is locally contained to a bounded, reversible unit
- Shows independent recovery without manual reconciliation
- Shows that no correctness-critical durable identity, external effect, or
  physical resource changes owner across contexts or attempts
- Names evidence that would falsify the exception

An unsupported “low risk” or “well tested” assertion is not an exception.

Critical additions may include:

- One or two explicit coverage matrices
- Same-head parallel implementation reviews synthesized into one finding batch
- Blind code-first review when contract anchoring is a material concern

These additions still count as one broad review round because all reviewers
inspect the same candidate before remediation.

Critical planning uses two independent Challenge passes with hidden findings
and different contexts or lenses. When a host cannot provide a second
independent context, record the limitation and obtain an explicit decision
before treating Challenge as complete. A lifecycle/ownership matrix is
conditional under `scope-policy.md`; it is not required for simple Standard
briefs or for Critical work whose risk is unrelated to lifecycle ownership.
