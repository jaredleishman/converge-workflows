# Change Brief

## Metadata

- Request source:
- Lane: `fast | standard | critical`
- Status: `PLANNING`
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

## Proposed change

Describe the smallest coherent mechanism. Avoid implementation choreography.

## Invariants

For Standard work, keep this to at most four important properties.

- `INV-1`:

## Acceptance criteria

For Standard work, keep this to at most six business-level examples.

- `AC-1` — Given / When / Then. Proposed regression:

## Challenge results

### Missing surfaces found

### Failure sequences found

### Unsupported assumptions

### Contract amendments

### Split decision

- Decision: `ONE_CHANGE | SPLIT`
- Rationale:

## Implementation crosswalk

Build fills this in.

| Obligation, including applicable BGs | Implementation seam | Paths covered | Tests | Deviations |
|---|---|---|---|---|

## Verification evidence

Verify fills this in.

| Obligation | Evidence | Result | Limitations |
|---|---|---|---|
