---
name: status
description: "Report the current Converge stage, lane, exact candidate, review budget, findings, and next allowed action without changing code."
disable-model-invocation: true
---

# Converge Status

When `.converge/state.yaml` exists, first run
`python3 "<plugin-root>/scripts/state_gate.py" show`, where `<plugin-root>` is
the installed plugin directory (`${CLAUDE_PLUGIN_ROOT}` in Claude Code), and
treat its output as authoritative for budgets and the next allowed action.

Read available files under `.converge/` and report:

- Lane and current status
- Request and Change Brief location
- Candidate identity
- Split or replan decisions
- Broad and closure review budget usage
- Open and closed finding IDs
- Missing or inconsistent artifacts
- The single next allowed action

Also report that one project root supports one active contract. If the state is
`BLOCKED`, include the recorded reason and resume status. If it is
`TARGETED_FIX` or `READY_FOR_TARGETED_CONFIRMATION`, state explicitly that broad
and closure review cannot reopen.

Do not modify code or advance the workflow. If no `.converge/` state exists,
report that `plan` is the normal starting point.
