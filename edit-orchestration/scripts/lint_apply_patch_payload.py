#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

BEGIN = "*** Begin Patch"
END = "*** End Patch"
HUNK_PREFIXES = (
    "*** Add File: ",
    "*** Update File: ",
    "*** Delete File: ",
)
ALLOWED_DIRECTIVES = HUNK_PREFIXES + (
    "*** Move to: ",
    "*** End of File",
    END,
)


def _is_hunk_start(line: str) -> bool:
    return line.startswith(HUNK_PREFIXES)


def lint_payload(text: str) -> list[str]:
    errors: list[str] = []
    stripped = text.strip()
    if not stripped:
        return ["payload is empty"]
    if stripped.startswith(("{", "[")):
        errors.append("payload looks like JSON; apply_patch expects raw freeform patch text")
    if "```" in text:
        errors.append("payload contains markdown fences; send only the raw patch")

    lines = text.splitlines()
    if not lines or lines[0] != BEGIN:
        errors.append(f"first line must be exactly {BEGIN!r}")
    end_indices = [index for index, line in enumerate(lines) if line == END]
    if not end_indices:
        errors.append(f"missing final {END!r}")
        end_index = len(lines)
    else:
        end_index = end_indices[-1]
        for line in lines[end_index + 1 :]:
            if line.strip():
                errors.append("non-empty text appears after *** End Patch")
                break

    add_file: str | None = None
    add_file_has_line = False
    saw_hunk = False

    for lineno, line in enumerate(lines[1:end_index], 2):
        if _is_hunk_start(line):
            if add_file is not None and not add_file_has_line:
                errors.append(f"{add_file}: Add File hunk has no added lines")
            saw_hunk = True
            if line.startswith("*** Add File: "):
                add_file = line.removeprefix("*** Add File: ").strip()
                add_file_has_line = False
            else:
                add_file = None
                add_file_has_line = False
            continue

        if line.startswith("*** "):
            if not line.startswith(ALLOWED_DIRECTIVES):
                errors.append(f"line {lineno}: unknown patch directive: {line}")
            if line == END:
                break
            continue

        if add_file is not None:
            if not line.startswith("+"):
                errors.append(f"line {lineno}: Add File lines must start with '+', including blank lines")
            else:
                add_file_has_line = True

    if add_file is not None and not add_file_has_line:
        errors.append(f"{add_file}: Add File hunk has no added lines")
    if not saw_hunk:
        errors.append("payload has no Add/Update/Delete file hunk")

    return errors


def run_self_test() -> list[str]:
    errors: list[str] = []
    valid = """*** Begin Patch
*** Add File: /tmp/example.txt
+first
+
+third
*** Update File: /tmp/existing.txt
@@
 old
-before
+after
 old
*** End Patch
"""
    cases = [
        ("valid", valid, True),
        ("missing plus", valid.replace("+first", "first", 1), False),
        ("missing end", valid.replace("*** End Patch\n", ""), False),
        ("json wrapper", '{"cmd": "*** Begin Patch"}', False),
        ("markdown fence", "```diff\n" + valid + "```\n", False),
    ]
    with tempfile.TemporaryDirectory(prefix="apply-patch-lint-") as tmp:
        for index, (name, text, should_pass) in enumerate(cases, 1):
            path = Path(tmp) / f"case-{index}.patch"
            path.write_text(text, encoding="utf-8")
            lint_errors = lint_payload(path.read_text(encoding="utf-8"))
            passed = not lint_errors
            if passed != should_pass:
                detail = "; ".join(lint_errors) if lint_errors else "unexpected pass"
                errors.append(f"{name}: expected pass={should_pass}, got pass={passed}: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an apply_patch freeform payload before submitting it.")
    parser.add_argument("payload", nargs="?", type=Path, help="Patch payload file. Reads stdin when omitted.")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
    else:
        text = args.payload.read_text(encoding="utf-8") if args.payload else sys.stdin.read()
        errors = lint_payload(text)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
