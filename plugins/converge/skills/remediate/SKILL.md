---
name: remediate
description: "Fix the complete Converge Review Round 1 finding batch by root-cause family, record the Remediation Report, and hand the candidate back to Verify."
disable-model-invocation: true
argument-hint: "[findings path or remediation instruction]"
---

# Converge Remediate

`../_shared/` is relative to this skill folder; `.converge/` is at the project
root; `<plugin-root>` is the installed plugin directory.

Read `.converge/brief.md`, `.converge/state.yaml`, `.converge/findings.md`,
`../_shared/workflow.md`, the Remediation and Loop breaker sections of
`../_shared/review-policy.md`, and `../_shared/candidate-checks.md`.

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check remediate`; stop
   with its guidance if it refuses. Before Round 1 remediation it also confirms
   the reviewed candidate is unchanged. Record
   `set-status REMEDIATING --stage remediate`; an interrupted `REMEDIATING`
   resumes in place.
2. Fix the complete blocking batch as one root-cause-grouped pass: fix the
   shared cause at its common seam and sweep every sibling path the finding
   names. Never patch only the cited example.
3. Stay inside the sealed contract. Do not fix follow-ups or baseline issues
   unless the user separately authorizes them. A fix that needs a sealed
   section amended is a contract amendment: stop and return to Plan.
4. Append a Remediation Report to `.converge/findings.md`: per finding, the
   cited row, sibling paths, shared root cause, fix seam, regressions added,
   and paths intentionally unchanged.
5. Run the planned-mechanism drift checkpoint in `candidate-checks.md` and
   record the declaration in the report.
6. If remediation reveals a distinct new blocker family, material scope
   expansion, or an unplanned mechanism that changes an axis, stop serial
   patching: `REPLAN` for the same outcome or `SPLIT` for independently
   provable outcomes. A new asynchronous mechanism is not a cheap targeted
   correction because it fixes a named example.
7. End with `set-status READY_FOR_VERIFY --stage remediate` so Verify reruns
   the invalidated obligations, or `REPLAN`, `SPLIT`, or `BLOCKED`.

Remediation is complete only when re-verification passes. No commit, push,
pull request, deploy, or production access without separate authorization.

## Targeted closure correction

When the gate reports `TARGETED_FIX`: record
`set-status TARGETED_FIX --stage remediate`, fix only the closure finding IDs
and named siblings, append the correction to `closure.md`, and end
`READY_FOR_TARGETED_CONFIRMATION` or a terminal `REPLAN`, `SPLIT`, or
`BLOCKED`. This path may complete a Round 1 ID Close kept open; it cannot
absorb a distinct `ORIGINAL_MISS`, expand scope, or reopen broad review.
