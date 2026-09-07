# Review policy

Converge permits one broad review and, when needed, one delta closure review.

## Round 1: broad review

The only unrestricted post-implementation review. The reviewer:

1. Resolves the exact candidate and the sealed brief.
2. Reviews contract compliance, changed behavior, and connected sibling paths.
3. Continues after the first blocker and returns one deduplicated,
   batch-complete set.
4. Generalizes each finding to its violated invariant or contract row and
   inspects every sibling entry point and consumer governed by that root cause
   before reporting it.
5. Separates blockers, non-blocking follow-ups, baseline issues, and proposed
   contract amendments.
6. Stays read-only.

### Findings cite rows

Every finding carries `Cites:` naming an AC, INV, BG, the Future change, or a
mechanism axis. A finding that cites nothing is not a blocker; it may be a
follow-up or a proposed amendment. Style or elegance-only observations are
follow-ups and spend no review effort. "The Future change has no home" is a
load-bearing miss: it goes to the remediate family or `REPLAN`, never to a
style note.

### Blocker standard

A P0/P1 blocker needs all of: a concrete reachable execution sequence;
material user, money, data, authorization, operational, or external-effect
impact; a violated invariant, acceptance criterion, or regression boundary;
evidence the candidate introduces, exposes, or materially worsens it;
relevance to the actual deployment envelope; a regression or deterministic
proof sketch. Without those it is a question or follow-up.

### Reviewer choice

Prefer a different model family from the one that built the candidate. If
only one exists, record `same-family-review` in the findings and continue; a
missing second family never blocks Review.

### Critical same-candidate lenses

For lifecycle-heavy Critical work, default to these complementary lenses:

1. Timing, cancellation, late completion, and physical-resource ownership
2. Persistent identity, collision/deduplication, transactions, and
   external-effect integrity
3. State lifecycle, recovery, promotion, and test realism or proof fidelity

A lens is an emphasis, not a silo. Every reviewer reads the sealed contract,
inspects the complete candidate, and does a full-candidate sweep for failures
outside the lens. Tailor the set with a recorded rationale when the risk is
authorization, cryptography, migration, or another shape. Keep reports hidden
from one another until they finish; each records reviewer identity,
repository, base/head or fingerprint, acquisition method, primary lens, sweep,
and limitations. If candidate identity differs, do not synthesize; resolve it
or record `BLOCKED`. The root workflow deduplicates root-cause families and
records one disposition. The parallel set consumes one broad-review budget.

## Remediation

The `remediate` skill fixes the complete batch by root-cause family at the
common seam, sweeping every named sibling. The Remediation Report records per
finding: the cited row, affected sibling paths, shared root cause, common fix
seam, regressions added, and paths intentionally unchanged. Rerun Verify
before closure.

## Round 2: delta closure

Closure validates only the prior finding batch, the remediation range, the
invariant families those findings named, sibling paths in the remediation
report, and paths the fix introduced or invalidated. It does not restart a full
review.

Classify every new issue against the Round 1 candidate and remediation range:

- `FIX_INTRODUCED` — not reachable at the Round 1 candidate; reachable because
  of the remediation range.
- `ORIGINAL_MISS` — reachable and supportable from evidence reasonably
  available at Round 1, violating the sealed brief or a baseline guarantee, but
  not reported.
- `NEW_EVIDENCE` — existed at Round 1, but decisive evidence was genuinely
  unavailable then. Record why; do not also label it `ORIGINAL_MISS`.
- `SCOPE_EXPANSION` — needs behavior outside the sealed brief and baseline
  guarantees, or arises from remediation that expanded the mechanism.
- `OUT_OF_SCOPE_FOLLOW_UP` — the candidate did not introduce, expose, or
  materially worsen it.

Do not pick a cheaper classification because its outcome is more convenient.
Record Round 1 reachability evidence for every new blocking issue.

## Loop breaker

After closure:

- Prior findings closed, no new blocker → `CLOSED`
- Small fix-introduced defect → one targeted fix and one targeted confirmation
- Prior family incomplete → keep its Round 1 ID open, finish it, then targeted
  confirmation
- New distinct original P1 family → `REPLAN` or `SPLIT`
- Blocking `NEW_EVIDENCE` → `REPLAN` or `SPLIT`, unless it only proves a named
  Round 1 family incomplete and the correction stays small and inside the
  sealed mechanism; then keep that ID open for the one targeted confirmation
- Material scope expansion → `REPLAN` or `SPLIT`
- Pre-existing weakness the candidate did not worsen → follow-up

A candidate-caused violation of a non-waivable baseline guarantee never becomes
a follow-up because the brief omitted it.
Do not begin a third broad review automatically.

The targeted path is finite. Close consumes its one closure budget and records
`TARGETED_FIX`. Remediate may change only the IDs Close kept open and records
`READY_FOR_TARGETED_CONFIRMATION`. Verify checks only those issues, their named
siblings, and invalidated obligations, then ends `CLOSED`, `REPLAN`, `SPLIT`,
or `BLOCKED`. It cannot return to another fix. No budget resets.
