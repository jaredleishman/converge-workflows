# Artifact protocol

## Candidate identity

Review and Verify must describe the exact candidate.

Preferred forms:

- Pull request: repository, PR number, base SHA, head SHA
- Commit range: repository, base SHA, head SHA
- Local worktree: base SHA plus a recorded patch fingerprint and dirty-path list

If a review names a remote PR, the remote head is authoritative. Follow the
repository's exact-review instructions when they are stricter.

For a local worktree candidate, use `candidate capture-worktree`; its base is
the current `HEAD`. The fingerprint separately includes staged and unstaged
binary diffs, untracked paths and contents, and file modes. It excludes
`.converge/` evidence artifacts. For a candidate that spans committed changes
relative to an earlier base, use `candidate record --kind commit` with the
intended base and head instead.
Verify captures the candidate, then checks it again after validation. Review
and Close check it before acting and again before recording an outcome.
Candidate identity is write-once within a Verify or targeted-confirmation
attempt. Repeating the exact same record is idempotent; attempting to replace it
is refused. When validation changes the candidate, return through Build or
Remediate, which clears the old identity, before capturing the next candidate.
Targeted confirmation deliberately has no return to mutation; drift there ends
`BLOCKED` rather than recording a replacement candidate. From that explicit
decision point, replan or split if the drift cannot be reversed.

For commits and pull requests, the caller resolves and records repository,
base, and head. The credential-free gate can compare a caller-supplied current
head but does not fetch remote state.

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
TARGETED_FIX
READY_FOR_TARGETED_CONFIRMATION
CLOSED
REPLAN
SPLIT
BLOCKED
```

`INTERNALLY_VERIFIED` means builder-owned evidence passed. It is not independent
approval.

Verify ends `INTERNALLY_VERIFIED` on the first pass. When it reruns after
remediation of Round 1 findings, it ends `READY_FOR_CLOSURE` instead.

Build may remain `BUILDING` across interrupted sessions. Verify may return
`READY_FOR_VERIFY` to `BUILDING` when candidate-owned checks fail. `BLOCKED`
records the exact prior status; after the blocker is resolved, only the gate's
`resume` command restores it. Terminal states do not transition. A new contract
starts with the gate's `init` command, which archives the finished files under
`.converge/archive/` and writes a fresh `PLANNING` state and brief.

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
python3 "<plugin-root>/scripts/state_gate.py" init --lane standard
python3 "<plugin-root>/scripts/state_gate.py" check review
python3 "<plugin-root>/scripts/state_gate.py" set-status READY_FOR_VERIFY --stage build
python3 "<plugin-root>/scripts/state_gate.py" candidate capture-worktree
python3 "<plugin-root>/scripts/state_gate.py" candidate check
python3 "<plugin-root>/scripts/state_gate.py" resume
```

Rules:

- Check the gate before acting. Review and Close budget is consumed
  automatically when their outcome transition succeeds.
- `init` creates `.converge/` from the templates, reuses an existing
  `PLANNING` contract, or archives a `CLOSED` / `REPLAN` / `SPLIT` contract
  and starts a new one. It refuses to clobber any other live status.
- `PLANNED` requires `brief.md`. Review outcomes require `findings.md`.
  Close outcomes require `closure.md`. Write the artifact, then `set-status`.
  Do not copy budget or disposition into the markdown; `state.yaml` is the
  machine record.
- Never edit `broad_used` or `closure_used` by hand.
- Record finding IDs with repeated `--finding` arguments on
  `REVIEW_FINDINGS`, `TARGETED_FIX`, or a terminal review outcome. Machine lists
  in `state.yaml` use JSON-style inline YAML such as `["REV-1", "REV-2"]`.
- `set-status BLOCKED` requires `--reason`; run `resume` only after resolving it.
- A `BLOCKED` Review or Close attempt does not consume its review budget. The
  corresponding successful outcome transition does.
- A refused check is a workflow decision point. Follow the printed guidance —
  usually `REPLAN`, `SPLIT`, or an explicit new contract — instead of routing
  around the gate.
- If Python 3 is unavailable, apply the same rules manually and say so in the
  artifact you produce.
