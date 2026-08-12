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

For a Fast change that skipped Challenge, a supported P1 is also a
lane-misjudgment signal. Record the signal, but do not inflate severity or add a
review round because of it.

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

The `remediate` skill owns this step. Fix the complete finding batch by
root-cause family. Do not patch only the cited example. For each finding record
in the Remediation Report:

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

Use the Round 1 candidate and remediation range as the temporal boundary:

- `FIX_INTRODUCED` — the failure was not reachable at the Round 1 candidate and
  became reachable because of the remediation range.
- `ORIGINAL_MISS` — the failure was reachable and supportable from evidence
  reasonably available at the Round 1 candidate, and it violated the sealed
  brief or a non-waivable baseline guarantee, but Round 1 did not report it.
- `NEW_EVIDENCE` — the relevant behavior existed at Round 1, but evidence not
  reasonably available then now supports a materially different disposition.
  Record the Round 1 reachability and why the decisive evidence was genuinely
  unavailable; do not also label it `ORIGINAL_MISS`.
- `SCOPE_EXPANSION` — the concern requires behavior outside the sealed brief and
  baseline guarantees, or arises from remediation that materially expanded the
  mechanism.
- `OUT_OF_SCOPE_FOLLOW_UP` — the candidate did not introduce, expose, or
  materially worsen the concern.

Do not select a cheaper classification because its workflow outcome is more
convenient. Record the Round 1 reachability evidence for every new blocking
issue.

## Loop breaker

After closure:

- Prior findings closed, no new blocker → `CLOSED`
- Small fix-introduced defect → one targeted fix and one targeted confirmation
- Prior root-cause family incomplete → keep its Round 1 finding ID open, finish
  the family, then targeted confirmation
- New distinct original P1 family → `REPLAN` or `SPLIT`
- Blocking `NEW_EVIDENCE` for a distinct family → `REPLAN` or `SPLIT`; if it
  only proves a named Round 1 family incomplete and the correction remains
  small and inside the sealed mechanism, keep that ID open and use the one
  targeted confirmation; otherwise `REPLAN` or `SPLIT`
- Material scope expansion → `REPLAN` or `SPLIT`
- Pre-existing baseline weakness or unrelated hardening that the candidate did
  not introduce, expose, or materially worsen → follow-up, not a blocker

A candidate-caused violation of a non-waivable baseline guarantee never becomes
a follow-up merely because the brief omitted it. A non-blocking
`NEW_EVIDENCE` issue may be recorded as a follow-up, but blocking new evidence
does not qualify for a cheap targeted fix unless it belongs to an already-open
Round 1 family.

Do not begin a third broad review automatically.

The targeted path is finite. Close consumes its one closure budget and records
`TARGETED_FIX`. Remediate may change only the finding IDs kept open by Close and
then records `READY_FOR_TARGETED_CONFIRMATION`. Verify checks only those issues,
their named siblings, and invalidated obligations. It ends `CLOSED`, `REPLAN`,
`SPLIT`, or `BLOCKED`; it cannot return to another targeted fix. No broad or
closure budget is reset.
