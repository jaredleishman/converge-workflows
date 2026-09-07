---
name: close
description: "Perform Converge Review Round 2: a delta-only closure review after the complete Round 1 finding batch has been remediated and re-verified."
disable-model-invocation: true
argument-hint: "<remediated candidate or exact head>"
---

# Converge Close

`../_shared/` is relative to this skill folder; `.converge/` is at the project
root; `<plugin-root>` is the installed plugin directory.

Read `.converge/findings.md`, `.converge/state.yaml`, the sealed contract and
crosswalk sections of `.converge/brief.md`, the Round 2 and Loop breaker
sections of `../_shared/review-policy.md`, `../_shared/artifact-protocol.md`,
and `../_shared/templates/closure.md`.

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check close`; stop with
   its guidance if it refuses. It confirms `READY_FOR_CLOSURE`, unused closure
   budget, open Round 1 IDs, and an unchanged candidate. For a pull request,
   run `candidate check --current-head <sha>`. Confirm the Remediation Report
   exists and Verify reran the invalidated obligations.
2. Review only the prior findings, the remediation range, the named invariant
   families and sibling paths, and code the fix introduced or invalidated. Do
   not restart a full review of untouched code.
3. Close or reject each prior finding with concrete evidence.
4. Classify every new issue as `FIX_INTRODUCED`, `ORIGINAL_MISS`,
   `NEW_EVIDENCE`, `SCOPE_EXPANSION`, or `OUT_OF_SCOPE_FOLLOW_UP` using the
   definitions and Round 1 reachability rules in `review-policy.md`. Each new
   blocking issue cites a row.
5. Apply the loop breaker: a distinct blocking `ORIGINAL_MISS`, blocking
   `NEW_EVIDENCE`, or material `SCOPE_EXPANSION` is `REPLAN` or `SPLIT`, not a
   third review. Exception: new evidence that only proves an already-open
   Round 1 family incomplete, with a small correction inside the sealed
   mechanism, keeps that ID open for the one targeted confirmation. Never
   demote a candidate-caused baseline regression to a follow-up.
6. Write `.converge/closure.md` from the template without copying budget or
   disposition. Run `candidate check` again. Record one outcome via
   `set-status`: `CLOSED`; `TARGETED_FIX --finding CLOSE-1` for a small
   fix-introduced defect; `TARGETED_FIX --finding REV-1` to keep an incomplete
   family open; `REPLAN` or `SPLIT` with finding IDs; or `BLOCKED --reason`.
   The gate consumes closure budget on a successful outcome, closes prior IDs
   not repeated on the outcome, and refuses if `closure.md` is missing.

A fix-introduced issue gets at most one targeted Remediate and one Verify
confirmation, which then closes, replans, splits, or blocks. Nothing here
authorizes another broad or closure review.
