# Change Brief

## Metadata

- Lane: `fast | standard | critical`
- Lane rationale:
- Compound-boundary screen: `not-triggered | critical | standard-exception`
- Last updated:

## Outcome

Describe the observable behavior that should change.

## Non-goals

List nearby behavior that is intentionally unchanged.

## Dangerous false successes

List outcomes that could look successful while the real system is wrong.

## Baseline guarantees

These are non-waivable regression boundaries even when an acceptance criterion
omits them. Keep applicable evidence in the crosswalk; `Not applicable` requires
a concrete scope reason.

- `BG-1` — Authorization and tenant-isolation boundaries are not weakened.
- `BG-2` — Confidentiality, privacy, and secret handling are not weakened.
- `BG-3` — Persistent data and external effects are not corrupted, duplicated, or silently lost.
- `BG-4` — Compatibility, legal obligations, repository policy, and explicitly preserved behavior remain intact unless the approved direction changes them.

## Map

### Entry points

### Sources of truth and provenance

### Consumers

### State mutations

### External effects

### Async, retry, and recovery paths

### Concurrency and stale-state boundaries

### Migration, rollout, and mixed-version boundaries

### Causal grounding trace (Standard and Critical)

Omit for Fast. Trace every materially distinct mapped path in execution order,
or give a concrete not-applicable reason. Merge identical tails. When a Critical
lifecycle matrix applies, reference its rows instead of duplicating them here.

| Material path | Trigger through ownership, mutation/effect, failure/recovery, durable result, and next consumer or attempt | Not-applicable reason |
|---|---|---|

## Proposed change

Describe the smallest coherent mechanism. Avoid implementation choreography.

## Planned mechanism baseline

Record the approved mechanism, ownership, ordering, identity, and failure-model
decisions before Build. Later Map observations may add facts but cannot make a
different mechanism retroactively planned.

- Organizing model:

## Invariants

Fast: at most two. Standard: at most four.

- `INV-1`:

## Acceptance criteria

Fast: at most three. Standard: at most six. Given / When / Then.

- `AC-1` — Given / When / Then. Proposed regression:

## Challenge results

Omit this whole section on Fast when Challenge was skipped. Record
`Challenge skipped (Fast)` instead.

### Alternative mechanisms (conditional)

Include only when `scope-policy.md` triggers structural alternatives. Compare
at least two mechanisms with a load-bearing difference before selecting or
synthesizing the baseline.

| Candidate | Caller-visible behavior | Organizing model | Ownership, ordering, identity, and failure | Complexity and proof burden | Dangerous false-success response |
|---|---|---|---|---|---|

- Selection or synthesis:
- Rationale:

### Missing surfaces found

### Failure sequences found

### Unsupported assumptions

### Contract amendments

### Split decision

- Decision: `ONE_CHANGE | SPLIT`
- Rationale:

## Implementation crosswalk

Build fills this in. Plan and Build also record any delegated work here so the
stage owner can inspect and reconcile it without creating another artifact.

| Obligation, including applicable BGs | Implementation seam | Paths covered | Tests | Deviations |
|---|---|---|---|---|

### Delegated Plan and Build ownership (conditional)

Omit when work is not delegated.

| Stage and delegate | Bounded scope and seams | Candidate identity and owned paths at dispatch | Success criteria | Owner-inspected evidence and discrepancies | Reconciliation and disposition |
|---|---|---|---|---|---|

### Build proof units (conditional)

Include when Build has more than one coherent dependency slice. Record each
unit before editing it and record its successful local check before starting
the next. For one indivisible change, use one compact crosswalk note instead.

| Unit | Coherent dependency slice | Owned paths | Local check before advancement | Result |
|---|---|---|---|---|

## Verification evidence

Verify fills this in.

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|

Use `PASS`, `PARTIAL`, `UNPROVEN`, `BLOCKED`, or `NOT_APPLICABLE`. A required
production boundary cannot be `PASS` on proxy-only evidence.
