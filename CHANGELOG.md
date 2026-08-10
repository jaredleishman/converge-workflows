# Changelog

All notable changes to Converge are documented here.

## [0.2.0] - 2026-08-10

### Added

- `remediate` skill that owns fixing the Round 1 finding batch by root-cause
  family and recording the Remediation Report before re-verification.
- Bundled state gate (`plugins/converge/scripts/state_gate.py`, stdlib only)
  that skills invoke to check stage preconditions, consume the review budget,
  and record state transitions; budget fields are no longer edited by hand.
- Runnable review eval: `evals/fixtures/review-standard/` with seeded defect
  families and `evals/grade_review.py` to grade batch- and family-completeness.
- Explicit contract sealing definition in `workflow.md`: which brief sections
  seal at `PLANNED` and how amendments must be routed back through Plan.
- `REMEDIATING` workflow state; Verify ends `READY_FOR_CLOSURE` when it
  re-verifies remediation.
- State gate unit tests.

### Changed

- Skill files document path resolution for their `../_shared/` reads
  (`${CLAUDE_PLUGIN_ROOT}` in Claude Code).
- Unified "Plan Attack" terminology to "Challenge" across lanes, scope policy,
  and eval scenarios.
- `review` and `close` consume budget through the state gate instead of
  editing `state.yaml` directly.

## [0.1.0] - 2026-08-09

### Added

- Fast, Standard, and Critical workflow lanes.
- One evolving Change Brief as the main source of truth.
- Code-aware Scope, Map, Challenge, and split decision before implementation.
- Build and Verify skills with exact-candidate evidence.
- One broad, batch-complete review and one delta-only closure review.
- A loop breaker that returns `REPLAN` or `SPLIT` instead of beginning a third
  broad review when distinct original blocker families continue to appear.
- Native marketplace manifests for Codex, Grok Build, and Claude Code.
- Standard-library validation and tests.
