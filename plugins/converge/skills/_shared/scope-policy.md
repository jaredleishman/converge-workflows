# Scope and split policy

## Review surface

Before implementation, map only the surfaces that can shape the requested
behavior:

- Entry points that create or mutate it
- Sources of truth and provenance
- Consumers and payload builders
- Database, cache, queue, and external effects
- Async dispatch, recovery, retry, and idempotency paths
- Concurrency and stale-state boundaries
- Migration, rollout, feature-fence, and mixed-version boundaries

Broaden only when repository evidence connects a path to the behavior.

## Split gate

Recommend splitting when the candidate has more than one independent proof
story. Warning signals include:

- Multiple sources of truth change
- Multiple external side-effect protocols change
- Migration, backfill, activation, and cutover are combined
- A new abstraction and many materially different consumers change together
- More than four substantial invariants are required
- More than six acceptance criteria are required
- Separate portions can ship safely and independently
- Challenge passes find unrelated root-cause families

A large diff may still be coherent. A small diff may still combine incompatible
state machines. Split by behavioral independence, not line count alone.

## Scope creep

A review finding blocks the current change only when it has a concrete reachable
path, material impact, a causal relationship to the candidate, and a violation
of the sealed brief or a regression introduced by the change.

Do not silently turn these into blockers:

- Unrelated baseline weaknesses
- General refactoring opportunities
- Defense in depth with no current reachable failure
- Future capabilities behind an effective fail-closed fence
- Product requirements absent from the sealed brief

A reviewer may propose a contract amendment, but must label it as such.
