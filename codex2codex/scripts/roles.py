#!/usr/bin/env python3
"""Central codex2codex role registry loaded from roles/*.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
ROLES_DIR = SKILL_DIR / "roles"


def _parse_scalar(value: str):
    value = value.strip()
    if value == "":
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def _parse_yaml_subset(path: Path) -> dict:
    data: dict[str, object] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if line.startswith(" ") or ":" not in line:
            raise ValueError(f"{path}:{index + 1}: expected top-level key")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if raw_value == "|":
            index += 1
            block: list[str] = []
            while index < len(lines):
                child = lines[index]
                if child and not child.startswith(" "):
                    break
                block.append(child[2:] if child.startswith("  ") else child.lstrip())
                index += 1
            data[key] = "\n".join(block).rstrip()
            continue
        if raw_value:
            data[key] = _parse_scalar(raw_value)
            index += 1
            continue
        next_index = index + 1
        while next_index < len(lines) and (
            not lines[next_index].strip() or lines[next_index].strip().startswith("#")
        ):
            next_index += 1
        if next_index >= len(lines) or not lines[next_index].startswith(" "):
            data[key] = None
            index += 1
            continue
        index += 1
        items: list[object] = []
        while index < len(lines):
            child = lines[index]
            child_stripped = child.strip()
            if not child_stripped or child_stripped.startswith("#"):
                index += 1
                continue
            if not child.startswith(" "):
                break
            if not child_stripped.startswith("- "):
                raise ValueError(f"{path}:{index + 1}: expected list item")
            items.append(_parse_scalar(child_stripped[2:]))
            index += 1
        data[key] = items
    return data


@dataclass(frozen=True)
class RoleSpec:
    name: str
    agent: str
    worker: bool
    config_path: str
    mode: str
    sandbox: str | None
    effort: str
    cap: int | None
    context_profile: str
    description: str
    aliases: tuple[str, ...]
    title_keywords: tuple[str, ...]
    skills: tuple[str, ...]
    prompt: str


class RoleError(ValueError):
    pass


def _as_str_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"expected list, got {type(value).__name__}")
    return tuple(str(item).strip() for item in value if str(item).strip())


def _load_defaults() -> dict:
    defaults_path = ROLES_DIR / "_defaults.yaml"
    if not defaults_path.exists():
        return {}
    return _parse_yaml_subset(defaults_path)


def _load_role_specs() -> dict[str, RoleSpec]:
    specs: dict[str, RoleSpec] = {}
    for path in sorted(ROLES_DIR.glob("*.yaml")):
        if path.name.startswith("_"):
            continue
        item = _parse_yaml_subset(path)
        name = str(item.get("role") or "").strip()
        if not name:
            continue
        spec = RoleSpec(
            name=name,
            agent=str(item.get("agent") or f"{name}-agent"),
            worker=bool(item.get("worker")),
            config_path=str(path),
            mode=str(item.get("mode") or "consult"),
            sandbox=item.get("sandbox") if item.get("sandbox") is None else str(item.get("sandbox")),
            effort=str(item.get("effort") or DEFAULT_EFFORT),
            cap=item.get("cap") if item.get("cap") is None else int(item["cap"]),
            context_profile=str(item.get("context_profile") or DEFAULT_CONTEXT_PROFILE),
            description=str(item.get("description") or ""),
            aliases=_as_str_tuple(item.get("aliases")),
            title_keywords=_as_str_tuple(item.get("title_keywords")),
            skills=_as_str_tuple(item.get("skills")),
            prompt=str(item.get("prompt") or ""),
        )
        specs[name] = spec
    return specs


DEFAULTS = _load_defaults()
ALLOWED_EFFORTS = tuple(str(item) for item in DEFAULTS.get("allowed_efforts", ["high", "xhigh"]))
DEFAULT_EFFORT = str(DEFAULTS.get("default_effort") or "high")
ALLOWED_CONTEXT_PROFILES = tuple(
    str(item) for item in DEFAULTS.get("allowed_context_profiles", ["role", "minimal", "standard", "full"])
)
ROLE_CONTEXT_PROFILES = tuple(profile for profile in ALLOWED_CONTEXT_PROFILES if profile != "role")
DEFAULT_CONTEXT_PROFILE = str(DEFAULTS.get("default_context_profile") or "minimal")
FALLBACK_ROLE = str(DEFAULTS.get("fallback_role") or "coding")
TITLE_PRIORITY = tuple(str(item) for item in DEFAULTS.get("title_priority", []))
GLOBAL_SKILL_POLICY = str(DEFAULTS.get("global_skill_policy") or "")
ROLE_SPECS = _load_role_specs()
WORKER_ROLE_SPECS = {name: role for name, role in ROLE_SPECS.items() if role.worker}

ROLE_ALIASES: dict[str, str] = {}
RESERVED_NON_WORKER_ROLES = set(str(item) for item in DEFAULTS.get("reserved_non_worker_roles", []))

for name, role in ROLE_SPECS.items():
    keys = {name, role.agent.removesuffix("-agent"), role.agent, *role.aliases}
    if role.worker:
        for key in keys:
            ROLE_ALIASES[key] = name
    else:
        RESERVED_NON_WORKER_ROLES.update(keys)

IMPLEMENT_ROLES = {
    role.name for role in WORKER_ROLE_SPECS.values() if role.mode == "implement"
}

ROLE_MODE = {
    name: (role.mode, role.sandbox or "ro", role.effort) for name, role in WORKER_ROLE_SPECS.items()
}

for name, role in WORKER_ROLE_SPECS.items():
    if role.effort not in ALLOWED_EFFORTS:
        raise ValueError(f"role {name} uses invalid effort {role.effort}; allowed: {', '.join(ALLOWED_EFFORTS)}")
    if role.context_profile not in ROLE_CONTEXT_PROFILES:
        raise ValueError(
            f"role {name} uses invalid context_profile {role.context_profile}; "
            f"allowed: {', '.join(ROLE_CONTEXT_PROFILES)}"
        )


def normalize_role(value: str, title: str = "") -> str:
    raw = (value or "").strip().lower()
    key = raw.split()[0].split(",")[0].split("/")[0].split("|")[0] if raw else ""
    if key.endswith("-agent"):
        key = key[: -len("-agent")]
    if key in RESERVED_NON_WORKER_ROLES:
        raise RoleError(f"{key}-agent is the lead/orchestrator role and cannot be used as a worker")
    if key in ROLE_ALIASES:
        return ROLE_ALIASES[key]

    lowered_title = title.lower()
    for role_name in TITLE_PRIORITY:
        role = WORKER_ROLE_SPECS.get(role_name)
        if role and any(keyword in lowered_title for keyword in role.title_keywords):
            return role_name
    return FALLBACK_ROLE


def role_instructions(role_name: str) -> str:
    role = ROLE_SPECS.get(role_name)
    if not role:
        return GLOBAL_SKILL_POLICY
    skills = ", ".join(role.skills) if role.skills else "none"
    parts = [
        f"Role contract: {role.agent} ({role.name})",
        f"Role config: {role.config_path}",
        f"Role focus: {role.description}",
        f"Preferred skills: {skills}",
    ]
    if role.prompt:
        parts.extend(["Role prompt:", role.prompt])
    if GLOBAL_SKILL_POLICY:
        parts.extend(["Global skill policy:", GLOBAL_SKILL_POLICY])
    return "\n".join(parts).strip()
