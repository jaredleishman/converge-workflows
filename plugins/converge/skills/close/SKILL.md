---
name: close
description: "Perform Converge Review Round 2: a delta-only closure review after the complete Round 1 finding batch has been remediated and re-verified."
disable-model-invocation: true
argument-hint: "<remediated candidate or exact head>"
---

# Converge Close

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/close/` (`${CLAUDE_PLUGIN_ROOT}/skills/close/` in Claude
Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `.converge/findings.md`
- `../_shared/workflow.md`
- `../_shared/review-policy.md`
- `../_shared/artifact-protocol.md`
- `../_shared/templates/closure.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check close` and stop
   with its guidance if it refuses; it confirms the state is
   `READY_FOR_CLOSURE`, closure budget is unused, Round 1 finding IDs are open,
   and the exact candidate is unchanged. For a pull request, resolve its head
   again and run `candidate check --current-head <sha>`. Confirm remediation was
   applied as one root-cause-grouped batch (the Remediation Report in
   `findings.md`) and that Verify reran the invalidated obligations.
2. Review only the prior findings, remediation range, named invariant families,
   named sibling paths, and code introduced or invalidated by the fix.
3. Do not restart an unconstrained full review of untouched code.
4. Close or reject each prior finding with concrete evidence.
5. Classify every new issue as `FIX_INTRODUCED`, `ORIGINAL_MISS`,
   `NEW_EVIDENCE`, `SCOPE_EXPANSION`, or `OUT_OF_SCOPE_FOLLOW_UP`.
   Record whether it was reachable at the Round 1 candidate and cite the
   remediation-range evidence. `ORIGINAL_MISS` requires Round 1 reachability
   plus a violated sealed obligation or non-waivable baseline guarantee;
   `FIX_INTRODUCED` requires that it was not reachable until remediation;
   `NEW_EVIDENCE` requires the decisive evidence to have been genuinely
   unavailable at Round 1 and must not also be labeled `ORIGINAL_MISS`.
6. Apply the loop breaker. A distinct blocking `ORIGINAL_MISS`, blocking
   `NEW_EVIDENCE`, or material `SCOPE_EXPANSION` means `REPLAN` or `SPLIT`, not
   Review Round 3. Exception: when new evidence only proves an already-open
   Round 1 family incomplete and the correction stays small and inside the
   sealed mechanism, keep that ID open for the one targeted confirmation;
   otherwise replan or split. Never demote a candidate-caused baseline
   regression to a follow-up.
7. Write `.converge/closure.md` from the template without copying budget or
   disposition. Then run `candidate check` again; for a pull request, resolve
   and pass its current head again. Record one outcome through the gate:
   `CLOSED`; `TARGETED_FIX --finding CLOSE-1` for a small remediation-caused
   defect; `TARGETED_FIX --finding REV-1` to keep an incomplete prior family
   open; `REPLAN` or `SPLIT` with finding IDs for an original miss or scope
   expansion or distinct blocking new evidence; or `BLOCKED --reason ...` when
   evidence is unavailable. A successful budgeted Close outcome consumes
   closure budget in the same state-file update; `BLOCKED` does not. It closes
   prior IDs that are not repeated on the outcome and keeps repeated IDs open.
   The gate refuses the outcome if `closure.md` is missing. Never edit budget
   or finding-list fields in `state.yaml` by hand.

A small fix-introduced issue receives at most one targeted Remediate and Verify
confirmation. Targeted confirmation cannot return to another fix; it closes,
replans, splits, or blocks. It never authorizes another broad or closure review.
