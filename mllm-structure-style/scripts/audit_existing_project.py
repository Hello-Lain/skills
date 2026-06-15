#!/usr/bin/env python3
"""Audit an existing MLLM repo before migrating it to the template structure."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any

PY_SKIP_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", "build", "dist"}
CONFIG_GROUPS = {
    "configs/data",
    "configs/model",
    "configs/method",
    "configs/env",
    "configs/paths",
    "configs/hydra",
    "configs/extras",
    "configs/logger",
    "configs/debug",
    "configs/experiment",
}

def _is_skipped(path: Path) -> bool:
    return any(part in PY_SKIP_PARTS for part in path.parts)

def _iter_python(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if not _is_skipped(path.relative_to(root)))

def _safe_parse(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return None

def _module_hints(path: Path, tree: ast.AST | None) -> list[str]:
    if tree is None:
        return ["unparsed"]
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    hints: list[str] = []
    if "dataset" in text or "dataloader" in text:
        hints.append("data")
    if "from_pretrained" in text or "automodel" in text or "autoprocessor" in text:
        hints.append("models")
    if "generate" in text or "decode" in text or "forward" in text:
        hints.append("methods")
    if "torch.distributed" in text or "torchrun" in text or "all_gather" in text:
        hints.append("utils/dist_or_entry")
    if "hydra.main" in text or "argparse" in text:
        hints.append("entry")
    return sorted(set(hints))

def _violations(path: Path, tree: ast.AST | None) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    if ".cuda(" in text or ".cuda()" in text:
        problems.append("cuda")
    if re.search(r'["\']/(mnt|data|home|workspace|scratch)/', text):
        problems.append("hardcoded_abs_path")
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                problems.append("print")
                break
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                missing_arg_hints = any(
                    arg.arg not in {"self", "cls"} and arg.annotation is None for arg in node.args.args
                )
                if node.returns is None or missing_arg_hints:
                    problems.append("missing_type_hints")
                    break
    return sorted(set(problems))

def audit(root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in _iter_python(root):
        tree = _safe_parse(path)
        rel = path.relative_to(root)
        hints = _module_hints(path, tree)
        problems = _violations(path, tree)
        if hints or problems:
            files.append({"path": str(rel), "hints": hints, "violations": problems})

    missing_groups = sorted(group for group in CONFIG_GROUPS if not (root / group).exists())
    candidate_entrypoints = [
        item["path"]
        for item in files
        if "entry" in item["hints"] or Path(item["path"]).name in {"infer.py", "eval.py", "main.py"}
    ]

    return {
        "root": str(root),
        "candidate_entrypoints": candidate_entrypoints,
        "missing_config_groups": missing_groups,
        "files": files,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Audit an existing MLLM project for migration.")
    parser.add_argument("root", help="Existing project root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    report = audit(Path(args.root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"root: {report['root']}")
    print("candidate_entrypoints:")
    for item in report["candidate_entrypoints"]:
        print(f"  - {item}")
    print("missing_config_groups:")
    for item in report["missing_config_groups"]:
        print(f"  - {item}")
    print("files:")
    for item in report["files"]:
        print(
            f"  - {item['path']} hints={','.join(item['hints']) or '-'} "
            f"violations={','.join(item['violations']) or '-'}"
        )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
