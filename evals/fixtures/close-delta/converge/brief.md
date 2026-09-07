# Change Brief

## Metadata

- Lane: `standard`
- Last updated: seeded

## Outcome

Refunds are available from the standard refund path and the admin console,
and each refund is clamped to the order's remaining total and applied at
most once per order.

## Non-goals

- No partial-refund ledger or audit trail.
- No changes to receipt rendering.

## Dangerous false successes

- A refund path that works for typical amounts but can refund more than
  the order's remaining total.
- A refund path that can refund the same order twice.

## Baseline guarantees

- `BG-1`: Administrative refund entry points preserve authorization boundaries.
- `BG-2`: Confidentiality, privacy, and secret handling are not weakened.
- `BG-3`: Refund state and money-moving effects are not corrupted, duplicated, or silently lost.
- `BG-4`: Existing compatibility and repository policy remain intact.

## Map

### Entry points

- Standard refund path and admin-console refund path in `src/refunds.py`
- Receipt rendering (display only)

### Sources of truth and provenance

- `order["total"]` and `order["refunded"]` mutated in place by both refund
  entry points.

### Consumers

- Billing (out of fixture scope).

### State mutations

- In-place mutation of order dictionaries.

### External effects

- None in fixture scope.

### Async, retry, and recovery paths

- None in fixture scope.

### Concurrency and stale-state boundaries

- None in fixture scope.

### Migration, rollout, and mixed-version boundaries

- None in fixture scope.

## Proposed change

Add the standard and admin refund entry points and the receipt renderer.


## Planned mechanism baseline

- Organizing model: one refund helper shared by the standard and admin refund entry points
- Ownership: each entry point owns the order dictionary it mutates for the duration of the call
- Ordering / commit: check the refunded flag, clamp to the remaining total, then mutate
- Identity: orders are identified by the caller-supplied dictionary; the refunded flag is the deduplication rule
- Failure model: an over-limit or repeated refund refuses before mutation; no partial writes
## Invariants

- `INV-1`: A refund never exceeds the order's remaining total.
- `INV-2`: A refunded order is never refunded twice.

## Acceptance criteria

- `AC-1` — Given a refund amount above the remaining total, when any refund
  entry point runs, then the applied refund equals the remaining total.
- `AC-2` — Given an already-refunded order, when any refund entry point
  runs, then it refuses to refund again.

## Future change

Adding a refund reason code later should touch only the shared refund helper.

## Challenge results

### Missing surfaces found

None recorded (the fixture simulates a Challenge miss).

### Failure sequences found

None recorded.

### Unsupported assumptions

None recorded.

### Contract amendments

None.

### Split decision

- Decision: `ONE_CHANGE`
- Rationale: one coherent proof story.

## Implementation crosswalk

| Obligation | Implementation seam | Paths covered | Tests | Deviations |
|---|---|---|---|---|
| INV-1 | remaining-total clamp in refund entry points | standard refund path | manual spot check | none recorded |
| INV-2 | double-refund guard in refund entry points | standard refund path | manual spot check | none recorded |

## Verification evidence

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
| AC-1 | re-run spot check on the standard refund path after remediation | pass | admin path not exercised |
| AC-2 | re-run spot check on the standard refund path after remediation | pass | repeated-refund sequence only |
