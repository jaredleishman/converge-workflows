# Change Brief

Standard and Critical. Fast uses `brief-fast.md`, which records
`Challenge skipped (Fast)`. Copy Critical sections from `brief-critical.md`
only when the lane or a Standard exception needs them. Keep this under about
150 lines before Build: one line per Map path, one sentence per table cell.

## Metadata

- Lane: `standard | critical`
- Lane rationale:
- Compound-boundary screen: `not-triggered | critical | standard-exception`
- Last updated:

## Outcome

Observable behavior that changes, and for whom.

## Non-goals

Nearby behavior that must not change.

## Dangerous false successes

Outcomes that look successful while the system is wrong.

## Baseline guarantees

Non-waivable regression boundaries even when no AC names them. `Not
applicable` needs a concrete scope reason.

- `BG-1` — Authorization and tenant-isolation boundaries are not weakened.
- `BG-2` — Confidentiality, privacy, and secret handling are not weakened.
- `BG-3` — Persistent data and external effects are not corrupted, duplicated, or silently lost.
- `BG-4` — Compatibility, legal obligations, repository policy, and explicitly preserved behavior remain intact unless the approved direction changes them.

## Map

One line per path. `Not applicable` with a reason for untouched boundaries.

- Entry points:
- Sources of truth and provenance:
- Consumers:
- State mutations:
- External effects:
- Async, retry, and recovery paths:
- Concurrency and stale-state boundaries:
- Migration, rollout, and mixed-version boundaries:

### Causal grounding trace (Standard and Critical)

One row per materially distinct path: trigger → owner → mutation or effect →
failure or recovery → durable result → next consumer. Merge identical tails.
When a Critical lifecycle matrix applies, reference its rows instead.

| Material path | Trace | Not-applicable reason |
|---|---|---|

## Proposed change

The smallest coherent mechanism. No implementation choreography.

## Planned mechanism baseline

Sealed at `PLANNED`. Build may not change these; if it must, `REPLAN`.

- Organizing model:
- Ownership:
- Ordering / commit:
- Identity:
- Failure model:

## Invariants

At most four.

- `INV-1`:

## Acceptance criteria

At most six. Given / When / Then. No "clean", "elegant", "maintainable",
"extensible", or "idiomatic".

- `AC-1` — Given / When / Then. Proposed regression:

## Future change

One sentence naming the most likely later edit this cut must survive with one
obvious seam, for example "Adding a dry-run flag should touch only the writer."

## Challenge results

### Alternative mechanisms (conditional)

Only when `scope-policy.md` triggers structural alternatives. Candidates must
disagree on at least one axis. Name the rejected option.

| Candidate (card or flipped axis) | Caller-visible behavior | Organizing model | Axis differences | Complexity and proof burden | Dangerous false-success response |
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

Build fills this in. Build reads Outcome, Non-goals, Baseline guarantees, Map,
Planned mechanism baseline, Invariants, Acceptance criteria, and Future change;
Challenge alternatives are for Review, not for Build to optimize against.

| Obligation, including applicable BGs | Implementation seam | Paths covered | Tests | Deviations |
|---|---|---|---|---|

- Future change seam:
- Drift checkpoint (seams inspected, or `none found`):
- Deleted: (or `Deletion pass: none required`)

### Delegated Plan and Build ownership (conditional)

Omit when nothing is delegated.

| Stage and delegate | Bounded scope and seams | Candidate identity and owned paths at dispatch | Success criteria | Owner-inspected evidence and discrepancies | Reconciliation and disposition |
|---|---|---|---|---|---|

### Build proof units (conditional)

Only when Build has more than one coherent dependency slice. Record each unit
before editing it and its passing local check before starting the next.

| Unit | Dependency slice | Owned paths | Local check | Result |
|---|---|---|---|---|

## Verification evidence

Verify fills this in. `PASS`, `PARTIAL`, `UNPROVEN`, `BLOCKED`, or
`NOT_APPLICABLE`. A required production boundary cannot be `PASS` on proxy-only
evidence.

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
