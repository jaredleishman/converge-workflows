# Scope and split policy

Plan reads this. Candidate-time rules (proof fidelity, drift, deletion) live in
`candidate-checks.md`.

## Map surface

Map only the surfaces that can shape the requested behavior: entry points,
sources of truth, consumers and payload builders, database/cache/queue/external
effects, async dispatch and retry/idempotency, concurrency and stale-state
boundaries, migration/rollout/mixed-version boundaries. Broaden only when
repository evidence connects a path to the behavior. One line per path.

## Causal grounding completion

For Standard and Critical work, Map is complete only when every materially
distinct path is connected in execution order: trigger → decision and owner →
mutation, durable write, or external effect (including no-mutation) → failure,
recovery, or cancellation → durable result → next attempt or consumer.

A category or file inventory plus one happy path is not enough. Merge paths
once their behavior is identical; do not repeat a shared tail. Close an
irrelevant path with a concrete not-applicable reason. When the Critical
lifecycle matrix applies, its rows satisfy this rule; do not restate them.

## Mechanism baseline

Before Plan seals, the brief names one repository-appropriate organizing model
and fills the four mechanism axes:

- Ownership: who owns each durable identity and resource, and when it is released
- Ordering / commit: what commits before what, and where the commit point is
- Identity: namespace, collision, and deduplication rules
- Failure model: what happens on error, retry, cancellation, and partial completion

These describe the selected mechanism; they do not require a new framework or
abstraction. Standard and Critical cannot seal `PLANNED` with a blank axis.
Build may not change an axis; if it must, that is `REPLAN`.

## Conditional structural alternatives

After Map and before the baseline is final, compare at least two mechanisms
when Map exposes material novelty or high-risk ambiguity in:

- Concurrency or logical/physical resource ownership
- Lifecycle, persistent state, identity, or partitioning
- Retry, timeout, cancellation, recovery, or partial completion
- A boundary or side effect with credible owners whose commit or lifecycle
  consequences differ

Also run it when the user or the Direction Summary asks to "search the cut".
Fast work never requires this branch. Do not trigger it for a routine use of an
established repository pattern, naming or helper layout, or alternatives that
preserve every load-bearing decision.

Two mechanisms count as different only when they disagree on at least one axis:
a load-bearing ownership, ordering/commit, identity, or lifecycle decision.
"Not like this" and a named engineer's style are not alternatives. Default
second mechanism: the same model with one flipped axis or another card from
`doctrine-cards.md`. A different model family is optional, never required.
Compare caller-visible behavior, organizing model, the four axes, complexity
and proof burden, and the dangerous false successes each prevents. Name the
rejected option; if none is named, Challenge did not run.

## Conditional lifecycle and ownership matrix

Use the matrix in `brief-critical.md` when a Critical change's correctness
depends on combinatorial timing, async handoff, retry/cancellation, persistent
identity, transaction ordering, external effects, state promotion, or
physical-resource ownership across contexts or attempts. Omit it for Fast,
ordinary Standard, and Critical work with no lifecycle-ownership dimension.
One row per applicable event or failure path; a not-applicable event needs a
concrete reason. The matrix is a plan-time ownership contract, not
implementation choreography.

## Split gate

Split when the candidate has more than one independent proof story. Signals:
multiple sources of truth change; multiple external side-effect protocols
change; migration, backfill, activation, and cutover are combined; a new
abstraction and many different consumers change together; more than four
substantial invariants or six acceptance criteria; portions can ship safely
alone; Challenge passes find unrelated root-cause families. Split by behavioral
independence, not line count.

## Non-waivable baseline guarantees

The brief cannot waive a candidate-caused regression by omission. Review may
block a concrete, material regression in:

- Authorization, tenant isolation, or permission boundaries
- Confidentiality, privacy, secret handling, or data exposure
- Persistent-data integrity or externally visible effect integrity
- Compatibility, legal obligations, repository policy, or explicitly preserved
  existing behavior

A weakness that was already reachable and is not introduced, exposed, or
materially worsened by the candidate is a baseline issue, not a blocker. A
product wish absent from both the sealed brief and this floor is a proposed
contract amendment. Do not silently turn unrelated baseline weaknesses,
refactoring opportunities, defense in depth with no reachable failure, or
fenced future capabilities into blockers.
