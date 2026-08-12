from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/converge"
BASE_SHA = "a" * 40
HEAD_SHA = "b" * 40


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
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
        kimi = json.loads(
            (ROOT / ".kimi-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        self.assertIn("converge", {p["id"] for p in kimi["plugins"]})

    def test_plugin_and_readme_versions_match(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        manifests = [
            PLUGIN / ".claude-plugin/plugin.json",
            PLUGIN / ".codex-plugin/plugin.json",
            PLUGIN / ".grok-plugin/plugin.json",
            PLUGIN / ".kimi-plugin/plugin.json",
        ]
        for path in manifests:
            with self.subTest(path=path):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(version, data["version"])
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn(f"Current version: `{version}`", readme)

    def test_public_skill_set_is_small_and_stable(self) -> None:
        names = {path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")}
        self.assertEqual(
            {"plan", "build", "verify", "review", "remediate", "close", "status"},
            names,
        )

    def test_review_budget_and_targeted_path_are_finite(self) -> None:
        state = (PLUGIN / "skills/_shared/templates/state.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("broad_max: 1", state)
        self.assertIn("closure_max: 1", state)
        policy = (PLUGIN / "skills/_shared/review-policy.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not begin a third broad review automatically", policy)
        self.assertIn("The targeted path is finite", policy)
        self.assertIn("Blocking `NEW_EVIDENCE`", policy)
        self.assertIn("candidate-caused violation", policy)
        findings = (PLUGIN / "skills/_shared/templates/findings.md").read_text(
            encoding="utf-8"
        )
        closure = (PLUGIN / "skills/_shared/templates/closure.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("pending | 0/1 | 1/1", findings)
        self.assertIn("PENDING | CLEAN | FINDINGS | REPLAN | SPLIT | BLOCKED", findings)
        self.assertIn("pending | 0/1 | 1/1", closure)

    def test_standard_and_fast_lanes_have_complexity_budgets(self) -> None:
        lanes = (PLUGIN / "skills/_shared/lanes.md").read_text(encoding="utf-8")
        self.assertIn("Important invariants: at most 4", lanes)
        self.assertIn("Acceptance criteria: at most 6", lanes)
        self.assertIn("at most two important invariants", lanes)
        self.assertRegex(lanes, r"three acceptance\s+criteria")

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
        self.stdout = ""
        self.stderr = ""

    def run_gate(self, *argv: str) -> int:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = self.gate.main(["--state", str(self.state), *argv])
        self.stdout = stdout.getvalue()
        self.stderr = stderr.getvalue()
        return result

    def transition(self, status: str, stage: str, *extra: str) -> int:
        return self.run_gate("set-status", status, "--stage", stage, *extra)

    def prepare_ready_for_verify(self) -> None:
        self.assertEqual(0, self.transition("PLANNED", "plan"))
        self.assertEqual(0, self.transition("BUILDING", "build"))
        self.assertEqual(0, self.transition("READY_FOR_VERIFY", "build"))

    def record_commit_candidate(self) -> None:
        self.assertEqual(
            0,
            self.run_gate(
                "candidate",
                "record",
                "--kind",
                "commit",
                "--repository",
                "example/repository",
                "--base-sha",
                BASE_SHA,
                "--head-sha",
                HEAD_SHA,
            ),
        )

    def prepare_verified(self) -> None:
        self.prepare_ready_for_verify()
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("INTERNALLY_VERIFIED", "verify"))

    def prepare_ready_for_closure(self) -> None:
        self.prepare_verified()
        self.assertEqual(
            0,
            self.transition(
                "REVIEW_FINDINGS",
                "review",
                "--finding",
                "REV-1",
                "--finding",
                "REV-2",
            ),
        )
        self.assertEqual(0, self.transition("REMEDIATING", "remediate"))
        self.assertEqual(0, self.transition("READY_FOR_VERIFY", "remediate"))
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("READY_FOR_CLOSURE", "verify"))

    def parsed(self) -> dict[str, object]:
        return self.gate.load(self.state)[1]

    def test_illegal_transition_is_refused_without_mutation(self) -> None:
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(1, self.transition("INTERNALLY_VERIFIED", "verify"))
        self.assertIn("illegal transition", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_build_resumes_and_verify_can_return_to_build(self) -> None:
        self.assertEqual(0, self.transition("PLANNED", "plan"))
        self.assertEqual(0, self.transition("BUILDING", "build"))
        self.assertEqual(0, self.run_gate("check", "build"))
        self.assertEqual(0, self.transition("BUILDING", "build"))
        self.assertEqual(0, self.transition("READY_FOR_VERIFY", "build"))
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("BUILDING", "build"))
        state = self.parsed()
        self.assertEqual("BUILDING", state["status"])
        self.assertEqual("unset", state["candidate.kind"])
        self.assertEqual(0, state["review_budget.broad_used"])

    def test_blocked_requires_reason_and_resumes_exact_prior_state(self) -> None:
        self.assertEqual(0, self.transition("PLANNED", "plan"))
        self.assertEqual(0, self.transition("BUILDING", "build"))
        self.assertEqual(1, self.transition("BLOCKED", "build"))
        self.assertIn("requires --reason", self.stderr)
        self.assertEqual(
            0,
            self.transition(
                "BLOCKED", "build", "--reason", "required test service unavailable"
            ),
        )
        state = self.parsed()
        self.assertEqual("BUILDING", state["decision.resume_status"])
        self.assertEqual(0, self.run_gate("resume"))
        state = self.parsed()
        self.assertEqual("BUILDING", state["status"])
        self.assertIsNone(state["decision.blocked_reason"])
        self.assertIsNone(state["decision.resume_status"])

    def test_review_requires_recorded_candidate(self) -> None:
        self.prepare_ready_for_verify()
        self.assertEqual(1, self.transition("INTERNALLY_VERIFIED", "verify"))
        self.assertIn("exact candidate is unset", self.stderr)
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("INTERNALLY_VERIFIED", "verify"))
        self.assertEqual(0, self.run_gate("check", "review"))

    def test_review_outcome_atomically_records_budget_and_findings(self) -> None:
        self.prepare_verified()
        self.assertEqual(
            0,
            self.transition(
                "REVIEW_FINDINGS",
                "review",
                "--finding",
                "REV-1",
                "--finding",
                "REV-2",
            ),
        )
        state = self.parsed()
        self.assertEqual("REVIEW_FINDINGS", state["status"])
        self.assertEqual(1, state["review_budget.broad_used"])
        self.assertEqual(["REV-1", "REV-2"], state["findings.open"])

    def test_review_outcome_requires_review_stage(self) -> None:
        self.prepare_verified()
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(
            1,
            self.transition(
                "REVIEW_FINDINGS", "build", "--finding", "REV-1"
            ),
        )
        self.assertIn("requires stage review", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_terminal_review_outcome_requires_finding_ids(self) -> None:
        self.prepare_verified()
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(1, self.transition("REPLAN", "review"))
        self.assertIn("requires one or more --finding IDs", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))
        self.assertEqual(
            1,
            self.transition(
                "BLOCKED",
                "review",
                "--reason",
                "evidence unavailable",
                "--finding",
                "REV-1",
            ),
        )
        self.assertIn("--finding is not valid", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_exhausted_broad_budget_is_still_a_loop_breaker(self) -> None:
        self.prepare_verified()
        self.assertEqual(
            0,
            self.transition("REVIEW_FINDINGS", "review", "--finding", "REV-1"),
        )
        text = self.state.read_text(encoding="utf-8")
        self.state.write_text(
            text.replace("status: REVIEW_FINDINGS", "status: INTERNALLY_VERIFIED"),
            encoding="utf-8",
        )
        self.assertEqual(1, self.run_gate("check", "review"))
        self.assertIn("review budget is exhausted", self.stderr)

    def test_reverify_requires_round_one_findings(self) -> None:
        self.prepare_ready_for_verify()
        self.record_commit_candidate()
        self.assertEqual(1, self.transition("READY_FOR_CLOSURE", "verify"))
        self.assertIn("broad_used 1 and open Round 1 findings", self.stderr)

    def test_failed_round_one_reverify_returns_to_remediating(self) -> None:
        self.prepare_verified()
        self.assertEqual(
            0,
            self.transition("REVIEW_FINDINGS", "review", "--finding", "REV-1"),
        )
        self.assertEqual(0, self.transition("REMEDIATING", "remediate"))
        self.assertEqual(0, self.transition("READY_FOR_VERIFY", "remediate"))
        self.assertEqual(1, self.transition("BUILDING", "build"))
        self.assertIn("returns to REMEDIATING", self.stderr)
        self.assertEqual(0, self.transition("REMEDIATING", "remediate"))
        state = self.parsed()
        self.assertEqual(1, state["review_budget.broad_used"])
        self.assertEqual(["REV-1"], state["findings.open"])

    def test_round_one_remediation_requires_the_reviewed_candidate(self) -> None:
        self.prepare_verified()
        self.assertEqual(
            0,
            self.transition("REVIEW_FINDINGS", "review", "--finding", "REV-1"),
        )
        text = self.state.read_text(encoding="utf-8")
        self.state.write_text(
            text.replace("kind: commit", "kind: unset"), encoding="utf-8"
        )
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(1, self.run_gate("check", "remediate"))
        self.assertIn("exact candidate is unset", self.stderr)
        self.assertEqual(1, self.transition("REMEDIATING", "remediate"))
        self.assertIn("exact candidate is unset", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_close_and_targeted_confirmation_are_finite(self) -> None:
        self.prepare_ready_for_closure()
        self.assertEqual(0, self.run_gate("check", "close"))
        self.assertEqual(
            0,
            self.transition(
                "TARGETED_FIX", "close", "--finding", "CLOSE-1"
            ),
        )
        state = self.parsed()
        self.assertEqual(1, state["review_budget.closure_used"])
        self.assertEqual(["CLOSE-1"], state["findings.open"])
        self.assertEqual(["REV-1", "REV-2"], state["findings.closed"])

        self.assertEqual(0, self.run_gate("check", "remediate"))
        self.assertEqual(0, self.transition("TARGETED_FIX", "remediate"))
        self.assertEqual(
            0,
            self.transition("READY_FOR_TARGETED_CONFIRMATION", "remediate"),
        )
        self.record_commit_candidate()
        self.assertEqual(0, self.run_gate("check", "verify"))
        self.assertEqual(1, self.transition("TARGETED_FIX", "remediate"))
        self.assertIn("illegal transition", self.stderr)
        self.assertEqual(0, self.transition("CLOSED", "verify"))
        state = self.parsed()
        self.assertEqual([], state["findings.open"])
        self.assertEqual(["REV-1", "REV-2", "CLOSE-1"], state["findings.closed"])
        self.assertEqual(1, state["review_budget.broad_used"])
        self.assertEqual(1, state["review_budget.closure_used"])

    def test_closure_can_keep_an_incomplete_round_one_finding_open(self) -> None:
        self.prepare_ready_for_closure()
        self.assertEqual(
            0,
            self.transition(
                "TARGETED_FIX",
                "close",
                "--finding",
                "REV-1",
                "--finding",
                "CLOSE-1",
            ),
        )
        state = self.parsed()
        self.assertEqual(["REV-1", "CLOSE-1"], state["findings.open"])
        self.assertEqual(["REV-2"], state["findings.closed"])

    def test_blocked_closure_preserves_findings_and_budget(self) -> None:
        self.prepare_ready_for_closure()
        self.assertEqual(
            0,
            self.transition(
                "BLOCKED", "close", "--reason", "required evidence unavailable"
            ),
        )
        state = self.parsed()
        self.assertEqual(["REV-1", "REV-2"], state["findings.open"])
        self.assertEqual([], state["findings.closed"])
        self.assertEqual(0, state["review_budget.closure_used"])
        self.assertEqual("READY_FOR_CLOSURE", state["decision.resume_status"])

    def test_terminal_closure_outcome_requires_finding_ids(self) -> None:
        self.prepare_ready_for_closure()
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(1, self.transition("REPLAN", "close"))
        self.assertIn("requires one or more --finding IDs", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))

    def test_nonempty_inline_lists_parse_structurally(self) -> None:
        text = self.state.read_text(encoding="utf-8").replace(
            "dirty_paths: []", 'dirty_paths: ["one.py", "two.py"]'
        )
        state = self.gate.parse_state(text)
        self.assertEqual(["one.py", "two.py"], state["candidate.dirty_paths"])

    def test_previous_schema_one_template_remains_readable_and_mutable(self) -> None:
        previous = self.state.read_text(encoding="utf-8").replace(
            "  resume_status: null\n", ""
        )
        self.state.write_text(previous, encoding="utf-8")
        state = self.gate.load(self.state)[1]
        self.assertIsNone(state.get("decision.resume_status"))

        self.assertEqual(0, self.transition("PLANNED", "plan"))
        state = self.parsed()
        self.assertIsNone(state["decision.resume_status"])
        self.assertIn("  resume_status: null", self.state.read_text(encoding="utf-8"))

    def test_yaml_block_list_is_rejected_with_canonical_guidance(self) -> None:
        with self.state.open("a", encoding="utf-8") as handle:
            handle.write("\n- REV-1\n")
        self.assertEqual(1, self.run_gate("show"))
        self.assertIn("JSON-style inline list", self.stderr)

    def test_duplicate_and_misindented_fields_are_rejected(self) -> None:
        original = self.state.read_text(encoding="utf-8")
        cases = {
            "top-level": original.replace("lane: standard", "lane: standard\nlane: fast"),
            "nested": original.replace(
                "  source: user", "  source: user\n  source: system"
            ),
            "indentation": original.replace("  source: user", "    source: user"),
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(self.gate.GateError):
                    self.gate.parse_state(text)

    def test_edited_budget_maximum_is_rejected(self) -> None:
        text = self.state.read_text(encoding="utf-8")
        self.state.write_text(text.replace("broad_max: 1", "broad_max: 2"), encoding="utf-8")
        self.assertEqual(1, self.run_gate("show"))
        self.assertIn("must remain 1", self.stderr)

    def test_worktree_candidate_detects_tracked_and_untracked_drift(self) -> None:
        repository = self.tmp / "repository"
        repository.mkdir()
        subprocess.run(["git", "init", "-q", str(repository)], check=True)
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.email", "eval@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.name", "Eval"], check=True
        )
        tracked = repository / "tracked.txt"
        tracked.write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repository), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(repository), "commit", "-qm", "base"], check=True)

        state_path = repository / ".converge/state.yaml"
        state_path.parent.mkdir()
        shutil.copy(PLUGIN / "skills/_shared/templates/state.yaml", state_path)
        self.gate.set_status(state_path, "PLANNED", "plan", cwd=repository)
        self.gate.set_status(state_path, "BUILDING", "build", cwd=repository)
        self.gate.set_status(state_path, "READY_FOR_VERIFY", "build", cwd=repository)
        tracked.write_text("candidate\n", encoding="utf-8")
        (repository / "untracked.txt").write_text("new\n", encoding="utf-8")
        self.gate.capture_worktree(state_path, repository)
        state = self.gate.load(state_path)[1]
        self.assertEqual(["tracked.txt", "untracked.txt"], state["candidate.dirty_paths"])
        self.gate.check_candidate(state_path, cwd=repository)
        first_state = state_path.read_text(encoding="utf-8")
        self.gate.capture_worktree(state_path, repository)
        self.assertEqual(first_state, state_path.read_text(encoding="utf-8"))

        tracked.write_text("drifted\n", encoding="utf-8")
        with self.assertRaisesRegex(self.gate.GateError, "candidate drifted"):
            self.gate.check_candidate(state_path, cwd=repository)
        with self.assertRaisesRegex(self.gate.GateError, "candidate drifted"):
            self.gate.capture_worktree(state_path, repository)
        self.assertEqual(first_state, state_path.read_text(encoding="utf-8"))

        self.gate.set_status(state_path, "BUILDING", "build", cwd=repository)
        self.gate.set_status(state_path, "READY_FOR_VERIFY", "build", cwd=repository)
        (repository / "untracked.txt").unlink()
        tracked.write_text("staged\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(repository), "add", "tracked.txt"], check=True
        )
        tracked.write_text("base\n", encoding="utf-8")
        self.gate.capture_worktree(state_path, repository)
        state = self.gate.load(state_path)[1]
        self.assertEqual(["tracked.txt"], state["candidate.dirty_paths"])
        self.gate.check_candidate(state_path, cwd=repository)

        subprocess.run(
            ["git", "-C", str(repository), "reset", "-q", "HEAD", "--", "tracked.txt"],
            check=True,
        )
        with self.assertRaisesRegex(self.gate.GateError, "candidate drifted"):
            self.gate.check_candidate(state_path, cwd=repository)

    def test_recorded_pull_request_head_can_be_compared(self) -> None:
        self.prepare_ready_for_verify()
        self.assertEqual(
            0,
            self.run_gate(
                "candidate",
                "record",
                "--kind",
                "pull_request",
                "--repository",
                "example/repository",
                "--base-sha",
                BASE_SHA,
                "--head-sha",
                HEAD_SHA,
                "--pull-request",
                "42",
            ),
        )
        self.assertEqual(
            0, self.run_gate("candidate", "check", "--current-head", HEAD_SHA)
        )
        self.assertEqual(
            0,
            self.run_gate(
                "candidate",
                "record",
                "--kind",
                "pull_request",
                "--repository",
                "example/repository",
                "--base-sha",
                BASE_SHA,
                "--head-sha",
                HEAD_SHA,
                "--pull-request",
                "42",
            ),
        )
        before = self.state.read_text(encoding="utf-8")
        self.assertEqual(
            1,
            self.run_gate(
                "candidate",
                "record",
                "--kind",
                "pull_request",
                "--repository",
                "example/repository",
                "--base-sha",
                BASE_SHA,
                "--head-sha",
                "c" * 40,
                "--pull-request",
                "42",
            ),
        )
        self.assertIn("cannot be replaced", self.stderr)
        self.assertEqual(before, self.state.read_text(encoding="utf-8"))
        self.assertEqual(
            1, self.run_gate("candidate", "check", "--current-head", "c" * 40)
        )
        self.assertIn("candidate head drifted", self.stderr)

    def test_recorded_candidate_requires_full_object_ids(self) -> None:
        self.prepare_ready_for_verify()
        self.assertEqual(
            1,
            self.run_gate(
                "candidate",
                "record",
                "--kind",
                "commit",
                "--repository",
                "example/repository",
                "--base-sha",
                "a" * 7,
                "--head-sha",
                HEAD_SHA,
            ),
        )
        self.assertIn("full 40- or 64-character", self.stderr)

    def test_missing_state_file_is_reported(self) -> None:
        self.state.unlink()
        self.assertEqual(1, self.run_gate("check", "build"))
        self.assertIn("does not exist", self.stderr)

    def test_orphan_nested_line_is_rejected(self) -> None:
        text = self.state.read_text(encoding="utf-8")
        self.state.write_text(
            text.replace("status: PLANNING", "status: PLANNING\n  stray: 1"),
            encoding="utf-8",
        )
        self.assertEqual(1, self.run_gate("show"))

    def test_unsupported_third_level_nesting_is_rejected(self) -> None:
        text = self.state.read_text(encoding="utf-8")
        self.state.write_text(
            text.replace(
                "review_budget:\n  broad_max: 1",
                "review_budget:\n  broad:\n    max: 1",
            ),
            encoding="utf-8",
        )
        self.assertEqual(1, self.run_gate("show"))

    def test_terminal_state_cannot_transition(self) -> None:
        self.prepare_verified()
        self.assertEqual(0, self.transition("CLOSED", "review"))
        self.assertEqual(1, self.transition("PLANNED", "plan"))
        self.assertIn("allowed: none", self.stderr)


class EvalGraderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grader = load_module(ROOT / "evals/grade_review.py", "converge_eval_grader")
        self.tmp = Path(tempfile.mkdtemp(prefix="converge-eval-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_grader_checks_artifact_and_exact_state(self) -> None:
        fixture = self.tmp / "fixture"
        fixture.mkdir()
        (fixture / "expected.json").write_text(
            json.dumps(
                {
                    "families": [
                        {
                            "id": "example",
                            "description": "example family",
                            "required_markers": ["marker"],
                            "required_any_markers": ["replan", "split"],
                        }
                    ],
                    "state_expectations": {
                        "status": {"one_of": ["PLANNING", "PLANNED"]},
                        "findings.open": [],
                    },
                }
            ),
            encoding="utf-8",
        )
        artifact = self.tmp / "findings.md"
        artifact.write_text("marker split\n", encoding="utf-8")
        state = self.tmp / "state.yaml"
        shutil.copy(PLUGIN / "skills/_shared/templates/state.yaml", state)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, self.grader.grade(fixture, artifact, state))

        expected = json.loads((fixture / "expected.json").read_text(encoding="utf-8"))
        expected["state_expectations"]["status"] = {"one_of": ["CLOSED"]}
        (fixture / "expected.json").write_text(json.dumps(expected), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, self.grader.grade(fixture, artifact, state))


if __name__ == "__main__":
    unittest.main()
