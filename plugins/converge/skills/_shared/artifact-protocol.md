# Artifact protocol

## Candidate identity

Review and Verify must describe the exact candidate.

Preferred forms:

- Pull request: repository, PR number, base SHA, head SHA
- Commit range: repository, base SHA, head SHA
- Local worktree: base SHA plus a recorded patch fingerprint and dirty-path list

If a review names a remote PR, the remote head is authoritative. Follow the
repository's exact-review instructions when they are stricter.

## State transitions

Recommended states:

```text
PLANNING
PLANNED
BUILDING
READY_FOR_VERIFY
INTERNALLY_VERIFIED
REVIEW_FINDINGS
READY_FOR_CLOSURE
CLOSED
REPLAN
SPLIT
BLOCKED
```

`INTERNALLY_VERIFIED` means builder-owned evidence passed. It is not independent
approval.

## Review budget

`state.yaml` records:

- `broad_max: 1`
- `broad_used`
- `closure_max: 1`
- `closure_used`

Replanning or splitting creates a new candidate and a new review cycle; do not
silently reset the budget on the same behavioral contract.
