#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import prepare_structural_tools


def load_manifest(root: Path) -> dict:
    path = root / "manifest.json"
    if not path.exists():
        return {"schema_version": 1, "tools": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def summary_lines(manifest: dict) -> list[str]:
    tools = manifest.get("tools") or {}
    if not tools:
        return ["No prepared tools recorded."]
    lines: list[str] = []
    for tool, record in sorted(tools.items()):
        command = record.get("command") or "<missing>"
        version = record.get("version") or "<unknown>"
        method = record.get("method") or "<unknown>"
        status = "ok" if record.get("last_self_check_ok") else f"fail ({record.get('last_self_check_reason') or 'unknown'})"
        lines.append(f"{tool}: {method} | {command} | {version} | {status}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Report prepared structural-edit tooling manifest state.")
    parser.add_argument("--root", type=Path, default=prepare_structural_tools.default_root())
    parser.add_argument("--tool", help="Emit only one tool record.")
    parser.add_argument("--summary", action="store_true", help="Emit text summary (default).")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON.")
    args = parser.parse_args()

    manifest = load_manifest(args.root.expanduser())
    if args.tool:
        tool_record = (manifest.get("tools") or {}).get(args.tool)
        if args.json:
            print(json.dumps({args.tool: tool_record}, indent=2, sort_keys=True))
        else:
            if not tool_record:
                print(f"{args.tool}: missing")
            else:
                print(f"{args.tool}: {json.dumps(tool_record, sort_keys=True)}")
        return 0
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    for line in summary_lines(manifest):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
