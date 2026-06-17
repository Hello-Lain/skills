#!/usr/bin/env python3
"""Track and clean literature-rag outputs in the caller working directory."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

MANIFEST = ".literature-rag-last-output.json"
OWNED_MARKERS = (
    "**Query:**",
    "**Selection rule:**",
    "Core mechanism:",
    "Core contribution:",
    "Pseudocode and formula design:",
    "Why useful / transferable insight:",
    "Formula evidence:",
    "Verification source:",
    "## Handoff",
    "# Candidate Literature From demo.rag.ac.cn",
)


def manifest_path(workdir: str) -> Path:
    return Path(workdir).resolve() / MANIFEST


def load_manifest(workdir: str) -> list[Path]:
    path = manifest_path(workdir)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    files = data.get("files") if isinstance(data, dict) else []
    if not isinstance(files, list):
        return []
    root = Path(workdir).resolve()
    paths: list[Path] = []
    for item in files:
        candidate = Path(str(item)).resolve()
        if root == candidate or root in candidate.parents:
            paths.append(candidate)
    return paths


def owned_markdown_files(workdir: str) -> list[Path]:
    root = Path(workdir).resolve()
    owned: list[Path] = []
    for path in root.glob("*.md"):
        if not path.is_file():
            continue
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:12000]
        except OSError:
            continue
        marker_hits = sum(1 for marker in OWNED_MARKERS if marker in head)
        if marker_hits >= 3 or "# Candidate Literature From demo.rag.ac.cn" in head:
            owned.append(path)
    return owned

def owned_audit_files(workdir: str) -> list[Path]:
    root = Path(workdir).resolve()
    owned: list[Path] = []
    for path in root.glob("*.audit.json"):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and {"query", "papers", "excluded_candidates"} <= set(data):
            owned.append(path)
    return owned

def cleanup(workdir: str, owned_md: bool = False) -> None:
    targets = set(load_manifest(workdir))
    if owned_md:
        targets.update(owned_markdown_files(workdir))
        targets.update(owned_audit_files(workdir))
    for path in targets:
        if path.exists() and path.is_file():
            path.unlink()
    path = manifest_path(workdir)
    if path.exists():
        path.unlink()


def register(workdir: str, files: list[str]) -> None:
    root = Path(workdir).resolve()
    kept: list[str] = []
    for item in files:
        candidate = Path(item).resolve()
        if root == candidate or root in candidate.parents:
            kept.append(str(candidate))
    manifest_path(workdir).write_text(json.dumps({"files": kept}, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean/register literature-rag round outputs.")
    parser.add_argument("--workdir", default=os.getcwd())
    parser.add_argument(
        "--owned-md",
        action="store_true",
        help="During cleanup, also delete top-level Markdown files that contain literature-rag output markers.",
    )
    parser.add_argument("command", choices=["cleanup", "register"])
    parser.add_argument("files", nargs="*")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "cleanup":
        cleanup(args.workdir, owned_md=args.owned_md)
    else:
        register(args.workdir, args.files)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
