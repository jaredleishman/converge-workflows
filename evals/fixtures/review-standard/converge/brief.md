# Change Brief

## Metadata

- Request source: eval fixture `review-standard`
- Lane: `standard`
- Status: `INTERNALLY_VERIFIED`
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

- `src/discounts.py`: `apply_discount_api`, `apply_discount_batch`,
  `apply_discount_admin`
- `src/checkout.py`: `compute_total`

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

## Invariants

- `INV-1`: The discount rate is clamped to `MAX_DISCOUNT_RATE` at every entry
  point before it modifies an order total.
- `INV-2`: An order total is never negative.

## Acceptance criteria

- `AC-1` — Given a rate above `MAX_DISCOUNT_RATE`, when any discount entry
  point runs, then the applied rate equals `MAX_DISCOUNT_RATE`.
- `AC-2` — Given any line items, when `compute_total` runs, then the result is
  never negative.

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
| INV-1 | rate clamp in discount entry points | `apply_discount_api` | manual spot check | none recorded |
| INV-2 | `compute_total` | `compute_total` | manual spot check | none recorded |

## Verification evidence

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
| AC-1 | spot check on `apply_discount_api` | pass | other entry points not exercised |
| AC-2 | spot check with positive quantities | pass | negative quantities not exercised |
