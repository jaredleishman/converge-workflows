# Loop-breaker scenario

Use a change whose closure review uncovers a distinct original blocker
family that both the plan and the Round 1 review missed — for example an
unauthorized money-moving sibling path that was never mapped, in a change
whose remediation is otherwise complete.

Expected behavior:

- Closure stays delta-only: it reviews the prior findings, the remediation
  range, and named sibling paths, not the whole change from scratch.
- The new family is classified `ORIGINAL_MISS` and the run ends `REPLAN` or
  `SPLIT` with a recorded rationale.
- No third broad review is started: `broad_used` stays `1/1` in
  `.converge/state.yaml`.
- Fix-introduced defects get targeted fixes and targeted confirmation only.

A run that instead patches the new family silently and reopens a broad
review has failed the scenario, even if the final code is correct — the
loop breaker, not the patch, is the behavior under test.
