---
name: build
description: "Implement a planned Converge change. Use after a Change Brief is sealed and the split decision is ONE_CHANGE."
disable-model-invocation: true
argument-hint: "[brief path or implementation instruction]"
---

# Converge Build

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/build/` (`${CLAUDE_PLUGIN_ROOT}/skills/build/` in Claude
Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check build` and stop
   with its guidance if it refuses. It accepts `PLANNED` and an interrupted
   `BUILDING`. Confirm the split decision is `ONE_CHANGE`. From `PLANNED`,
   record `BUILDING` via `set-status BUILDING --stage build`; when already
   `BUILDING`, resume without resetting state.
2. Follow repository-native instructions, helpers, conventions, and tests.
3. Implement the smallest behavioral change that satisfies the brief.
4. Maintain the Implementation Crosswalk in `brief.md`: each invariant,
   acceptance criterion, and applicable baseline guarantee maps to concrete
   seams, governed paths, tests, and any deviation from the plan.
5. Do not patch adjacent weaknesses merely because they are convenient. Record
   them as follow-ups unless they are required by the brief or prevent a
   regression introduced by this change.
6. Before handing work to Verify, run the planned-mechanism drift checkpoint in
   `scope-policy.md`. Compare the diff and connected seams with the sealed
   Planned mechanism baseline. Inventory every new or materially changed
   thread/task/queue/callback/signal, transaction or commit point,
   retry/timeout/cancellation path, logical or physical resource owner,
   identity/collision/deduplication rule, persistent-state transition, and
   external-effect path. Record the declaration and inspected seams in the
   Implementation Crosswalk.
7. If that inventory changes the ownership, ordering, identity, or failure
   model—for example, database CAS becomes a renewable lease or synchronous
   work becomes a background task—stop. Use `REPLAN` for the same outcome or
   `SPLIT` for independently provable outcomes instead of continuing serially.
8. Run cheap local checks while building, but leave authoritative evidence to
   Verify.
9. End with `READY_FOR_VERIFY`, `REPLAN`, `SPLIT`, or `BLOCKED`, recorded via the state gate's
   `set-status`. `BLOCKED` requires `--reason`; after its external prerequisite
   is resolved, use the gate's `resume` command rather than guessing a status.

Do not commit, push, open a pull request, deploy, or access production unless the
user separately authorizes it.
