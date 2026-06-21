#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

SUPPORTED_TOOLS = ("ast-grep", "aider", "jscodeshift", "openrewrite")


def default_root() -> Path:
    base = os.environ.get("CODEX_HOME")
    if base:
        return Path(base).expanduser() / "tools" / "edit-orchestration"
    return Path.home() / ".codex" / "tools" / "edit-orchestration"


def _candidate_paths(tool: str, root: Path) -> list[Path]:
    node_bin = root / "node" / "node_modules" / ".bin"
    paths = {
        "ast-grep": [root / "bin" / "ast-grep", node_bin / "ast-grep", node_bin / "sg"],
        "aider": [root / "venvs" / "aider" / "bin" / "aider"],
        "jscodeshift": [node_bin / "jscodeshift", root / "bin" / "jscodeshift"],
        "openrewrite": [],
    }
    return paths.get(tool, [])


def find_command(tool: str, root: Path) -> str | None:
    for path in _candidate_paths(tool, root):
        if path.exists() and os.access(path, os.X_OK):
            return str(path)
    names = {
        # Do not accept PATH `sg`: on Linux it is commonly shadow-utils `sg`,
        # not ast-grep's alias. The project-local npm bin alias is still checked
        # above through `_candidate_paths`.
        "ast-grep": ("ast-grep",),
        "aider": ("aider",),
        "jscodeshift": ("jscodeshift",),
    }.get(tool, ())
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def run_version(command: str) -> tuple[bool, str]:
    for args in ([command, "--version"], [command, "version"]):
        try:
            result = subprocess.run(args, text=True, capture_output=True, timeout=20, check=False)
        except OSError as exc:
            return False, str(exc)
        except subprocess.TimeoutExpired:
            return False, "version command timed out"
        output = (result.stdout or result.stderr).strip()
        if result.returncode == 0:
            return True, output.splitlines()[0] if output else "version command passed"
    return False, output or "version command failed"


def check_openrewrite(cwd: Path) -> dict[str, Any]:
    mvn = shutil.which("mvn")
    gradle = shutil.which("gradle")
    gradlew = cwd / "gradlew"
    has_maven = (cwd / "pom.xml").exists()
    has_gradle = any((cwd / name).exists() for name in ("build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"))
    if has_maven and mvn:
        return {"ok": True, "tool": "openrewrite", "method": "maven-plugin", "command": mvn, "version": "maven available"}
    if has_gradle and gradlew.exists() and os.access(gradlew, os.X_OK):
        return {"ok": True, "tool": "openrewrite", "method": "gradle-wrapper-plugin", "command": str(gradlew), "version": "gradle wrapper available"}
    if has_gradle and gradle:
        return {"ok": True, "tool": "openrewrite", "method": "gradle-plugin", "command": gradle, "version": "gradle available"}
    reason = "requires pom.xml+mvn or Gradle build+gradle/gradlew in current project"
    return {"ok": False, "tool": "openrewrite", "method": "project-plugin", "command": None, "version": None, "reason": reason}


def check_tool(tool: str, root: Path, cwd: Path) -> dict[str, Any]:
    if tool not in SUPPORTED_TOOLS:
        return {"ok": False, "tool": tool, "reason": f"unsupported tool: {tool}"}
    if tool == "openrewrite":
        return check_openrewrite(cwd)
    command = find_command(tool, root)
    if not command:
        return {"ok": False, "tool": tool, "command": None, "version": None, "reason": f"{tool} not found under {root} or PATH"}
    ok, version = run_version(command)
    return {"ok": ok, "tool": tool, "command": command, "version": version, "reason": None if ok else version}


def main() -> int:
    parser = argparse.ArgumentParser(description="Self-check edit helper tools for the edit-orchestration skill.")
    parser.add_argument("--tool", required=True, choices=SUPPORTED_TOOLS)
    parser.add_argument("--root", type=Path, default=default_root())
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    result = check_tool(args.tool, root, Path.cwd())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result.get("ok"):
        print(f"PASS {args.tool}: {result.get('command') or result.get('method')} ({result.get('version')})")
    else:
        print(f"FAIL {args.tool}: {result.get('reason')}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
