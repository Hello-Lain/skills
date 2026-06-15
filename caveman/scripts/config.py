#!/usr/bin/env python3
"""Local Caveman config for Codex skills."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

MODES = {
    "lite": 25,
    "full": 50,
    "ultra": 75,
    "wenyan-lite": 35,
    "wenyan-full": 70,
    "wenyan-ultra": 85,
}

PROVIDERS = {"auto", "codex", "anthropic", "claude"}


def config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "caveman" / "config.json"


def mode_for_savings(value: int) -> str:
    if value < 35:
        return "lite"
    if value < 65:
        return "full"
    return "ultra"


def parse_savings(raw: str | None) -> int | None:
    if raw is None:
        return None
    text = raw.strip().removesuffix("%")
    value = int(text)
    if value < 0 or value > 90:
        raise argparse.ArgumentTypeError("savings must be 0..90")
    return value


def load() -> dict:
    path = config_path()
    if not path.exists():
        return {
            "enabled": True,
            "defaultMode": "full",
            "targetSavings": 50,
            "provider": "auto",
        }
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        data = {}
    return {
        "enabled": bool(data.get("enabled", data.get("defaultMode") != "off")),
        "defaultMode": data.get("defaultMode", "full"),
        "targetSavings": int(data.get("targetSavings", MODES.get(data.get("defaultMode", "full"), 50))),
        "provider": data.get("provider", "auto"),
    }


def save(data: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def apply_env(data: dict) -> dict:
    result = dict(data)
    enabled = os.environ.get("CAVEMAN_ENABLED")
    if enabled is not None:
        result["enabled"] = enabled.lower() not in {"0", "false", "no", "off"}

    mode = os.environ.get("CAVEMAN_DEFAULT_MODE")
    if mode:
        if mode == "off":
            result["enabled"] = False
        elif mode in MODES:
            result["defaultMode"] = mode
            result["targetSavings"] = MODES[mode]

    savings = os.environ.get("CAVEMAN_TOKEN_SAVINGS")
    if savings:
        value = parse_savings(savings)
        if value is not None:
            result["targetSavings"] = value
            result["defaultMode"] = mode_for_savings(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure local Caveman Codex skill")
    sub = parser.add_subparsers(dest="command", required=True)

    on = sub.add_parser("on", help="enable Caveman")
    on.add_argument("mode", nargs="?", choices=sorted(MODES), default=None)
    on.add_argument("--savings", type=parse_savings, default=None)

    off = sub.add_parser("off", help="disable Caveman")
    off.add_argument("--keep-mode", action="store_true")

    set_cmd = sub.add_parser("set", help="set compression intensity")
    set_cmd.add_argument("mode", nargs="?", choices=sorted(MODES), default=None)
    set_cmd.add_argument("--savings", type=parse_savings, default=None)
    set_cmd.add_argument("--provider", choices=sorted(PROVIDERS), default=None)

    sub.add_parser("status", help="print effective config")

    args = parser.parse_args()
    data = load()

    if args.command == "on":
        data["enabled"] = True
        if args.savings is not None:
            data["targetSavings"] = args.savings
            data["defaultMode"] = mode_for_savings(args.savings)
        elif args.mode:
            data["defaultMode"] = args.mode
            data["targetSavings"] = MODES[args.mode]
        save(data)
    elif args.command == "off":
        data["enabled"] = False
        if not args.keep_mode:
            data["defaultMode"] = data.get("defaultMode", "full")
        save(data)
    elif args.command == "set":
        if args.savings is not None:
            data["targetSavings"] = args.savings
            data["defaultMode"] = mode_for_savings(args.savings)
        elif args.mode:
            data["defaultMode"] = args.mode
            data["targetSavings"] = MODES[args.mode]
        if args.provider:
            data["provider"] = args.provider
        data["enabled"] = True
        save(data)

    effective = apply_env(load())
    effective["path"] = str(config_path())
    print(json.dumps(effective, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
