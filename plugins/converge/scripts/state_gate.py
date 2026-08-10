#!/usr/bin/env python3
"""Converge state gate.

Skills invoke this script to check stage preconditions, consume review
budget, and record state transitions in the project's
`.converge/state.yaml`. Budget fields must never be edited by hand; a
refused check is a workflow decision point, not an obstacle to route
around.

Standard library only. Parses the constrained state.yaml schema shipped
in `skills/_shared/templates/state.yaml`; it is not a general YAML
parser.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_STATE = Path(".converge/state.yaml")

STATES = {
    "PLANNING",
    "PLANNED",
    "BUILDING",
    "READY_FOR_VERIFY",
    "INTERNALLY_VERIFIED",
    "REVIEW_FINDINGS",
    "REMEDIATING",
    "READY_FOR_CLOSURE",
    "CLOSED",
    "REPLAN",
    "SPLIT",
    "BLOCKED",
}

NEXT_ACTION = {
    "PLANNING": "plan — finish and seal the Change Brief",
    "PLANNED": "build",
    "BUILDING": "build — implementation in progress",
    "READY_FOR_VERIFY": "verify",
    "INTERNALLY_VERIFIED": "review — the single broad review",
    "REVIEW_FINDINGS": "remediate — fix the complete batch by root-cause family",
    "REMEDIATING": "remediate — remediation in progress",
    "READY_FOR_CLOSURE": "close — the single delta-only closure review",
    "CLOSED": "none — the change is closed",
    "REPLAN": "plan — new contract, new state, new review cycle",
    "SPLIT": "plan — split into independently provable changes",
    "BLOCKED": "resolve the recorded blocker, then rerun the blocked stage",
}

LOOP_BREAKER = (
    "The {name} review budget is exhausted ({used}/{max}). Do not begin "
    "another {name} review on this contract. Apply the loop breaker: return "
    "REPLAN or SPLIT, or have the user explicitly open a new contract with a "
    "new plan and new state. Do not edit budget fields by hand."
)


class GateError(RuntimeError):
    """A refused gate check or invalid state file."""


def parse_state(text: str) -> dict:
    """Parse the constrained two-level state.yaml schema into a flat dict."""
    data: dict[str, object] = {}
    section: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if ":" not in raw:
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, value = raw.strip().partition(":")
        key, value = key.strip(), value.strip()
        if indent == 0:
            if value == "":
                section = key
                continue
            section = None
            data[key] = _coerce(value)
        elif section is not None and value != "":
            data[f"{section}.{key}"] = _coerce(value)
    return data


def _coerce(value: str) -> object:
    if value in {"null", "~"}:
        return None
    if value == "[]":
        return []
    if value in {"true", "false"}:
        return value == "true"
    try:
        return int(value)
    except ValueError:
        return value.strip("'\"")


def load(path: Path) -> tuple[str, dict]:
    if not path.is_file():
        raise GateError(
            f"{path} does not exist. Run plan first; it creates the state "
            "file from the shared template."
        )
    text = path.read_text(encoding="utf-8")
    return text, parse_state(text)


def _budget(state: dict, name: str) -> tuple[int, int]:
    try:
        used = int(state[f"review_budget.{name}_used"])
        maximum = int(state[f"review_budget.{name}_max"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GateError(f"state file is missing a valid {name} budget: {exc}")
    return used, maximum


def check(state: dict, action: str) -> str:
    status = state.get("status")
    if status not in STATES:
        raise GateError(f"state file has unknown status: {status!r}")
    broad_used, broad_max = _budget(state, "broad")
    closure_used, closure_max = _budget(state, "closure")

    def require_status(*allowed: str) -> None:
        if status not in allowed:
            raise GateError(
                f"{action} requires status {' or '.join(allowed)}, but the "
                f"current status is {status}. Next allowed action: "
                f"{NEXT_ACTION[status]}."
            )

    if action == "build":
        require_status("PLANNED")
    elif action == "verify":
        require_status("READY_FOR_VERIFY")
    elif action == "review":
        require_status("INTERNALLY_VERIFIED")
        if broad_used >= broad_max:
            raise GateError(
                LOOP_BREAKER.format(name="broad", used=broad_used, max=broad_max)
            )
    elif action == "remediate":
        require_status("REVIEW_FINDINGS", "REMEDIATING")
        if broad_used < 1:
            raise GateError(
                "remediate requires a completed Round 1 review; broad_used is 0."
            )
    elif action == "close":
        require_status("READY_FOR_CLOSURE")
        if closure_used >= closure_max:
            raise GateError(
                LOOP_BREAKER.format(
                    name="closure", used=closure_used, max=closure_max
                )
            )
    else:
        raise GateError(f"unknown action: {action}")
    return f"OK: {action} may proceed (status {status})."


def consume(path: Path, name: str) -> str:
    text, state = load(path)
    used, maximum = _budget(state, name)
    if used >= maximum:
        raise GateError(LOOP_BREAKER.format(name=name, used=used, max=maximum))
    pattern = rf"(?m)^(\s*){name}_used:\s*{used}\s*$"
    new_text, count = re.subn(pattern, rf"\g<1>{name}_used: {used + 1}", text, count=1)
    if count != 1:
        raise GateError(f"could not update {name}_used in {path}")
    path.write_text(new_text, encoding="utf-8")
    return f"OK: {name}_used is now {used + 1}/{maximum}."


def set_status(path: Path, status: str, stage: str | None) -> str:
    if status not in STATES:
        raise GateError(
            f"unknown status {status!r}; allowed: {', '.join(sorted(STATES))}"
        )
    text, _ = load(path)
    new_text, count = re.subn(r"(?m)^status:\s*\S.*$", f"status: {status}", text, count=1)
    if count != 1:
        raise GateError(f"could not find a top-level status line in {path}")
    if stage is not None:
        new_text, count = re.subn(
            r"(?m)^stage:\s*\S.*$", f"stage: {stage}", new_text, count=1
        )
        if count != 1:
            raise GateError(f"could not find a top-level stage line in {path}")
    path.write_text(new_text, encoding="utf-8")
    suffix = f", stage {stage}" if stage else ""
    return f"OK: status is now {status}{suffix}. Next allowed action: {NEXT_ACTION[status]}."


def show(state: dict) -> str:
    status = state.get("status")
    broad_used, broad_max = _budget(state, "broad")
    closure_used, closure_max = _budget(state, "closure")
    lines = [
        f"lane: {state.get('lane')}",
        f"stage: {state.get('stage')}",
        f"status: {status}",
        f"candidate: {state.get('candidate.kind')}",
        f"broad review budget: {broad_used}/{broad_max}",
        f"closure review budget: {closure_used}/{closure_max}",
        f"next allowed action: {NEXT_ACTION.get(status, 'unknown status')}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--state",
        type=Path,
        default=DEFAULT_STATE,
        help="path to state.yaml (default: .converge/state.yaml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show", help="print state and the next allowed action")
    check_p = sub.add_parser("check", help="verify an action's preconditions")
    check_p.add_argument("action", choices=["build", "verify", "review", "remediate", "close"])
    consume_p = sub.add_parser("consume", help="consume one unit of review budget")
    consume_p.add_argument("budget", choices=["broad", "closure"])
    set_p = sub.add_parser("set-status", help="record a state transition")
    set_p.add_argument("status")
    set_p.add_argument("--stage", default=None)
    args = parser.parse_args(argv)

    try:
        if args.command == "show":
            _, state = load(args.state)
            print(show(state))
        elif args.command == "check":
            _, state = load(args.state)
            print(check(state, args.action))
        elif args.command == "consume":
            print(consume(args.state, args.budget))
        elif args.command == "set-status":
            print(set_status(args.state, args.status, args.stage))
    except GateError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
