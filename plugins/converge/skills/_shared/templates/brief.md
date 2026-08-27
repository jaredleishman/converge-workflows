# Change Brief

## Metadata

- Request source:
- Lane: `fast | standard | critical`
- Lane rationale:
- Compound-boundary screen: `not-triggered | critical | standard-exception`
- Status: `PLANNING`
- Last updated:

### Standard exception (conditional)

Omit this subsection for Fast, ordinary Standard, and Critical work. Include it
only when the compound-boundary screen would select Critical but Standard is
claimed.

- Coupled boundaries and defeating sequence:
- Local containment and reversible unit:
- Independent recovery:
- Cross-context or cross-attempt ownership analysis:
- Falsifying evidence:

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

## Planned mechanism baseline

Record the approved mechanism, ownership, ordering, identity, and failure-model
decisions before Build. Later Map observations may add facts but cannot make a
different mechanism retroactively planned.

## Conditional lifecycle and ownership matrix

Include this section only when `scope-policy.md` triggers it for Critical work;
otherwise omit it. Use one row per applicable event or failure path and give a
concrete reason for any omitted required event.

| Event or failure path | Control context and handoff | Election or visibility effect | Persistence owner and timing | Resource owner and release | Durable state | Identity, collision, and deduplication | Transaction or effect commit | Retry, cleanup, and next attempt | Failure evidence |
|---|---|---|---|---|---|---|---|---|---|

## Invariants

For Standard work, keep this to at most four important properties.

- `INV-1`:

## Acceptance criteria

For Standard work, keep this to at most six business-level examples.

- `AC-1` — Given / When / Then. Proposed regression:

## Critical proof obligations

Include this section only for material Critical boundaries; otherwise omit it.

| Obligation | Production event or boundary | Sufficient direct or faithful evidence | Proxy or mock limitations | Planned disposition |
|---|---|---|---|---|

## Challenge results

### Independent passes

For Critical work, record both independent passes, their exact planning
candidate, primary lens, and limitations. Omit this table for other lanes.

| Pass | Exact planning candidate | Primary lens | Limitations |
|---|---|---|---|

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

Use `PASS`, `PARTIAL`, `UNPROVEN`, `BLOCKED`, or `NOT_APPLICABLE`. A required
production boundary cannot be `PASS` on proxy-only evidence.
