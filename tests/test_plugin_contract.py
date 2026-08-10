from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/converge"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        self.assertEqual(
            {"plan", "build", "verify", "review", "remediate", "close", "status"}, names
        )

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
        module = load_module(ROOT / "scripts/validate.py", "converge_validate")
        module.validate()


class StateGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = load_module(
            PLUGIN / "scripts/state_gate.py", "converge_state_gate"
        )
        self.tmp = Path(tempfile.mkdtemp(prefix="converge-gate-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.state = self.tmp / "state.yaml"
        shutil.copy(PLUGIN / "skills/_shared/templates/state.yaml", self.state)

    def run_gate(self, *argv: str) -> int:
        return self.gate.main(["--state", str(self.state), *argv])

    def test_review_refused_until_internally_verified(self) -> None:
        self.assertEqual(1, self.run_gate("check", "review"))
        self.assertEqual(0, self.run_gate("set-status", "INTERNALLY_VERIFIED", "--stage", "verify"))
        self.assertEqual(0, self.run_gate("check", "review"))

    def test_broad_budget_cannot_be_consumed_twice(self) -> None:
        self.assertEqual(0, self.run_gate("consume", "broad"))
        self.assertEqual(1, self.run_gate("consume", "broad"))
        state = self.gate.parse_state(self.state.read_text(encoding="utf-8"))
        self.assertEqual(1, state["review_budget.broad_used"])

    def test_second_broad_review_is_refused(self) -> None:
        self.run_gate("set-status", "INTERNALLY_VERIFIED")
        self.run_gate("consume", "broad")
        self.assertEqual(1, self.run_gate("check", "review"))

    def test_close_requires_ready_for_closure_and_budget(self) -> None:
        self.assertEqual(1, self.run_gate("check", "close"))
        self.run_gate("consume", "broad")
        self.run_gate("set-status", "READY_FOR_CLOSURE", "--stage", "verify")
        self.assertEqual(0, self.run_gate("check", "close"))
        self.run_gate("consume", "closure")
        self.assertEqual(1, self.run_gate("check", "close"))

    def test_remediate_requires_findings_and_round_one(self) -> None:
        self.run_gate("set-status", "REVIEW_FINDINGS", "--stage", "review")
        self.assertEqual(1, self.run_gate("check", "remediate"))
        self.run_gate("consume", "broad")
        self.assertEqual(0, self.run_gate("check", "remediate"))

    def test_unknown_status_is_rejected(self) -> None:
        self.assertEqual(1, self.run_gate("set-status", "SHIPPED"))

    def test_missing_state_file_is_reported(self) -> None:
        self.state.unlink()
        self.assertEqual(1, self.run_gate("check", "build"))


if __name__ == "__main__":
    unittest.main()
