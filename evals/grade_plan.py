#!/usr/bin/env python3
"""Grade a Converge Plan run against structural brief and state expectations.

Usage:

    python3 evals/grade_plan.py evals/fixtures/plan-standard <brief.md> --state <state.yaml>

This is a protocol check: required headings and forbidden Critical ceremony.
It does not prove that Plan found real missing paths.
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
    spec = importlib.util.spec_from_file_location("converge_eval_plan_gate", gate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load state gate from {gate_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _, state = module.load(path)
    return state


def grade(fixture: Path, brief_path: Path, state_path: Path | None = None) -> int:
    expected_path = fixture / "expected.json"
    if not expected_path.is_file():
        print(f"ERROR: {expected_path} not found", file=sys.stderr)
        return 2
    if not brief_path.is_file():
        print(f"ERROR: {brief_path} not found", file=sys.stderr)
        return 2

    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    brief = brief_path.read_text(encoding="utf-8")
    lowered = brief.lower()
    all_pass = True
    print(f"Scenario: {expected.get('scenario', fixture.name)}\n")

    for heading in expected.get("required_headings", []):
        ok = heading.lower() in lowered
        all_pass = all_pass and ok
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] heading {heading}")

    for phrase in expected.get("required_phrases", []):
        ok = phrase.lower() in lowered
        all_pass = all_pass and ok
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] required {phrase}")

    required_any = expected.get("required_any_phrases", [])
    if required_any:
        ok = any(phrase.lower() in lowered for phrase in required_any)
        all_pass = all_pass and ok
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] one of {', '.join(required_any)}")

    for phrase in expected.get("forbidden_phrases", []):
        leaked = phrase.lower() in lowered
        all_pass = all_pass and not leaked
        label = "FAIL" if leaked else "PASS"
        print(f"[{label}] forbidden {phrase}")

    state_expectations = expected.get("state_expectations", {})
    if state_expectations:
        if state_path is None:
            print("[FAIL] workflow-state — --state is required by this fixture\n")
            return 1
        state = _load_state(state_path)
        for key, wanted in state_expectations.items():
            got = state.get(key)
            if isinstance(wanted, dict) and "one_of" in wanted:
                ok = got in wanted["one_of"]
            else:
                ok = got == wanted
            all_pass = all_pass and ok
            label = "PASS" if ok else "FAIL"
            print(f"[{label}] state {key}={got!r} expected {wanted!r}")

    print()
    print("PASS" if all_pass else "FAIL")
    print("Protocol check only. Not evidence that Plan found missing paths.")
    return 0 if all_pass else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--state", type=Path, default=None)
    args = parser.parse_args(argv)
    return grade(args.fixture, args.brief, args.state)


if __name__ == "__main__":
    raise SystemExit(main())
