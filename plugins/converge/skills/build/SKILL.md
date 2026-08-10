---
name: build
description: "Implement a planned Converge change. Use after a Change Brief is sealed and the split decision is ONE_CHANGE."
disable-model-invocation: true
argument-hint: "[brief path or implementation instruction]"
---

# Converge Build

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/scope-policy.md`
- `../_shared/artifact-protocol.md`

Then:

1. Confirm the state is `PLANNED` and the split decision is `ONE_CHANGE`.
2. Follow repository-native instructions, helpers, conventions, and tests.
3. Implement the smallest behavioral change that satisfies the brief.
4. Maintain the Implementation Crosswalk in `brief.md`: each invariant and
   acceptance criterion maps to concrete seams, governed paths, tests, and any
   deviation from the plan.
5. Do not patch adjacent weaknesses merely because they are convenient. Record
   them as follow-ups unless they are required by the brief or prevent a
   regression introduced by this change.
6. If the implementation mechanism materially differs from the plan—for
   example, database CAS becomes a renewable lease—stop and return to Plan's
   Challenge step before proceeding. The failure model changed.
7. Run cheap local checks while building, but leave authoritative evidence to
   Verify.
8. End with `READY_FOR_VERIFY` or `BLOCKED`.

Do not commit, push, open a pull request, deploy, or access production unless the
user separately authorizes it.
