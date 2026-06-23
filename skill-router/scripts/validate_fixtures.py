#!/usr/bin/env python3
"""Validate skill-router policies and deterministic route fixtures."""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policies" / "known-conflicts.json"
FIXTURE_PATH = ROOT / "references" / "scenario-fixtures.json"
REPO_ROOT = ROOT.parent
POLICY_ID_RE = re.compile(r"^sr-\d{3}-[a-z0-9-]+$")
ALLOWED_CATEGORIES = {
    "duplicate-name",
    "stale-route",
    "router-child-overlap",
    "same-domain-skills",
    "same-capability-tools",
    "mandatory-interrupt",
    "mode-gated-tool",
    "missing-tool",
    "fallback-policy",
}
ALLOWED_ROUTE_KINDS = {"skill", "tool", "mcp", "blocked"}
REQUIRED_POLICY_FIELDS = {
    "id",
    "status",
    "category",
    "triggers",
    "conditions",
    "primary_route",
    "why",
    "suppressed",
    "fallbacks",
    "evidence",
    "safety_notes",
    "created_at",
    "updated_at",
    "review_notes",
}
KNOWN_SKILL_RENAMES = {
    "edit-orchestration": "structural-edit",
}
MANUAL_EDIT_POLICY_ID = "sr-013-manual-file-edit"
MANUAL_EDIT_PRIMARY = {"kind": "skill", "name": "structural-edit"}


def replace_known_drift(value):
    if isinstance(value, dict):
        return {key: replace_known_drift(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace_known_drift(item) for item in value]
    if isinstance(value, str):
        for old, new in KNOWN_SKILL_RENAMES.items():
            value = value.replace(old, new)
        return value
    return value


def repair_known_drift(policy_doc: dict) -> bool:
    changed = False
    repaired = replace_known_drift(policy_doc)
    if repaired != policy_doc:
        policy_doc.clear()
        policy_doc.update(repaired)
        changed = True

    today = date.today().isoformat()
    for policy in policy_doc.get("policies", []):
        if not isinstance(policy, dict) or policy.get("id") != MANUAL_EDIT_POLICY_ID:
            continue
        policy_changed = False
        fallbacks = policy.setdefault("fallbacks", [])
        before = list(fallbacks)
        fallbacks[:] = [
            item
            for item in fallbacks
            if not (
                isinstance(item, dict)
                and item.get("route") == MANUAL_EDIT_PRIMARY
            )
        ]
        if fallbacks != before:
            policy_changed = True
        if policy.get("primary_route") != MANUAL_EDIT_PRIMARY:
            policy["primary_route"] = dict(MANUAL_EDIT_PRIMARY)
            policy["why"] = (
                "structural-edit is the default manual edit decision route; apply_patch is the strict text "
                "fallback and execution tool only when structural-edit allows it."
            )
            apply_patch_fallback = {
                "route": {"kind": "tool", "name": "functions.apply_patch"},
                "condition": "structural-edit classifies the edit as tiny, unique, low-risk strict text fallback.",
            }
            if apply_patch_fallback not in fallbacks:
                fallbacks.insert(0, apply_patch_fallback)
            notes = policy.setdefault("safety_notes", [])
            note = "Run structural-edit route classification before choosing apply_patch for manual edits."
            if note not in notes:
                notes.append(note)
            policy_changed = True
        if policy_changed:
            policy["updated_at"] = today
            policy["review_notes"] = "Repaired by validate_fixtures.py --repair-known-drift."
            changed = True
    if changed:
        policy_doc["updated_at"] = today
    return changed


def repair_known_fixture_drift(fixture_doc: dict) -> bool:
    changed = False
    for fixture in fixture_doc.get("fixtures", []):
        if not isinstance(fixture, dict):
            continue
        if fixture.get("expected_policy_id") == MANUAL_EDIT_POLICY_ID and fixture.get("expected_primary_route") != "skill:structural-edit":
            fixture["expected_primary_route"] = "skill:structural-edit"
            changed = True
    return changed


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact parser message is enough
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def route_id(route: dict) -> str:
    if not isinstance(route, dict):
        raise ValueError(f"route must be object, got {route!r}")
    kind = route.get("kind")
    name = route.get("name")
    if kind not in ALLOWED_ROUTE_KINDS or not isinstance(name, str) or not name:
        raise ValueError(f"invalid route: {route!r}")
    return f"{kind}:{name}"


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def validate_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_POLICY_FIELDS - set(policy)
    if missing:
        errors.append(f"{policy.get('id', '<missing id>')}: missing fields {sorted(missing)}")
        return errors

    policy_id = policy["id"]
    if not isinstance(policy_id, str) or not POLICY_ID_RE.match(policy_id):
        errors.append(f"{policy_id!r}: id must match sr-NNN-slug")
    if policy["status"] not in {"active", "stale"}:
        errors.append(f"{policy_id}: invalid status {policy['status']!r}")
    if policy["category"] not in ALLOWED_CATEGORIES:
        errors.append(f"{policy_id}: invalid category {policy['category']!r}")
    for field in ("triggers", "conditions", "suppressed", "fallbacks", "evidence", "safety_notes"):
        if not isinstance(policy[field], list) or not policy[field]:
            errors.append(f"{policy_id}: {field} must be a non-empty list")
    for field in ("why", "created_at", "updated_at", "review_notes"):
        if not isinstance(policy[field], str) or not policy[field].strip():
            errors.append(f"{policy_id}: {field} must be a non-empty string")

    try:
        route_id(policy["primary_route"])
    except ValueError as exc:
        errors.append(f"{policy_id}: {exc}")
    if policy["primary_route"].get("kind") == "blocked" and policy["primary_route"].get("name") != "no-safe-route":
        errors.append(f"{policy_id}: blocked primary_route must be blocked:no-safe-route")
    if policy["primary_route"].get("kind") == "skill":
        skill_name = policy["primary_route"].get("name")
        expected_suffix = f"{skill_name}/SKILL.md"
        has_path_evidence = any(
            isinstance(evidence, dict)
            and evidence.get("type") == "path"
            and str(evidence.get("value", "")).endswith(expected_suffix)
            for evidence in policy["evidence"]
        )
        if not has_path_evidence:
            errors.append(f"{policy_id}: primary skill route lacks path evidence ending {expected_suffix}")
    if policy_id == MANUAL_EDIT_POLICY_ID and policy["primary_route"] != MANUAL_EDIT_PRIMARY:
        errors.append(
            f"{policy_id}: manual edits must route first to skill:structural-edit; "
            f"run {Path(__file__).name} --repair-known-drift"
        )

    for item in policy["suppressed"]:
        if not isinstance(item, dict) or "route" not in item or "reason" not in item:
            errors.append(f"{policy_id}: suppressed entries need route and reason")
            continue
        try:
            route_id(item["route"])
        except ValueError as exc:
            errors.append(f"{policy_id}: suppressed {exc}")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            errors.append(f"{policy_id}: suppressed reason must be non-empty")

    for item in policy["fallbacks"]:
        if not isinstance(item, dict) or "route" not in item or "condition" not in item:
            errors.append(f"{policy_id}: fallback entries need route and condition")
            continue
        try:
            route_id(item["route"])
        except ValueError as exc:
            errors.append(f"{policy_id}: fallback {exc}")
        if not isinstance(item["condition"], str) or not item["condition"].strip():
            errors.append(f"{policy_id}: fallback condition must be non-empty")

    for evidence in policy["evidence"]:
        if not isinstance(evidence, dict) or "type" not in evidence or "value" not in evidence:
            errors.append(f"{policy_id}: evidence entries need type and value")
            continue
        if evidence["type"] == "path":
            path = resolve_path(evidence["value"])
            if not path.exists():
                errors.append(f"{policy_id}: evidence path missing: {evidence['value']}")
        elif evidence["type"] not in {"session", "spec"}:
            errors.append(f"{policy_id}: unsupported evidence type {evidence['type']!r}")
    text = json.dumps(policy, sort_keys=True)
    for old, new in KNOWN_SKILL_RENAMES.items():
        if old in text:
            errors.append(f"{policy_id}: stale route name {old!r}; use {new!r} or run {Path(__file__).name} --repair-known-drift")

    return errors


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    repair = "--repair-known-drift" in argv
    unknown = [arg for arg in argv if arg != "--repair-known-drift"]
    if unknown:
        print(f"usage: {Path(__file__).name} [--repair-known-drift]", file=sys.stderr)
        return 2

    errors: list[str] = []
    policy_doc = load_json(POLICY_PATH)
    fixture_doc = load_json(FIXTURE_PATH)
    if repair and repair_known_drift(policy_doc):
        POLICY_PATH.write_text(json.dumps(policy_doc, indent=2) + "\n", encoding="utf-8")
        policy_doc = load_json(POLICY_PATH)
    if repair and repair_known_fixture_drift(fixture_doc):
        FIXTURE_PATH.write_text(json.dumps(fixture_doc, indent=2) + "\n", encoding="utf-8")
        fixture_doc = load_json(FIXTURE_PATH)
    policies = policy_doc.get("policies")
    fixtures = fixture_doc.get("fixtures")
    if not isinstance(policies, list) or not policies:
        errors.append("policies must be a non-empty list")
        policies = []
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("fixtures must be a non-empty list")
        fixtures = []

    seen: set[str] = set()
    by_id: dict[str, dict] = {}
    for policy in policies:
        policy_id = policy.get("id") if isinstance(policy, dict) else None
        if policy_id in seen:
            errors.append(f"duplicate policy id: {policy_id}")
        if isinstance(policy_id, str):
            seen.add(policy_id)
            by_id[policy_id] = policy
        if isinstance(policy, dict):
            errors.extend(validate_policy(policy))
        else:
            errors.append(f"policy must be object, got {policy!r}")

    for fixture in fixtures:
        if not isinstance(fixture, dict):
            errors.append(f"fixture must be object, got {fixture!r}")
            continue
        for field in ("id", "prompt", "expected_policy_id", "expected_primary_route"):
            if not isinstance(fixture.get(field), str) or not fixture[field].strip():
                errors.append(f"fixture {fixture.get('id', '<missing>')}: {field} must be non-empty string")
        policy = by_id.get(fixture.get("expected_policy_id"))
        if not policy:
            errors.append(f"fixture {fixture.get('id')}: missing policy {fixture.get('expected_policy_id')}")
            continue
        actual_route = route_id(policy["primary_route"])
        if actual_route != fixture.get("expected_primary_route"):
            errors.append(
                f"fixture {fixture.get('id')}: expected {fixture.get('expected_primary_route')}, got {actual_route}"
            )

    if errors:
        print("FAIL skill-router validation", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        print(f"Hint: {Path(__file__).name} --repair-known-drift can repair known stale route drift.", file=sys.stderr)
        return 1

    print(f"PASS skill-router validation: {len(policies)} policies, {len(fixtures)} fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
