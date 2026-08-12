---
name: review
description: "Perform Converge Review Round 1: one read-only, broad, batch-complete review of the exact candidate against the sealed Change Brief."
disable-model-invocation: true
argument-hint: "<candidate, pull request, or exact head>"
---

# Converge Review

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/review/` (`${CLAUDE_PLUGIN_ROOT}/skills/review/` in
Claude Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/review-policy.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`
- `../_shared/templates/findings.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check review` and stop
   with its guidance if it refuses; it confirms `INTERNALLY_VERIFIED`, unused
   broad budget, and an unchanged exact candidate. For a pull request, resolve
   the remote head again and run `candidate check --current-head <sha>`.
2. Remain read-only. Do not implement fixes or silently amend the brief.
3. Perform the only broad implementation review. Continue after the first
   blocker and return all currently supported findings in one batch.
4. For every finding, identify the root-cause family and sweep the sibling paths
   governed by the same invariant before reporting it.
5. Apply the blocker evidence standard. Separate current blockers from baseline
   issues, future prerequisites, non-blocking hardening, and proposed contract
   amendments.
   A candidate-caused regression may also violate a non-waivable baseline
   guarantee even when the brief omitted an explicit acceptance criterion.
6. For Critical work, independent same-head reviewers may run in parallel. Hide
   their findings from one another, synthesize once, and remediate only after
   all complete. The set consumes one broad review.
7. If Fast skipped Challenge and Review finds a supported P1, record the
   lane-misjudgment signal in `findings.md`; it does not add a review round.
8. Write `.converge/findings.md`, then record the outcome with one gate
   transition. First run `candidate check` again; for a pull request, resolve
   and pass its current head again. Use `CLOSED` when clean; use
   `REVIEW_FINDINGS --finding REV-1`
   (repeat `--finding` for the batch) when blockers exist; use `REPLAN` or
   `SPLIT` with one or more `--finding` IDs for a contract-level outcome; or
   use `BLOCKED --reason ...` when evidence is unavailable. A successful Review
   outcome transition
   automatically consumes broad budget in the same state-file update.
   `BLOCKED` does not. After the gate succeeds, update `findings.md` with the
   actual disposition and budget. Never edit budget or finding-list fields in
   `state.yaml` by hand.

Do not start another broad review on the same contract and candidate lineage.
When blockers exist, the next step is the `remediate` skill.
