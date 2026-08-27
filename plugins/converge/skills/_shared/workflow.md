# Converge workflow

Converge exists to make software review converge predictably by moving missing
path discovery and failure analysis before implementation.

## The flow

```text
Plan: Interview → Direction approval → Map → Challenge → Split decision
Build
Verify
Review: one broad, batch-complete review
Remediate: fix the complete finding batch by root-cause family, then re-verify
Close: one delta-only closure review, only when Review found blockers
Targeted correction, only for a small remediation-caused defect or an
  incomplete prior finding family: Remediate → targeted Verify confirmation
Outcome: CLOSED, REPLAN, SPLIT, or BLOCKED
```

Plan is gated on the user: it opens with an interview and does not map,
challenge, or write artifacts until the user explicitly approves a Direction
Summary in chat.

## Central rule

One broad implementation review is allowed. One closure review is allowed after
substantive remediation. A third broad review is not the default next step.

When closure finds a distinct original blocker family that the first review and
plan both missed, stop serial patching. Return `REPLAN` or `SPLIT` unless the
user explicitly chooses a new contract and review cycle.

Inside an invoked Converge workflow, the bundled state gate mechanically checks
legal transitions and couples Review and Close outcomes to their budget use
(see the artifact protocol). Converge remains skill-only: it does not intercept
freehand agent actions outside the protocol. Budget fields in `state.yaml` are
never edited by hand.

Ordinary pre-review iteration is allowed. Build may resume after interruption.
When Verify finds a candidate defect inside the sealed contract, it returns the
candidate to Build without spending review budget. Missing external evidence or
another unresolved prerequisite is `BLOCKED`, not a candidate defect.

## Sealing

The contract seals when Plan ends `PLANNED`. The sealed sections of
`brief.md` are the lane rationale and any Standard exception, Outcome,
Non-goals, Dangerous false successes, Baseline guarantees, Proposed change,
Planned mechanism baseline, Invariants, Acceptance criteria, any triggered
lifecycle/ownership matrix and Critical proof obligations, the Challenge
contract amendments, and the Split decision.

Build, Verify, Remediate, and reviewers append to the Map, Implementation
Crosswalk, Verification Evidence, findings, and closure sections; they do not
edit sealed sections. The Map may gain newly observed facts, but those facts do
not make an unplanned mechanism retroactively approved. Any change to a sealed
section is a contract amendment: it must be labeled as such, routed back
through Plan's Challenge step, and it starts a new contract with a new review
cycle rather than silently reusing the current budget.

## One source of truth

Use `.converge/brief.md` as the evolving behavioral source of truth. Plan writes
it; Build adds the implementation crosswalk; Verify adds evidence. Findings and
closure results are separate only because they are produced by an independent
review phase.

Use these local artifacts:

```text
.converge/
├── brief.md
├── state.yaml
├── findings.md   # only when Review finds issues
└── closure.md    # only when Close is needed
```

One project root or worktree has one active `.converge/` contract. Use a
separate worktree for a parallel or stacked change. Converge does not namespace
multiple active contracts inside one root.

Do not commit these files unless the user explicitly wants durable workflow
artifacts. Prefer adding `.converge/` to `.git/info/exclude`, not silently
editing the repository's committed `.gitignore`.

## Authorization boundaries

Converge does not itself authorize commits, pushes, pull requests, deployments,
production access, external writes, or destructive commands. Follow the user’s
request and the repository’s own instructions.
