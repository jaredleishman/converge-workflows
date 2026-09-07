# Change Brief

## Metadata

- Lane: `standard`
- Last updated: seeded

## Outcome

Discount application is available from the API, the nightly batch job, and the
admin console, and order totals are computed from line items.

## Non-goals

- No currency conversion.
- No new persistence layer.

## Dangerous false successes

- A discount entry point that works for typical rates but does not clamp an
  excessive rate.
- A checkout that returns a plausible-looking total for malformed line items.

## Baseline guarantees

- `BG-1`: Authorization and tenant-isolation boundaries are not weakened.
- `BG-2`: Confidentiality, privacy, and secret handling are not weakened.
- `BG-3`: Order data and billing effects are not corrupted or silently lost.
- `BG-4`: Existing compatibility and repository policy remain intact.

## Map

### Entry points

- Discount application from the public API, the nightly batch job, and the
  admin console
- Checkout line-item totaling

### Sources of truth and provenance

- `order["total"]` mutated in place by every discount entry point.

### Consumers

- Billing (out of fixture scope).

### State mutations

- In-place mutation of order dictionaries.

### External effects

- None.

### Async, retry, and recovery paths

- The batch entry point runs nightly over many orders.

### Concurrency and stale-state boundaries

- None in fixture scope.

### Migration, rollout, and mixed-version boundaries

- None in fixture scope.

## Proposed change

Add the three discount entry points and the checkout total computation.


## Planned mechanism baseline

- Organizing model: one clamp helper shared by every discount entry point; totals computed from line items
- Ownership: each entry point owns the order dictionary it mutates for the duration of the call
- Ordering / commit: clamp the rate before any mutation of `order["total"]`
- Identity: orders are identified by the caller-supplied dictionary; no deduplication
- Failure model: an invalid rate or line item raises before mutation; no partial writes
## Invariants

- `INV-1`: The discount rate is clamped to `MAX_DISCOUNT_RATE` at every entry
  point before it modifies an order total.
- `INV-2`: An order total is never negative.

## Acceptance criteria

- `AC-1` — Given a rate above `MAX_DISCOUNT_RATE`, when any discount entry
  point runs, then the applied rate equals `MAX_DISCOUNT_RATE`.
- `AC-2` — Given any line items, when checkout totals an order, then the
  result is never negative.

## Future change

Adding a per-tenant maximum rate later should touch only the clamp helper.

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
| INV-1 | rate clamp in discount entry points | public API path | manual spot check | none recorded |
| INV-2 | checkout totaling | checkout totaling | manual spot check | none recorded |

## Verification evidence

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
| AC-1 | spot check on the public API discount path | pass | other entry points not exercised |
| AC-2 | spot check with positive quantities | pass | negative quantities not exercised |
