#!/usr/bin/env python3
"""Grade a Converge review or closure run against a fixture's expected families.

Usage:

    python3 evals/grade_review.py evals/fixtures/review-standard <findings.md> --state <state.yaml>
    python3 evals/grade_review.py evals/fixtures/close-delta <closure.md> --state <state.yaml>

Checks that the produced artifact is batch-complete (every expected root-cause
family is reported) and family-complete (every required sibling path or
classification marker for a family appears). A family may also require at least
one of several alternative markers. Markers are case-insensitive substring
checks: passing is necessary, not sufficient — read the artifact before
trusting a PASS.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_state(path: Path) -> dict[str, object]:
    gate_path = ROOT / "plugins/converge/scripts/state_gate.py"
    spec = importlib.util.spec_from_file_location("converge_eval_state_gate", gate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load state gate from {gate_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _, state = module.load(path)
    return state


def grade(
    fixture: Path, findings_path: Path, state_path: Path | None = None
) -> int:
    expected_path = fixture / "expected.json"
    if not expected_path.is_file():
        print(f"ERROR: {expected_path} not found", file=sys.stderr)
        return 2
    if not findings_path.is_file():
        print(f"ERROR: {findings_path} not found", file=sys.stderr)
        return 2

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    findings = findings_path.read_text(encoding="utf-8").lower()

    all_pass = True
    print(f"Scenario: {expected.get('scenario', fixture.name)}\n")
    for family in expected["families"]:
        missing = [
            marker
            for marker in family.get("required_markers", [])
            if marker.lower() not in findings
        ]
        required_any = family.get("required_any_markers", [])
        missing_any = bool(required_any) and not any(
            marker.lower() in findings for marker in required_any
        )
        ok = not missing and not missing_any
        all_pass = all_pass and ok
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] {family['id']}")
        print(f"       {family['description']}")
        if missing:
            print(f"       missing markers: {', '.join(missing)}")
        if missing_any:
            print(f"       missing one of markers: {', '.join(required_any)}")
        print()

    state_expectations = expected.get("state_expectations", {})
    if state_expectations:
        if state_path is None:
            print("[FAIL] workflow-state — --state is required by this fixture\n")
            all_pass = False
        elif not state_path.is_file():
            print(f"[FAIL] workflow-state — {state_path} not found\n")
            all_pass = False
        else:
            try:
                state = _load_state(state_path)
            except Exception as exc:  # the grader must report malformed state cleanly
                print(f"[FAIL] workflow-state — cannot load state: {exc}\n")
                all_pass = False
            else:
                for key, wanted in state_expectations.items():
                    actual = state.get(key)
                    if isinstance(wanted, dict) and "one_of" in wanted:
                        ok = actual in wanted["one_of"]
                    else:
                        ok = actual == wanted
                    all_pass = all_pass and ok
                    label = "PASS" if ok else "FAIL"
                    print(f"[{label}] state {key}")
                    if not ok:
                        print(f"       expected {wanted!r}; found {actual!r}")
                    print()

    if all_pass:
        print("RESULT: PASS — artifact markers and workflow state match the fixture.")
        print("Markers are substrings; confirm the artifact is substantively correct.")
        return 0
    print("RESULT: FAIL — the artifact or finite workflow state is incomplete.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="fixture directory containing expected.json")
    parser.add_argument("findings", type=Path, help="path to the produced findings.md")
    parser.add_argument("--state", type=Path, default=None, help="path to the produced state.yaml")
    args = parser.parse_args()
    return grade(args.fixture, args.findings, args.state)


if __name__ == "__main__":
    raise SystemExit(main())
