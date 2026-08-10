# Standard scenario

Use a backend behavior change spanning an API path, model/service path, and
background consumer, but sharing one source of truth and one coherent mechanism.

Expected behavior:

- Map identifies all three paths before Build.
- One independent Challenge finds omitted sibling paths or confirms coverage.
- Review Round 1 returns one root-cause-grouped batch.
- Closure reviews only remediation and named siblings.
