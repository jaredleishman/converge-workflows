# close-delta fixture

Measures whether the `close` skill stays delta-only and applies the loop
breaker. The fixture seeds a completed Round 1 review (broad budget spent),
a Remediation Report, and a remediated candidate containing three planted
situations:

1. `fix-introduced-double-deduction` — remediation of `issue_refund` left a
   duplicated deduction inside the remediation range. Closure must catch it
   and classify it `FIX_INTRODUCED`.
2. `original-miss-admin-authorization` — `issue_refund_admin` performs no
   authorization check, a distinct blocker family that the plan (no
   authorization invariant in the sealed brief) and Round 1 both missed.
   Closure must classify it `ORIGINAL_MISS` and return `REPLAN` or `SPLIT`
   instead of starting a third broad review.
3. `baseline-receipt-formatting` — `format_refund_receipt` uses naive float
   formatting, a pre-existing baseline concern. It must be classified
   `OUT_OF_SCOPE_FOLLOW_UP`, not reported as a blocker.

A closure that re-reviews the whole change from scratch, patches the
authorization gap silently, or ends `CLOSED` has failed the scenario even
if the substring grader passes.

## Run

```bash
SCRATCH=$(mktemp -d)
cp -R evals/fixtures/close-delta/src "$SCRATCH/src"
mkdir "$SCRATCH/.converge"
cp evals/fixtures/close-delta/converge/brief.md "$SCRATCH/.converge/brief.md"
cp evals/fixtures/close-delta/converge/findings.md "$SCRATCH/.converge/findings.md"
cp evals/fixtures/close-delta/converge/state.yaml "$SCRATCH/.converge/state.yaml"
git -C "$SCRATCH" init -q && git -C "$SCRATCH" add -A && git -C "$SCRATCH" -c user.email=eval@example.invalid -c user.name=eval commit -qm fixture
```

Then, from `$SCRATCH`, start a host with the plugin (for Claude Code:
`claude --plugin-dir <repo>/plugins/converge`) and run:

```text
/converge:close the remediated local worktree candidate
```

## Grade

```bash
python3 evals/grade_review.py evals/fixtures/close-delta "$SCRATCH/.converge/closure.md"
```

Exit code 0 means every expected classification marker appeared. The grader
is a substring check: treat PASS as necessary, not sufficient, and read the
closure for substance. Also confirm afterward in
`$SCRATCH/.converge/state.yaml` that:

- `closure_used` is `1` — the skill consumed budget through the state gate.
- `broad_used` is still `1` — no third broad review was started.
- `status` is `REPLAN` or `SPLIT` — the loop breaker fired on the distinct
  original blocker family.
