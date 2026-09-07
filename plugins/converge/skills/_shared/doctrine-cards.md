# Doctrine cards

Plan reads this only when the structural-alternatives branch runs. A card
generates a Challenge candidate. Name the card in the alternatives table;
never name an engineer.

- `minimal` — one source of truth; no new type unless an AC names it; failures
  are returned, not wrapped.
- `supervision` — every durable identity has one owner; crash and retry are
  explicit; no shared bag of state.
- `evidence` — no production file until a failing test or AC names the seam;
  no API beyond what tests and ACs need.

Three cards. Add a fourth only when a real run shows all three produced the
same cut.
