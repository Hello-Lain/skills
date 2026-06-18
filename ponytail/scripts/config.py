#!/usr/bin/env python3
"""Ponytail intensity config for Codex skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Named mode presets
MODES: dict[str, int] = {"lite": 30, "full": 60, "ultra": 85}
INTENSITY_LEVELS = set(MODES.keys())
MODE_NAMES = sorted(INTENSITY_LEVELS)


def config_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "ponytail" / "config.json"


def load() -> dict:
    path = config_path()
    if not path.exists():
        return {"enabled": True, "defaultMode": "full", "intensity": 60}
    try:
        data = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        data = {}
    mode = data.get("defaultMode", "full")
    return {
        "enabled": bool(data.get("enabled", mode != "off")),
        "defaultMode": mode if mode in INTENSITY_LEVELS else "full",
        "intensity": int(data.get("intensity", MODES.get(mode, 60))),
    }


def save(data: dict) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def snap_mode(intensity: int) -> str:
    """Snap intensity 0-100 to nearest named mode."""
    return min(INTENSITY_LEVELS, key=lambda m: abs(MODES[m] - intensity))


def apply_env(data: dict) -> dict:
    result = dict(data)
    enabled = os.environ.get("PONYTAIL_ENABLED")
    if enabled is not None:
        result["enabled"] = enabled.lower() not in {"0", "false", "no", "off"}
    mode = os.environ.get("PONYTAIL_DEFAULT_MODE")
    if mode == "off":
        result["enabled"] = False
    elif mode in INTENSITY_LEVELS:
        result["defaultMode"] = mode
        result["intensity"] = MODES[mode]
    return result


def resolve_mode(data: dict) -> str:
    return "off" if not data["enabled"] else data["defaultMode"]


def cmd_on(data: dict, args) -> None:
    data["enabled"] = True
    if args.intensity is not None:
        data["intensity"] = args.intensity
        data["defaultMode"] = snap_mode(args.intensity)
    elif args.mode:
        data["defaultMode"] = args.mode
        data["intensity"] = MODES[args.mode]
    else:
        data["defaultMode"] = data.get("defaultMode", "full")
        data["intensity"] = MODES[data["defaultMode"]]
    save(data)


def cmd_off(data: dict, args) -> None:
    data["enabled"] = False
    save(data)


def cmd_set(data: dict, args) -> None:
    if args.intensity is not None:
        data["intensity"] = args.intensity
        data["defaultMode"] = snap_mode(args.intensity)
    elif args.mode:
        data["defaultMode"] = args.mode
        data["intensity"] = MODES[args.mode]
    data["enabled"] = True
    save(data)


def cmd_status(data: dict) -> dict:
    effective = apply_env(load())
    effective["configPath"] = str(config_path())
    effective["activeMode"] = resolve_mode(effective)
    return effective


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Configure Ponytail intensity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  config.py status\n"
            "  config.py on ultra\n"
            "  config.py set --intensity 45\n"
            "  config.py off\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_on = sub.add_parser("on", help="enable Ponytail at given intensity")
    p_on.add_argument("mode", nargs="?", choices=MODE_NAMES, default=None)
    p_on.add_argument("--intensity", type=int, choices=range(0, 101), metavar="0-100", default=None)

    sub.add_parser("off", help="disable Ponytail")

    p_set = sub.add_parser("set", help="set intensity mode or level")
    p_set.add_argument("mode", nargs="?", choices=MODE_NAMES, default=None)
    p_set.add_argument("--intensity", type=int, choices=range(0, 101), metavar="0-100", default=None)

    sub.add_parser("status", help="show effective config")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = load()

    if args.command == "on":
        cmd_on(data, args)
    elif args.command == "off":
        cmd_off(data, args)
    elif args.command == "set":
        cmd_set(data, args)
    elif args.command == "status":
        result = cmd_status(data)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0

    # After mutation, show status
    result = cmd_status(data)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
