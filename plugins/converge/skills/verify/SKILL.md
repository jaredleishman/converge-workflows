---
name: verify
description: "Verify the exact Converge candidate against its Change Brief, invariants, acceptance criteria, connected paths, and repository-native checks."
disable-model-invocation: true
argument-hint: "[candidate, commit, branch, or pull request]"
---

# Converge Verify

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/verify/` (`${CLAUDE_PLUGIN_ROOT}/skills/verify/` in
Claude Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/artifact-protocol.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check verify` and stop
   with its guidance if it refuses. It accepts ordinary `READY_FOR_VERIFY` and
   `READY_FOR_TARGETED_CONFIRMATION`. Resolve and record the exact candidate:
   use `candidate capture-worktree` locally, or `candidate record` with the
   caller-resolved repository/base/head for a commit or pull request. Candidate
   identity is write-once for this attempt; an exact repeat is idempotent, but
   replacing it requires a legal return through Build or Remediate. Targeted
   confirmation cannot return to mutation; candidate drift there must end
   `BLOCKED`, followed by `REPLAN` or `SPLIT` if the drift cannot be reversed.
2. Verify every acceptance criterion and invariant using the implementation
   crosswalk. Exercise the important entry points, consumers, and relevant
   failure cases named in the brief.
3. Remain read-only on candidate files. Run repository-native validation in
   cheap-to-expensive order. Do not claim checks that were not run. If a
   formatter-capable check changes candidate files, verification is invalid;
   do not silently accept, patch, or revert the drift.
4. For material tests, explain which broken mechanism or injected failure they
   would detect. This is a sensitivity claim, not mathematical proof.
5. Record evidence, results, and unavailable or partial evidence in the
   Verification Evidence table in `brief.md`.
6. Run `candidate check` after validation (and pass the freshly resolved remote
   head for a pull request). Reassess whether the implementation expanded the contract or invalidated the
   split decision. Return to Plan when it did.
7. Choose the result by branch:
   - Initial Verify passes (`broad_used` is `0`) → `INTERNALLY_VERIFIED`.
   - Round 1 remediation re-verifies (`broad_used` is `1` with open findings)
     → `READY_FOR_CLOSURE`.
   - Targeted confirmation passes → `CLOSED`; append its evidence to
     `closure.md`. It may otherwise end only `REPLAN`, `SPLIT`, or `BLOCKED`.
   - A candidate-owned check fails before Review → record the failed evidence
     and return to `BUILDING` via `set-status BUILDING --stage build`.
   - Re-verification of Round 1 remediation fails → return to `REMEDIATING` via
     `set-status REMEDIATING --stage remediate`; keep the original finding IDs
     and broad budget intact.
   - Missing external evidence or an unresolved prerequisite → `BLOCKED` with
     `--reason`; use `resume` after it is resolved.
   Record every result through the gate's `set-status`.

`INTERNALLY_VERIFIED` means builder-owned evidence passed. It is not independent
review approval.
