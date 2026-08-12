# Evaluation plan

Treat Converge as a workflow hypothesis and measure whether it reduces review
cycles without increasing invalid blocker findings or planning overhead.

Replay historical changes in three lanes and record:

- Blocker families found before Build
- Blocker families found in Review Round 1
- New original blocker families found during closure
- Invalid P1 rate
- Build/review cycles
- Human adjudications
- Agent time or token cost
- Artifact size
- Escaped defects found after merge

Compare the original workflow, Converge, and a minimal build-plus-review control.

## Dogfood evidence

Fixtures test whether an agent follows the protocol. They do not prove that the
protocol reduces review cycles without increasing escaped defects. For every
real replay or dogfood change, record one row outside the candidate repository
with at least:

- Date, host, model/context, lane, and change identifier
- Challenge performed, Round 1 blocker families, Fast-lane misjudgment signal,
  and invalid-P1 adjudications
- Closure classification counts, including original misses, fix-introduced
  issues, and blocking new-evidence dispositions
- Build/Verify iterations, broad reviews, closure reviews, targeted corrections,
  replans, and splits
- Approximate elapsed time, agent tokens when available, and artifact size
- Defects found after `CLOSED`, merge, or deployment, with the evidence boundary

Use the same adjudication rules and comparable tasks for the Converge and
minimal-control runs. Do not publish an efficacy conclusion from fixture pass
rates alone.

## Runnable fixtures

`fixtures/` contains seeded scenarios with known defect families and a grader:

- `fixtures/review-standard/` — measures whether the `review` skill is
  batch-complete and sweeps sibling paths. See its `INSTRUCTIONS.md`.
- `fixtures/close-delta/` — measures whether the `close` skill stays
  delta-only, classifies new issues, and fires the loop breaker on a
  distinct original blocker family instead of starting a third broad
  review. See its `INSTRUCTIONS.md`.
- `grade_review.py` — grades a produced findings or closure file and its state
  against a fixture's `expected.json`. Substring markers make artifact PASS
  necessary, not sufficient; alternative markers allow equivalent terminal
  decisions such as `REPLAN` or `SPLIT`. State assertions check the finite
  workflow outcome and review budgets.

The scenario files under `scenarios/` remain descriptive replay guides for
evaluating full workflow runs on real changes.
