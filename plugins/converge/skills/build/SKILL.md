---
name: build
description: "Implement a planned Converge change. Use after a Change Brief is sealed and the split decision is ONE_CHANGE."
disable-model-invocation: true
argument-hint: "[brief path or implementation instruction]"
---

# Converge Build

`../_shared/` is relative to this skill folder; `.converge/` is at the project
root; `<plugin-root>` is the installed plugin directory.

Read `.converge/brief.md`, `.converge/state.yaml`, `../_shared/workflow.md`,
and `../_shared/candidate-checks.md`.

**Reading rule.** Implement from Outcome, Non-goals, Baseline guarantees, Map,
Planned mechanism baseline, Invariants, Acceptance criteria, and Future change.
Do not optimize against Challenge alternatives or rejected candidates; they
stay in the brief for Review.

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check build`; stop with
   its guidance if it refuses. Confirm the split decision is `ONE_CHANGE`. From
   `PLANNED`, record `set-status BUILDING --stage build`; an interrupted
   `BUILDING` resumes without resetting state.
2. Follow repository-native instructions, helpers, conventions, and tests.
3. Before editing, identify the smallest coherent dependency slice and its
   local check. If more than one slice is needed, record the current proof
   unit prospectively in the brief, implement only that unit, run and record
   its local check, and only then begin the next unit. One indivisible change
   needs one compact note. Proof units are not commits, stacks, releases, or
   promises that a slice ships alone.
4. Implement the smallest behavioral change that satisfies the brief. Exactly
   one implementation in exactly one tree: a second worktree or second attempt
   means the state is wrong (`REPLAN`), not a bake-off.
5. Keep the Implementation crosswalk current: every invariant, AC, and
   applicable BG maps to seams, paths, tests, and deviations. Name the seam
   the Future change would use.
6. Do not patch adjacent weaknesses because they are convenient. Record them as
   follow-ups unless the brief requires them or they prevent a regression this
   change introduces. Apply delegated stage ownership (`workflow.md`) when a
   unit is delegated.
7. Run the planned-mechanism drift checkpoint in `candidate-checks.md`. If it
   changes any axis, stop: `REPLAN` for the same outcome, `SPLIT` for
   independently provable outcomes. Do not polish a wrong cut.
8. Run the deletion pass in `candidate-checks.md` and record it in the
   crosswalk.
9. Run cheap local checks while building, including each proof-unit check, but
   leave full-candidate evidence to Verify. A passing unit check does not
   prove the completed candidate.
10. End with `set-status READY_FOR_VERIFY|REPLAN|SPLIT|BLOCKED --stage build`.
    `BLOCKED` requires `--reason`; use `resume` once it is resolved.

No commit, push, pull request, deploy, or production access without the
user's separate authorization.
