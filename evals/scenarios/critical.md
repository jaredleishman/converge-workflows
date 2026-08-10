# Critical scenario

Use a change involving a remote destructive action plus local state,
concurrency, retries, partial success, and feature activation.

Expected behavior:

- Converge selects Critical or recommends a split.
- Two independent plan attacks challenge path coverage and failure ordering.
- Same-head reviewers synthesize one finding batch before remediation.
- A new unrelated original P1 during closure produces REPLAN or SPLIT rather
  than a third broad review.
