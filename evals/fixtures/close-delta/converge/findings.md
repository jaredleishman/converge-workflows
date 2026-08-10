# Review Findings

## Candidate

- Repository: eval fixture `close-delta`
- Base: seeded
- Head or worktree fingerprint: seeded
- Review round: `BROAD-1`

## Contract reviewed

- Brief path: `.converge/brief.md`
- Lane: `standard`
- Review limitations: none

## Blocking findings

### REV-1 — [P1] issue_refund can refund more than the remaining total

- Root-cause family: missing remaining-total clamp
- Violated invariant or criterion: `INV-1` / `AC-1`
- Concrete execution sequence: `issue_refund(order, amount)` with
  `amount > order["total"]` drives the total negative
- Material impact: money — the refund exceeds what was charged
- Candidate relationship: introduced by the candidate
- Sibling paths inspected: `src/refunds.py`
- Regression or deterministic proof sketch: total 50, refund 80 → total -30
- Required behavioral correction: clamp the amount to the remaining total

### REV-2 — [P1] issue_refund can refund the same order twice

- Root-cause family: missing double-refund guard
- Violated invariant or criterion: `INV-2` / `AC-2`
- Concrete execution sequence: two `issue_refund` calls on the same order
  both apply
- Material impact: money — the order is refunded twice
- Candidate relationship: introduced by the candidate
- Sibling paths inspected: `src/refunds.py`
- Regression or deterministic proof sketch: total 50, refund 50 twice →
  total -50
- Required behavioral correction: guard on the order's refunded state

## Non-blocking follow-ups

None.

## Baseline issues

None recorded.

## Proposed contract amendments

None.

## Review disposition

- Status: `FINDINGS`
- Broad review budget used: `1/1`

## Remediation Report

### REV-1 — missing remaining-total clamp

- Violated invariant: `INV-1`
- Affected sibling paths: `src/refunds.py` (`issue_refund`)
- Shared root cause: refund amount applied without clamping
- Common fix seam: clamp at the top of `issue_refund`
- Regressions: none recorded
- Paths intentionally unchanged: `issue_refund_admin`,
  `format_refund_receipt`

### REV-2 — missing double-refund guard

- Violated invariant: `INV-2`
- Affected sibling paths: `src/refunds.py` (`issue_refund`)
- Shared root cause: no refunded-state guard
- Common fix seam: guard on `order["refunded"]`
- Regressions: none recorded
- Paths intentionally unchanged: `issue_refund_admin`,
  `format_refund_receipt`
