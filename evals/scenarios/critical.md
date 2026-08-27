# Critical scenario — slip-hold PR #1847

## Purpose and claim boundary

Use [PR #1847](https://github.com/pebbleferry/slip-hold/pull/5360)
to evaluate whether Converge improves planning coverage, proof fidelity, and
finite-loop decisions for a lifecycle-heavy change. Do not copy its reservation rules
into generic workflow policy.

The historical record is a retrospective, not causal proof. It can show which
failure families a plan or review covers and where protocol-compliant artifacts
create false confidence. Only a paired, blinded Build replay can support a
first-candidate-prevention claim.

## Frozen runner input

Expose only this section and a contemporaneous source-request snapshot to the
agent being scored. Hide the historical record and scoring key below.

- Source tree: a content-only export of the pre-change code prepared and
  provenance-checked by the evaluator. It contains no Git metadata, refs,
  remotes, later objects, or repository identity.
- Required task input: the original issue or user-request snapshot as it existed
  before implementation. Do not substitute the current PR body; it contains
  later mechanism and validation details.
- Access boundary: disable network, source-history, PR-page, and issue-page
  access for the scored agent.
- Do not reveal repository or PR identity, commit hashes, later implementation,
  normalized retrospective summaries, review findings, or the answer key.

If the contemporaneous request snapshot is unavailable, the run is
`HINDSIGHT_LIMITED`. It may still score retrospective coverage, but it cannot be
called a blinded replay.

## Replay procedure

1. Verify the exact pre-change provenance outside the scored context, then
   export a content-only source tree with Git metadata and remotes removed.
2. Freeze host, model/context, tools, time or token budget, and request input.
3. Run matched conditions: released Converge v0.2.4, this candidate policy, and
   optionally a minimal build-plus-review control. Do not share artifacts or
   findings across conditions.
4. Capture the Direction Summary, lane/exception, Map, sealed mechanism,
   lifecycle matrix when triggered, proof obligations, both Critical Challenge
   outputs, split decision, first Build candidate when one is produced, Verify
   evidence, and review/closure decisions.
5. Reveal the answer key only after each condition's artifacts and candidate
   identity are frozen. Use semantic adjudication; do not grade substrings.
6. Record invalid blockers and cost as well as valid detections. A larger plan
   is not automatically better.

## Required proof-fidelity probe

Include at least one tempting proxy test in the input or candidate, such as:

- Setting a downstream “late” or “out of budget” flag without crossing the
  request deadline
- Calling a promotion/refresh helper directly without exercising the approval
  event that production relies on
- Asserting only that cancellation was requested while physical HTTP or a pool
  slot remains owned

The candidate policy passes this probe only when it labels proxy-only evidence
`PARTIAL` or `UNPROVEN` and requires a production-path or boundary-faithful
test. A controlled clock, fake endpoint, or test database is sufficient when it
preserves the real control path, ownership, transaction, and failure semantics.

## Hidden historical record and adjudication key

Do not expose this section to the replay agent.

- Repository: `pebbleferry/slip-hold`
- Pre-change base: `2cfee7b7435e1bd04a322b06a79ed529ef09b0e5`
- Opening implementation: `123f9da9024825520d075fcf20f1893fef6b6bb2`
- Normalized opening intent used only for retrospective adjudication: persist
  valid carrier slot offers once as short-lived, reusable unscheduled holds; reuse
  eligible rows before another carrier call; mark a hold scheduled only when
  selected.

The prior review transcript recorded nine review iterations on evolving
candidates. Eight led to another revision; the ninth was GREEN.

| Pass | Exact reviewed candidate | Recorded result | Root-cause families surfaced |
|---|---|---|---|
| 1 | `14135c6b3188a902b89b3131f0d7dbbaa1301e8c` | NOT GREEN | genuine late results discarded; timestamp/identity collision aliasing; winner bound to the wrong carrier/terminal; global lookup cap hid carrier slip roster |
| 2 | `f815d1b3ed6b085f6307358a6328ba713902ffea` | NOT GREEN | post-deadline payload could still compete; ordinary slow physical HTTP was cancelled; late raw offers remained unusable; content equality merged distinct offers |
| 3 | `5cba0f3f1809f872333295b12a5375cdafc3571c` | NOT GREEN | just-finished persistence blocked serving; logical permit ownership diverged from physical pool ownership; successful prefetch left rows hidden |
| 4 | `0e35622f38b9ae4c88d3878e1205d32906a263d5` | NOT GREEN | prefetch raced row creation; requested-to-approved promotion stranded rows; background threads and database cleanup were unbounded |
| 5 | `20eec6377c4c8f28b44d7fe43ff75b4f36eff59d` | NOT GREEN | approval test bypassed the production event; cleanup leaked permit/thread ownership; drain-thread start failure escaped into serving |
| 6 | `22f6db05617874664c6bf9434f766e9f2490a493` | NOT GREEN | bulk-created and partial slip-group approval paths did not promote hold rows |
| 7 | `964aec780d6961b7128940ef848cf2046aa0a9e2` | NOT GREEN | external pending/preapproved states did not promote rows after approval |
| 8 | `474f0fca56add99c9a6c83354ec5cce2bfafe3fc` | NOT GREEN | deterministic port-authority regression expectation was stale; no new production family was reported |
| 9 | `4ae5834d076131a97502986643aff84a28b41646` | GREEN | no supported blocker at that exact candidate |

Do not infer `ORIGINAL_PRESENT` or `FIX_INTRODUCED` from the pass number. For
each family, compare reachability at the opening candidate with the remediation
range that preceded discovery. Use `UNPROVEN` when the necessary historical
candidate or evidence is missing. The transcript supports discovery order; it
does not, by itself, prove the origin of every family.

The final merged head was
`39fc03103f578c28533849923eebfe93c5811496`, which is later than the recorded
GREEN candidate. This record does not prove independent review coverage of the
final merged delta. Keep the heads distinct.

Use these semantic family groups for adjudication; equivalent language earns
credit:

1. Election deadline versus permission to persist a late result
2. Logical cancellation versus physical HTTP/capacity ownership and release
3. Background persistence admission, setup failure, cleanup, and boundedness
4. Persistent identity namespace, collisions, carrier/terminal binding, and
   partitioned slip lookup
5. Approval/promotion lifecycle across ordinary save, bulk child creation,
   partial approval, and external approval states
6. Proof that crosses the real timeout, cancellation, transaction, or approval
   boundary instead of simulating downstream state

For each family and workflow phase, grade:

- `0` — absent or contradicted
- `1` — concern named, but no causal sequence, connected surfaces, or usable
  contract/proof amendment
- `2` — violated property, defeating sequence, connected surfaces, and a
  falsifiable plan, split, or proof obligation are all present

Score lane/split quality separately. The representative combination of hard
deadline, external HTTP, persistent identity, detached work, shared capacity,
and asynchronous promotion should select Critical. A Standard decision earns
credit only with a sealed exception that demonstrates local containment,
independent recovery, no correctness-critical ownership transfer, and a
falsifier.

## Result record

Record at least:

- Provenance, blinding status, exact base/candidate, host, model/context, tools,
  and budget
- Lane rationale or exception and split decision
- Family scores captured before Build, in Challenge, and first found in Review
- Fix-introduced defects and mechanism-drift decisions
- Direct/faithful/proxy/unavailable evidence counts and the fidelity probe result
- Broad, closure, targeted, replan, and split counts
- Invalid blockers and adjudication rationale
- First-candidate defects, escaped defects, elapsed time, tokens when available,
  and artifact size
- Hindsight, source-snapshot, candidate-head, and environment limitations

Interpret finite-loop compliance, first-candidate coverage, proof fidelity,
accuracy, and cost separately. Do not turn one good dimension into a general
efficacy claim.
