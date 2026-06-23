#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PYTHON_EXTS = {".py", ".pyi"}
JS_TS_EXTS = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
JSON_EXTS = {".json"}
YAML_EXTS = {".yaml", ".yml"}
MARKDOWN_EXTS = {".md", ".mdx", ".markdown"}
JAVA_EXTS = {".java"}


def classify_file(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in PYTHON_EXTS:
        return "python"
    if suffix in JS_TS_EXTS:
        return "javascript-typescript"
    if suffix in JSON_EXTS:
        return "json"
    if suffix in YAML_EXTS:
        return "yaml"
    if suffix in MARKDOWN_EXTS:
        return "markdown"
    if suffix in JAVA_EXTS:
        return "java"
    return "generic-text"


def _fallback_allowed(*, file_class: str, tiny: bool, unique: bool, structured_op: bool, repeated_pattern: bool, prose_only: bool) -> bool:
    if not tiny or not unique or repeated_pattern or structured_op:
        return False
    return prose_only or file_class in {"markdown", "generic-text"}


def decide_route(
    *,
    path: str,
    generator_owned: bool = False,
    formatter_owned: bool = False,
    structured_op: bool = False,
    repeated_pattern: bool = False,
    tiny: bool = False,
    unique: bool = False,
    prose_only: bool = False,
    java_build_context: bool = False,
) -> dict[str, object]:
    file_class = classify_file(path)
    fallback_allowed = _fallback_allowed(
        file_class=file_class,
        tiny=tiny,
        unique=unique,
        structured_op=structured_op,
        repeated_pattern=repeated_pattern,
        prose_only=prose_only,
    )
    base = {
        "path": path,
        "file_class": file_class,
        "fallback_allowed": fallback_allowed,
    }
    if generator_owned or formatter_owned:
        return {
            **base,
            "route": "generator-owned",
            "tool": "project-owned",
            "hard_stop_if_missing": False,
            "reason": "project-owned output should be regenerated instead of manually patched",
        }
    if file_class == "python":
        if fallback_allowed:
            return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "tiny unique prose-like Python edit does not justify AST tooling"}
        return {**base, "route": "structural", "tool": "ast-grep", "hard_stop_if_missing": True, "reason": "Python edits should prefer AST-aware rewrite before text patching"}
    if file_class == "javascript-typescript":
        if fallback_allowed:
            return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "tiny unique JS/TS edit qualifies for strict fallback"}
        tool = "jscodeshift" if (structured_op or repeated_pattern or not prose_only) else "ast-grep"
        return {**base, "route": "structural", "tool": tool, "hard_stop_if_missing": True, "reason": "JS/TS edits should prefer codemod or AST rewrite routes"}
    if file_class == "json":
        if fallback_allowed:
            return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "tiny unique formatting-preserving JSON edit qualifies for strict fallback"}
        return {**base, "route": "structured-data", "tool": "jq", "hard_stop_if_missing": True, "reason": "JSON field/value edits should use parser-aware transforms"}
    if file_class == "yaml":
        if fallback_allowed:
            return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "tiny unique YAML prose/format edit qualifies for strict fallback"}
        return {**base, "route": "structured-data", "tool": "yq", "hard_stop_if_missing": True, "reason": "YAML key/path/value edits should use parser-aware transforms"}
    if file_class == "markdown":
        if fallback_allowed:
            return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "tiny unique prose change is cheaper than AST section rewrite"}
        return {**base, "route": "markdown-ast", "tool": "remark", "hard_stop_if_missing": True, "reason": "Markdown section, heading, list, or frontmatter edits should use AST-aware tools"}
    if file_class == "java":
        if java_build_context:
            return {**base, "route": "structural", "tool": "openrewrite", "hard_stop_if_missing": True, "reason": "Java migrations require OpenRewrite-capable build context"}
        return {**base, "route": "block", "tool": "openrewrite", "hard_stop_if_missing": True, "reason": "Java structural editing is only supported when Maven/Gradle OpenRewrite context is valid"}
    if fallback_allowed:
        return {**base, "route": "strict-text-fallback", "tool": "apply_patch", "hard_stop_if_missing": False, "reason": "generic text edit is tiny, unique, and low-risk"}
    return {**base, "route": "block", "tool": "manual-review", "hard_stop_if_missing": True, "reason": "unknown file class needs explicit route reasoning before editing"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify the primary structural-edit route for a target file.")
    parser.add_argument("--path", required=True, help="Target file path.")
    parser.add_argument("--generator-owned", action="store_true", help="Project-owned generator or formatter owns the output.")
    parser.add_argument("--formatter-owned", action="store_true", help="Formatting command owns the output.")
    parser.add_argument("--structured-op", action="store_true", help="The intent is a structured field/path/AST operation.")
    parser.add_argument("--repeated-pattern", action="store_true", help="The same syntactic pattern repeats.")
    parser.add_argument("--tiny", action="store_true", help="The edit is tiny.")
    parser.add_argument("--unique", action="store_true", help="The edit target is uniquely anchored.")
    parser.add_argument("--prose-only", action="store_true", help="The change is prose-like rather than semantic structure.")
    parser.add_argument("--java-build-context", action="store_true", help="A valid OpenRewrite-capable Maven/Gradle context exists.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    decision = decide_route(
        path=args.path,
        generator_owned=args.generator_owned,
        formatter_owned=args.formatter_owned,
        structured_op=args.structured_op,
        repeated_pattern=args.repeated_pattern,
        tiny=args.tiny,
        unique=args.unique,
        prose_only=args.prose_only,
        java_build_context=args.java_build_context,
    )
    if args.json:
        print(json.dumps(decision, indent=2, sort_keys=True))
    else:
        print(f"{decision['route']} -> {decision['tool']}: {decision['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
