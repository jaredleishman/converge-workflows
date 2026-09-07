---
name: plan
description: "Start or revise a meaningful software change with Converge. Use for scoping, code-path mapping, acceptance criteria, design challenge, lane selection, or deciding whether a change should be split before implementation."
disable-model-invocation: true
argument-hint: "<request, issue, or existing plan>"
---

# Converge Plan

`../_shared/` is relative to this skill folder (`${CLAUDE_PLUGIN_ROOT}/skills/plan/`
in Claude Code). `.converge/` is at the project root. `<plugin-root>` is the
installed plugin directory.

Plan has two phases. Phase 1 is a conversation that ends with the user
explicitly approving a direction. Phase 2 turns that direction into the
contract. Do not map deeply, Challenge, or write `.converge/` before approval.

## Phase 1 — Interview

Read `../_shared/workflow.md` and `../_shared/lanes.md`.

1. Skim the repository just enough to ask informed questions: its instructions
   and the obviously relevant modules. This is reconnaissance, not the Map.
2. Interview in rounds of at most three questions, each round shaped by the
   last. Prefer concrete, code-grounded questions ("X currently happens on
   retry; keep that?") over open ones. Use the host's structured-question tool
   when one exists. Resolve whatever the request leaves ambiguous among:
   observable outcome; non-goals; constraints; failure model; the examples the
   user would accept as proof; appetite and natural split candidates. Skip
   questions the request or repository already answers.
3. When the direction feels settled, present a Direction Summary: outcome,
   non-goals, key constraints, the rough mechanism (including any axis that is
   genuinely open), the one likely Future change, and the proposed lane. Say
   whether the alternatives branch will run; the user may ask to "search the
   cut" on any Standard change. Ask the user to approve, adjust, or redirect.
4. Iterate until the user gives an explicit yes. Silence is not approval. On a
   redirect, restart from the correction rather than defending the summary.

Collapse Phase 1 to one confirmation only when the request is trivially
unambiguous or the user says to skip the interview. Even then, show the summary
and get the yes. Bias toward Fast when repository evidence supports every Fast
condition; do not manufacture rounds after the direction is clear.

## Phase 2 — Contract

Fast: read only `../_shared/templates/brief-fast.md` and do steps 1, 2, 3, 4,
9, and 10. Standard and Critical: read `../_shared/scope-policy.md` and
`../_shared/templates/brief.md`, adding `../_shared/templates/brief-critical.md`
sections only when Critical or a Standard exception needs them, and
`../_shared/doctrine-cards.md` only if the alternatives branch runs.

1. Read the repository's instructions and the smallest relevant code context
   beyond the Phase 1 skim.
2. Map entry points, sources of truth, consumers, state mutations, external
   effects, async/retry paths, concurrency boundaries, and rollout boundaries.
   For Standard and Critical, apply causal grounding completion from
   `scope-policy.md` to every materially distinct path. Reuse an applicable
   Critical lifecycle matrix instead of duplicating it.
3. Confirm the lane against the actual impact and failure model using the
   compound-boundary screen in `lanes.md`; record a short rationale. A Standard
   exception uses the fields in `brief-critical.md`. Tell the user if mapping
   changed the lane.
4. Draft the smallest coherent proposed change and enough of the mechanism to
   Challenge it, but do not finalize the Planned mechanism baseline yet.
   Include the baseline guarantees. Respect the lane's invariant and AC caps.
   Write the Future change sentence.
5. When `scope-policy.md` triggers the Critical lifecycle matrix, copy those
   sections and the proof obligations from `brief-critical.md`. Otherwise omit
   them.
6. After Map, apply the conditional structural-alternatives rule in
   `scope-policy.md`. When it triggers (or the user asked to search the cut),
   Challenge at least two mechanisms that disagree on an axis; cosmetic
   variants do not count. Use a doctrine card or one flipped axis for the
   second candidate. Otherwise record the reason in one line.
7. Fast skips Challenge; if mapping showed the change is no longer Fast,
   return to lane selection. Standard uses one Challenge pass. Critical uses
   two independent passes with hidden findings and different contexts or
   lenses, synthesized only after both finish and recorded in the
   `brief-critical.md` table; if the host cannot provide a second context,
   record the limitation and get an explicit user decision. Apply delegated
   stage ownership from `workflow.md` when a pass is delegated.
8. Select or synthesize the mechanism after Challenge. Finalize the Planned
   mechanism baseline: one coherent organizing model plus all four axes
   (ownership, ordering/commit, identity, failure model). Standard and Critical
   cannot seal with a blank axis. Amend the contract with supported Challenge
   findings and decide `ONE_CHANGE` or `SPLIT`. If Map or Challenge contradicts
   the approved direction, return to Phase 1 with what you found.
9. Run `python3 "<plugin-root>/scripts/state_gate.py" init --lane <lane>`.
   It creates `.converge/`, reuses `PLANNING`, archives a finished contract,
   and refuses any other live status. Write `.converge/brief.md` from the
   lane's template. Leave budget fields to the gate. Add `.converge/` to
   `.git/info/exclude` when appropriate; do not edit committed ignore files.
10. End with `set-status PLANNED|SPLIT|BLOCKED --stage plan`. `PLANNED`
    requires the brief; `BLOCKED` requires `--reason`. `PLANNED` seals the
    contract sections (`workflow.md`); later changes are contract amendments
    that return here.

Do not implement. After `PLANNED`, tell the user to run Build.
