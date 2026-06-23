#!/usr/bin/env python3
from __future__ import annotations

from route_decision import decide_route


SCENARIOS = [
    {
        "name": "python semantic edit",
        "kwargs": {"path": "pkg/module.py", "structured_op": True},
        "expect": {"route": "structural", "tool": "ast-grep", "hard_stop_if_missing": True},
    },
    {
        "name": "typescript migration",
        "kwargs": {"path": "src/app.ts", "structured_op": True, "repeated_pattern": True},
        "expect": {"route": "structural", "tool": "jscodeshift", "hard_stop_if_missing": True},
    },
    {
        "name": "json update",
        "kwargs": {"path": "config.json", "structured_op": True},
        "expect": {"route": "structured-data", "tool": "jq", "hard_stop_if_missing": True},
    },
    {
        "name": "yaml path update",
        "kwargs": {"path": "config.yaml", "structured_op": True},
        "expect": {"route": "structured-data", "tool": "yq", "hard_stop_if_missing": True},
    },
    {
        "name": "markdown section rewrite",
        "kwargs": {"path": "README.md", "structured_op": True},
        "expect": {"route": "markdown-ast", "tool": "remark", "hard_stop_if_missing": True},
    },
    {
        "name": "tiny prose fallback",
        "kwargs": {"path": "notes.md", "tiny": True, "unique": True, "prose_only": True},
        "expect": {"route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False},
    },
    {
        "name": "missing required structural tool policy",
        "kwargs": {"path": "schema.yaml", "structured_op": True},
        "expect": {"route": "structured-data", "tool": "yq", "hard_stop_if_missing": True},
    },
    {
        "name": "java no openrewrite context",
        "kwargs": {"path": "src/Main.java"},
        "expect": {"route": "block", "tool": "openrewrite", "hard_stop_if_missing": True},
    },
    {
        "name": "generated output route",
        "kwargs": {"path": "package-lock.json", "generator_owned": True},
        "expect": {"route": "generator-owned", "tool": "project-owned", "hard_stop_if_missing": False},
    },
]


def main() -> int:
    failures: list[str] = []
    for scenario in SCENARIOS:
        result = decide_route(**scenario["kwargs"])
        for key, expected in scenario["expect"].items():
            actual = result.get(key)
            if actual != expected:
                failures.append(f"{scenario['name']}: expected {key}={expected!r}, got {actual!r}")
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS structural-edit route scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
