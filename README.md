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
Plan: Scope → Map → Challenge → Split decision
Build → Verify
Review: one batch-complete broad review
Remediate: fix the whole batch by root-cause family → re-verify
Close: one delta-only closure review when needed
Outcome: CLOSED, REPLAN, SPLIT, or BLOCKED
```

The review budget is enforced mechanically: skills call a bundled
standard-library state gate (`plugins/converge/scripts/state_gate.py`) that
checks stage preconditions and consumes the one-broad-plus-one-closure budget
recorded in `.converge/state.yaml`.

## Why Converge

A late finding is sometimes a real defect. Repeated distinct blocker families
usually mean the plan omitted an invariant, the remediation expanded scope, the
change should be split, or review is expanding the contract. Converge makes
that a workflow decision instead of automatically starting another review loop.

## Supported hosts

The repository packages the same `skills/` tree for:

- OpenAI Codex
- xAI Grok Build
- Anthropic Claude Code
- Moonshot Kimi Code

The host-neutral workflow lives under
`plugins/converge/skills/_shared/`. Host manifests contain packaging metadata
only.

## Install

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

## Local development

Clone the repository, then validate it:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

Test the plugin without publishing:

```bash
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
└── closure.md
```

The plugin recommends excluding `.converge/` through `.git/info/exclude` unless
you explicitly want the artifacts committed.

## Development principles

- Keep the Standard lane lightweight.
- Use one evolving Change Brief rather than many duplicated ledgers.
- Prefer a different model or context for the pre-build Challenge and broad
  Review.
- Do not silently expand scope during review.
- A third broad review is a signal to replan or split, not the default next
  step.

## Repository layout

```text
.agents/plugins/marketplace.json       # Codex marketplace
.claude-plugin/marketplace.json        # Claude Code marketplace
.grok-plugin/marketplace.json          # Grok Build marketplace
.kimi-plugin/marketplace.json          # Kimi Code marketplace
plugins/converge/                      # installable plugin
scripts/                               # repository validation/version tools
tests/                                 # contract tests
evals/                                 # replay scenarios
```

## Version

Current version: `0.2.0`

## License

MIT
