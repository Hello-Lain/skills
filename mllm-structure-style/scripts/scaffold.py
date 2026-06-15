#!/usr/bin/env python3
"""Scaffold an MLLM inference project from the bundled template."""

from __future__ import annotations

import argparse
import compileall
import contextlib
import importlib.util
import io
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "mllm-infer-template"
TEXT_SUFFIXES = {
    ".cfg",
    ".gitignore",
    ".ini",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {".editorconfig", ".gitignore"}


def _project_slug(name: str) -> str:
    return name.strip().replace("_", "-").replace(" ", "-").lower()


def _package_name(name: str) -> str:
    return _project_slug(name).replace("-", "_")


def _is_text(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name in TEXT_NAMES


def _render(text: str, *, project_name: str) -> str:
    values = {
        "{{PROJECT_NAME}}": project_name,
        "{{PACKAGE_NAME}}": _package_name(project_name),
    }
    for key, value in values.items():
        text = text.replace(key, value)
    return text


def _ensure_target(root: Path, *, force: bool) -> int:
    if root.exists() and not root.is_dir():
        print(f"error: target exists and is not a directory: {root}", file=sys.stderr)
        return 2
    if root.exists() and any(root.iterdir()) and not force:
        print(f"error: target is not empty: {root} (use --force)", file=sys.stderr)
        return 2
    root.mkdir(parents=True, exist_ok=True)
    return 0


def _copy_template(root: Path, *, project_name: str) -> list[Path]:
    if not TEMPLATE_ROOT.exists():
        raise FileNotFoundError(f"missing template root: {TEMPLATE_ROOT}")

    written: list[Path] = []
    for source in sorted(TEMPLATE_ROOT.rglob("*")):
        relative = source.relative_to(TEMPLATE_ROOT)
        destination = root / relative
        if source.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        if _is_text(source):
            text = source.read_text(encoding="utf-8")
            destination.write_text(_render(text, project_name=project_name), encoding="utf-8", newline="\n")
        else:
            shutil.copy2(source, destination)

        if source.suffix == ".sh" or source.name == "scaffold.py":
            mode = destination.stat().st_mode
            destination.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        written.append(destination)
    return written


def _has_unrendered_placeholders(root: Path) -> list[Path]:
    offenders: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and _is_text(path):
            text = path.read_text(encoding="utf-8")
            if "{{PROJECT_NAME}}" in text or "{{PACKAGE_NAME}}" in text:
                offenders.append(path)
    return offenders

def _can_run_hydra_compose() -> bool:
    required = ("hydra", "rootutils", "torch", "omegaconf")
    return all(importlib.util.find_spec(module) is not None for module in required)


def _selftest() -> int:
    with tempfile.TemporaryDirectory(prefix="mllm_structure_style_") as tmp:
        target = Path(tmp) / "demo-project"
        rc = main([str(target), "--name", "demo-project"])
        assert rc == 0, rc
        assert compileall.compile_file(SKILL_ROOT / "scripts" / "audit_existing_project.py", quiet=1)

        required = [
            target / ".env.example",
            target / ".project-root",
            target / "configs" / "debug" / "default.yaml",
            target / "configs" / "experiment" / "mock_smoke.yaml",
            target / "configs" / "experiment" / "vlmeval_smoke.yaml",
            target / "configs" / "extras" / "default.yaml",
            target / "configs" / "eval.yaml",
            target / "configs" / "infer.yaml",
            target / "configs" / "hparams_search" / "method_optuna.yaml",
            target / "configs" / "hydra" / "default.yaml",
            target / "configs" / "eval_tasks" / "default.yaml",
            target / "configs" / "logger" / "jsonl.yaml",
            target / "configs" / "logger" / "null.yaml",
            target / "configs" / "logger" / "wandb.yaml",
            target / "configs" / "local" / "default.yaml.example",
            target / "configs" / "method" / "standard.yaml",
            target / "configs" / "paths" / "default.yaml",
            target / "scripts" / "run_eval.sh",
            target / "scripts" / "run_infer.sh",
            target / "scripts" / "run_single.sh",
            target / "scripts" / "run_dist.sh",
            target / "src" / "adapters" / "vlmeval_adapter.py",
            target / "src" / "eval.py",
            target / "src" / "infer.py",
            target / "src" / "methods" / "base_method.py",
            target / "src" / "models" / "base.py",
            target / "src" / "utils" / "experiment_logger.py",
            target / "src" / "utils" / "rich_utils.py",
            target / "src" / "utils" / "task_utils.py",
            target / "tests" / "test_eval_orchestration.py",
            target / "tests" / "test_mock_infer.py",
            target / "tests" / "test_vlmeval_adapter.py",
            target / "pyproject.toml",
        ]
        missing = [str(path) for path in required if not path.exists()]
        assert not missing, missing

        assert target.joinpath("scripts", "run_single.sh").stat().st_mode & stat.S_IXUSR
        assert target.joinpath("scripts", "run_eval.sh").stat().st_mode & stat.S_IXUSR
        assert not _has_unrendered_placeholders(target)
        assert compileall.compile_dir(target / "src", quiet=1)
        subprocess.run(
            [sys.executable, str(SKILL_ROOT / "scripts" / "audit_existing_project.py"), str(target)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if _can_run_hydra_compose():
            env = os.environ.copy()
            env["PYTHONPATH"] = str(target / "src")
            subprocess.run(
                [sys.executable, "src/infer.py", "--cfg", "job"],
                cwd=target,
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert main([str(target)]) == 2

    print("selftest: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Hydra + torchrun MLLM inference project.")
    parser.add_argument("target", nargs="?", help="Target project directory.")
    parser.add_argument("--name", help="Project name. Defaults to target directory name.")
    parser.add_argument("--force", action="store_true", help="Allow writing into a non-empty target directory.")
    parser.add_argument("--selftest", action="store_true", help="Run offline scaffold self-test.")
    args = parser.parse_args(argv)

    if args.selftest:
        return _selftest()
    if not args.target:
        parser.error("target is required unless --selftest is used")

    target = Path(args.target).resolve()
    project_name = _project_slug(args.name or target.name)
    rc = _ensure_target(target, force=args.force)
    if rc != 0:
        return rc

    written = _copy_template(target, project_name=project_name)
    print(f"created: {target}")
    print(f"project: {project_name}")
    print(f"files: {len(written)}")
    print("next:")
    print("  uv sync")
    print("  uv run torchrun --nproc_per_node=1 src/infer.py")
    print("  uv run torchrun --nproc_per_node=2 src/infer.py")
    print("  uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke debug=default")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
