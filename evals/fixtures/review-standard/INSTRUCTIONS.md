# review-standard fixture

Measures whether the `review` skill produces one batch-complete,
family-complete finding set. The fixture contains two known blocker families:

1. `discount-clamp-siblings` — the clamp required by `INV-1` exists only in
   `apply_discount_api`; `apply_discount_batch` and `apply_discount_admin`
   are unclamped siblings of the same root cause.
2. `negative-total` — `compute_total` violates `INV-2` for negative
   quantities.

A passing review reports both families in one batch and names both unclamped
sibling entry points. A review that reports only the first unclamped function
it finds fails the sibling-sweep requirement.

## Run

```bash
SCRATCH=$(mktemp -d)
cp -R evals/fixtures/review-standard/src "$SCRATCH/src"
mkdir "$SCRATCH/.converge"
cp evals/fixtures/review-standard/converge/brief.md "$SCRATCH/.converge/brief.md"
cp evals/fixtures/review-standard/converge/state.yaml "$SCRATCH/.converge/state.yaml"
git -C "$SCRATCH" init -q && git -C "$SCRATCH" add -A && git -C "$SCRATCH" -c user.email=eval@example.invalid -c user.name=eval commit -qm fixture
```

From the scratch repository, capture the exact local candidate and finish the
seeded Verify transition with the plugin under test:

```text
python3 <converge-repo>/plugins/converge/scripts/state_gate.py candidate capture-worktree
python3 <converge-repo>/plugins/converge/scripts/state_gate.py set-status INTERNALLY_VERIFIED --stage verify
```

Then, from `$SCRATCH`, start a host with the plugin (for Claude Code:
`claude --plugin-dir <repo>/plugins/converge`) and run:

```text
/converge:review the local worktree candidate
```

## Grade

```bash
python3 evals/grade_review.py evals/fixtures/review-standard "$SCRATCH/.converge/findings.md" --state "$SCRATCH/.converge/state.yaml"
```

Exit code 0 means every expected family and sibling marker appeared and the
state records `REVIEW_FINDINGS`, both finding IDs, and broad budget `1/1`. The
grader is a substring check: treat PASS as necessary, not sufficient, and read
the findings for substance.
