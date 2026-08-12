#!/usr/bin/env python3
"""Converge state gate.

Skills invoke this script to check stage preconditions, record legal state
transitions, couple review outcomes to their budget use, and capture or check
exact candidate identity. A refused operation is a workflow decision point,
not an obstacle to route around.

The script uses only the Python standard library. It parses the constrained
state.yaml schema shipped in ``skills/_shared/templates/state.yaml``; it is not
a general YAML parser. Non-empty lists use JSON-style inline YAML, for example
``["REV-1", "REV-2"]``. Unsupported or malformed state fails loudly.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
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
    "TARGETED_FIX",
    "READY_FOR_TARGETED_CONFIRMATION",
    "CLOSED",
    "REPLAN",
    "SPLIT",
    "BLOCKED",
}

TERMINAL_STATES = {"CLOSED", "REPLAN", "SPLIT"}
LANES = {"fast", "standard", "critical"}
STAGES = {"plan", "build", "verify", "review", "remediate", "close"}
CANDIDATE_KINDS = {"unset", "worktree", "commit", "pull_request"}
CANDIDATE_CAPTURE_STATES = {"READY_FOR_VERIFY", "READY_FOR_TARGETED_CONFIRMATION"}

NEXT_ACTION = {
    "PLANNING": "plan — finish and seal the Change Brief",
    "PLANNED": "build",
    "BUILDING": "build — implementation in progress",
    "READY_FOR_VERIFY": "verify",
    "INTERNALLY_VERIFIED": "review — the single broad review",
    "REVIEW_FINDINGS": "remediate — fix the complete batch by root-cause family",
    "REMEDIATING": "remediate — remediation in progress",
    "READY_FOR_CLOSURE": "close — the single delta-only closure review",
    "TARGETED_FIX": "remediate — fix only the closure-scoped issue",
    "READY_FOR_TARGETED_CONFIRMATION": "verify — targeted confirmation only",
    "CLOSED": "none — the change is closed",
    "REPLAN": "plan — create a new contract and state file",
    "SPLIT": "plan — create independently provable contracts",
    "BLOCKED": "resolve the blocker, then run the gate's resume command",
}

TRANSITIONS = {
    "PLANNING": {"PLANNED", "SPLIT", "BLOCKED"},
    "PLANNED": {"BUILDING", "REPLAN", "SPLIT", "BLOCKED"},
    "BUILDING": {"BUILDING", "READY_FOR_VERIFY", "REPLAN", "SPLIT", "BLOCKED"},
    "READY_FOR_VERIFY": {
        "BUILDING",
        "REMEDIATING",
        "INTERNALLY_VERIFIED",
        "READY_FOR_CLOSURE",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "INTERNALLY_VERIFIED": {
        "CLOSED",
        "REVIEW_FINDINGS",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "REVIEW_FINDINGS": {"REMEDIATING", "REPLAN", "SPLIT", "BLOCKED"},
    "REMEDIATING": {
        "REMEDIATING",
        "READY_FOR_VERIFY",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "READY_FOR_CLOSURE": {
        "CLOSED",
        "TARGETED_FIX",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "TARGETED_FIX": {
        "TARGETED_FIX",
        "READY_FOR_TARGETED_CONFIRMATION",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "READY_FOR_TARGETED_CONFIRMATION": {
        "CLOSED",
        "REPLAN",
        "SPLIT",
        "BLOCKED",
    },
    "BLOCKED": {"REPLAN", "SPLIT"},
    "CLOSED": set(),
    "REPLAN": set(),
    "SPLIT": set(),
}

BROAD_OUTCOMES = {"CLOSED", "REVIEW_FINDINGS", "REPLAN", "SPLIT"}
CLOSURE_OUTCOMES = {"CLOSED", "TARGETED_FIX", "REPLAN", "SPLIT"}
FINDING_ID = re.compile(r"^[A-Z][A-Z0-9_-]*-[1-9][0-9]*$")
SHA = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
STATE_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

LOOP_BREAKER = (
    "The {name} review budget is exhausted ({used}/{max}). Do not begin "
    "another {name} review on this contract. Apply the loop breaker: return "
    "REPLAN or SPLIT, or have the user explicitly open a new contract with a "
    "new plan and new state. Do not edit budget fields by hand."
)


class GateError(RuntimeError):
    """A refused gate operation or invalid state file."""


@dataclass(frozen=True)
class WorktreeSnapshot:
    repository: str
    base_sha: str
    patch_sha256: str
    dirty_paths: tuple[str, ...]


def parse_state(text: str) -> dict[str, object]:
    """Parse the constrained two-level state schema into a flat dictionary."""
    data: dict[str, object] = {}
    section: str | None = None
    top_level_names: set[str] = set()
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or raw.lstrip().startswith("#"):
            continue
        if stripped.startswith("- "):
            raise GateError(
                f"state file line {lineno} uses a YAML block list; use a "
                f"JSON-style inline list such as [\"REV-1\"]: {stripped!r}"
            )
        if ":" not in raw:
            raise GateError(
                f"state file line {lineno} is not a 'key: value' pair: "
                f"{stripped!r}"
            )
        indent = len(raw) - len(raw.lstrip())
        key, _, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        if not STATE_KEY.fullmatch(key):
            raise GateError(
                f"state file line {lineno} has an invalid key: {key!r}"
            )
        if indent == 0:
            if key in top_level_names:
                raise GateError(
                    f"state file line {lineno} duplicates top-level key or "
                    f"section {key!r}"
                )
            top_level_names.add(key)
            if value == "":
                section = key
                continue
            section = None
            data[key] = _coerce(value)
        else:
            if indent != 2 or not raw.startswith("  "):
                raise GateError(
                    f"state file line {lineno} must use exactly two spaces "
                    f"for one level of nesting: {stripped!r}"
                )
            if section is None:
                raise GateError(
                    f"state file line {lineno} is nested but follows no "
                    f"section header: {stripped!r}"
                )
            if value == "":
                raise GateError(
                    f"state file line {lineno} opens unsupported nesting: "
                    f"{stripped!r}"
                )
            dotted_key = f"{section}.{key}"
            if dotted_key in data:
                raise GateError(
                    f"state file line {lineno} duplicates field {dotted_key!r}"
                )
            data[dotted_key] = _coerce(value)
    return data


def _coerce(value: str) -> object:
    if value in {"null", "~"}:
        return None
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise GateError(f"invalid JSON-style inline list {value!r}: {exc}") from exc
        if not isinstance(parsed, list):
            raise GateError(f"state value is not a list: {value!r}")
        return parsed
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise GateError(f"invalid quoted state value {value!r}: {exc}") from exc
        if not isinstance(parsed, str):
            raise GateError(f"quoted state value is not text: {value!r}")
        return parsed
    try:
        return int(value)
    except ValueError:
        return value.strip("'")


def load(path: Path) -> tuple[str, dict[str, object]]:
    if not path.is_file():
        raise GateError(
            f"{path} does not exist. Run plan first; it creates the state "
            "file from the shared template."
        )
    text = path.read_text(encoding="utf-8")
    state = parse_state(text)
    validate_state(state)
    return text, state


def validate_state(state: dict[str, object]) -> None:
    if state.get("schema_version") != 1:
        raise GateError(
            f"state file has unsupported schema_version: {state.get('schema_version')!r}"
        )
    if state.get("lane") not in LANES:
        raise GateError(f"state file has unknown lane: {state.get('lane')!r}")
    if state.get("stage") not in STAGES:
        raise GateError(f"state file has unknown stage: {state.get('stage')!r}")
    if state.get("status") not in STATES:
        raise GateError(f"state file has unknown status: {state.get('status')!r}")
    if state.get("candidate.kind") not in CANDIDATE_KINDS:
        raise GateError(
            f"state file has unknown candidate kind: {state.get('candidate.kind')!r}"
        )

    _budget(state, "broad")
    _budget(state, "closure")
    _string_list(state, "candidate.dirty_paths")
    open_findings = _finding_list(state, "findings.open")
    closed_findings = _finding_list(state, "findings.closed")
    overlap = sorted(set(open_findings) & set(closed_findings))
    if overlap:
        raise GateError(
            "finding IDs cannot be both open and closed: " + ", ".join(overlap)
        )

    resume_status = state.get("decision.resume_status")
    if resume_status is not None and resume_status not in STATES - TERMINAL_STATES - {"BLOCKED"}:
        raise GateError(f"state file has invalid resume status: {resume_status!r}")


def _budget(state: dict[str, object], name: str) -> tuple[int, int]:
    try:
        used = int(state[f"review_budget.{name}_used"])
        maximum = int(state[f"review_budget.{name}_max"])
    except (KeyError, TypeError, ValueError) as exc:
        raise GateError(f"state file is missing a valid {name} budget: {exc}") from exc
    if maximum != 1:
        raise GateError(
            f"{name}_max must remain 1 for this contract; found {maximum}. "
            "Do not edit review budgets by hand."
        )
    if used not in {0, 1}:
        raise GateError(f"{name}_used must be 0 or 1; found {used}")
    return used, maximum


def _string_list(state: dict[str, object], key: str) -> list[str]:
    value = state.get(key)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise GateError(f"state file field {key} must be a JSON-style inline text list")
    if len(value) != len(set(value)):
        raise GateError(f"state file field {key} contains duplicate values")
    return list(value)


def _finding_list(state: dict[str, object], key: str) -> list[str]:
    values = _string_list(state, key)
    invalid = [value for value in values if not FINDING_ID.fullmatch(value)]
    if invalid:
        raise GateError(f"state file field {key} has invalid finding IDs: {invalid}")
    return values


def check(
    state: dict[str, object], action: str, cwd: Path | None = None
) -> str:
    status = str(state["status"])
    broad_used, broad_max = _budget(state, "broad")
    closure_used, closure_max = _budget(state, "closure")
    cwd = cwd or Path.cwd()

    def require_status(*allowed: str) -> None:
        if status not in allowed:
            raise GateError(
                f"{action} requires status {' or '.join(allowed)}, but the "
                f"current status is {status}. Next allowed action: "
                f"{NEXT_ACTION[status]}."
            )

    if action == "build":
        require_status("PLANNED", "BUILDING")
    elif action == "verify":
        require_status("READY_FOR_VERIFY", "READY_FOR_TARGETED_CONFIRMATION")
    elif action == "review":
        require_status("INTERNALLY_VERIFIED")
        if broad_used >= broad_max:
            raise GateError(
                LOOP_BREAKER.format(name="broad", used=broad_used, max=broad_max)
            )
        validate_candidate(state, cwd)
    elif action == "remediate":
        require_status("REVIEW_FINDINGS", "REMEDIATING", "TARGETED_FIX")
        open_findings = _finding_list(state, "findings.open")
        if not open_findings:
            raise GateError(f"{status} requires at least one open finding ID")
        if status in {"REVIEW_FINDINGS", "REMEDIATING"} and broad_used != 1:
            raise GateError("Round 1 remediation requires broad_used to be 1.")
        if status == "TARGETED_FIX" and closure_used != 1:
            raise GateError("Targeted closure remediation requires closure_used to be 1.")
        if status == "REVIEW_FINDINGS":
            validate_candidate(state, cwd)
    elif action == "close":
        require_status("READY_FOR_CLOSURE")
        if broad_used != 1:
            raise GateError("close requires a completed Round 1 review.")
        if not _finding_list(state, "findings.open"):
            raise GateError("close requires the open Round 1 finding IDs.")
        if closure_used >= closure_max:
            raise GateError(
                LOOP_BREAKER.format(
                    name="closure", used=closure_used, max=closure_max
                )
            )
        validate_candidate(state, cwd)
    else:
        raise GateError(f"unknown action: {action}")
    return f"OK: {action} may proceed (status {status})."


def set_status(
    path: Path,
    status: str,
    stage: str,
    *,
    reason: str | None = None,
    findings: list[str] | None = None,
    cwd: Path | None = None,
) -> str:
    if status not in STATES:
        raise GateError(
            f"unknown status {status!r}; allowed: {', '.join(sorted(STATES))}"
        )
    if stage not in STAGES:
        raise GateError(
            f"unknown stage {stage!r}; allowed: {', '.join(sorted(STAGES))}"
        )

    text, state = load(path)
    current = str(state["status"])
    cwd = cwd or Path.cwd()
    if status not in TRANSITIONS[current]:
        allowed = ", ".join(sorted(TRANSITIONS[current])) or "none"
        guidance = " Use resume for blocked work." if current == "BLOCKED" else ""
        raise GateError(
            f"illegal transition {current} -> {status}; allowed: {allowed}.{guidance}"
        )
    _validate_transition_stage(state, current, status, stage)

    normalized_findings = _normalize_findings(findings or [])
    if status == "BLOCKED":
        if reason is None or not reason.strip():
            raise GateError("BLOCKED requires --reason with the unresolved condition")
    elif reason is not None:
        raise GateError("--reason is only valid when setting BLOCKED")

    broad_used, broad_max = _budget(state, "broad")
    closure_used, closure_max = _budget(state, "closure")
    budget_used: str | None = None

    if current == "INTERNALLY_VERIFIED" and status in BROAD_OUTCOMES:
        if broad_used >= broad_max:
            raise GateError(
                LOOP_BREAKER.format(name="broad", used=broad_used, max=broad_max)
            )
        validate_candidate(state, cwd)
        broad_used += 1
        budget_used = "broad"
    elif current == "READY_FOR_CLOSURE" and status in CLOSURE_OUTCOMES:
        if closure_used >= closure_max:
            raise GateError(
                LOOP_BREAKER.format(
                    name="closure", used=closure_used, max=closure_max
                )
            )
        validate_candidate(state, cwd)
        closure_used += 1
        budget_used = "closure"
    elif current == "READY_FOR_VERIFY" and status in {
        "INTERNALLY_VERIFIED",
        "READY_FOR_CLOSURE",
    }:
        validate_candidate(state, cwd)
    elif current == "READY_FOR_TARGETED_CONFIRMATION" and status in {
        "CLOSED",
        "REPLAN",
        "SPLIT",
    }:
        validate_candidate(state, cwd)
    elif current == "REVIEW_FINDINGS" and status == "REMEDIATING":
        validate_candidate(state, cwd)

    open_findings = _finding_list(state, "findings.open")
    closed_findings = _finding_list(state, "findings.closed")

    if current == "READY_FOR_VERIFY":
        round_one_remediation = broad_used == 1 and bool(open_findings)
        if status == "INTERNALLY_VERIFIED" and round_one_remediation:
            raise GateError(
                "Round 1 remediation must end READY_FOR_CLOSURE, not "
                "INTERNALLY_VERIFIED"
            )
        if status == "INTERNALLY_VERIFIED" and (broad_used != 0 or open_findings):
            raise GateError(
                "initial Verify requires broad_used 0 and no open findings"
            )
        if status == "BUILDING" and round_one_remediation:
            raise GateError(
                "failed re-verification returns to REMEDIATING, not BUILDING"
            )
        if status == "REMEDIATING" and not round_one_remediation:
            raise GateError(
                "REMEDIATING requires broad_used 1 and open Round 1 findings"
            )

    if current == "INTERNALLY_VERIFIED":
        if status == "REVIEW_FINDINGS":
            if not normalized_findings:
                raise GateError("REVIEW_FINDINGS requires one or more --finding IDs")
            open_findings = normalized_findings
        elif status == "CLOSED":
            if normalized_findings:
                raise GateError("a clean Review outcome cannot include --finding IDs")
            if open_findings:
                raise GateError("a clean Review outcome requires no pre-existing open findings")
        elif status in {"REPLAN", "SPLIT"}:
            if not normalized_findings:
                raise GateError(
                    f"{status} as a Review outcome requires one or more "
                    "--finding IDs"
                )
            open_findings = normalized_findings
        elif normalized_findings:
            raise GateError(
                f"--finding is not valid for transition {current} -> {status}"
            )
    elif current == "READY_FOR_CLOSURE" and status in CLOSURE_OUTCOMES:
        if not open_findings:
            raise GateError("closure requires the open Round 1 finding IDs")
        prior_open = open_findings
        if status == "CLOSED":
            if normalized_findings:
                raise GateError("a clean Close outcome cannot include --finding IDs")
            closed_findings = _ordered_union(closed_findings, prior_open)
            open_findings = []
        else:
            if not normalized_findings:
                raise GateError(
                    f"{status} as a Close outcome requires one or more "
                    "--finding IDs"
                )
            resolved_prior = [
                finding for finding in prior_open if finding not in normalized_findings
            ]
            closed_findings = _ordered_union(closed_findings, resolved_prior)
            open_findings = normalized_findings
    elif current == "READY_FOR_TARGETED_CONFIRMATION":
        if normalized_findings:
            raise GateError("targeted confirmation cannot introduce new finding IDs")
        if status == "CLOSED":
            closed_findings = _ordered_union(closed_findings, open_findings)
            open_findings = []
    elif normalized_findings:
        raise GateError(f"--finding is not valid for transition {current} -> {status}")

    if status == "READY_FOR_CLOSURE":
        if broad_used != 1 or not open_findings:
            raise GateError(
                "READY_FOR_CLOSURE requires broad_used 1 and open Round 1 findings"
            )
    if status == "READY_FOR_TARGETED_CONFIRMATION":
        if closure_used != 1 or not open_findings:
            raise GateError(
                "READY_FOR_TARGETED_CONFIRMATION requires closure_used 1 and an open targeted finding"
            )

    changes: dict[str, object] = {
        "status": status,
        "stage": stage,
        "review_budget.broad_used": broad_used,
        "review_budget.closure_used": closure_used,
        "findings.open": open_findings,
        "findings.closed": closed_findings,
        "decision.replan_required": status == "REPLAN",
        "decision.split_required": status == "SPLIT",
    }
    if status == "BLOCKED":
        changes["decision.blocked_reason"] = reason.strip() if reason else None
        changes["decision.resume_status"] = current
    else:
        changes["decision.blocked_reason"] = None
        changes["decision.resume_status"] = None

    if status in {"BUILDING", "REMEDIATING", "TARGETED_FIX"}:
        changes.update(_empty_candidate())

    new_text = _apply_changes(text, changes)
    _write_state(path, new_text)
    suffix = f" {budget_used} review budget is now 1/1." if budget_used else ""
    return (
        f"OK: {current} -> {status}, stage {stage}.{suffix} "
        f"Next allowed action: {NEXT_ACTION[status]}."
    )


def resume(path: Path) -> str:
    text, state = load(path)
    if state["status"] != "BLOCKED":
        raise GateError(f"resume requires BLOCKED, but current status is {state['status']}")
    target = state.get("decision.resume_status")
    if target not in STATES - TERMINAL_STATES - {"BLOCKED"}:
        raise GateError(
            "BLOCKED state has no valid decision.resume_status. Record a new "
            "contract decision instead of guessing the prior state."
        )
    changes = {
        "status": target,
        "decision.blocked_reason": None,
        "decision.resume_status": None,
    }
    new_text = _apply_changes(text, changes)
    _write_state(path, new_text)
    return f"OK: resumed {target}. Next allowed action: {NEXT_ACTION[str(target)]}."


def capture_worktree(path: Path, cwd: Path | None = None) -> str:
    text, state = load(path)
    _require_candidate_capture_state(state)
    cwd = cwd or Path.cwd()
    if state["candidate.kind"] != "unset":
        if state["candidate.kind"] != "worktree":
            raise GateError(
                "exact candidate is already recorded and cannot be replaced "
                "during Verify. Return to the owning mutation stage when the "
                "workflow permits; otherwise record BLOCKED before replanning "
                "or splitting."
            )
        detail = validate_candidate(state, cwd)
        return f"OK: exact candidate is already recorded ({detail}); identity unchanged."

    snapshot = worktree_snapshot(cwd)
    changes = {
        "candidate.kind": "worktree",
        "candidate.repository": snapshot.repository,
        "candidate.base_sha": snapshot.base_sha,
        "candidate.head_sha": None,
        "candidate.patch_sha256": snapshot.patch_sha256,
        "candidate.dirty_paths": list(snapshot.dirty_paths),
        "candidate.pull_request": None,
    }
    new_text = _apply_changes(text, changes)
    _write_state(path, new_text)
    return (
        f"OK: captured worktree candidate at {snapshot.base_sha[:12]} with "
        f"{len(snapshot.dirty_paths)} dirty path(s), fingerprint "
        f"{snapshot.patch_sha256}."
    )


def record_candidate(
    path: Path,
    *,
    kind: str,
    repository: str,
    base_sha: str,
    head_sha: str,
    pull_request: str | None = None,
) -> str:
    text, state = load(path)
    _require_candidate_capture_state(state)
    if kind not in {"commit", "pull_request"}:
        raise GateError("recorded candidate kind must be commit or pull_request")
    if not repository.strip():
        raise GateError("candidate repository must not be empty")
    if not SHA.fullmatch(base_sha) or not SHA.fullmatch(head_sha):
        raise GateError(
            "candidate base and head must be full 40- or 64-character "
            "hexadecimal object IDs"
        )
    if kind == "pull_request":
        try:
            pr_number = int(pull_request or "")
        except ValueError as exc:
            raise GateError("pull_request candidate requires a positive PR number") from exc
        if pr_number < 1:
            raise GateError("pull_request candidate requires a positive PR number")
    else:
        if pull_request is not None:
            raise GateError("commit candidate cannot include a pull request number")
        pr_number = None

    expected = {
        "candidate.kind": kind,
        "candidate.repository": repository.strip(),
        "candidate.base_sha": base_sha.lower(),
        "candidate.head_sha": head_sha.lower(),
        "candidate.patch_sha256": None,
        "candidate.dirty_paths": [],
        "candidate.pull_request": pr_number,
    }
    if state["candidate.kind"] != "unset":
        if all(state.get(key) == value for key, value in expected.items()):
            detail = validate_candidate(state, Path.cwd())
            return (
                f"OK: exact candidate is already recorded ({detail}); "
                "identity unchanged."
            )
        raise GateError(
            "exact candidate is already recorded and cannot be replaced during "
            "Verify. Return to the owning mutation stage when the workflow "
            "permits; otherwise record BLOCKED before replanning or splitting."
        )

    new_text = _apply_changes(text, expected)
    _write_state(path, new_text)
    label = f"PR {pr_number}" if pr_number is not None else "commit range"
    return f"OK: recorded {label} candidate {base_sha[:12]}..{head_sha[:12]}."


def check_candidate(
    path: Path,
    *,
    cwd: Path | None = None,
    current_head: str | None = None,
) -> str:
    _, state = load(path)
    detail = validate_candidate(state, cwd or Path.cwd(), current_head=current_head)
    return f"OK: exact candidate matches ({detail})."


def validate_candidate(
    state: dict[str, object], cwd: Path, current_head: str | None = None
) -> str:
    kind = state.get("candidate.kind")
    if kind == "unset":
        raise GateError(
            "exact candidate is unset. Verify must capture or record it before approval."
        )
    if kind == "worktree":
        repository = state.get("candidate.repository")
        base_sha = state.get("candidate.base_sha")
        fingerprint = state.get("candidate.patch_sha256")
        dirty_paths = _string_list(state, "candidate.dirty_paths")
        if not all(
            isinstance(value, str) and value
            for value in [repository, base_sha, fingerprint]
        ):
            raise GateError(
                "worktree candidate is missing repository, base SHA, or fingerprint"
            )
        if (
            state.get("candidate.head_sha") is not None
            or state.get("candidate.pull_request") is not None
        ):
            raise GateError(
                "worktree candidate cannot include head SHA or pull request"
            )
        snapshot = worktree_snapshot(cwd)
        mismatches: list[str] = []
        if Path(str(repository)).resolve() != Path(snapshot.repository).resolve():
            mismatches.append("repository")
        if str(base_sha).lower() != snapshot.base_sha.lower():
            mismatches.append("base SHA")
        if str(fingerprint).lower() != snapshot.patch_sha256.lower():
            mismatches.append("patch fingerprint")
        if dirty_paths != list(snapshot.dirty_paths):
            mismatches.append("dirty-path list")
        if mismatches:
            raise GateError(
                "exact worktree candidate drifted in "
                + ", ".join(mismatches)
                + ". Return to the owning stage; do not review stale evidence."
            )
        return f"worktree {snapshot.patch_sha256[:12]}"

    repository = state.get("candidate.repository")
    base_sha = state.get("candidate.base_sha")
    head_sha = state.get("candidate.head_sha")
    if not isinstance(repository, str) or not repository.strip():
        raise GateError(f"{kind} candidate is missing repository")
    if not isinstance(base_sha, str) or not SHA.fullmatch(base_sha):
        raise GateError(f"{kind} candidate is missing a valid base SHA")
    if not isinstance(head_sha, str) or not SHA.fullmatch(head_sha):
        raise GateError(f"{kind} candidate is missing a valid head SHA")
    if state.get("candidate.patch_sha256") is not None:
        raise GateError(f"{kind} candidate cannot include a worktree fingerprint")
    if _string_list(state, "candidate.dirty_paths"):
        raise GateError(f"{kind} candidate cannot include dirty worktree paths")
    if kind == "pull_request":
        pr_number = state.get("candidate.pull_request")
        if not isinstance(pr_number, int) or pr_number < 1:
            raise GateError("pull_request candidate is missing a positive PR number")
    elif state.get("candidate.pull_request") is not None:
        raise GateError("commit candidate cannot include a pull request number")
    if current_head is not None:
        if not SHA.fullmatch(current_head):
            raise GateError("caller-supplied current head is not a valid hexadecimal SHA")
        if current_head.lower() != head_sha.lower():
            raise GateError(
                f"candidate head drifted: recorded {head_sha}, current {current_head.lower()}"
            )
    return f"{kind} {head_sha[:12]}"


def worktree_snapshot(cwd: Path) -> WorktreeSnapshot:
    root_text = _git(cwd, "rev-parse", "--show-toplevel").decode("utf-8").strip()
    root = Path(root_text).resolve()
    base_sha = _git(root, "rev-parse", "HEAD").decode("ascii").strip().lower()
    pathspec = ["--", ".", ":(exclude).converge", ":(exclude).converge/**"]
    staged_diff = _git(
        root,
        "diff",
        "--cached",
        "--binary",
        "--full-index",
        "--no-ext-diff",
        "--no-textconv",
        "HEAD",
        *pathspec,
    )
    unstaged_diff = _git(
        root,
        "diff",
        "--binary",
        "--full-index",
        "--no-ext-diff",
        "--no-textconv",
        *pathspec,
    )
    staged_raw = _git(
        root, "diff", "--cached", "--name-only", "-z", "HEAD", *pathspec
    )
    unstaged_raw = _git(root, "diff", "--name-only", "-z", *pathspec)
    tracked = {
        value.decode("utf-8", "surrogateescape")
        for value in (staged_raw + unstaged_raw).split(b"\0")
        if value
    }
    untracked_raw = _git(
        root, "ls-files", "--others", "--exclude-standard", "-z", "--", "."
    )
    untracked = sorted(
        value.decode("utf-8", "surrogateescape")
        for value in untracked_raw.split(b"\0")
        if value and not _is_converge_artifact(value.decode("utf-8", "surrogateescape"))
    )

    digest = hashlib.sha256()
    _hash_part(digest, b"converge-worktree-v1")
    _hash_part(digest, base_sha.encode("ascii"))
    _hash_part(digest, b"staged")
    _hash_part(digest, staged_diff)
    _hash_part(digest, b"unstaged")
    _hash_part(digest, unstaged_diff)
    for relative in untracked:
        path = root / relative
        try:
            metadata = path.lstat()
            mode = stat.S_IMODE(metadata.st_mode)
            if stat.S_ISLNK(metadata.st_mode):
                content = os.readlink(path).encode("utf-8", "surrogateescape")
                kind = b"symlink"
            elif stat.S_ISREG(metadata.st_mode):
                content = path.read_bytes()
                kind = b"file"
            else:
                raise GateError(f"unsupported untracked candidate path type: {relative}")
        except OSError as exc:
            raise GateError(f"cannot fingerprint untracked path {relative}: {exc}") from exc
        _hash_part(digest, relative.encode("utf-8", "surrogateescape"))
        _hash_part(digest, kind)
        _hash_part(digest, str(mode).encode("ascii"))
        _hash_part(digest, content)

    dirty_paths = tuple(sorted(tracked | set(untracked)))
    return WorktreeSnapshot(
        repository=str(root),
        base_sha=base_sha,
        patch_sha256=digest.hexdigest(),
        dirty_paths=dirty_paths,
    )


def _git(cwd: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise GateError(f"cannot run git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise GateError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _is_converge_artifact(path: str) -> bool:
    normalized = path.removeprefix("./")
    return normalized == ".converge" or normalized.startswith(".converge/")


def _hash_part(digest, value: bytes) -> None:
    digest.update(len(value).to_bytes(8, "big"))
    digest.update(value)


def _validate_transition_stage(
    state: dict[str, object], current: str, destination: str, stage: str
) -> None:
    destination_stages = {
        "PLANNED": {"plan"},
        "BUILDING": {"build"},
        "READY_FOR_VERIFY": {"build", "remediate"},
        "INTERNALLY_VERIFIED": {"verify"},
        "REVIEW_FINDINGS": {"review"},
        "REMEDIATING": {"remediate"},
        "READY_FOR_CLOSURE": {"verify"},
        "TARGETED_FIX": {"close"} if current == "READY_FOR_CLOSURE" else {"remediate"},
        "READY_FOR_TARGETED_CONFIRMATION": {"remediate"},
    }
    owner_stages = {
        "PLANNING": {"plan"},
        "PLANNED": {"plan", "build"},
        "BUILDING": {"build"},
        "READY_FOR_VERIFY": {"verify"},
        "INTERNALLY_VERIFIED": {"review"},
        "REVIEW_FINDINGS": {"remediate"},
        "REMEDIATING": {"remediate"},
        "READY_FOR_CLOSURE": {"close"},
        "TARGETED_FIX": {"remediate"},
        "READY_FOR_TARGETED_CONFIRMATION": {"verify"},
        "BLOCKED": {str(state.get("stage"))},
    }
    if destination in TERMINAL_STATES or destination == "BLOCKED":
        allowed = owner_stages[current]
    else:
        allowed = destination_stages.get(destination, set())
    if stage not in allowed:
        raise GateError(
            f"transition {current} -> {destination} requires stage "
            f"{' or '.join(sorted(allowed))}; received {stage}"
        )


def _require_candidate_capture_state(state: dict[str, object]) -> None:
    status = state.get("status")
    if status not in CANDIDATE_CAPTURE_STATES:
        raise GateError(
            "candidate identity may be recorded only while READY_FOR_VERIFY or "
            f"READY_FOR_TARGETED_CONFIRMATION; current status is {status}"
        )


def _normalize_findings(findings: list[str]) -> list[str]:
    result: list[str] = []
    for finding in findings:
        value = finding.strip().upper()
        if not FINDING_ID.fullmatch(value):
            raise GateError(
                f"invalid finding ID {finding!r}; use stable IDs such as REV-1 or CLOSE-1"
            )
        if value not in result:
            result.append(value)
    return result


def _ordered_union(existing: list[str], additions: list[str]) -> list[str]:
    return existing + [value for value in additions if value not in existing]


def _empty_candidate() -> dict[str, object]:
    return {
        "candidate.kind": "unset",
        "candidate.repository": None,
        "candidate.base_sha": None,
        "candidate.head_sha": None,
        "candidate.patch_sha256": None,
        "candidate.dirty_paths": [],
        "candidate.pull_request": None,
    }


def _apply_changes(text: str, changes: dict[str, object]) -> str:
    updated = text
    for key, value in changes.items():
        updated = _set_field(updated, key, value)
    return updated


def _set_field(text: str, dotted_key: str, value: object) -> str:
    parts = dotted_key.split(".", 1)
    lines = text.splitlines()
    rendered = _render(value)

    if len(parts) == 1:
        key = parts[0]
        for index, line in enumerate(lines):
            if re.fullmatch(rf"{re.escape(key)}:\s*.*", line):
                lines[index] = f"{key}: {rendered}"
                return "\n".join(lines) + "\n"
        raise GateError(f"could not find top-level state field {key}")

    section, key = parts
    header = f"{section}:"
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise GateError(f"could not find state section {section}") from exc

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line and not line[0].isspace() and line.endswith(":"):
            end = index
            break
        if line and not line[0].isspace() and ":" in line:
            end = index
            break

    nested = re.compile(rf"\s+{re.escape(key)}:\s*.*")
    for index in range(start + 1, end):
        if nested.fullmatch(lines[index]):
            lines[index] = f"  {key}: {rendered}"
            return "\n".join(lines) + "\n"

    insert_at = end
    while insert_at > start + 1 and lines[insert_at - 1] == "":
        insert_at -= 1
    lines.insert(insert_at, f"  {key}: {rendered}")
    return "\n".join(lines) + "\n"


def _render(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=True)
    if isinstance(value, str):
        if re.fullmatch(r"[A-Za-z0-9_./@+:-]+", value) and value not in {
            "null",
            "true",
            "false",
        }:
            return value
        return json.dumps(value, ensure_ascii=True)
    raise GateError(f"unsupported state value type for {value!r}")


def _write_state(path: Path, text: str) -> None:
    if path.is_symlink():
        raise GateError(f"refusing to replace symlinked state file: {path}")
    validate_state(parse_state(text))
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except OSError as exc:
        raise GateError(f"could not atomically update {path}: {exc}") from exc
    finally:
        if temporary.exists():
            temporary.unlink()


def show(state: dict[str, object]) -> str:
    status = str(state["status"])
    broad_used, broad_max = _budget(state, "broad")
    closure_used, closure_max = _budget(state, "closure")
    open_findings = _finding_list(state, "findings.open")
    closed_findings = _finding_list(state, "findings.closed")
    candidate = str(state.get("candidate.kind"))
    if candidate == "worktree" and state.get("candidate.patch_sha256"):
        candidate += f" {str(state['candidate.patch_sha256'])[:12]}"
    elif candidate in {"commit", "pull_request"} and state.get("candidate.head_sha"):
        candidate += f" {str(state['candidate.head_sha'])[:12]}"
    lines = [
        f"lane: {state.get('lane')}",
        f"stage: {state.get('stage')}",
        f"status: {status}",
        f"candidate: {candidate}",
        f"broad review budget: {broad_used}/{broad_max}",
        f"closure review budget: {closure_used}/{closure_max}",
        f"open findings: {', '.join(open_findings) if open_findings else 'none'}",
        f"closed findings: {', '.join(closed_findings) if closed_findings else 'none'}",
    ]
    if status == "BLOCKED":
        lines.append(f"blocked reason: {state.get('decision.blocked_reason')}")
        lines.append(f"resume status: {state.get('decision.resume_status')}")
    lines.append(f"next allowed action: {NEXT_ACTION[status]}")
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
    check_p.add_argument(
        "action", choices=["build", "verify", "review", "remediate", "close"]
    )

    set_p = sub.add_parser("set-status", help="record one legal state transition")
    set_p.add_argument("status")
    set_p.add_argument("--stage", required=True)
    set_p.add_argument("--reason", default=None)
    set_p.add_argument("--finding", action="append", default=[])
    sub.add_parser("resume", help="resume the exact state recorded before BLOCKED")

    candidate_p = sub.add_parser("candidate", help="record or check exact candidate identity")
    candidate_sub = candidate_p.add_subparsers(dest="candidate_command", required=True)
    candidate_sub.add_parser(
        "capture-worktree", help="capture the current local Git worktree candidate"
    )
    record_p = candidate_sub.add_parser(
        "record", help="record a caller-resolved commit or pull-request candidate"
    )
    record_p.add_argument("--kind", choices=["commit", "pull_request"], required=True)
    record_p.add_argument("--repository", required=True)
    record_p.add_argument("--base-sha", required=True)
    record_p.add_argument("--head-sha", required=True)
    record_p.add_argument("--pull-request", default=None)
    candidate_check_p = candidate_sub.add_parser(
        "check", help="check the recorded candidate and optional current remote head"
    )
    candidate_check_p.add_argument("--current-head", default=None)

    args = parser.parse_args(argv)
    try:
        if args.command == "show":
            _, state = load(args.state)
            print(show(state))
        elif args.command == "check":
            _, state = load(args.state)
            print(check(state, args.action))
        elif args.command == "set-status":
            print(
                set_status(
                    args.state,
                    args.status,
                    args.stage,
                    reason=args.reason,
                    findings=args.finding,
                )
            )
        elif args.command == "resume":
            print(resume(args.state))
        elif args.command == "candidate":
            if args.candidate_command == "capture-worktree":
                print(capture_worktree(args.state))
            elif args.candidate_command == "record":
                print(
                    record_candidate(
                        args.state,
                        kind=args.kind,
                        repository=args.repository,
                        base_sha=args.base_sha,
                        head_sha=args.head_sha,
                        pull_request=args.pull_request,
                    )
                )
            elif args.candidate_command == "check":
                print(check_candidate(args.state, current_head=args.current_head))
    except GateError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
