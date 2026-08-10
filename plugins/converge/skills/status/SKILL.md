---
name: status
description: "Report the current Converge stage, lane, exact candidate, review budget, findings, and next allowed action without changing code."
disable-model-invocation: true
---

# Converge Status

Read available files under `.converge/` and report:

- Lane and current status
- Request and Change Brief location
- Candidate identity
- Split or replan decisions
- Broad and closure review budget usage
- Open and closed finding IDs
- Missing or inconsistent artifacts
- The single next allowed action

Do not modify code or advance the workflow. If no `.converge/` state exists,
report that `plan` is the normal starting point.
