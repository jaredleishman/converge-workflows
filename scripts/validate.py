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


def flattened(text: str) -> str:
    return " ".join(text.lower().split())


def markdown_section(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        fail(f"cannot find Markdown section boundary: {start!r} .. {end!r}")
    return text.split(start, 1)[1].split(end, 1)[0]


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

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    version_lines = re.findall(r"(?m)^Current version: `([^`]+)`$", readme)
    if version_lines != [version]:
        fail("README.md Current version does not match VERSION")

    required_json = [
        ROOT / ".agents/plugins/marketplace.json",
        ROOT / ".claude-plugin/marketplace.json",
        ROOT / ".grok-plugin/marketplace.json",
        ROOT / ".kimi-plugin/marketplace.json",
        PLUGIN / ".claude-plugin/plugin.json",
        PLUGIN / ".codex-plugin/plugin.json",
        PLUGIN / ".grok-plugin/plugin.json",
        PLUGIN / ".kimi-plugin/plugin.json",
    ]
    documents = {path: load_json(path) for path in required_json}

    for path in required_json[4:]:
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

    kimi_market = documents[ROOT / ".kimi-plugin/marketplace.json"]
    kimi_entries = [p for p in kimi_market.get("plugins", []) if p.get("id") == "converge"]
    if len(kimi_entries) != 1:
        fail("Kimi marketplace must contain exactly one converge entry")
    if kimi_entries[0].get("source") != "./plugins/converge":
        fail("Kimi marketplace source must point to ./plugins/converge")

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
    for folder in expected_skills:
        meta = frontmatter(PLUGIN / "skills" / folder / "SKILL.md")
        if meta.get("disable-model-invocation") != "true":
            fail(f"{folder} skill must set disable-model-invocation: true")

    required_shared = [
        "workflow.md", "lanes.md", "scope-policy.md", "review-policy.md",
        "artifact-protocol.md", "candidate-checks.md",
        "templates/brief.md", "templates/brief-critical.md",
        "templates/state.yaml", "templates/findings.md", "templates/closure.md",
    ]
    for rel in required_shared:
        if not (PLUGIN / "skills/_shared" / rel).is_file():
            fail(f"missing shared file: {rel}")

    if not (PLUGIN / "scripts/state_gate.py").is_file():
        fail("missing state gate script: plugins/converge/scripts/state_gate.py")

    review_policy = (PLUGIN / "skills/_shared/review-policy.md").read_text(encoding="utf-8")
    required_policy_text = [
        "one broad", "delta closure", "Do not begin a third broad review automatically",
        "ORIGINAL_MISS", "SCOPE_EXPANSION", "Round 1 candidate",
        "targeted path is finite", "Blocking `NEW_EVIDENCE`",
    ]
    for phrase in required_policy_text:
        if phrase.lower() not in review_policy.lower():
            fail(f"review policy is missing required phrase: {phrase}")

    for phrase in [
        "Timing, cancellation, late completion, and physical-resource ownership",
        "Persistent identity, collision/deduplication, transactions",
        "State lifecycle, recovery, promotion, and test realism",
        "full-candidate sweep",
        "one broad-review budget",
    ]:
        if phrase.lower() not in flattened(review_policy):
            fail(f"review policy is missing Critical review contract: {phrase}")

    state_template = (PLUGIN / "skills/_shared/templates/state.yaml").read_text(encoding="utf-8")
    for line in ["broad_max: 1", "closure_max: 1", "resume_status: null", "predecessor: null"]:
        if line not in state_template:
            fail(f"state template must contain {line}")
    for forbidden in ["replan_required", "split_required"]:
        if forbidden in state_template:
            fail(f"state template still contains dropped field {forbidden}")
    if "\nrequest:" in "\n" + state_template:
        fail("state template still contains dropped field request")

    scope_policy = (PLUGIN / "skills/_shared/scope-policy.md").read_text(encoding="utf-8")
    for phrase in ["Non-waivable baseline guarantees", "Authorization", "data integrity"]:
        if phrase.lower() not in scope_policy.lower():
            fail(f"scope policy is missing required baseline phrase: {phrase}")

    candidate_checks = (PLUGIN / "skills/_shared/candidate-checks.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "BOUNDARY_DIRECT",
        "BOUNDARY_FAITHFUL",
        "proxy-only evidence is `UNPROVEN`",
        "Planned-mechanism drift",
        "Identity namespace, collision, or deduplication rule",
    ]:
        if phrase.lower() not in flattened(candidate_checks):
            fail(f"candidate checks are missing proof/drift contract: {phrase}")

    for phrase in [
        "Causal grounding completion",
        "every materially distinct path",
        "category or file inventory",
        "organizing model",
        "Conditional structural alternatives",
        "Fast work never requires this branch",
        "load-bearing ownership, ordering/commit, identity, or lifecycle decision",
    ]:
        if phrase.lower() not in flattened(scope_policy):
            fail(f"scope policy is missing standalone planning contract: {phrase}")

    if "conditional lifecycle and ownership matrix" not in flattened(scope_policy):
        fail("scope policy is missing the lifecycle matrix contract")

    workflow = (PLUGIN / "skills/_shared/workflow.md").read_text(encoding="utf-8")
    for phrase in [
        "Delegated stage ownership",
        "dispatch-time fingerprint",
        "Inspect the cited source, diff, commands, and evidence directly",
        "The stage owner writes the synthesis and disposition",
        "Do not create a new artifact merely because work was delegated",
        "findings.md # every broad Review, including a clean Review",
        "run the gate's `init` command",
    ]:
        if phrase.lower() not in flattened(workflow):
            fail(f"workflow is missing delegated-ownership contract: {phrase}")

    lanes = (PLUGIN / "skills/_shared/lanes.md").read_text(encoding="utf-8")
    for phrase in [
        "three or more boundary types",
        "falsifiable exception",
        "deadline plus external HTTP plus persistent identity plus detached work",
        "does not make one ordinary transaction, queue, or external call Critical",
        "two independent Challenge passes",
    ]:
        if phrase.lower() not in flattened(lanes):
            fail(f"lane policy is missing compound-boundary contract: {phrase}")

    brief_template = (PLUGIN / "skills/_shared/templates/brief.md").read_text(
        encoding="utf-8"
    )
    brief_critical = (PLUGIN / "skills/_shared/templates/brief-critical.md").read_text(
        encoding="utf-8"
    )
    if "conditional lifecycle and ownership matrix" in flattened(brief_template):
        fail("Standard brief template must not contain the Critical lifecycle matrix")
    if "critical proof obligations" in flattened(brief_template):
        fail("Standard brief template must not contain Critical proof obligations")
    for phrase in [
        "Planned mechanism baseline",
        "A required production boundary cannot be `PASS` on proxy-only evidence",
        "Causal grounding trace (Standard and Critical)",
        "Alternative mechanisms (conditional)",
        "Organizing model",
        "Delegated Plan and Build ownership (conditional)",
        "Build proof units (conditional)",
        "Challenge skipped (Fast)",
    ]:
        if phrase.lower() not in flattened(brief_template):
            fail(f"brief template is missing standalone workflow field: {phrase}")
    for phrase in [
        "Conditional lifecycle and ownership matrix",
        "Critical proof obligations",
        "Election or visibility effect",
        "Persistence owner and timing",
        "Resource owner and release",
        "Identity, collision, and deduplication",
        "Transaction or effect commit",
        "Retry, cleanup, and next attempt",
        "Failure evidence",
        "Independent Challenge passes",
    ]:
        if phrase.lower() not in flattened(brief_critical):
            fail(f"Critical brief addendum is missing contract: {phrase}")

    for fixture in sorted((ROOT / "evals/fixtures").glob("*/converge/brief.md")):
        text = fixture.read_text(encoding="utf-8").lower()
        if "lane: `standard`" not in text:
            fail(f"expected Standard fixture brief: {fixture.relative_to(ROOT)}")
        if "lifecycle and ownership matrix" in text or "critical proof obligations" in text:
            fail(f"Standard fixture carries Critical ceremony: {fixture.relative_to(ROOT)}")

    for skill_name in ["build", "verify", "remediate"]:
        text = (PLUGIN / f"skills/{skill_name}/SKILL.md").read_text(encoding="utf-8")
        for phrase in ["planned-mechanism drift checkpoint", "REPLAN", "SPLIT"]:
            if phrase.lower() not in flattened(text):
                fail(f"{skill_name} skill is missing mechanism-drift route: {phrase}")

    plan_skill = (PLUGIN / "skills/plan/SKILL.md").read_text(encoding="utf-8")
    for phrase in [
        "do not finalize the Planned mechanism baseline yet",
        "After Map, apply the conditional structural-alternatives rule",
        "cosmetic variants do not count",
        "one coherent organizing model",
        "Fast skips Challenge",
        "Do not implement",
        "state_gate.py\" init",
    ]:
        if phrase.lower() not in flattened(plan_skill):
            fail(f"plan skill is missing planning sequence contract: {phrase}")

    build_skill = (PLUGIN / "skills/build/SKILL.md").read_text(encoding="utf-8")
    for phrase in [
        "record the current proof unit prospectively",
        "only then begin the next unit",
        "Proof units are not commits, stacks, releases",
        "does not prove the completed candidate",
    ]:
        if phrase.lower() not in flattened(build_skill):
            fail(f"build skill is missing proof-unit contract: {phrase}")

    verify_skill = (PLUGIN / "skills/verify/SKILL.md").read_text(encoding="utf-8")
    for phrase in [
        "controlled clock or fake endpoint",
        "direct helper call",
        "every required obligation is `PASS`",
    ]:
        if phrase.lower() not in flattened(verify_skill):
            fail(f"verify skill is missing proof-fidelity rule: {phrase}")

    findings_template = (PLUGIN / "skills/_shared/templates/findings.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "Critical reviewer audit",
        "Candidate identity match",
        "Full-candidate cross-lens sweep",
        "Delegated review ownership (conditional)",
        "Synthesis-owner inspection and discrepancies",
        "Outcome, budget, and finding IDs live in `state.yaml`",
    ]:
        if phrase.lower() not in flattened(findings_template):
            fail(f"findings template is missing reviewer audit field: {phrase}")
    if "pending | clean | findings" in flattened(findings_template):
        fail("findings template still duplicates disposition vocabulary")

    critical_scenario = (ROOT / "evals/scenarios/critical.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "PR #1847",
        "2cfee7b7435e1bd04a322b06a79ed529ef09b0e5",
        "4ae5834d076131a97502986643aff84a28b41646",
        "39fc03103f578c28533849923eebfe93c5811496",
        "HINDSIGHT_LIMITED",
        "Use semantic adjudication; do not grade substrings",
        "Required proof-fidelity probe",
    ]:
        if phrase.lower() not in flattened(critical_scenario):
            fail(f"Critical scenario is missing bounded replay evidence: {phrase}")

    visible_replay = markdown_section(
        critical_scenario,
        "## Frozen runner input",
        "## Replay procedure",
    )
    for forbidden in [
        "pebbleferry",
        "PR #1847",
        "2cfee7b7435e1bd04a322b06a79ed529ef09b0e5",
        "123f9da9024825520d075fcf20f1893fef6b6bb2",
        "4ae5834d076131a97502986643aff84a28b41646",
        "39fc03103f578c28533849923eebfe93c5811496",
        "Normalized opening intent",
    ]:
        if forbidden.lower() in visible_replay.lower():
            fail(f"Critical runner input leaks hidden provenance: {forbidden}")
    for phrase in [
        "content-only export",
        "no Git metadata",
        "disable network",
        "Do not reveal repository or PR identity",
    ]:
        if phrase.lower() not in flattened(visible_replay):
            fail(f"Critical runner input is missing blinding control: {phrase}")

    eval_readme = (ROOT / "evals/README.md").read_text(encoding="utf-8")
    for phrase in [
        "content-only export of the pre-change source tree",
        "static checks are `PROXY` evidence for agent behavior",
        "Matched policy behavior probes",
        "Freeze and hash the request",
        "Capture chronology, not only the final answer or artifact",
        "one pair supports only the observed difference",
    ]:
        if phrase.lower() not in flattened(eval_readme):
            fail(f"evaluation guidance is missing proof boundary: {phrase}")

    artifact_protocol = (PLUGIN / "skills/_shared/artifact-protocol.md").read_text(
        encoding="utf-8"
    )
    for phrase in [
        "candidate capture-worktree",
        "write-once",
        "TARGETED_FIX",
        "resume",
        "init",
        "brief.md",
        "findings.md",
        "closure.md",
    ]:
        if phrase not in artifact_protocol:
            fail(f"artifact protocol is missing required gate contract: {phrase}")

    for expected_path in sorted((ROOT / "evals/fixtures").glob("*/expected.json")):
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        fixture = expected_path.parent
        brief_path = fixture / "converge/brief.md"
        src_dir = fixture / "src"
        if not brief_path.is_file() or not src_dir.is_dir():
            continue
        brief = brief_path.read_text(encoding="utf-8")
        src = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(src_dir.glob("*.py"))
        )
        for family in expected.get("families", []):
            for marker in family.get("required_markers", []):
                if marker in src and marker.lower() in brief.lower():
                    fail(
                        f"{brief_path.relative_to(ROOT)} leaks code marker "
                        f"{marker!r} from {expected_path.parent.name}"
                    )

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
