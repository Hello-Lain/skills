#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import self_check_structural_tools

SUPPORTED_TOOLS = self_check_structural_tools.SUPPORTED_TOOLS


def default_root() -> Path:
    return self_check_structural_tools.default_root()


def safe_root(root: Path) -> Path:
    resolved = root.expanduser().resolve()
    forbidden = {Path("/"), Path("/usr"), Path("/usr/local"), Path("/bin"), Path("/sbin"), Path("/etc"), Path("/var"), Path("/opt")}
    if resolved in forbidden:
        raise SystemExit(f"ERROR: refusing system install root: {resolved}")
    if any(str(resolved).startswith(prefix) for prefix in ("/usr/", "/etc/", "/var/", "/opt/")):
        raise SystemExit(f"ERROR: refusing system install root: {resolved}")
    return resolved


def package_spec(tool: str) -> str | None:
    defaults = {
        "ast-grep": "@ast-grep/cli",
        "jscodeshift": "jscodeshift",
        "remark": "remark-cli",
    }
    env_names = {
        "ast-grep": "STRUCTURAL_EDIT_AST_GREP_PACKAGE",
        "jscodeshift": "STRUCTURAL_EDIT_JSCODESHIFT_PACKAGE",
        "remark": "STRUCTURAL_EDIT_REMARK_PACKAGE",
    }
    env_name = env_names.get(tool)
    default = defaults.get(tool)
    return os.environ.get(env_name, default) if default else None


def download_spec(tool: str) -> str | None:
    overrides = {
        "jq": os.environ.get("STRUCTURAL_EDIT_JQ_URL"),
        "yq": os.environ.get("STRUCTURAL_EDIT_YQ_URL"),
    }
    if overrides.get(tool):
        return overrides[tool]
    system = platform.system().lower()
    machine = platform.machine().lower()
    jq_urls = {
        ("linux", "x86_64"): "https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64",
        ("linux", "aarch64"): "https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-arm64",
        ("darwin", "x86_64"): "https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-macos-amd64",
        ("darwin", "arm64"): "https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-macos-arm64",
    }
    yq_urls = {
        ("linux", "x86_64"): "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64",
        ("linux", "aarch64"): "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_arm64",
        ("darwin", "x86_64"): "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_darwin_amd64",
        ("darwin", "arm64"): "https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_darwin_arm64",
    }
    lookup = jq_urls if tool == "jq" else yq_urls
    return lookup.get((system, machine))


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


def save_record(root: Path, tool: str, method: str, source: str | None, check: dict[str, Any]) -> None:
    manifest_path = root / "manifest.json"
    manifest = load_manifest(manifest_path)
    manifest.setdefault("schema_version", 1)
    manifest.setdefault("tools", {})
    manifest["tools"][tool] = {
        "method": method,
        "source": source,
        "command": check.get("command"),
        "version": check.get("version"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_self_check_ok": bool(check.get("ok")),
        "last_self_check_reason": check.get("reason"),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def npm_install(root: Path, spec: str) -> None:
    npm = os.environ.get("NPM_BIN") or "npm"
    node_root = root / "node"
    node_root.mkdir(parents=True, exist_ok=True)
    run([npm, "install", "--prefix", str(node_root), spec])


def download_binary(root: Path, tool: str, url: str) -> None:
    target = root / "bin" / tool
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".download")
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            data = response.read()
        tmp.write_bytes(data)
    except Exception as exc:
        downloader = shutil.which("curl")
        if downloader:
            run([downloader, "-L", "--fail", "--retry", "3", "--output", str(tmp), url])
        else:
            downloader = shutil.which("wget")
            if not downloader:
                raise SystemExit(f"ERROR: download failed and neither curl nor wget is available: {exc}") from exc
            run([downloader, "-O", str(tmp), url])
    tmp.replace(target)
    target.chmod(0o755)


def prepare(tool: str, root: Path, *, check_only: bool, force_user_root: bool = False) -> dict[str, Any]:
    check = self_check_structural_tools.check_tool(tool, root, Path.cwd())
    if check.get("ok") and not force_user_root:
        save_record(root, tool, "existing", None, check)
        return check
    if check_only:
        return check
    if tool in {"ast-grep", "jscodeshift", "remark"}:
        spec = package_spec(tool)
        assert spec is not None
        npm_install(root, spec)
        check = self_check_structural_tools.check_tool(tool, root, Path.cwd())
        if check.get("ok"):
            save_record(root, tool, "npm-prefix", spec, check)
        return check
    if tool in {"jq", "yq"}:
        url = download_spec(tool)
        if not url:
            raise SystemExit(f"ERROR: no supported download URL for {tool} on {platform.system().lower()}-{platform.machine().lower()}")
        download_binary(root, tool, url)
        check = self_check_structural_tools.check_tool(tool, root, Path.cwd())
        if check.get("ok"):
            save_record(root, tool, "binary-download", url, check)
        return check
    if tool == "openrewrite":
        return check
    raise SystemExit(f"ERROR: unsupported tool: {tool}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare user-level helper tools for structural-edit routes.")
    parser.add_argument("--tool", choices=SUPPORTED_TOOLS, help="Tool id to prepare.")
    parser.add_argument("--root", type=Path, default=default_root(), help="User-controlled tool root.")
    parser.add_argument("--check-only", action="store_true", help="Only self-check; do not install.")
    parser.add_argument("--force-user-root", action="store_true", help="Install into --root even when PATH already has a working command.")
    parser.add_argument("--list", action="store_true", help="List supported tool ids.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    if args.list:
        print("\n".join(SUPPORTED_TOOLS))
        return 0
    if not args.tool:
        parser.error("--tool is required unless --list is used")
    root = safe_root(args.root)
    if not args.check_only:
        root.mkdir(parents=True, exist_ok=True)
    result = prepare(args.tool, root, check_only=args.check_only, force_user_root=args.force_user_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result.get("ok"):
        print(f"PASS {args.tool}: {result.get('command') or result.get('method')} ({result.get('version')})")
    else:
        print(f"FAIL {args.tool}: {result.get('reason')}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
