# Changelog

All notable changes to Converge are documented here.

## Unreleased

### Added

- `state_gate.py init` archives a `CLOSED`, `REPLAN`, or `SPLIT` contract under
  `.converge/archive/` and writes a fresh `PLANNING` pair. Plan calls it
  instead of overwriting `state.yaml` by hand.
- Review and Close outcomes require `findings.md` or `closure.md` to exist
  before the gate records them. `PLANNED` requires `brief.md`.
- A Critical brief addendum template and a `candidate-checks.md` file so
  Fast and Standard Plan do not ingest Critical ceremony or candidate-time
  proof rules.
- `evals/fixtures/plan-standard/` and `evals/grade_plan.py` for Standard Plan
  protocol shape.
- Standard and Critical causal-path completion, a named organizing model, and a
  conditional structural-alternatives branch that stays off for Fast and
  established routine mechanisms.
- Optional delegated-stage ownership and prospective Build proof-unit records
  in the existing brief and findings artifacts.
- Matched policy behavior-probe guidance that freezes inputs, captures
  chronology and intermediate candidates, and bounds claims from a single run.
- A compound-boundary Critical screen with a falsifiable Standard exception,
  plus a conditional lifecycle/ownership matrix and Critical proof obligations
  in `templates/brief-critical.md`.
- A provenance-aware PR #1847 replay and retrospective that separates planning
  coverage, proof fidelity, finite-loop compliance, accuracy, and cost.

### Changed

- Fast skips Challenge in the Plan skill. Standard remains one pass. Critical
  remains two.
- Plan does not implement. Continued execution hands off to Build.
- Plan Phase 1 reads only workflow and lanes. Build, Verify, and Remediate
  read `candidate-checks.md` instead of the full scope policy.
- The Fast/Standard brief template no longer contains the Critical lifecycle
  matrix. Disposition and budget live only in `state.yaml`.
- Dropped unused `request.*` and `decision.replan_required` /
  `decision.split_required` fields.
- Review-standard and close-delta seeded briefs no longer name the defective
  functions the grader requires, so copying the brief cannot substring-pass.
- Plan now selects or synthesizes its mechanism after Map and Challenge, and
  Build records successful local checks before advancing between coherent
  dependency slices while leaving full-candidate proof to Verify.
- Plan now seals the planned mechanism baseline, and Build, Remediate, and
  Verify explicitly route material ownership or failure-model drift to REPLAN
  or SPLIT.
- Critical verification now distinguishes direct or boundary-faithful evidence
  from proxies, and lifecycle-heavy Critical review uses auditable,
  complementary same-candidate lenses inside the existing broad-review budget.

## [0.2.4] - 2026-08-11

### Added

- Legal state transitions, resumable blocked work, interrupted Build support,
  ordinary Verify-to-Build correction, and a finite targeted closure-fix path.
- Local Git worktree candidate capture and drift checking, plus caller-resolved
  commit and pull-request candidate recording.
- Non-waivable baseline regression guarantees and temporal evidence rules for
  closure classifications.

### Changed

- Review and Close outcomes now consume their budget in the same state update;
  the standalone budget-consumption command is removed.
- State lists support JSON-style non-empty inline values and finding IDs are
  used as workflow preconditions.
- Candidate identity is write-once within each Verify attempt, and Closure now
  gives blocking new evidence an explicit loop-breaker outcome.
- Fast-lane guidance is more explicit, one active contract per project root is
  documented, and evaluation guidance separates protocol checks from efficacy
  evidence.

## [0.2.3] - 2026-08-10

### Changed

- Plan now runs in two phases. Phase 1 is a conversational interview: short
  rounds of code-grounded questions, ending in a Direction Summary the user
  must explicitly approve. Phase 2 (mapping, Challenge, brief and state
  artifacts) does not start until that approval, and returns to Phase 1 when
  mapping contradicts the approved direction.
- `workflow.md` and the README flow diagrams show the interview and
  direction-approval gate inside Plan.

## [0.2.2] - 2026-08-10

### Added

- Kimi Code packaging: `plugins/converge/.kimi-plugin/plugin.json` manifest
  and `.kimi-plugin/marketplace.json`, installable via `/plugins install` or
  `/plugins marketplace`.

## [0.2.1] - 2026-08-10

### Added

- Runnable closure eval: `evals/fixtures/close-delta/` seeds a remediated
  candidate with a fix-introduced defect, a distinct original blocker family,
  and a baseline concern, graded for delta-only scope, issue classification,
  and loop-breaker behavior (`REPLAN`/`SPLIT`, no third broad review).
- `evals/scenarios/loop-breaker.md` replay guide for closure runs that are
  tempted to reopen a broad review.
- State gate parser tests for malformed, orphaned, and over-nested state
  file lines.

### Changed

- The state gate now rejects state file lines that do not fit the
  constrained schema instead of silently ignoring them, so a hand-edited or
  corrupted `state.yaml` fails loudly.

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
