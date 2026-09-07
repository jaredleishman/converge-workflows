# Converge Workflows

Converge is an installable, cross-harness software-development workflow that
front-loads path discovery and failure analysis, then bounds post-implementation
review to one broad review and one closure review.

It is designed to prevent this:

```text
review → fix → broad review → fix → broad review → ...
```

by using this:

```text
Plan: Interview → Direction approval → Map → Challenge → Split decision
Build → Verify
Review: one batch-complete broad review
Remediate: fix the whole batch by root-cause family → re-verify
Close: one delta-only closure review when needed
Targeted correction: one fix + confirmation for a small remediation-caused
  defect or an incomplete prior finding family
Outcome: CLOSED, REPLAN, SPLIT, or BLOCKED
```

Inside an invoked Converge workflow, the review budget and legal state
transitions are enforced mechanically by a bundled standard-library state gate
(`plugins/converge/scripts/state_gate.py`). Review and Close outcomes consume
their one-broad-plus-one-closure budget in the same state update. The plugin is
skill-only and does not intercept freehand actions outside Converge.

## Why Converge

A late finding is sometimes a real defect. Repeated distinct blocker families
usually mean the plan omitted an invariant, the remediation expanded scope, the
change should be split, or review is expanding the contract. Converge makes
that a workflow decision instead of automatically starting another review loop.

## Packaged hosts

The repository packages the same `skills/` tree for:

- Cursor
- OpenAI Codex
- xAI Grok Build
- Anthropic Claude Code
- Moonshot Kimi Code

The host-neutral workflow lives under
`plugins/converge/skills/_shared/`. Host manifests contain packaging metadata
only.

Repository validation checks those packages structurally. A release should
record which host install/load smoke tests were actually run; manifest success
alone is not a cross-host runtime claim.

## Install

### Cursor

Import this GitHub repository as a marketplace, then install the plugin:

1. Open **Customize → Plugins**.
2. Choose **Import marketplace** (or **Add marketplace**).
3. Paste `https://github.com/jaredleishman/converge-workflows`.
4. Install **converge**.

Reload the window if the skills do not appear. Invoke them as `/plan`, `/build`, `/verify`, `/review`, `/remediate`, `/close`, and `/status`.

On a Teams or Enterprise plan, the same URL works from **Dashboard → Plugins → Add Marketplace → Import from Repo**.

For local use from a clone:

```bash
mkdir -p ~/.cursor/plugins/local
ln -sfn "$(pwd)/plugins/converge" ~/.cursor/plugins/local/converge
```

Then reload Cursor (**Developer: Reload Window**).

To list it on the public Cursor Marketplace, submit the repository at [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish).

### Claude Code

```bash
claude plugin marketplace add jaredleishman/converge-workflows
claude plugin install converge@converge-workflows --scope user
```

Or in an interactive session:

```text
/plugin marketplace add jaredleishman/converge-workflows
/plugin install converge@converge-workflows
```

### Grok Build

```bash
grok plugin marketplace add jaredleishman/converge-workflows
grok plugin install converge --trust
```

Enable or inspect the plugin through `/plugins` when needed.

### Codex

```bash
codex plugin marketplace add jaredleishman/converge-workflows
```

Then start Codex, open `/plugins`, choose the `converge-workflows` marketplace,
and install `converge`.

### Kimi Code

From a local clone:

```text
/plugins marketplace .kimi-plugin/marketplace.json
```

or install the plugin directory directly:

```text
/plugins install ./plugins/converge
```

Then run `/reload` or start a new session. Manage the plugin through
`/plugins`.

### Muse Code

Muse Code has no plugin marketplace; it loads skills directly. All seven
converge skills pass `muse skills validate` unmodified. From a local clone:

```bash
for s in plan build verify review remediate close status; do
  muse skills install ./plugins/converge/skills/$s --scope user
done
```

The skills reference `../_shared/` siblings and invoke
`scripts/state_gate.py` by relative path, so confirm the installed layout
keeps each skill directory next to `_shared/` with `scripts/` two levels up:

```bash
muse skills inspect plan
```

If an install isolates skill directories, preserve the tree instead (copy or
symlink the `skills/` content so the relative layout stays intact). If
`converge` is already installed in Claude Code or Codex,
`muse skills import --from claude` or `muse skills import --from codex`
picks those skills up.

## Local development

Clone the repository, then validate it:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Test the plugin without publishing:

```bash
ln -sfn "$(pwd)/plugins/converge" ~/.cursor/plugins/local/converge
claude --plugin-dir ./plugins/converge
grok --plugin-dir ./plugins/converge
codex plugin marketplace add .
kimi -p "/plugins install ./plugins/converge"   # or /plugins install interactively
```

## Typical use

```text
/converge:plan <request>
/converge:build
/converge:verify
/converge:review
/converge:remediate   # only when Review produced blockers
/converge:verify      # rerun the invalidated obligations
/converge:close
# only if Close records TARGETED_FIX:
/converge:remediate
/converge:verify
```

Names vary slightly by host, but the skill folders and workflow artifacts are
the same.

## Local workflow artifacts

Converge uses a small project-local protocol:

```text
.converge/
├── brief.md
├── state.yaml
├── findings.md
├── closure.md
└── archive/    # previous CLOSED, REPLAN, or SPLIT contracts
```

The plugin recommends excluding `.converge/` through `.git/info/exclude` unless
you explicitly want the artifacts committed.

One project root or worktree supports one active `.converge/` contract. Use
separate worktrees for parallel or stacked changes.

## What "done" means

Two checks, no score. The contract passes: every acceptance criterion,
invariant, and baseline guarantee has evidence. And the brief's one-sentence
**Future change** has an obvious seam in the candidate. A cut that passes the
contract but would make that edit spray across the tree is `REPLAN`.

Plan seals a mechanism on four axes (ownership, ordering/commit, identity,
failure model). Build implements exactly that mechanism in exactly one tree,
then runs one bounded deletion pass. Review findings must cite a row; style
notes are follow-ups. There is no numeric score and no multi-model arena.

## Development principles

- Keep the Standard lane lightweight, and Fast lighter: Fast has its own
  short brief template.
- Every rule lives in one shared file; skills reference it instead of
  restating it. The validator budgets the policy each skill loads.
- Use one evolving Change Brief rather than many duplicated ledgers.
- Prefer a different model or context for Challenge and Review; a missing
  second model never blocks.
- Do not silently expand scope during review.
- A third broad review is a signal to replan or split, not the default next
  step.
- Treat fixture passes as protocol checks, not proof that Converge reduces
  real-world cycles or escaped defects.

## Repository layout

```text
.agents/plugins/marketplace.json       # Codex marketplace
.claude-plugin/marketplace.json        # Claude Code marketplace
.cursor-plugin/marketplace.json        # Cursor marketplace
.grok-plugin/marketplace.json          # Grok Build marketplace
.kimi-plugin/marketplace.json          # Kimi Code marketplace
plugins/converge/                      # installable plugin
scripts/                               # repository validation/version tools
tests/                                 # contract tests
evals/                                 # replay scenarios
```

## Version

Current version: `0.2.4`

## License

MIT
