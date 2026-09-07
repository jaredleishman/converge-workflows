---
name: status
description: "Report the current Converge stage, lane, exact candidate, review budget, findings, and next allowed action without changing code."
disable-model-invocation: true
---

# Converge Status

If `.converge/state.yaml` exists, run
`python3 "<plugin-root>/scripts/state_gate.py" show` (`<plugin-root>` is the
installed plugin directory, `${CLAUDE_PLUGIN_ROOT}` in Claude Code) and treat
its output as authoritative for budgets, predecessor, and next allowed action.

Report: lane and status; brief location; candidate identity; broad and closure
budget use; open and closed finding IDs; archived predecessor if `show` printed
one; missing or inconsistent artifacts; the single next allowed action. If
`BLOCKED`, include the reason and resume status.

Do not modify code or advance the workflow. Without `.converge/`, report that
`plan` is the normal starting point. One project root holds one active
contract.
