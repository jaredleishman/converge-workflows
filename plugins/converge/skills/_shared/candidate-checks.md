# Candidate checks

Build, Verify, and Remediate read this file. Plan-time mapping, split, and
baseline-guarantee rules live in `scope-policy.md`.

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
