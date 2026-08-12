---
name: remediate
description: "Fix the complete Converge Review Round 1 finding batch by root-cause family, record the Remediation Report, and hand the candidate back to Verify."
disable-model-invocation: true
argument-hint: "[findings path or remediation instruction]"
---

# Converge Remediate

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/remediate/` (`${CLAUDE_PLUGIN_ROOT}/skills/remediate/`
in Claude Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `.converge/findings.md`
- `../_shared/workflow.md`
- `../_shared/review-policy.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check remediate` and
   stop with its guidance if it refuses. Before Round 1 remediation, the gate
   also confirms that the reviewed candidate is unchanged. Record `REMEDIATING`
   via `set-status REMEDIATING --stage remediate`; an interrupted `REMEDIATING`
   resumes in place.
2. Fix the complete blocking batch as one root-cause-grouped pass. For each
   finding, fix the shared root cause at its common seam and sweep every
   sibling path named in the finding. Do not patch only the cited example.
3. Stay inside the sealed contract. Do not fix non-blocking follow-ups or
   baseline issues unless the user separately authorizes them. A fix that
   requires amending a sealed brief section is a contract amendment: stop and
   return to Plan's Challenge step.
4. Append a Remediation Report section to `.converge/findings.md` recording,
   per finding: violated invariant, affected sibling paths, shared root cause,
   common fix seam, regressions added, and paths intentionally unchanged.
5. If remediation reveals a distinct new original blocker family or material
   scope expansion, stop serial patching and record `REPLAN` or `SPLIT`.
6. End by recording `READY_FOR_VERIFY` via
   `set-status READY_FOR_VERIFY --stage remediate` so Verify reruns the
   invalidated obligations, or `REPLAN`, `SPLIT`, or `BLOCKED`.

Verify runs next and ends `READY_FOR_CLOSURE`; remediation is not complete
until re-verification passes. Do not commit, push, open a pull request,
deploy, or access production unless the user separately authorizes it.

## Targeted closure correction

When the gate reports `TARGETED_FIX`, do not rerun the Round 1 remediation
process. Record the start with `set-status TARGETED_FIX --stage remediate`, fix
only the closure finding IDs and named siblings, and append the correction to
`closure.md`. End `READY_FOR_TARGETED_CONFIRMATION` or a terminal `REPLAN`,
`SPLIT`, or `BLOCKED`. This path may complete a Round 1 finding ID that Close
kept open, but it cannot absorb a distinct `ORIGINAL_MISS`, expand scope, or
reopen broad review.
