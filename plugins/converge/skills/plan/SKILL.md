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

Then:

1. Resolve the requested outcome, affected users or systems, constraints, and
   explicit non-goals. Use repository evidence to resolve ambiguity when
   possible; ask only when the behavioral outcome cannot be inferred safely.
2. Read the repository's instructions and obtain the smallest relevant code
   context.
3. Map entry points, sources of truth, consumers, state mutations, external
   effects, async/retry paths, concurrency boundaries, and rollout boundaries.
4. Choose Fast, Standard, or Critical using the actual impact and failure model.
5. Write the smallest coherent proposed change, up to four important invariants
   and six acceptance criteria for Standard work.
6. Perform a code-aware Challenge pass focused only on missing surfaces,
   defeating failure sequences, unsupported assumptions, and split candidates.
   Prefer an independent context or different model when available.
7. Decide whether the work has one proof story or should be split.
8. Create or update `.converge/brief.md` and `.converge/state.yaml` from the
   templates. Leave the review-budget fields exactly as templated; only the
   state gate changes them. Add `.converge/` to `.git/info/exclude` when
   appropriate; do not silently change committed ignore files.
9. End with `PLANNED`, `SPLIT`, or `BLOCKED`, recorded via
   `python3 "<plugin-root>/scripts/state_gate.py" set-status <STATUS> --stage plan`.
   Ending `PLANNED` seals the contract sections of the brief (see
   `workflow.md`); later changes to them are labeled contract amendments that
   return through this skill.

Do not implement unless the user explicitly requested continued execution.
Do not propose unrelated cleanup or generalized hardening.
