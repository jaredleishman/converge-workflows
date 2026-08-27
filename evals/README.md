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

## Keep the claims separate

Score these dimensions independently:

- **Lane and split quality** — whether impact, coupled boundaries, and proof
  independence justify the chosen route.
- **Pre-Build prevention** — root-cause families captured in the sealed plan or
  Challenge before implementation starts.
- **Proof fidelity** — whether evidence crosses the claimed production boundary
  rather than calling a helper or injecting downstream state.
- **Round 1 detection** — supported blocker families first found by the broad
  review.
- **Finite-loop compliance** — broad, closure, targeted, replan, and split
  counts and whether the loop breaker fires at the correct time.
- **Accuracy and cost** — invalid blockers, escaped defects, elapsed time,
  tokens when available, and artifact size.

A protocol-compliant artifact is not evidence of first-candidate prevention.
Planning coverage is not prevention unless a blinded Build run also produces a
candidate and the hidden defect families are then adjudicated. Report the
narrowest claim the run supports.

## Replay controls

For paired replays, freeze the request, repository base, host, model/context,
tool access, and budget before either condition runs. Keep the historical
outcome, later commits, final PR body, and answer key hidden from the agent.
Give the scored agent a content-only export of the pre-change source tree:
remove Git metadata and remotes, and disable network or PR-page access that
could recover later objects. Keep the exact repository and commit provenance in
the evaluator's hidden record.
Compare the released policy with the candidate policy on that same input; add a
minimal build-plus-review control when cost permits.

Grade causal properties and execution sequences, not terminology. A finding
earns credit when it identifies the violated property, a defeating sequence,
the connected surfaces, and the needed contract or proof amendment. Keyword or
substring matches are never efficacy evidence. Record hindsight contamination,
missing source snapshots, unavailable tools, and candidate-head gaps as
limitations rather than silently filling them in.

## Matched policy behavior probes

Use a matched behavior probe before adopting workflow policy based mainly on a
plausible instruction. Freeze and hash the request, content-only source,
released control policy, candidate treatment overlay, hidden semantic rubric,
host/model/context, tool access, and budget before either condition runs. Use
fresh isolated contexts. The treatment condition differs only by the candidate
policy overlay; do not reveal the rubric or expected behavior to either agent.

Capture chronology, not only the final answer or artifact. Preserve delegate
dispatch and follow-up, edit and check order, intermediate candidate
fingerprints or source snapshots, command logs, and the final candidate. A
finished table can be backfilled and therefore does not prove that an owner
inspected delegated evidence or that a local check passed before the next Build
unit began. Treat missing timestamps or intermediate state as a limitation.

Adjudicate semantically against the hidden rubric. Useful dimensions include:

- Completion of every materially distinct causal path
- Structurally different alternatives when the mapped trigger applies
- One explicit organizing model for the selected mechanism
- Direct owner inspection, discrepancy recording, and delegated-work
  reconciliation
- Prospective Build units and successful local checks before advancement
- Fast and ordinary Standard lane cost when conditional branches do not apply

Static contract checks remain `PROXY`. An isolated matched run that preserves
the intended control path may provide `BOUNDARY_FAITHFUL` protocol evidence,
but one pair supports only the observed difference on that task and model
family. It does not establish lower defect rates, production reliability, or
general superiority. Repeat across representative changes before making an
efficacy claim.

## Dogfood evidence

Fixtures test whether an agent follows the protocol. They do not prove that the
protocol reduces review cycles without increasing escaped defects. For every
real replay or dogfood change, record one row outside the candidate repository
with at least:

- Date, host, model/context, lane, and change identifier
- Lane rationale or Standard exception, split decision, Challenge findings
  before Build, Round 1 blocker families, Fast-lane misjudgment signal, and
  invalid-P1 adjudications
- Triggered lifecycle-matrix paths, proof-fidelity classifications, and
  planned-mechanism drift decisions
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

The repository validator and unit tests check that the packaged policy contract
is present and internally consistent. Under Converge's own proof taxonomy,
those static checks are `PROXY` evidence for agent behavior; they cannot by
themselves prove lane selection, evidence disposition, drift routing, or review
quality.

- `fixtures/plan-standard/` — measures whether `plan` seals a Standard brief
  without Critical ceremony and records `PLANNED` with unused review budgets.
  See its `INSTRUCTIONS.md`.
- `fixtures/review-standard/` — measures whether the `review` skill is
  batch-complete and sweeps sibling paths. See its `INSTRUCTIONS.md`.
- `fixtures/close-delta/` — measures whether the `close` skill stays
  delta-only, classifies new issues, and fires the loop breaker on a
  distinct original blocker family instead of starting a third broad
  review. See its `INSTRUCTIONS.md`.
- `grade_plan.py` — grades a sealed brief and state for Standard-lane
  protocol shape. Heading and forbidden-ceremony checks are necessary, not
  sufficient.
- `grade_review.py` — grades a produced findings or closure file and its state
  against a fixture's `expected.json`. Substring markers make artifact PASS
  necessary, not sufficient; alternative markers allow equivalent terminal
  decisions such as `REPLAN` or `SPLIT`. State assertions check the finite
  workflow outcome and review budgets. Required code markers must not already
  appear in the seeded brief.

The scenario files under `scenarios/` remain descriptive replay guides for
evaluating full workflow runs on real changes. Their hidden answer keys require
semantic human or independent-model adjudication; do not extend the substring
fixture grader and claim that it measures efficacy.
