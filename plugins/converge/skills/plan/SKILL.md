---
name: plan
description: "Start or revise a meaningful software change with Converge. Use for scoping, code-path mapping, acceptance criteria, design challenge, lane selection, or deciding whether a change should be split before implementation."
disable-model-invocation: true
argument-hint: "<request, issue, or existing plan>"
---

# Converge Plan

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/plan/` (`${CLAUDE_PLUGIN_ROOT}/skills/plan/` in Claude
Code). `.converge/` paths resolve against the project root.

Read:

- `../_shared/workflow.md`
- `../_shared/lanes.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`
- `../_shared/templates/brief.md`
- `../_shared/templates/state.yaml`

Plan runs in two phases. Phase 1 is a conversation that ends with the user
explicitly approving a direction. Phase 2 turns the approved direction into
the contract. Do not start Phase 2 — no deep mapping, no `.converge/` files,
no Challenge pass — before Phase 1 ends in approval.

## Phase 1 — Interview

1. Skim only enough of the repository (its instructions plus the obviously
   relevant modules) to ask informed questions. This is reconnaissance, not
   the Map.
2. Interview the user about what they actually want. Ask in small rounds of
   at most three questions, and let each round's answers shape the next.
   Prefer concrete questions grounded in what the code actually does
   ("X currently happens on retry — keep that or change it?") over
   open-ended ones. Use the host's structured-question tool when one exists;
   otherwise ask in chat. Across rounds, resolve whichever of these the
   request leaves ambiguous:
   - Observable outcome: what behavior changes, and for whom
   - Non-goals: nearby behavior that must not change
   - Constraints: compatibility, rollout, performance, data, deadlines
   - Failure model: dangerous false successes and worst-case impact
   - Success judgment: the examples the user would accept as proof
   - Appetite: smallest useful version versus the full ask, and any
     natural split candidates
   Skip questions whose answers are already explicit in the request or
   unambiguous in the repository. The goal is to surface real decisions,
   not to run a questionnaire.
3. When the direction feels settled, present a Direction Summary in chat: a
   short restatement of outcome, non-goals, key constraints, the rough
   mechanism, and the proposed lane. Ask the user to approve, adjust, or
   redirect. The summary is a proposal for discussion, not the contract.
4. Iterate — more questions, revised summary — until the user gives an
   explicit yes to the Direction Summary. Silence or absence of objection
   is not approval. If the user redirects, restart the round from their
   correction rather than defending the previous summary.

Phase 1 may collapse to a single confirmation of the Direction Summary only
when the request is trivially unambiguous or the user explicitly asks to
skip the interview ("just plan it"). Even then, show the summary and get the
yes before Phase 2.

Bias toward the Fast lane when repository evidence satisfies every Fast
condition. Fast still needs explicit Direction Summary approval, but do not
manufacture interview rounds after the direction is already clear.

## Phase 2 — Contract

1. Read the repository's instructions and obtain the smallest relevant code
   context beyond the Phase 1 skim.
2. Map entry points, sources of truth, consumers, state mutations, external
   effects, async/retry paths, concurrency boundaries, and rollout boundaries.
3. Confirm the lane proposed in the Direction Summary against the actual
   impact and failure model. Apply the compound-boundary screen in `lanes.md`
   and record a short lane rationale. When Standard relies on an exception,
   enumerate its boundaries, containment, recovery, ownership, and falsifying
   evidence. Tell the user if mapping changed the proposed lane.
4. Write the smallest coherent proposed change and a Planned mechanism
   baseline that names its ownership, ordering, identity, and failure-model
   decisions. Include the shared baseline guarantees as non-waivable regression
   boundaries. Fast uses at most two important invariants and three acceptance
   criteria; Standard uses at most four important invariants and six acceptance
   criteria.
5. When `scope-policy.md` triggers the Critical lifecycle/ownership matrix,
   model the applicable event and failure paths in the existing brief. Add
   Critical proof obligations that distinguish direct or boundary-faithful
   evidence from proxies. Omit both sections when their trigger does not apply;
   do not burden a simple Standard brief with Critical ceremony.
6. Perform code-aware Challenge focused only on missing surfaces, defeating
   failure sequences, unsupported assumptions, proof fidelity, and split
   candidates. Standard uses one pass. Critical uses two independent passes
   with hidden findings and different contexts or lenses; synthesize only after
   both finish. If the host cannot provide the second independent context,
   record the limitation and obtain an explicit user decision before calling
   Challenge complete.
7. Amend the contract with supported Challenge findings, then decide whether
   the work has one proof story or should be split. If mapping or Challenge
   contradicts the approved direction, return to Phase 1 with what you found
   instead of silently changing the direction.
8. Create or update `.converge/brief.md` and `.converge/state.yaml` from the
   templates. Leave the review-budget fields exactly as templated; only the
   state gate changes them. Add `.converge/` to `.git/info/exclude` when
   appropriate; do not silently change committed ignore files.
9. End with `PLANNED`, `SPLIT`, or `BLOCKED`, recorded via
   `python3 "<plugin-root>/scripts/state_gate.py" set-status <STATUS> --stage plan`.
   `BLOCKED` also requires `--reason`. A terminal `REPLAN` or `SPLIT` starts a
   new contract from a newly created state file; do not reset the current file.
   Ending `PLANNED` seals the contract sections of the brief (see
   `workflow.md`); later changes to them are labeled contract amendments that
   return through this skill.

Do not implement unless the user explicitly requested continued execution.
Do not propose unrelated cleanup or generalized hardening.

One project root or worktree supports one active `.converge/` contract. Direct
parallel or stacked changes to separate worktrees instead of overwriting state.
