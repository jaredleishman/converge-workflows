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

## Runnable fixtures

`fixtures/` contains seeded scenarios with known defect families and a grader:

- `fixtures/review-standard/` — measures whether the `review` skill is
  batch-complete and sweeps sibling paths. See its `INSTRUCTIONS.md`.
- `grade_review.py` — grades a produced `findings.md` against a fixture's
  `expected.json`. Substring markers make PASS necessary, not sufficient.

The scenario files under `scenarios/` remain descriptive replay guides for
evaluating full workflow runs on real changes.
