# Converge workflow

Converge moves path discovery and failure analysis before implementation, then
bounds post-implementation review to one broad review and one closure review.

## The flow

```text
Plan: Interview → Direction approval → Map → Challenge → Split decision
Build → Verify
Review: one broad, batch-complete review
Remediate: fix the whole batch by root-cause family → re-verify
Close: one delta-only closure review, only when Review found blockers
Targeted correction: one fix + one confirmation, only for a small
  remediation-caused defect or an incomplete prior finding family
Outcome: CLOSED, REPLAN, SPLIT, or BLOCKED
```

Plan does not map, challenge, or write artifacts until the user explicitly
approves a Direction Summary in chat.

## Central rule

One broad implementation review. One closure review after substantive
remediation. A third broad review is never the default next step: when closure
finds a distinct original blocker family that Plan and Review both missed,
return `REPLAN` or `SPLIT`.

The bundled state gate enforces transitions and budget mechanically (see
`artifact-protocol.md`). Budget fields in `state.yaml` are never edited by
hand. Converge is skill-only and does not intercept work outside the protocol.

Pre-review iteration is ordinary: Build may resume after interruption, and
Verify returns a defective candidate to Build without spending review budget.
A missing external prerequisite is `BLOCKED`, not a candidate defect.

## What "done" means

Two checks, no total score:

1. **Contract.** Every acceptance criterion, invariant, and applicable baseline
   guarantee has passing evidence.
2. **Future change.** The brief names one likely later edit. That edit must
   have one obvious seam in the candidate. If it would spray across the tree,
   the cut is wrong: `REPLAN`, even when the contract passes.

Never write "clean", "elegant", "extensible", "maintainable", or "idiomatic"
into an invariant or acceptance criterion. Maintainability is the Future change
sentence. Elegance is Build's deletion pass.

## Sealing

The contract seals when Plan ends `PLANNED`. Sealed sections of `brief.md`:
lane rationale and any Standard exception, Outcome, Non-goals, Dangerous false
successes, Baseline guarantees, Proposed change, Planned mechanism baseline,
Invariants, Acceptance criteria, Future change, any triggered lifecycle matrix
and Critical proof obligations, the plan-time causal grounding trace, Challenge
contract amendments, and the Split decision.

Later stages append to the Map, Implementation crosswalk, Verification
evidence, findings, and closure. They do not rewrite sealed sections. A new Map
fact never makes an unplanned mechanism retroactively planned. Any change to a
sealed section is a contract amendment: label it, route it back through Plan's
Challenge step, and start a new contract with a new review cycle.

## One source of truth

`.converge/brief.md` is the evolving behavioral record. Plan writes it, Build
adds the crosswalk, Verify adds evidence. Findings and closure are separate
only because an independent review phase produces them.

```text
.converge/
├── brief.md
├── state.yaml
├── findings.md   # every broad Review, including a clean Review
├── closure.md    # only when Close is needed
└── archive/      # previous CLOSED, REPLAN, or SPLIT contracts
```

One project root or worktree holds one active contract. Use a separate worktree
for a parallel or stacked change. After `CLOSED`, `REPLAN`, or `SPLIT`, run the
gate's `init` command; it archives the finished contract and writes a fresh
`PLANNING` pair. Never overwrite `state.yaml` by hand.

Do not commit `.converge/` unless the user wants durable artifacts. Prefer
`.git/info/exclude` over editing a committed `.gitignore`.

## Delegated stage ownership

Delegation is optional. The invoking stage owner still owns the result:

1. Dispatch a bounded scope, the relevant seams, success criteria, and the
   candidate identity that exists at that stage: the planning head or
   fingerprint for Challenge; the base, dispatch-time fingerprint, and owned
   paths for Build; the exact captured candidate for Review.
2. Inspect the cited source, diff, commands, and evidence directly. Record
   unsupported claims, stale observations, and identity mismatches instead of
   forwarding the delegate's conclusion.
3. The stage owner writes the synthesis and disposition in the stage's existing
   artifact (brief for Challenge and Build, findings for Review). A missing,
   failed, or uninspectable delegate result is a stated limitation, not
   evidence. Do not create a new artifact merely because work was delegated.

## Authorization

Converge never authorizes commits, pushes, pull requests, deployments,
production access, external writes, or destructive commands. Those need the
user's separate request and the repository's own rules.
