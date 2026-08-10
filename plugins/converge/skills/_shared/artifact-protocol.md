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
REMEDIATING
READY_FOR_CLOSURE
CLOSED
REPLAN
SPLIT
BLOCKED
```

`INTERNALLY_VERIFIED` means builder-owned evidence passed. It is not independent
approval.

Verify ends `INTERNALLY_VERIFIED` on the first pass. When it reruns after
remediation of Round 1 findings, it ends `READY_FOR_CLOSURE` instead.

## Review budget

`state.yaml` records:

- `broad_max: 1`
- `broad_used`
- `closure_max: 1`
- `closure_used`

Replanning or splitting creates a new candidate and a new review cycle; do not
silently reset the budget on the same behavioral contract.

## State gate

The plugin bundles a standard-library gate script at
`<plugin-root>/scripts/state_gate.py`, where `<plugin-root>` is the installed
plugin directory (`${CLAUDE_PLUGIN_ROOT}` in Claude Code; in other hosts,
resolve it from this file's location: it is two directories above `_shared/`).

Skills run it against the project's `.converge/state.yaml`:

```text
python3 "<plugin-root>/scripts/state_gate.py" show
python3 "<plugin-root>/scripts/state_gate.py" check review
python3 "<plugin-root>/scripts/state_gate.py" consume broad
python3 "<plugin-root>/scripts/state_gate.py" set-status READY_FOR_VERIFY --stage build
```

Rules:

- Check the gate before acting; consume budget through the gate only.
- Never edit `broad_used` or `closure_used` by hand.
- A refused check is a workflow decision point. Follow the printed guidance —
  usually `REPLAN`, `SPLIT`, or an explicit new contract — instead of routing
  around the gate.
- If Python 3 is unavailable, apply the same rules manually and say so in the
  artifact you produce.
