#!/usr/bin/env python3
"""Synchronize the Converge version across package manifests."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
JSON_PATHS = [
    ROOT / "plugins/converge/.claude-plugin/plugin.json",
    ROOT / "plugins/converge/.codex-plugin/plugin.json",
    ROOT / "plugins/converge/.grok-plugin/plugin.json",
    ROOT / ".claude-plugin/marketplace.json",
    ROOT / ".grok-plugin/marketplace.json",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    args = parser.parse_args()
    if not SEMVER.fullmatch(args.version):
        parser.error("version must be semantic version text such as 0.2.0")

    (ROOT / "VERSION").write_text(args.version + "\n", encoding="utf-8")
    for path in JSON_PATHS:
        data = json.loads(path.read_text(encoding="utf-8"))
        if path.name == "marketplace.json":
            for plugin in data.get("plugins", []):
                if plugin.get("name") == "converge":
                    plugin["version"] = args.version
        else:
            data["version"] = args.version
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Synchronized Converge version to {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
