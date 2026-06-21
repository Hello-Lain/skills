#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

COMPLETE_RE = re.compile(r"^\s*(?:[-*]\s*)?Status\s*:\s*`?COMPLETE`?\s*$", re.IGNORECASE | re.MULTILINE)
INCOMPLETE_RE = re.compile(r"^\s*(?:[-*]\s*)?Status\s*:\s*`?INCOMPLETE`?\s*$", re.IGNORECASE | re.MULTILINE)
MATERIAL_SKILL_RE = re.compile(
    r"\b(new skill|material skill|skill-tokenless|validator/script|workflow/safety|metadata change|production report)\b",
    re.IGNORECASE,
)


def _repo_root_from_workspace(workspace: Path) -> Path:
    parts = workspace.resolve().parts
    for index, part in enumerate(parts):
        if part == ".codex" and index + 1 < len(parts) and parts[index + 1] == "work":
            return Path(*parts[:index]) if index else Path("/")
    return workspace.resolve()


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc


def _nonempty(path: Path) -> bool:
    try:
        return path.is_file() and bool(path.read_text(encoding="utf-8").strip())
    except OSError:
        return False


def _task_path(task: dict, workspace: Path) -> Path:
    raw = str(task.get("output_artifact_path") or task.get("output_artifact") or "")
    path = Path(raw)
    if path.is_absolute():
        return path
    if raw.startswith(".codex/"):
        return (_repo_root_from_workspace(workspace) / path).resolve()
    return (workspace / path).resolve()


def _is_material_skill_work(workspace: Path) -> bool:
    for name in ("plan.md", "spec.md"):
        path = workspace / name
        try:
            if MATERIAL_SKILL_RE.search(path.read_text(encoding="utf-8")):
                return True
        except OSError:
            continue
    return False


def _production_validator() -> Path:
    return Path(__file__).resolve().parents[2] / "skill-tokenless" / "scripts" / "validate_skill_production.py"


def _validate_production_report(path: Path, *, root: Path, stage: str) -> list[str]:
    validator = _production_validator()
    if not validator.is_file():
        return [f"missing production report validator: {validator}"]
    result = subprocess.run(
        [sys.executable, str(validator), str(path), "--root", str(root), "--stage", stage],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    detail = (result.stderr or result.stdout).strip()
    if not detail:
        return [f"production report validation failed: {path}"]
    return [f"production report validation failed: {line}" for line in detail.splitlines()[:8]]


def _final_report_state(path: Path) -> str:
    if not _nonempty(path):
        return "missing"
    text = path.read_text(encoding="utf-8")
    if COMPLETE_RE.search(text):
        return "complete"
    if INCOMPLETE_RE.search(text):
        return "incomplete"
    return "unknown"


def validate_workspace(
    workspace: Path,
    *,
    stage: str = "draft",
    require_production_report: bool | None = None,
    require_final_report: bool = False,
    production_report: Path | None = None,
) -> list[str]:
    workspace = workspace.resolve()
    root = _repo_root_from_workspace(workspace)
    state_path = workspace / "execution" / "tasks.json"
    final_report_path = workspace / "artifacts" / "final-report.md"
    report_path = production_report or (workspace / "artifacts" / "production-report.md")
    errors: list[str] = []

    if stage not in {"draft", "final"}:
        return [f"invalid stage: {stage}"]
    if not state_path.exists():
        return [f"missing execution task state: {state_path}"]

    try:
        state = _load_json(state_path)
    except ValueError as exc:
        return [str(exc)]

    tasks = state.get("tasks")
    if state.get("schema_version") != 1:
        errors.append(f"unsupported execution schema_version: {state.get('schema_version')}")
    if state.get("status") != "compiled":
        errors.append(f"execution state status is not compiled: {state.get('status')}")
    if not isinstance(tasks, list) or not tasks:
        errors.append("execution state has no tasks")
        tasks = []

    final_state = _final_report_state(final_report_path)
    if require_final_report or stage == "final":
        if final_state == "missing":
            errors.append(f"missing or empty final report: {final_report_path}")
        elif stage == "final" and final_state != "complete":
            errors.append(f"final stage requires final report Status: COMPLETE: {final_report_path}")

    for task in tasks:
        number = task.get("number", "<unknown>")
        role = str(task.get("role") or "").lower()
        status = str(task.get("status") or "").lower()
        artifact = _task_path(task, workspace)
        if role == "review" and stage == "draft" and status != "complete":
            continue
        if not _nonempty(artifact):
            errors.append(f"missing or empty output artifact for task {number}: {artifact}")
        if status == "complete":
            continue
        errors.append(f"task {number} status is not review-ready for {stage}: {status or 'missing'}")

    require_report = _is_material_skill_work(workspace) if require_production_report is None else require_production_report
    if require_report or report_path.exists():
        if not _nonempty(report_path):
            errors.append(f"missing or empty production report: {report_path}")
        else:
            errors.extend(_validate_production_report(report_path, root=root, stage=stage))

    return errors


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _production_report(changed: Path, *, reviewer_verdict: str | None) -> str:
    reviewer_line = "" if reviewer_verdict is None else f"- Verdict: {reviewer_verdict}\n"
    return f"""# Skill Production Report

- Skill: plan2do
- Change Type: material-update
- Verdict: PASS

## Behavior Lock
- Preserved: readiness gate validates execution artifacts before reviewer.
- Changed intentionally: production report stage can be draft.
- Fallbacks: block on missing evidence.

## Token Budget
- Before: 10 lines.
- After: 12 lines.
- Moved to references: readiness details.

## Deterministic Validators
- `python3 plan2do/scripts/pre_review_ready.py --self-test`: PASS

## Scenario Gate
- Scenario: skill workflow readiness.
- RED/control: missing artifacts fail.
- GREEN/retest: readiness passes.
- Cleanup: not launched.

## Reviewer Gate
- Mode: heavy
- Route: subagent
{reviewer_line}- Report: not saved
- Cleanup: not launched

## Reuse Attribution
| Source | URL | Borrowed idea | Component | Adoption | Target change | Rejected/why |
| --- | --- | --- | --- | --- | --- | --- |
| pre-commit | https://github.com/pre-commit/pre-commit | deterministic gate | local script | adapted | readiness gate | runtime dependency rejected |

## Changed Files
- `{changed}`

## Residual Risks
- None known.
"""


def _make_workspace(root: Path, *, stage: str, missing_report: bool = False) -> Path:
    workspace = root / "repo" / ".codex" / "work" / f"case-{stage}-{len(list(root.rglob('tasks.json')))}"
    artifacts = workspace / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    changed = workspace / "changed.md"
    changed.write_text("changed\n", encoding="utf-8")
    (workspace / "plan.md").write_text("material skill update production report\n", encoding="utf-8")
    (artifacts / "task1-execution.md").write_text("task 1\n", encoding="utf-8")
    (artifacts / "final-report.md").write_text("- Status: COMPLETE\n- Verification: self-test fixture\n", encoding="utf-8")
    tasks = [
        {
            "number": 1,
            "role": "coding",
            "status": "complete",
            "output_artifact": f".codex/work/{workspace.name}/artifacts/task1-execution.md",
        },
        {
            "number": 2,
            "role": "review",
            "status": "pending" if stage == "draft" else "complete",
            "output_artifact": f".codex/work/{workspace.name}/review.md",
        },
    ]
    if stage == "final":
        (workspace / "review.md").write_text("Verdict: PASS\n", encoding="utf-8")
    _write_json(workspace / "execution" / "tasks.json", {"schema_version": 1, "status": "compiled", "tasks": tasks})
    if not missing_report:
        reviewer_verdict = "PENDING" if stage == "draft" else "PASS"
        (artifacts / "production-report.md").write_text(
            _production_report(changed, reviewer_verdict=reviewer_verdict),
            encoding="utf-8",
        )
    return workspace


def run_self_test() -> list[str]:
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="pre-review-ready-") as tmp:
        root = Path(tmp)
        cases = [
            ("valid draft", _make_workspace(root, stage="draft"), "draft", True, True, True),
            ("valid final", _make_workspace(root, stage="final"), "final", True, True, True),
            ("missing production report", _make_workspace(root, stage="draft", missing_report=True), "draft", True, True, False),
        ]

        missing_artifact = _make_workspace(root, stage="draft")
        (missing_artifact / "artifacts" / "task1-execution.md").unlink()
        cases.append(("missing artifact", missing_artifact, "draft", True, True, False))

        pending_task = _make_workspace(root, stage="draft")
        state = _load_json(pending_task / "execution" / "tasks.json")
        state["tasks"][0]["status"] = "pending"
        _write_json(pending_task / "execution" / "tasks.json", state)
        cases.append(("pending task", pending_task, "draft", True, True, False))

        blocked_task = _make_workspace(root, stage="draft")
        (blocked_task / "artifacts" / "final-report.md").write_text("- Status: INCOMPLETE\n", encoding="utf-8")
        state = _load_json(blocked_task / "execution" / "tasks.json")
        state["tasks"][0]["status"] = "blocked"
        _write_json(blocked_task / "execution" / "tasks.json", state)
        cases.append(("blocked non-review task", blocked_task, "draft", True, True, False))

        missing_final = _make_workspace(root, stage="draft")
        (missing_final / "artifacts" / "final-report.md").unlink()
        cases.append(("missing final report", missing_final, "draft", True, True, False))

        for name, workspace, stage, require_report, require_final, should_pass in cases:
            case_errors = validate_workspace(
                workspace,
                stage=stage,
                require_production_report=require_report,
                require_final_report=require_final,
            )
            passed = not case_errors
            if passed != should_pass:
                detail = "; ".join(case_errors) if case_errors else "unexpected pass"
                errors.append(f"{name}: expected pass={should_pass}, got pass={passed}: {detail}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a plan2do workspace is ready before reviewer launch.")
    parser.add_argument("workspace", nargs="?", type=Path)
    parser.add_argument("--stage", choices=("draft", "final"), default="draft")
    parser.add_argument("--production-report", type=Path, help="Override production report path.")
    parser.add_argument("--require-production-report", action="store_true")
    parser.add_argument("--no-require-production-report", action="store_true")
    parser.add_argument("--require-final-report", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        errors = run_self_test()
    elif args.workspace:
        if args.require_production_report:
            require_report: bool | None = True
        elif args.no_require_production_report:
            require_report = False
        else:
            require_report = None
        errors = validate_workspace(
            args.workspace,
            stage=args.stage,
            require_production_report=require_report,
            require_final_report=args.require_final_report,
            production_report=args.production_report,
        )
    else:
        parser.error("provide a workspace path or --self-test")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
