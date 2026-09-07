# Candidate checks

Build, Verify, and Remediate read this.

## Proof fidelity

Classify material evidence by the boundary it actually crosses:

- `BOUNDARY_DIRECT` — exercises the production entry point and real boundary.
- `BOUNDARY_FAITHFUL` — a controlled clock, fake endpoint, test database, or
  similar substitute that preserves the production control path, ownership,
  transaction, and failure semantics being claimed.
- `PROXY` — calls a helper directly, injects downstream state, checks only that
  a mock was called, relies on static inspection, or bypasses the mechanism.
- `UNAVAILABLE` — required evidence cannot currently be obtained.

A material obligation is `PASS` only on boundary-direct or boundary-faithful
evidence. Proxy evidence may support `PARTIAL`; proxy-only evidence is
`UNPROVEN` for a required production boundary. `UNAVAILABLE` evidence for a
required obligation is `BLOCKED`. Live traffic and wall-clock sleep are not
required when a controlled test faithfully crosses the same boundary.

Examples: `BOUNDARY_FAITHFUL` is a retry test with a fake clock and fake
endpoint that keeps the production ownership and commit path. `PROXY` is
calling the helper directly or asserting a mock was called without crossing
the entry point.

For every material test record the production event or boundary exercised, the
broken mechanism or injected failure it would detect, and each proxy or mock
that limits the claim.

## Planned-mechanism drift checkpoint

Run before Build or Remediate hands a candidate to Verify; Verify repeats it
independently. Compare the diff and connected seams with the sealed Planned
mechanism baseline. Inventory every new or materially changed:

- Thread, task, queue, callback, or signal
- Transaction boundary or commit point
- Retry, timeout, cancellation, recovery, or late-completion behavior
- Logical or physical resource owner and release point
- Identity namespace, collision, or deduplication rule
- Persistent-state transition, external effect, or promotion path

Append observed facts to the Map; never use them to rewrite the baseline. If
any item changes one of the four axes (ownership, ordering/commit, identity,
failure model), the contract cannot continue serially: `REPLAN` for the same
outcome or `SPLIT` for independently provable outcomes. Do not open a second
worktree or second implementation to resolve drift. When the checkpoint
passes, record a concrete "none found" with the seams inspected.

Examples: drift is Build adding a retry queue that moves failure handling to
a new worker, changing the failure-model axis → `REPLAN`. No drift is
extracting a helper with identical ownership, ordering, identity, and failure
behavior → record "none found".

## Deletion pass (Build only)

After the drift checkpoint passes and before Verify, remove anything the
contract did not buy: unused types, wrapper layers, extra endpoints or flags,
speculative registries, comments that restate the brief. Never delete a seam
the Future change would use, a baseline-guarantee path, or the only test
evidencing an acceptance criterion. One pass; if an acceptance criterion fails
afterwards, restore it and fix narrowly. Extracting classes, renaming for
cleanliness, or adding an interface "for extensibility" is not deletion.
Record `Deleted:` or `Deletion pass: none required` in the crosswalk.
