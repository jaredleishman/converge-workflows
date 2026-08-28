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


def squash(text: str) -> str:
    return " ".join(text.split())


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
            ROOT / ".cursor-plugin/marketplace.json",
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
            PLUGIN / ".cursor-plugin/plugin.json",
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
        self.assertIn("predecessor: null", state)
        self.assertNotIn("replan_required", state)
        policy = (PLUGIN / "skills/_shared/review-policy.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Do not begin a third broad review automatically", policy)
        findings = (PLUGIN / "skills/_shared/templates/findings.md").read_text(
            encoding="utf-8"
        )
        closure = (PLUGIN / "skills/_shared/templates/closure.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Outcome, budget, and finding IDs live in `state.yaml`", findings)
        self.assertIn("Outcome, budget, and finding IDs live in `state.yaml`", closure)
        self.assertNotIn("CLEAN", findings)

    def test_standard_and_fast_lanes_have_complexity_budgets(self) -> None:
        lanes = squash(
            (PLUGIN / "skills/_shared/lanes.md").read_text(encoding="utf-8")
        )
        self.assertIn("Important invariants: at most 4", lanes)
        self.assertIn("Acceptance criteria: at most 6", lanes)
        self.assertIn("at most two important invariants", lanes)
        self.assertRegex(lanes, r"three acceptance\s+criteria")

    def test_compound_boundary_screen_contract_is_packaged(self) -> None:
        lanes = squash(
            (PLUGIN / "skills/_shared/lanes.md").read_text(encoding="utf-8")
        )
        for phrase in [
            "three or more boundary types",
            "persistent-data, external-effect, or physical-resource consequence",
            "deadline plus external HTTP plus persistent identity plus detached work",
            "locally contained to a bounded, reversible unit",
            "independent recovery without manual reconciliation",
            "Names evidence that would falsify the exception",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lanes)
        self.assertIn(
            "does not make one ordinary transaction, queue, or external call Critical",
            lanes,
        )

    def test_conditional_matrix_lives_in_the_critical_addendum(
        self,
    ) -> None:
        brief = (PLUGIN / "skills/_shared/templates/brief.md").read_text(
            encoding="utf-8"
        )
        addendum = (PLUGIN / "skills/_shared/templates/brief-critical.md").read_text(
            encoding="utf-8"
        )
        plan = (PLUGIN / "skills/plan/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("Conditional lifecycle and ownership matrix", brief)
        self.assertIn("Conditional lifecycle and ownership matrix", addendum)
        self.assertIn("Fast skips Challenge", plan)
        self.assertIn("Do not implement", plan)
        flattened_addendum = squash(addendum)
        for column in [
            "Event or failure path",
            "Control context and handoff",
            "Election or visibility effect",
            "Persistence owner and timing",
            "Resource owner and release",
            "Durable state",
            "Identity, collision, and deduplication",
            "Transaction or effect commit",
            "Retry, cleanup, and next attempt",
            "Failure evidence",
        ]:
            with self.subTest(column=column):
                self.assertIn(column, flattened_addendum)

        for fixture in sorted((ROOT / "evals/fixtures").glob("*/converge/brief.md")):
            with self.subTest(fixture=fixture):
                text = fixture.read_text(encoding="utf-8")
                self.assertIn("Lane: `standard`", text)
                self.assertNotIn("lifecycle and ownership matrix", text.lower())
                self.assertNotIn("critical proof obligations", text.lower())

    def test_standalone_planning_execution_contract_is_packaged(self) -> None:
        scope = squash(
            (PLUGIN / "skills/_shared/scope-policy.md").read_text(
                encoding="utf-8"
            )
        )
        checks = squash(
            (PLUGIN / "skills/_shared/candidate-checks.md").read_text(
                encoding="utf-8"
            )
        )
        workflow = squash(
            (PLUGIN / "skills/_shared/workflow.md").read_text(encoding="utf-8")
        )
        plan = squash(
            (PLUGIN / "skills/plan/SKILL.md").read_text(encoding="utf-8")
        )
        brief = squash(
            (PLUGIN / "skills/_shared/templates/brief.md").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn("Causal grounding completion", scope)
        self.assertIn("Fast work never requires this branch", scope)
        self.assertIn("Planned-mechanism drift", checks)
        self.assertIn("run the gate's `init` command", workflow)
        self.assertIn("Fast skips Challenge", plan)
        self.assertLess(
            plan.index("After Map, apply the conditional structural-alternatives rule"),
            plan.index("Select or synthesize the mechanism after Challenge"),
        )
        self.assertIn("Causal grounding trace (Standard and Critical)", brief)
        self.assertIn("Challenge skipped (Fast)", brief)

    def test_proof_fidelity_contract_is_packaged(self) -> None:
        checks = squash(
            (PLUGIN / "skills/_shared/candidate-checks.md").read_text(
                encoding="utf-8"
            )
        )
        verify = squash(
            (PLUGIN / "skills/verify/SKILL.md").read_text(encoding="utf-8")
        )
        for phrase in [
            "BOUNDARY_DIRECT",
            "BOUNDARY_FAITHFUL",
            "PROXY",
            "UNAVAILABLE",
            "proxy-only evidence is `UNPROVEN`",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, checks)
        self.assertIn("controlled clock or fake endpoint", verify)
        self.assertIn("candidate-checks.md", verify)

    def test_mechanism_drift_routes_are_packaged(self) -> None:
        paths = [
            PLUGIN / "skills/build/SKILL.md",
            PLUGIN / "skills/remediate/SKILL.md",
            PLUGIN / "skills/verify/SKILL.md",
        ]
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("planned-mechanism drift checkpoint", text)
                self.assertIn("REPLAN", text)
                self.assertIn("SPLIT", text)
        remediate = paths[1].read_text(encoding="utf-8")
        self.assertIn("A new asynchronous mechanism", remediate)

    def test_critical_review_lens_contract_is_packaged(self) -> None:
        policy = squash(
            (PLUGIN / "skills/_shared/review-policy.md").read_text(
                encoding="utf-8"
            )
        )
        findings = (PLUGIN / "skills/_shared/templates/findings.md").read_text(
            encoding="utf-8"
        )
        for phrase in [
            "Timing, cancellation, late completion, and physical-resource ownership",
            "Persistent identity, collision/deduplication, transactions",
            "State lifecycle, recovery, promotion, and test realism",
            "Every reviewer reads the sealed contract",
            "The root workflow",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, policy)
        self.assertIn("Critical reviewer audit", findings)
        self.assertIn("Candidate identity match", findings)
        self.assertIn("Full-candidate cross-lens sweep", findings)
        self.assertIn("one broad-review budget", policy)

    def test_critical_scenario_contract_is_semantic_bounded_and_blinded(self) -> None:
        scenario_text = (ROOT / "evals/scenarios/critical.md").read_text(
            encoding="utf-8"
        )
        scenario = squash(scenario_text)
        readme = squash((ROOT / "evals/README.md").read_text(encoding="utf-8"))
        for phrase in [
            "PR #1847",
            "2cfee7b7435e1bd04a322b06a79ed529ef09b0e5",
            "123f9da9024825520d075fcf20f1893fef6b6bb2",
            "4ae5834d076131a97502986643aff84a28b41646",
            "39fc03103f578c28533849923eebfe93c5811496",
            "HINDSIGHT_LIMITED",
            "Use semantic adjudication; do not grade substrings",
            "Required proof-fidelity probe",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, scenario)
        visible = scenario_text.split("## Frozen runner input", 1)[1].split(
            "## Replay procedure", 1
        )[0]
        visible_flat = squash(visible)
        for forbidden in [
            "pebbleferry",
            "PR #1847",
            "2cfee7b7435e1bd04a322b06a79ed529ef09b0e5",
            "123f9da9024825520d075fcf20f1893fef6b6bb2",
            "4ae5834d076131a97502986643aff84a28b41646",
            "39fc03103f578c28533849923eebfe93c5811496",
            "Normalized opening intent",
        ]:
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, visible_flat)
        for required in [
            "content-only export",
            "no Git metadata",
            "disable network",
            "Do not reveal repository or PR identity",
        ]:
            with self.subTest(required=required):
                self.assertIn(required, visible_flat)
        self.assertIn("Keep the claims separate", readme)
        self.assertIn("Keyword or substring matches are never efficacy evidence", readme)
        self.assertIn("static checks are `PROXY` evidence for agent behavior", readme)

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
        (self.state.parent / "brief.md").write_text(
            "# Change Brief\n\n## Outcome\n\nfixture\n", encoding="utf-8"
        )
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

    def write_findings(self) -> None:
        (self.state.parent / "findings.md").write_text(
            "# Review Findings\n\n## Blocking findings\n", encoding="utf-8"
        )

    def write_closure(self) -> None:
        (self.state.parent / "closure.md").write_text(
            "# Closure Review\n\n## Follow-up work\n", encoding="utf-8"
        )

    def prepare_verified(self) -> None:
        self.prepare_ready_for_verify()
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("INTERNALLY_VERIFIED", "verify"))
        self.write_findings()

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
        self.write_closure()

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

    def test_replan_and_split_preserve_budgets_from_owned_stages(self) -> None:
        def fresh_state(label: str) -> Path:
            path = self.tmp / f"{label}.yaml"
            shutil.copy(PLUGIN / "skills/_shared/templates/state.yaml", path)
            return path

        def advance(path: Path, status: str) -> None:
            self.gate.set_status(path, "PLANNED", "plan")
            self.gate.set_status(path, "BUILDING", "build")
            if status == "BUILDING":
                return
            self.gate.set_status(path, "READY_FOR_VERIFY", "build")
            if status == "READY_FOR_VERIFY_INITIAL":
                return
            self.gate.record_candidate(
                path,
                kind="commit",
                repository="example/repository",
                base_sha=BASE_SHA,
                head_sha=HEAD_SHA,
            )
            self.gate.set_status(path, "INTERNALLY_VERIFIED", "verify")
            (path.parent / "findings.md").write_text(
                "# Review Findings\n", encoding="utf-8"
            )
            self.gate.set_status(
                path,
                "REVIEW_FINDINGS",
                "review",
                findings=["REV-1"],
            )
            self.gate.set_status(path, "REMEDIATING", "remediate")
            if status == "REMEDIATING":
                return
            self.gate.set_status(path, "READY_FOR_VERIFY", "remediate")

        owner_stage = {
            "BUILDING": "build",
            "READY_FOR_VERIFY_INITIAL": "verify",
            "REMEDIATING": "remediate",
            "READY_FOR_VERIFY_REMEDIATION": "verify",
        }
        for current in owner_stage:
            for destination in ["REPLAN", "SPLIT"]:
                with self.subTest(current=current, destination=destination):
                    path = fresh_state(f"{current}-{destination}")
                    advance(path, current)
                    before = self.gate.load(path)[1]
                    self.gate.set_status(
                        path,
                        destination,
                        owner_stage[current],
                    )
                    after = self.gate.load(path)[1]
                    self.assertEqual(
                        before["review_budget.broad_used"],
                        after["review_budget.broad_used"],
                    )
                    self.assertEqual(
                        before["review_budget.closure_used"],
                        after["review_budget.closure_used"],
                    )
                    self.assertEqual(destination, after["status"])

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
                "  blocked_reason: null",
                "  blocked_reason: null\n  blocked_reason: missing",
            ),
            "indentation": original.replace(
                "  blocked_reason: null", "    blocked_reason: null"
            ),
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
        (state_path.parent / "brief.md").write_text(
            "# Change Brief\n\n## Outcome\n\nworktree\n", encoding="utf-8"
        )
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

    def test_review_outcome_requires_findings_file(self) -> None:
        self.prepare_ready_for_verify()
        self.record_commit_candidate()
        self.assertEqual(0, self.transition("INTERNALLY_VERIFIED", "verify"))
        self.assertEqual(1, self.transition("CLOSED", "review"))
        self.assertIn("findings.md must exist", self.stderr)

    def test_init_archives_terminal_contract(self) -> None:
        self.prepare_verified()
        self.assertEqual(0, self.transition("CLOSED", "review"))
        self.assertEqual(0, self.run_gate("init", "--lane", "fast"))
        self.assertIn("archived CLOSED", self.stdout)
        state = self.parsed()
        self.assertEqual("PLANNING", state["status"])
        self.assertEqual("fast", state["lane"])
        self.assertTrue(str(state["predecessor"]).startswith("archive/"))
        archived = self.state.parent / str(state["predecessor"])
        self.assertTrue((archived / "state.yaml").is_file())
        self.assertTrue((archived / "findings.md").is_file())
        self.assertEqual(0, self.run_gate("init", "--lane", "standard"))
        self.assertIn("reused PLANNING", self.stdout)
        self.assertEqual("standard", self.parsed()["lane"])

    def test_init_refuses_a_live_contract(self) -> None:
        self.assertEqual(0, self.transition("PLANNED", "plan"))
        self.assertEqual(1, self.run_gate("init"))
        self.assertIn("cannot init while status is PLANNED", self.stderr)


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
