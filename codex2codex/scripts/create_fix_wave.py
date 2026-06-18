#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

VERDICT_RE = re.compile(r"^\s*(?:-\s*)?(?:#{1,6}\s*)?Verdict\s*:?\s*`?(PASS|FAIL)?`?\.?\s*$", re.I)
FILE_REF_RE = re.compile(r"(?:\[([^\]\s]+):\d+[^\]]*\])|(?:\[([^\]\s]+\.[A-Za-z0-9_./-]+)\]\([^)]+\):\d+)|`([^`]+\.[A-Za-z0-9_./-]+)`")
WAVE_RE = re.compile(r"^##\s+Wave\s+(\d+)", re.M)
WAVE_HEADER_RE = re.compile(r"^##\s+(Wave\s+\d+.*)$")


def _file_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in FILE_REF_RE.finditer(text):
        ref = (match.group(1) or match.group(2) or match.group(3) or "").strip()
        if not ref or ref.startswith(".codex/") or ref.endswith(".md"):
            continue
        if ref not in refs:
            refs.append(ref)
    return refs


def _review_verdict(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = VERDICT_RE.match(line)
        if not match:
            continue
        if match.group(1):
            return match.group(1).upper()
        for next_line in lines[index + 1 :]:
            value = next_line.strip().strip("`").rstrip(".").upper()
            if value in {"PASS", "FAIL"}:
                return value
            if value:
                break
    return ""


def _next_wave_name(tasks_text: str) -> str:
    nums = [int(match.group(1)) for match in WAVE_RE.finditer(tasks_text)]
    return f"Wave {max(nums, default=0) + 1}: fix review findings"


def _repo_root(spec_dir: Path) -> Path:
    if len(spec_dir.parents) >= 3 and spec_dir.parent.name == "specs":
        return spec_dir.parents[2]
    return Path.cwd()


def _review_refs(review: Path, spec_dir: Path) -> list[str]:
    repo_root = _repo_root(spec_dir)
    refs: list[str] = []
    for candidate in (review, review.resolve()):
        for text in (str(candidate),):
            if text not in refs:
                refs.append(text)
        for base in (repo_root, spec_dir):
            try:
                rel = os.path.relpath(candidate, base)
            except ValueError:
                continue
            if rel not in refs:
                refs.append(rel)
    if review.name not in refs:
        refs.append(review.name)
    return refs


def _existing_fix_wave(tasks_text: str, refs: list[str]) -> str:
    current_wave = ""
    for line in tasks_text.splitlines():
        match = WAVE_HEADER_RE.match(line)
        if match:
            current_wave = match.group(1).strip()
            continue
        if "Fix review findings from" not in line or "- [ ]" not in line:
            continue
        if any(ref and (f"`{ref}`" in line or ref in line) for ref in refs):
            return current_wave
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a fix wave from a FAIL review artifact.")
    parser.add_argument("--spec-dir", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--verify", default="")
    args = parser.parse_args()

    review_text = args.review.read_text(encoding="utf-8")
    if _review_verdict(review_text) != "FAIL":
        print("ERROR: review verdict is not FAIL", file=sys.stderr)
        return 1

    tasks_path = args.spec_dir / "tasks.md"
    tasks_text = tasks_path.read_text(encoding="utf-8") if tasks_path.exists() else "# Tasks\n"
    existing = _existing_fix_wave(tasks_text, _review_refs(args.review, args.spec_dir))
    if existing:
        print(f"existing fix wave: {existing}")
        return 0
    wave_name = _next_wave_name(tasks_text)
    files = _file_refs(review_text)
    file_scope = ", ".join(f"`{file}`" for file in files) if files else "`<fill-file-scope>`"
    verify = args.verify or "rerun affected tests"

    task = (
        f"\n## {wave_name}\n"
        f"- [ ] [coding] Fix review findings from `{args.review}` | {file_scope} | "
        f"Verify: {verify}\n"
    )
    tasks_path.write_text(tasks_text.rstrip() + "\n" + task, encoding="utf-8")
    print(wave_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
