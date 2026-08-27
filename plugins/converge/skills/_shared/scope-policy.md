# Scope and split policy

## Review surface

Before implementation, map only the surfaces that can shape the requested
behavior:

- Entry points that create or mutate it
- Sources of truth and provenance
- Consumers and payload builders
- Database, cache, queue, and external effects
- Async dispatch, recovery, retry, and idempotency paths
- Concurrency and stale-state boundaries
- Migration, rollout, feature-fence, and mixed-version boundaries

Broaden only when repository evidence connects a path to the behavior.

## Causal grounding completion

For Standard and Critical work, Map is complete only when every materially
distinct path revealed by the review surface is connected in execution order:

- Trigger or entry point
- Decision and control or resource owner
- Mutation, durable write, or external effect, including no-mutation outcomes
- Failure, recovery, cleanup, or cancellation behavior
- Durable result
- Next attempt or downstream consumer

A category or file inventory and one representative happy path are not enough.
Merge paths after their behavior becomes identical; do not repeat a shared
tail. Close an irrelevant path with a concrete not-applicable reason. When the
Critical lifecycle and ownership matrix below applies, its event rows satisfy
this trace requirement; do not restate the same path in a second format.

Before Plan seals, name one repository-appropriate organizing model that makes
the important ownership, ordering, identity, state, and failure decisions
coherent. This is a description of the selected mechanism, not a requirement
to introduce a framework or abstraction.

## Conditional structural alternatives

After Map and before the Planned mechanism baseline is final, compare at least
two structurally different mechanisms when Map exposes material novelty or
high-risk ambiguity in any of these areas:

- Concurrency or logical/physical resource ownership
- Lifecycle, persistent state, identity, or partitioning
- Retry, timeout, cancellation, recovery, or partial completion
- A boundary or side effect with credible owners whose commit or lifecycle
  consequences differ

Fast work never requires this branch. Do not trigger it for a routine use of an
established repository pattern, naming or helper-layout choices, or alternatives
that preserve every load-bearing decision. When triggered, the candidates must
differ in at least one load-bearing ownership, ordering/commit, identity, or
lifecycle decision. Compare caller-visible behavior, organizing model,
ownership and ordering, identity and failure behavior, complexity and proof
burden, and the dangerous false successes each design prevents. Record why one
candidate was selected or how the final mechanism synthesizes them.

## Conditional lifecycle and ownership matrix

Use the matrix in the existing Change Brief when a Critical change's
correctness depends on combinatorial timing, async handoff, retry/cancellation,
persistent identity, transaction ordering, external effects, state promotion,
or physical-resource ownership across contexts or attempts. Omit it for Fast,
ordinary Standard, and Critical changes whose risk has no lifecycle-ownership
dimension. A Standard exception to the compound-boundary screen uses the
compact exception record in `lanes.md`, not this full matrix.

Create one row per applicable event or failure path, including admission,
start/setup failure, deadline, cancellation, late completion, persist/commit,
retry or next attempt, asynchronous promotion, and cleanup/release. Mark an
event not applicable only with a concrete reason. Record:

- The control context and handoff
- Current-request election or visibility effect
- Persistence owner and timing
- Physical or agent resource owner and release point
- Durable state before and after
- Identity namespace, collision rule, and deduplication behavior
- Transaction or external-effect commit point
- Retry, cleanup, and next-attempt behavior
- The evidence that exercises the failure path

The matrix is a plan-time ownership contract, not implementation choreography.

## Proof fidelity

Classify material verification evidence by the boundary it actually crosses:

- `BOUNDARY_DIRECT` — exercises the production entry point and real boundary.
- `BOUNDARY_FAITHFUL` — uses a controlled clock, fake endpoint, test database,
  or equivalent substitute while preserving the production control path,
  ownership, transaction, and failure semantics being claimed.
- `PROXY` — calls a helper directly, injects downstream state, checks only that
  a mock was called, relies on static inspection, or bypasses the mechanism.
- `UNAVAILABLE` — required evidence cannot currently be obtained.

A material obligation is `PASS` only with boundary-direct or
boundary-faithful evidence. Proxy evidence may support `PARTIAL`, but proxy-only
evidence is `UNPROVEN` for a required production boundary. `UNAVAILABLE`
evidence for a required obligation is `BLOCKED`, not a silent pass. Live
production traffic and real wall-clock sleep are not required when a controlled
test faithfully crosses the same boundary.

For every material test, record the production event or boundary exercised,
the broken mechanism or injected failure it detects, and every proxy or mock
that limits the claim.

## Planned-mechanism drift

Before Build or Remediate hands a candidate to Verify, compare the
implementation with the sealed Planned mechanism baseline. Verify repeats the
comparison independently. Inventory every new or materially changed:

- Thread, task, queue, callback, or signal
- Transaction boundary or commit point
- Retry, timeout, cancellation, recovery, or late-completion behavior
- Logical or physical resource owner and release point
- Identity namespace, collision, or deduplication rule
- Persistent-state transition, external effect, or promotion path

Append observed facts to the Map, but do not use them to rewrite the planned
baseline. If an item changes the ownership, ordering, identity, or failure
model, the current contract cannot continue serially: use `REPLAN` for the same
outcome or `SPLIT` for independently provable outcomes. Record a concrete
“none found” declaration and the inspected seams when the checkpoint passes.

## Split gate

Recommend splitting when the candidate has more than one independent proof
story. Warning signals include:

- Multiple sources of truth change
- Multiple external side-effect protocols change
- Migration, backfill, activation, and cutover are combined
- A new abstraction and many materially different consumers change together
- More than four substantial invariants are required
- More than six acceptance criteria are required
- Separate portions can ship safely and independently
- Challenge passes find unrelated root-cause families

A large diff may still be coherent. A small diff may still combine incompatible
state machines. Split by behavioral independence, not line count alone.

## Scope creep

A review finding blocks the current change only when it has a concrete reachable
path, material impact, a causal relationship to the candidate, and a violation
of the sealed brief, a non-waivable baseline guarantee, or a regression
introduced by the change.

## Non-waivable baseline guarantees

The brief cannot waive candidate-caused regressions merely by omission. Review
may block a concrete, material regression in:

- Authorization, tenant isolation, or permission boundaries
- Confidentiality, privacy, secret handling, or data exposure
- Persistent-data integrity or externally visible effect integrity
- Compatibility, legal obligations, repository policy, or explicitly preserved
  existing behavior

A weakness that was already reachable and is not introduced, exposed, or
materially worsened by the candidate remains a baseline issue. A product wish
that is absent from both the sealed brief and this safety floor is a proposed
contract amendment, not a current blocker.

Use “baseline issue” only for that pre-existing, candidate-unworsened case. A
candidate-caused violation of this safety floor remains eligible to block even
when the brief omitted it.

Do not silently turn these into blockers:

- Unrelated baseline weaknesses
- General refactoring opportunities
- Defense in depth with no current reachable failure
- Future capabilities behind an effective fail-closed fence
- Product requirements absent from the sealed brief and baseline guarantees

A reviewer may propose a contract amendment, but must label it as such.
