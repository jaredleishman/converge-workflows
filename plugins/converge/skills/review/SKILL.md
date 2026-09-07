---
name: review
description: "Perform Converge Review Round 1: one read-only, broad, batch-complete review of the exact candidate against the sealed Change Brief."
disable-model-invocation: true
argument-hint: "<candidate, pull request, or exact head>"
---

# Converge Review

`../_shared/` is relative to this skill folder; `.converge/` is at the project
root; `<plugin-root>` is the installed plugin directory.

Read `.converge/brief.md`, `.converge/state.yaml`, `../_shared/workflow.md`,
`../_shared/review-policy.md`, the baseline-guarantees section of
`../_shared/scope-policy.md`, `../_shared/artifact-protocol.md`, and
`../_shared/templates/findings.md`.

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check review`; stop with
   its guidance if it refuses. It confirms `INTERNALLY_VERIFIED`, unused broad
   budget, and an unchanged candidate. For a pull request, resolve the remote
   head and run `candidate check --current-head <sha>`.
2. Stay read-only. Do not fix or amend the brief.
3. Perform the only broad review. Continue past the first blocker; return all
   supported findings in one batch. Prefer a different model family from the
   builder; otherwise record `same-family-review`.
4. For every finding, name the root-cause family and sweep the sibling paths
   governed by the same invariant before reporting.
5. Every finding cites a row (`Cites:`). Apply the blocker standard. Separate
   blockers from baseline issues, non-blocking follow-ups, and proposed
   amendments. A candidate-caused regression may violate a baseline guarantee
   even without an AC. Check that the Future change has a home; if not, it is
   a load-bearing miss.
6. For lifecycle-heavy Critical work, use the complementary lenses in
   `review-policy.md`, keep reports hidden until they finish, record the
   Critical reviewer audit, deduplicate families once, and treat the set as one
   broad review. Do not synthesize mismatched candidates.
7. If Fast skipped Challenge and Review finds a supported P1, record the
   lane-misjudgment signal; it does not add a round.
8. Write `.converge/findings.md` from the template without copying budget or
   disposition. Run `candidate check` again (with `--current-head` for a pull
   request). Record one outcome via `set-status`: `CLOSED` when clean;
   `REVIEW_FINDINGS --finding REV-1 [--finding REV-2 ...]` for blockers;
   `REPLAN` or `SPLIT` with finding IDs for a contract-level outcome; or
   `BLOCKED --reason`. The gate consumes broad budget on a successful outcome
   and refuses if `findings.md` is missing.

Never start another broad review on the same contract and candidate lineage.
When blockers exist, the next step is Remediate.
