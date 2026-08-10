# Change Brief

## Metadata

- Request source: eval fixture `close-delta`
- Lane: `standard`
- Status: `READY_FOR_CLOSURE`
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

## Map

### Entry points

- `src/refunds.py`: `issue_refund`, `issue_refund_admin`
- `src/refunds.py`: `format_refund_receipt` (display only)

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

## Invariants

- `INV-1`: A refund never exceeds the order's remaining total.
- `INV-2`: A refunded order is never refunded twice.

## Acceptance criteria

- `AC-1` — Given a refund amount above the remaining total, when any refund
  entry point runs, then the applied refund equals the remaining total.
- `AC-2` — Given an already-refunded order, when any refund entry point
  runs, then it refuses to refund again.

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
| INV-1 | remaining-total clamp in refund entry points | `issue_refund` | manual spot check | none recorded |
| INV-2 | double-refund guard in refund entry points | `issue_refund` | manual spot check | none recorded |

## Verification evidence

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
| AC-1 | re-run spot check on `issue_refund` after remediation | pass | admin path not exercised |
| AC-2 | re-run spot check on `issue_refund` after remediation | pass | repeated-refund sequence only |
