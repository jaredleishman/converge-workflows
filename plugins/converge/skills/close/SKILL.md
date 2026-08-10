---
name: close
description: "Perform Converge Review Round 2: a delta-only closure review after the complete Round 1 finding batch has been remediated and re-verified."
disable-model-invocation: true
argument-hint: "<remediated candidate or exact head>"
---

# Converge Close

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `.converge/findings.md`
- `../_shared/workflow.md`
- `../_shared/review-policy.md`
- `../_shared/artifact-protocol.md`
- `../_shared/templates/closure.md`

Then:

1. Confirm Round 1 used the broad-review budget, all remediation was applied as
   one root-cause-grouped batch, Verify reran invalidated obligations, and
   `closure_used` is `0`.
2. Review only the prior findings, remediation range, named invariant families,
   named sibling paths, and code introduced or invalidated by the fix.
3. Do not restart an unconstrained full review of untouched code.
4. Close or reject each prior finding with concrete evidence.
5. Classify every new issue as `FIX_INTRODUCED`, `ORIGINAL_MISS`,
   `NEW_EVIDENCE`, `SCOPE_EXPANSION`, or `OUT_OF_SCOPE_FOLLOW_UP`.
6. Apply the loop breaker. A distinct new original P1 family normally means
   `REPLAN` or `SPLIT`, not Review Round 3.
7. Write `.converge/closure.md`, increment `closure_used` to `1`, update
   `state.yaml`, and return `CLOSED`, `REPLAN`, `SPLIT`, or `BLOCKED`.

A small fix-introduced issue may receive targeted confirmation after a targeted
fix. That does not authorize another broad review.
