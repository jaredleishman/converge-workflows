#!/usr/bin/env python3
"""Grade a Converge review run against a fixture's expected finding families.

Usage:

    python3 evals/grade_review.py evals/fixtures/review-standard <findings.md>

Checks that the produced findings file is batch-complete (every expected
root-cause family is reported) and family-complete (every required sibling
path marker for a family appears). Markers are case-insensitive substring
checks: passing is necessary, not sufficient — read the findings before
trusting a PASS.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def grade(fixture: Path, findings_path: Path) -> int:
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
        ok = not missing
        all_pass = all_pass and ok
        label = "PASS" if ok else "FAIL"
        print(f"[{label}] {family['id']}")
        print(f"       {family['description']}")
        if missing:
            print(f"       missing markers: {', '.join(missing)}")
        print()

    if all_pass:
        print("RESULT: PASS — batch-complete and family-complete on markers.")
        print("Markers are substrings; confirm the findings are substantively correct.")
        return 0
    print("RESULT: FAIL — the review missed a family or a sibling path.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path, help="fixture directory containing expected.json")
    parser.add_argument("findings", type=Path, help="path to the produced findings.md")
    args = parser.parse_args()
    return grade(args.fixture, args.findings)


if __name__ == "__main__":
    raise SystemExit(main())
