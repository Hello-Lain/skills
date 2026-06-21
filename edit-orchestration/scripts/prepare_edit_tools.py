#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import self_check_edit_tools

SUPPORTED_TOOLS = ("ast-grep", "aider", "jscodeshift", "openrewrite")


def default_root() -> Path:
    return self_check_edit_tools.default_root()


def package_spec(tool: str) -> str:
    defaults = {
        "ast-grep": "@ast-grep/cli",
        "jscodeshift": "jscodeshift",
        "aider": "aider-chat",
    }
    env_names = {
        "ast-grep": "EDIT_ORCH_AST_GREP_PACKAGE",
        "jscodeshift": "EDIT_ORCH_JSCODESHIFT_PACKAGE",
        "aider": "EDIT_ORCH_AIDER_PACKAGE",
    }
    env_name = env_names.get(tool)
    return os.environ.get(env_name, defaults[tool]) if env_name else tool


def safe_root(root: Path) -> Path:
    resolved = root.expanduser().resolve()
    forbidden = {Path("/"), Path("/usr"), Path("/usr/local"), Path("/bin"), Path("/sbin"), Path("/etc"), Path("/var"), Path("/opt")}
    if resolved in forbidden:
        raise SystemExit(f"ERROR: refusing system install root: {resolved}")
    if str(resolved).startswith("/usr/") or str(resolved).startswith("/etc/") or str(resolved).startswith("/var/"):
        raise SystemExit(f"ERROR: refusing system install root: {resolved}")
    return resolved


def run(args: list[str], *, cwd: Path | None = None) -> None:
    try:
        result = subprocess.run(args, text=True, capture_output=True, cwd=cwd, check=False)
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot run {args[0]}: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise SystemExit(f"ERROR: command failed ({' '.join(args)}): {detail}")


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "tools": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid manifest {path}: {exc}") from exc


def save_record(root: Path, tool: str, method: str, spec: str | None, check: dict[str, Any]) -> None:
    manifest_path = root / "manifest.json"
    manifest = load_manifest(manifest_path)
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("tools", {})
    manifest["tools"][tool] = {
        "method": method,
        "package": spec,
        "command": check.get("command"),
        "version": check.get("version"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def npm_install(root: Path, tool: str, spec: str) -> None:
    npm = os.environ.get("NPM_BIN") or "npm"
    node_root = root / "node"
    node_root.mkdir(parents=True, exist_ok=True)
    run([npm, "install", "--prefix", str(node_root), spec])


def venv_install(root: Path, spec: str) -> None:
    venv = root / "venvs" / "aider"
    if not (venv / "bin" / "python").exists():
        venv.parent.mkdir(parents=True, exist_ok=True)
        run([sys.executable, "-m", "venv", str(venv)])
    python = venv / "bin" / "python"
    run([str(python), "-m", "pip", "install", spec])


def prepare(tool: str, root: Path, *, check_only: bool) -> dict[str, Any]:
    check = self_check_edit_tools.check_tool(tool, root, Path.cwd())
    if check.get("ok"):
        save_record(root, tool, "existing", None, check)
        return check
    if check_only:
        return check
    if tool == "ast-grep":
        spec = package_spec(tool)
        npm_install(root, tool, spec)
        check = self_check_edit_tools.check_tool(tool, root, Path.cwd())
        if check.get("ok"):
            save_record(root, tool, "npm-prefix", spec, check)
        return check
    if tool == "jscodeshift":
        spec = package_spec(tool)
        npm_install(root, tool, spec)
        check = self_check_edit_tools.check_tool(tool, root, Path.cwd())
        if check.get("ok"):
            save_record(root, tool, "npm-prefix", spec, check)
        return check
    if tool == "aider":
        spec = package_spec(tool)
        venv_install(root, spec)
        check = self_check_edit_tools.check_tool(tool, root, Path.cwd())
        if check.get("ok"):
            save_record(root, tool, "venv-pip", spec, check)
        return check
    if tool == "openrewrite":
        return check
    raise SystemExit(f"ERROR: unsupported tool: {tool}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare user-level edit helper tools for edit-orchestration routes.")
    parser.add_argument("--tool", choices=SUPPORTED_TOOLS, help="Tool id to prepare.")
    parser.add_argument("--root", type=Path, default=default_root(), help="User-controlled tool root.")
    parser.add_argument("--check-only", action="store_true", help="Only self-check; do not install.")
    parser.add_argument("--list", action="store_true", help="List supported tool ids.")
    parser.add_argument("--json", action="store_true", help="Emit JSON for tool preparation.")
    args = parser.parse_args()

    if args.list:
        print("\n".join(SUPPORTED_TOOLS))
        return 0
    if not args.tool:
        parser.error("--tool is required unless --list is used")
    root = safe_root(args.root)
    if not args.check_only:
        root.mkdir(parents=True, exist_ok=True)
    result = prepare(args.tool, root, check_only=args.check_only)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result.get("ok"):
        print(f"PASS {args.tool}: {result.get('command') or result.get('method')} ({result.get('version')})")
    else:
        print(f"FAIL {args.tool}: {result.get('reason')}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
