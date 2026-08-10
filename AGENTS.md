# Repository instructions

This repository packages one host-neutral workflow for several agent harnesses.

## Sources of truth

- Workflow policy: `plugins/converge/skills/_shared/`
- Public entry points: `plugins/converge/skills/*/SKILL.md`
- Version: `VERSION`

Do not duplicate workflow policy in host manifests or root documentation.
Host manifests should contain only packaging and display metadata.

## Change discipline

- Keep the Standard lane lightweight.
- Do not add a new artifact unless it replaces duplication or closes a measured
  workflow failure.
- Do not expand Converge into a general-purpose SDLC framework.
- Preserve the rule: one broad review, one closure review, then close, replan,
  or split.
- Keep the plugin skill-only unless a concrete evaluation proves that hooks,
  MCP, or runtime orchestration are necessary.

## Validation

Run before committing:

```bash
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```
