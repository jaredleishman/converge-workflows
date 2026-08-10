from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/converge"


class PluginContractTests(unittest.TestCase):
    def test_all_marketplaces_expose_converge(self) -> None:
        paths = [
            ROOT / ".agents/plugins/marketplace.json",
            ROOT / ".claude-plugin/marketplace.json",
            ROOT / ".grok-plugin/marketplace.json",
        ]
        for path in paths:
            with self.subTest(path=path):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn("converge", {p["name"] for p in data["plugins"]})

    def test_plugin_versions_match(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        manifests = [
            PLUGIN / ".claude-plugin/plugin.json",
            PLUGIN / ".codex-plugin/plugin.json",
            PLUGIN / ".grok-plugin/plugin.json",
        ]
        for path in manifests:
            with self.subTest(path=path):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(version, data["version"])

    def test_public_skill_set_is_small_and_stable(self) -> None:
        names = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual({"plan", "build", "verify", "review", "close", "status"}, names)

    def test_review_budget_is_one_plus_one(self) -> None:
        state = (PLUGIN / "skills/_shared/templates/state.yaml").read_text(encoding="utf-8")
        self.assertIn("broad_max: 1", state)
        self.assertIn("closure_max: 1", state)
        policy = (PLUGIN / "skills/_shared/review-policy.md").read_text(encoding="utf-8")
        self.assertIn("Do not begin a third broad review automatically", policy)

    def test_standard_lane_has_complexity_budgets(self) -> None:
        lanes = (PLUGIN / "skills/_shared/lanes.md").read_text(encoding="utf-8")
        self.assertIn("Important invariants: at most 4", lanes)
        self.assertIn("Acceptance criteria: at most 6", lanes)
        self.assertIn("Broad implementation reviews: 1", lanes)

    def test_repository_validator_passes(self) -> None:
        path = ROOT / "scripts/validate.py"
        spec = importlib.util.spec_from_file_location("converge_validate", path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.validate()


if __name__ == "__main__":
    unittest.main()
