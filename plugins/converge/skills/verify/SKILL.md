---
name: verify
description: "Verify the exact Converge candidate against its Change Brief, invariants, acceptance criteria, connected paths, and repository-native checks."
disable-model-invocation: true
argument-hint: "[candidate, commit, branch, or pull request]"
---

# Converge Verify

`../_shared/` is relative to this skill folder; `.converge/` is at the project
root; `<plugin-root>` is the installed plugin directory.

Read `.converge/brief.md`, `.converge/state.yaml`, `../_shared/workflow.md`,
`../_shared/candidate-checks.md`, and `../_shared/artifact-protocol.md`.
Verify needs the sealed contract, the crosswalk, and the Map's entry points;
it does not re-derive the Map.

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check verify`; stop with
   its guidance if it refuses. It accepts `READY_FOR_VERIFY` and
   `READY_FOR_TARGETED_CONFIRMATION`. Record the exact candidate:
   `candidate capture-worktree` locally, or `candidate record` with the
   caller-resolved repository/base/head for a commit or pull request. Identity
   is write-once for this attempt (`artifact-protocol.md`).
2. Verify every acceptance criterion, invariant, triggered matrix path, and
   applicable baseline guarantee through the crosswalk. Exercise the entry
   points, consumers, and failure cases the brief names. Check that the Future
   change has one obvious seam.
3. Stay read-only on candidate files. Run repository-native validation
   cheapest first. Never claim a check that was not run. If a formatter-capable
   check changes candidate files, verification is invalid; do not accept,
   patch, or revert the drift silently.
4. Classify material evidence per `candidate-checks.md`: `BOUNDARY_DIRECT`,
   `BOUNDARY_FAITHFUL`, `PROXY`, or `UNAVAILABLE`. A controlled clock or fake
   endpoint that follows the production control path is boundary-faithful; a
   direct helper call or downstream-state injection is not.
5. Grade each obligation `PASS`, `PARTIAL`, `UNPROVEN`, `BLOCKED`, or
   `NOT_APPLICABLE`. Required obligations need direct or boundary-faithful
   evidence; proxy-only is `UNPROVEN`. Advance only when every required
   obligation is `PASS`.
6. Independently repeat the planned-mechanism drift checkpoint from
   `candidate-checks.md`. Append observed facts to the Map; return `REPLAN` or
   `SPLIT` when an axis changed.
7. Record evidence, result, and limitations in the Verification evidence
   table. Then run `candidate check` (with `--current-head` for a pull
   request). If the implementation expanded the contract or invalidated the
   split decision, return to Plan.
8. Record the result through `set-status`:
   - First Verify passes (`broad_used` is 0) → `INTERNALLY_VERIFIED`.
   - Re-verify after Round 1 remediation passes → `READY_FOR_CLOSURE`.
   - Targeted confirmation passes → `CLOSED`, with evidence appended to
     `closure.md`; otherwise only `REPLAN`, `SPLIT`, or `BLOCKED`.
   - A candidate-owned check or required proof fails before Review →
     `BUILDING --stage build`.
   - Re-verify after remediation fails → `REMEDIATING --stage remediate`;
     finding IDs and budget stay intact.
   - Required external evidence `UNAVAILABLE` → `BLOCKED --reason`; `resume`
     when resolved.

`INTERNALLY_VERIFIED` is builder-owned evidence, not independent approval.
