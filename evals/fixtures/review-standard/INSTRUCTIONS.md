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

Then, from `$SCRATCH`, start a host with the plugin (for Claude Code:
`claude --plugin-dir <repo>/plugins/converge`) and run:

```text
/converge:review the local worktree candidate
```

## Grade

```bash
python3 evals/grade_review.py evals/fixtures/review-standard "$SCRATCH/.converge/findings.md"
```

Exit code 0 means every expected family and sibling marker appeared. The
grader is a substring check: treat PASS as necessary, not sufficient, and read
the findings for substance. Also confirm afterward that `broad_used` is `1` in
`$SCRATCH/.converge/state.yaml` — the skill must consume the budget through
the state gate.
