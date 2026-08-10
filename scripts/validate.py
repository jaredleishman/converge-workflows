#!/usr/bin/env python3
"""Validate the cross-harness Converge plugin repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/converge"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path.relative_to(ROOT)} is invalid JSON: {exc}")


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(f"{path.relative_to(ROOT)} has no YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"{path.relative_to(ROOT)} has unterminated YAML frontmatter")
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            fail(f"{path.relative_to(ROOT)} has unsupported frontmatter line: {line}")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"\'')
    return result


def validate() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        fail("VERSION is not valid semantic version text")

    required_json = [
        ROOT / ".agents/plugins/marketplace.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / ".grok-plugin/marketplace.json",
        PLUGIN / ".claude-plugin/plugin.json",
        PLUGIN / ".codex-plugin/plugin.json",
        PLUGIN / ".grok-plugin/plugin.json",
    ]
    documents = {path: load_json(path) for path in required_json}

    for path in required_json[3:]:
        data = documents[path]
        if data.get("name") != "converge":
            fail(f"{path.relative_to(ROOT)} must name the plugin converge")
        if data.get("version") != version:
            fail(f"{path.relative_to(ROOT)} version does not match VERSION")

    claude_market = documents[ROOT / ".claude-plugin/marketplace.json"]
    grok_market = documents[ROOT / ".grok-plugin/marketplace.json"]
    codex_market = documents[ROOT / ".agents/plugins/marketplace.json"]
    for name, data in [("Claude", claude_market), ("Grok", grok_market), ("Codex", codex_market)]:
        entries = [p for p in data.get("plugins", []) if p.get("name") == "converge"]
        if len(entries) != 1:
            fail(f"{name} marketplace must contain exactly one converge entry")

    if claude_market["plugins"][0].get("source") != "./plugins/converge":
        fail("Claude marketplace source must point to ./plugins/converge")
    if grok_market["plugins"][0].get("source") != {"type": "local", "path": "./plugins/converge"}:
        fail("Grok marketplace local source is incorrect")
    if codex_market["plugins"][0].get("source") != {"source": "local", "path": "./plugins/converge"}:
        fail("Codex marketplace local source is incorrect")

    expected_skills = {"plan", "build", "verify", "review", "remediate", "close", "status"}
    found: set[str] = set()
    for path in sorted((PLUGIN / "skills").glob("*/SKILL.md")):
        meta = frontmatter(path)
        folder = path.parent.name
        if meta.get("name") != folder:
            fail(f"{path.relative_to(ROOT)} name must match its folder")
        if not meta.get("description"):
            fail(f"{path.relative_to(ROOT)} is missing a description")
        found.add(folder)
    if found != expected_skills:
        fail(f"skills differ from expected set: found {sorted(found)}")

    required_shared = [
        "workflow.md", "lanes.md", "scope-policy.md", "review-policy.md",
        "artifact-protocol.md", "templates/brief.md", "templates/state.yaml",
        "templates/findings.md", "templates/closure.md",
    ]
    for rel in required_shared:
        if not (PLUGIN / "skills/_shared" / rel).is_file():
            fail(f"missing shared file: {rel}")

    if not (PLUGIN / "scripts/state_gate.py").is_file():
        fail("missing state gate script: plugins/converge/scripts/state_gate.py")

    review_policy = (PLUGIN / "skills/_shared/review-policy.md").read_text(encoding="utf-8")
    required_policy_text = [
        "one broad", "delta closure", "Do not begin a third broad review automatically",
        "ORIGINAL_MISS", "SCOPE_EXPANSION",
    ]
    for phrase in required_policy_text:
        if phrase.lower() not in review_policy.lower():
            fail(f"review policy is missing required phrase: {phrase}")

    state_template = (PLUGIN / "skills/_shared/templates/state.yaml").read_text(encoding="utf-8")
    for line in ["broad_max: 1", "closure_max: 1"]:
        if line not in state_template:
            fail(f"state template must contain {line}")

    for path in ROOT.rglob("*"):
        if path.is_symlink() and not path.exists():
            fail(f"broken symlink: {path.relative_to(ROOT)}")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".yml", ".py"}:
            text = path.read_text(encoding="utf-8")
            if ("YOUR_" + "GITHUB_USER") in text or ("[TO" + "DO") in text:
                fail(f"unresolved placeholder in {path.relative_to(ROOT)}")


def main() -> int:
    try:
        validate()
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print("Converge plugin repository is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
