---
name: review
description: "Perform Converge Review Round 1: one read-only, broad, batch-complete review of the exact candidate against the sealed Change Brief."
disable-model-invocation: true
argument-hint: "<candidate, pull request, or exact head>"
---

# Converge Review

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/review-policy.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`
- `../_shared/templates/findings.md`

Then:

1. Confirm the candidate is `INTERNALLY_VERIFIED`, the exact candidate can be
   resolved, and `broad_used` is `0`.
2. Remain read-only. Do not implement fixes or silently amend the brief.
3. Perform the only broad implementation review. Continue after the first
   blocker and return all currently supported findings in one batch.
4. For every finding, identify the root-cause family and sweep the sibling paths
   governed by the same invariant before reporting it.
5. Apply the blocker evidence standard. Separate current blockers from baseline
   issues, future prerequisites, non-blocking hardening, and proposed contract
   amendments.
6. For Critical work, independent same-head reviewers may run in parallel. Hide
   their findings from one another, synthesize once, and remediate only after
   all complete. The set consumes one broad review.
7. Write `.converge/findings.md`, increment `broad_used` to `1`, and update
   `state.yaml`.
8. End with `CLOSED` when clean, `REVIEW_FINDINGS` when blockers exist, or
   `BLOCKED` when evidence is unavailable.

Do not start another broad review on the same contract and candidate lineage.
