# plan-standard fixture

Measures whether `/converge:plan` seals a Standard brief without Critical
ceremony and records `PLANNED` with unused review budgets.

Use a small, well-understood change that is Standard, not Fast or Critical.
The grader checks headings, a split decision, and the absence of the Critical
lifecycle matrix. It does not score whether Map found the real missing paths.

## Run

```bash
SCRATCH=$(mktemp -d)
git -C "$SCRATCH" init -q
# copy or create a tiny repository the agent can map
```

From `$SCRATCH`, start a host with the plugin and run:

```text
/converge:plan add a clamp so a discount rate cannot exceed MAX_DISCOUNT_RATE
```

Approve the Direction Summary. Do not implement.

## Grade

```bash
python3 evals/grade_plan.py evals/fixtures/plan-standard "$SCRATCH/.converge/brief.md" --state "$SCRATCH/.converge/state.yaml"
```

Exit code 0 means the brief looks like a Standard contract and state is
`PLANNED` with unused budgets. Treat PASS as a protocol check, not efficacy.
