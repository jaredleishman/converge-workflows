# Artifact protocol

## State gate

`<plugin-root>/scripts/state_gate.py` (`${CLAUDE_PLUGIN_ROOT}` in Claude
Code; otherwise two directories above `_shared/`). Skills run it against
`.converge/state.yaml`:

```text
show                                   # status, budgets, next allowed action
init --lane <fast|standard|critical>   # new contract; archives a finished one
check <skill>                          # precondition for a stage
set-status <STATUS> --stage <stage>    # record a transition
candidate capture-worktree | record | check
resume                                 # after BLOCKED is resolved
```

Rules:

- Check the gate before acting. A refusal is a workflow decision point: follow
  its guidance (`REPLAN`, `SPLIT`, or a new contract), do not route around it.
- `PLANNED` requires `brief.md`. Review outcomes require `findings.md`. Close
  outcomes require `closure.md`. Write the artifact, then `set-status`.
- Review and Close outcomes consume their budget in the same state update.
  `BLOCKED` does not. Never edit `broad_used`, `closure_used`, or finding
  lists by hand; pass finding IDs with repeated `--finding`.
- `BLOCKED` requires `--reason`; `resume` restores the exact prior status.
- Terminal states (`CLOSED`, `REPLAN`, `SPLIT`) do not transition. `init`
  archives them under `.converge/archive/` and starts fresh. Replanning or
  splitting creates a new candidate and cycle; budget is never reset on the
  same contract.
- Budget and disposition live only in `state.yaml`; do not copy them into
  Markdown.
- If Python 3 is unavailable, apply the same rules by hand and say so.

## Candidate identity

Verify, Review, and Close act on an exact candidate:

- Pull request: repository, PR number, base SHA, head SHA
- Commit range: repository, base SHA, head SHA
- Local worktree: base SHA plus patch fingerprint and dirty-path list, via
  `candidate capture-worktree` (excludes `.converge/`)

Verify captures the candidate, then checks it again after validation. Review
and Close check it before acting and again before recording an outcome. For a
pull request the remote head is authoritative; the caller resolves it and
passes `--current-head`.

Identity is write-once within a Verify or targeted-confirmation attempt: an
exact repeat is idempotent, a replacement is refused. When validation changes
the candidate, return through Build or Remediate, which clears the identity.
Targeted confirmation has no return to mutation: drift there ends `BLOCKED`,
then `REPLAN` or `SPLIT` if it cannot be reversed. After `TARGETED_FIX`, only
the kept-open IDs may change.
