# Review convergence policy

Converge permits one broad review and, when needed, one delta closure review.

## Round 1: broad review

This is the only unrestricted post-implementation review.

The reviewer must:

1. Resolve the exact candidate and the sealed Change Brief.
2. Review contract compliance, changed behavior, and connected sibling paths.
3. Continue after finding the first blocker.
4. Generalize each finding to its violated invariant or behavioral contract.
5. Inspect all sibling entry points and consumers governed by that same root
   cause before returning the finding.
6. Return one deduplicated, batch-complete finding set.
7. Separate blockers, non-blocking follow-ups, baseline issues, and proposed
   contract amendments.
8. Remain read-only unless the user separately authorizes remediation.

For Critical work, parallel reviewers may inspect the same exact candidate.
Synthesize all results before any fix is made. The parallel set consumes one
broad-review budget.

## Blocker standard

A P0/P1 blocker requires:

- A concrete reachable execution sequence
- Material user, money, data, authorization, operational, or external-effect
  impact
- A violated invariant, acceptance criterion, or regression boundary
- Evidence that the candidate introduces, exposes, or materially worsens it
- Relevance to the candidate's actual deployment envelope
- A regression or deterministic proof sketch

A plausible concern without this evidence is a question or follow-up, not a
blocking P1.

## Remediation

Fix the complete finding batch by root-cause family. Do not patch only the cited
example. For each finding record:

- Violated invariant
- Affected sibling paths
- Shared root cause
- Common fix seam
- Regressions
- Paths intentionally unchanged

Material implementation changes may invalidate additional acceptance criteria
or plan assumptions; rerun Verify before closure.

## Round 2: delta closure

Closure validates only:

- The prior finding batch
- The remediation range
- The invariant families named by those findings
- Sibling paths named in the remediation report
- New paths introduced or invalidated by the fix

It does not restart an unconstrained full-PR review.

Classify every new issue as:

- `FIX_INTRODUCED`
- `ORIGINAL_MISS`
- `NEW_EVIDENCE`
- `SCOPE_EXPANSION`
- `OUT_OF_SCOPE_FOLLOW_UP`

## Loop breaker

After closure:

- Prior findings closed, no new blocker → `CLOSED`
- Small fix-introduced defect → targeted fix and targeted confirmation
- Same root-cause family incomplete → finish the family, then targeted confirmation
- New distinct original P1 family → `REPLAN` or `SPLIT`
- Material scope expansion → `REPLAN` or `SPLIT`
- Baseline or unrelated hardening → follow-up, not a blocker

Do not begin a third broad review automatically.
