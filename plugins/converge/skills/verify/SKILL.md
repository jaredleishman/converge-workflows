---
name: verify
description: "Verify the exact Converge candidate against its Change Brief, invariants, acceptance criteria, connected paths, and repository-native checks."
disable-model-invocation: true
argument-hint: "[candidate, commit, branch, or pull request]"
---

# Converge Verify

Paths beginning with `../` resolve against this skill's installed folder,
`<plugin-root>/skills/verify/` (`${CLAUDE_PLUGIN_ROOT}/skills/verify/` in
Claude Code). `.converge/` paths resolve against the project root.

Read:

- `.converge/brief.md`
- `.converge/state.yaml`
- `../_shared/workflow.md`
- `../_shared/artifact-protocol.md`

Then:

1. Run `python3 "<plugin-root>/scripts/state_gate.py" check verify` and stop
   with its guidance if it refuses. Resolve the exact candidate: PR base/head,
   commit range, or local worktree fingerprint. Record it in `state.yaml`.
2. Verify every acceptance criterion and invariant using the implementation
   crosswalk. Exercise the important entry points, consumers, and relevant
   failure cases named in the brief.
3. Run repository-native validation in cheap-to-expensive order. Do not claim
   checks that were not run.
4. For material tests, explain which broken mechanism or injected failure they
   would detect. This is a sensitivity claim, not mathematical proof.
5. Record evidence, results, and unavailable or partial evidence in the
   Verification Evidence table in `brief.md`.
6. Reassess whether the implementation expanded the contract or invalidated the
   split decision. Return to Plan when it did.
7. End with `INTERNALLY_VERIFIED`, `REPLAN`, `SPLIT`, or `BLOCKED`, recorded
   via the state gate's `set-status --stage verify`. Exception: when this run
   re-verified remediation of Round 1 findings (`broad_used` is `1` and open
   findings exist), end `READY_FOR_CLOSURE` instead so Close can run.

`INTERNALLY_VERIFIED` means builder-owned evidence passed. It is not independent
review approval.
