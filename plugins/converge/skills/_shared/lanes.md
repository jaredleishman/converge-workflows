# Lanes

Choose the lightest lane that matches the actual failure impact and complexity.

## Fast

A localized, well-understood change with no new state, authorization, external
side-effect, retry, rollout, or compatibility boundary.

```text
Short brief (brief-fast.md) → Build → Verify → one Review
```

Fast skips Challenge and uses at most two important invariants and three
acceptance criteria. Write `Not applicable` for irrelevant boundaries instead
of analysing them. Keep the Direction Summary to one confirmation unless a real
product decision remains.

**Promotion.** If Fast Verify or Review fails a load-bearing row (a mechanism
axis changed, or the Future change has no home), do not keep repairing in
Fast: promote to Standard via `REPLAN`. A mechanical miss may use a targeted
fix. A supported P1 after a skipped Challenge is also a lane-misjudgment signal
to record in `findings.md`; it never adds a review round.

## Standard

Most meaningful changes that span several paths but share one proof story.

- Important invariants: at most 4
- Acceptance criteria: at most 6
- Independent Challenge passes: 1
- Coverage matrices: 0 unless behavior is genuinely combinatorial
- Broad implementation reviews: 1
- Closure reviews: 0 or 1
- One evolving Change Brief, target under about 150 lines before Build

A Standard brief that will not fit that target is a signal the change is
Critical or should split, not a reason to write more.

## Critical

Use when false success could materially affect money, authorization, tenant
isolation, destructive remote state, irreversible data, difficult concurrency,
representation cutover, or mixed-version safety. A transaction, migration,
queue, or database by itself is not a trigger; escalate when impact and failure
complexity are both high, or impact alone is catastrophic.

### Compound-boundary screen

Boundary types (not implementation keywords):

- Hard deadline or late-completion cutoff
- External I/O or externally visible effect
- Async handoff through a task, thread, queue, callback, or signal
- Retry, cancellation, recovery, or next-attempt behavior
- Persistent identity, collision, or deduplication rule
- Transaction or commit-order boundary
- Shared physical resource such as a connection, permit, worker, or pool slot
- Asynchronous approval, promotion, activation, or partitioned streams

Select Critical when three or more boundary types are causally coupled and at
least one has a persistent-data, external-effect, or physical-resource
consequence. Causally coupled means correctness depends on their ordering or on
ownership moving between contexts or attempts. This makes a deadline plus
external HTTP plus persistent identity plus detached work Critical; it does not
make one ordinary transaction, queue, or external call Critical by itself.

Standard is allowed only with a sealed, falsifiable exception (fields in
`brief-critical.md`) that:

- Enumerates the coupled boundaries and the defeating failure sequence
- Shows failure is locally contained to a bounded, reversible unit
- Shows independent recovery without manual reconciliation
- Shows no correctness-critical durable identity, external effect, or physical
  resource changes owner across contexts or attempts
- Names evidence that would falsify the exception

"Low risk" or "well tested" without that evidence is not an exception.

### Critical additions

- Two independent Challenge passes with hidden findings and different contexts
  or lenses. If the host cannot provide a second context, record the limitation
  and get an explicit user decision before calling Challenge complete.
- The lifecycle/ownership matrix and proof obligations from
  `brief-critical.md`, only when `scope-policy.md` triggers them.
- Optionally one or two coverage matrices and same-candidate parallel reviews.
  Parallel reviewers still count as one broad review because they all inspect
  the same candidate before remediation.
