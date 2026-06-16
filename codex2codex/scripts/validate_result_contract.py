#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


PROGRESS_CUES = (
    "i will inspect",
    "i'll inspect",
    "i am inspecting",
    "i'm inspecting",
    "i will check",
    "i'll check",
    "i am checking",
    "i'm checking",
    "i will look",
    "i'll look",
    "i need to inspect",
    "i need to check",
    "我将检查",
    "我会检查",
    "我将先检查",
    "我会先检查",
    "正在检查",
    "我先检查",
    "先检查",
    "接下来检查",
)

HEADING_RE = re.compile(r"(?m)^#{1,6}\s+\S+")


def _looks_progress_only(text: str, required_markers: list[str], window_chars: int) -> bool:
    """Reject status notes without rejecting real artifacts that quote progress phrases."""
    stripped = text.strip()
    if not stripped:
        return True

    headings = HEADING_RE.findall(stripped)
    missing_required = [marker for marker in required_markers if marker not in stripped]
    head = stripped[:window_chars].casefold()
    has_progress_cue = any(cue.casefold() in head for cue in PROGRESS_CUES)
    if has_progress_cue and len(headings) < 2:
        return True

    if headings and not missing_required:
        return False

    if has_progress_cue and (missing_required or not headings):
        return True

    first_lines = [line.strip() for line in stripped.splitlines()[:6] if line.strip()]
    if not headings and first_lines:
        short_status = " ".join(first_lines).casefold()
        if any(cue.casefold() in short_status for cue in PROGRESS_CUES):
            return True

    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a worker result against a simple text contract.")
    parser.add_argument("result_path", type=Path)
    parser.add_argument("--min-chars", type=int, default=400)
    parser.add_argument("--must-contain", action="append", default=[])
    parser.add_argument("--must-not-contain", action="append", default=[])
    parser.add_argument(
        "--reject-progress-only",
        action="store_true",
        help="Reject status/progress notes while allowing real artifacts that mention progress phrases.",
    )
    parser.add_argument(
        "--progress-window-chars",
        type=int,
        default=800,
        help="Prefix window used by --reject-progress-only.",
    )
    parser.add_argument(
        "--min-heading-count",
        type=int,
        default=0,
        help="Require at least this many Markdown headings.",
    )
    args = parser.parse_args()

    try:
        text = args.result_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INVALID: cannot read result: {exc}", file=sys.stderr)
        return 1

    stripped = text.strip()
    if len(stripped) < args.min_chars:
        print(f"INVALID: result too short ({len(stripped)} < {args.min_chars})", file=sys.stderr)
        return 1

    missing = [needle for needle in args.must_contain if needle not in text]
    if missing:
        print(f"INVALID: missing required text: {missing}", file=sys.stderr)
        return 1

    if args.min_heading_count:
        heading_count = len(HEADING_RE.findall(text))
        if heading_count < args.min_heading_count:
            print(
                f"INVALID: too few Markdown headings ({heading_count} < {args.min_heading_count})",
                file=sys.stderr,
            )
            return 1

    if args.reject_progress_only and _looks_progress_only(text, args.must_contain, args.progress_window_chars):
        print("INVALID: result looks like a progress/status note, not the requested artifact", file=sys.stderr)
        return 1

    forbidden = [needle for needle in args.must_not_contain if needle in text]
    if forbidden:
        print(f"INVALID: contains forbidden text: {forbidden}", file=sys.stderr)
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
