# Converge workflow

Converge exists to make software review converge predictably by moving missing
path discovery and failure analysis before implementation.

## The flow

```text
Plan: Scope → Map → Challenge → Split decision
Build
Verify
Review: one broad, batch-complete review
Close: one delta-only closure review, only when Review found blockers
Outcome: CLOSED, REPLAN, SPLIT, or BLOCKED
```

## Central rule

One broad implementation review is allowed. One closure review is allowed after
substantive remediation. A third broad review is not the default next step.

When closure finds a distinct original blocker family that the first review and
plan both missed, stop serial patching. Return `REPLAN` or `SPLIT` unless the
user explicitly chooses a new contract and review cycle.

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

Do not commit these files unless the user explicitly wants durable workflow
artifacts. Prefer adding `.converge/` to `.git/info/exclude`, not silently
editing the repository's committed `.gitignore`.

## Authorization boundaries

Converge does not itself authorize commits, pushes, pull requests, deployments,
production access, external writes, or destructive commands. Follow the user’s
request and the repository’s own instructions.
