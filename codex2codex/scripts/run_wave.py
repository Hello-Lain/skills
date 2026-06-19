#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from roles import ALLOWED_CONTEXT_PROFILES, DEFAULT_EFFORT, ROLE_MODE

HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
VERDICT_LINE_RE = re.compile(r"^\s*(?:-\s*)?(?:#{1,6}\s*)?Verdict\s*:?\s*`?(PASS|FAIL)?`?\.?\s*$", re.I)
ARTIFACT_BODY_RE = re.compile(r"(?mis)^ARTIFACT_BODY:\s*\n(?P<body>.*)$")
PATCH_BODY_RE = re.compile(r"(?mis)^PATCH_BODY:\s*\n(?P<body>.*?)(?=^ARTIFACT_BODY:\s*|\Z)")
BLOCKED_RE = re.compile(r"(?mi)^\s*(Blocked|Cannot complete|Unable to write|could not write)\b")

TRANSIENT_API = "TRANSIENT_API"
TOOL_INFRA = "TOOL_INFRA"
PATCH_CONTEXT = "PATCH_CONTEXT"
TASK_BLOCKER = "TASK_BLOCKER"
CONTRACT_FAIL = "CONTRACT_FAIL"
INFRA_FAILED = "INFRA_FAILED"
CONTRACT_FAILED = "CONTRACT_FAILED"
TASK_BLOCKED = "TASK_BLOCKED"
RECOVERY_RETRY = "retry"
RECOVERY_STOP = "stop"
ACTIVE_WORKER_STATES = {"starting", "running"}
TERMINAL_WORKER_STATES = {"completed", "failed", "interrupted"}

RECOVERABLE_FAILURES = {TRANSIENT_API, TOOL_INFRA, PATCH_CONTEXT, CONTRACT_FAIL}
TERMINAL_FAILURES = {TASK_BLOCKER}

TRANSIENT_API_RE = re.compile(
    r"(?is)\b("
    r"provider\s+(?:timeout|timed?\s*out|unavailable)|"
    r"unavailable\s+provider|"
    r"no\s+active\s+credentials|"
    r"app[-\s]?server|"
    r"socket\s+(?:disconnect|closed|timeout|error)|"
    r"server\s+disconnect(?:ed)?|"
    r"api\s+(?:timeout|connection|server)\s+error|"
    r"rate\s*limit|"
    r"\b(?:429|5\d\d)\b|"
    r"bad\s+gateway|service\s+unavailable|gateway\s+timeout"
    r")\b"
)
TOOL_INFRA_RE = re.compile(
    r"(?is)\b("
    r"(?:worker\s+)?tool\s+backend\s+failure|"
    r"approval\s+backend\s+failure|"
    r"approval\s+review\s+failed|"
    r"apply_patch\s+backend\s+(?:unavailable|failure)|"
    r"tool\s+approval|"
    r"meight\s+(?:(?:daemon|socket)\s+)?(?:daemon|socket)\s+drift|"
    r"mcp\s+(?:server|tool).*?(?:unavailable|failed)|"
    r"tool\s+call\s+failed"
    r")\b"
)
PATCH_CONTEXT_RE = re.compile(
    r"(?is)\b("
    r"stale\s+hunk|"
    r"target\s+changed|"
    r"patch\s+context\s+mismatch|"
    r"context\s+mismatch|"
    r"failed\s+to\s+find\s+expected\s+lines|"
    r"hunk\s+(?:failed|mismatch|context)|"
    r"patch\s+does\s+not\s+apply|"
    r"cannot\s+apply\s+patch"
    r")\b"
)
TASK_BLOCKER_RE = re.compile(
    r"(?is)(^|\n)\s*QUESTION\s*:|"
    r"\b("
    r"ambiguous\s+requirement|"
    r"design\s+conflict|"
    r"writable[-\s]?scope\s+conflict|"
    r"repo[-\s]?unanswerable\s+question|"
    r"requires?\s+(?:orchestrator|user)\s+(?:decision|input)|"
    r"blocked\s+on\s+(?:scope|requirements?|decision)"
    r")\b"
)
CONTRACT_FAIL_RE = re.compile(
    r"(?is)\b("
    r"missing\s+(?:output\s+)?artifact|"
    r"blocked\s+artifact|"
    r"missing\s+review\s+verdict|"
    r"no\s+verdict|"
    r"missing\s+expected\s+(?:file\s+change|implementation\s+evidence)|"
    r"no\s+(?:scoped\s+)?diff|"
    r"result\s+reports\s+blocked|"
    r"output\s+artifact\s+reports\s+blocked"
    r")\b"
)

TERMINAL_BY_FAILURE = {
    TRANSIENT_API: INFRA_FAILED,
    TOOL_INFRA: INFRA_FAILED,
    PATCH_CONTEXT: CONTRACT_FAILED,
    CONTRACT_FAIL: CONTRACT_FAILED,
    TASK_BLOCKER: TASK_BLOCKED,
}


@dataclass(frozen=True)
class RecoveryDecision:
    category: str
    action: str
    terminal_category: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class PatchFallbackResult:
    applied: bool = False
    paths: tuple[str, ...] = ()
    category: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    category: str | None = None
    reason: str = ""


def classify_failure_text(text: str) -> str | None:
    if not text:
        return None
    if TASK_BLOCKER_RE.search(text):
        return TASK_BLOCKER
    if PATCH_CONTEXT_RE.search(text):
        return PATCH_CONTEXT
    if CONTRACT_FAIL_RE.search(text):
        return CONTRACT_FAIL
    if TOOL_INFRA_RE.search(text):
        return TOOL_INFRA
    if TRANSIENT_API_RE.search(text):
        return TRANSIENT_API
    return None


def classify_worker_failure(
    *,
    status: dict | None = None,
    result: str = "",
    validation_output: str = "",
) -> str | None:
    parts = [result, validation_output]
    if status:
        for key in (
            "failure_detail",
            "needs_input_detail",
            "stalled_reason",
            "last_error",
            "error",
        ):
            value = status.get(key)
            if isinstance(value, str):
                parts.append(value)
        if status.get("needs_input_source") == "question":
            parts.append("QUESTION: worker needs orchestrator input")
    return classify_failure_text("\n".join(part for part in parts if part))


def classify_contract_failure(
    *,
    artifact_missing: bool = False,
    missing_verdict: bool = False,
    missing_diff: bool = False,
    blocked_artifact: bool = False,
) -> str | None:
    if artifact_missing or missing_verdict or missing_diff or blocked_artifact:
        return CONTRACT_FAIL
    return None


def recovery_decision(category: str | None, *, attempts: int, max_attempts: int) -> RecoveryDecision:
    failure = category or TOOL_INFRA
    terminal = TERMINAL_BY_FAILURE.get(failure, INFRA_FAILED)
    if failure in TERMINAL_FAILURES:
        return RecoveryDecision(failure, RECOVERY_STOP, terminal, "task requires orchestrator input")
    if attempts < max_attempts:
        return RecoveryDecision(failure, RECOVERY_RETRY, None, "recovery budget available")
    return RecoveryDecision(failure, RECOVERY_STOP, terminal, "recovery budget exhausted")


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}") from exc


def _repo_root(spec_dir: Path) -> Path:
    if len(spec_dir.parents) >= 3 and spec_dir.parent.name == "specs":
        return spec_dir.parents[2]
    return Path.cwd()


def _prepare(spec_dir: Path, wave: str, profile: str, include_completed: bool = False) -> Path:
    script = Path(__file__).with_name("prepare_wave.py")
    cmd = [sys.executable, str(script), "--spec-dir", str(spec_dir), "--wave", wave, "--profile", profile]
    if include_completed:
        cmd.append("--include-completed")
    proc = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        raise SystemExit(proc.returncode)
    return Path((proc.stdout or "").strip().splitlines()[-1])


def _run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["MEIGHT_HOME"] = str(meight_home)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )

def _shutdown_workers(meight: str, meight_home: Path, cwd: Path) -> None:
    proc = _run([meight, "shutdown"], meight_home, cwd, capture=True)
    if proc.returncode == 0:
        return
    sys.stderr.write(proc.stderr or proc.stdout or "")
    force_proc = _run([meight, "shutdown", "--force"], meight_home, cwd, capture=True)
    if force_proc.stdout:
        print(force_proc.stdout.strip())
    if force_proc.stderr:
        sys.stderr.write(force_proc.stderr)


def _start_worker(worker: dict, meight_home: Path, cwd: Path, meight: str, *, name: str | None = None) -> str:
    worker_name = name or worker["name"]
    cmd = [
        meight,
        "start",
        worker_name,
        "--brief-file",
        worker["brief"],
        "--cwd",
        str(cwd),
        "--sandbox",
        worker.get("sandbox") or "ws",
        "--effort",
        worker.get("effort") or ROLE_MODE.get(worker.get("role"), ("implement", "ws", DEFAULT_EFFORT))[2],
    ]
    proc = _run(cmd, meight_home, cwd, capture=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"ERROR: failed to start worker {worker_name}")
    return worker_name


def _start_workers(manifest: dict, meight_home: Path, cwd: Path, meight: str) -> list[str]:
    names: list[str] = []
    for worker in manifest.get("workers", []):
        names.append(_start_worker(worker, meight_home, cwd, meight))
    return names


def _wait_worker_once(name: str, meight_home: Path, cwd: Path, meight: str, timeout: int) -> int:
    proc = _run([meight, "wait", name, "--timeout", str(timeout)], meight_home, cwd, capture=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        print(f"ERROR: worker {name} wait exit {proc.returncode}", file=sys.stderr)
    return proc.returncode


def _worker_status(meight_home: Path, name: str, cwd: Path, meight: str) -> dict:
    proc = _run([meight, "status", name, "--json"], meight_home, cwd, capture=True)
    if proc.returncode != 0:
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        return {}
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def _run_worker_control(cmd: list[str], meight_home: Path, cwd: Path) -> int:
    proc = _run(cmd, meight_home, cwd, capture=True)
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def _recovery_brief(worker_name: str, category: str | None, reason: str) -> str:
    return "\n".join(
        [
            "[run_wave recovery]",
            f"Previous attempt for `{worker_name}` failed with category `{category or TOOL_INFRA}`.",
            f"Observed reason: {reason or 'recovery checkpoint'}",
            "Continue the original task in the original scope.",
            "Write the required output artifact. Use QUESTION only for a required orchestrator decision.",
        ]
    )


def _steer_brief(worker_name: str, reason: str) -> str:
    return (
        f"run_wave recovery checkpoint for `{worker_name}`: {reason or 'no recent activity'}. "
        "Continue, finish the scoped task, and write the required artifact; if truly blocked, end with QUESTION."
    )


def _copy_worker_outcome(meight_home: Path, source: str, dest: str) -> None:
    if source == dest:
        return
    source_dir = meight_home / "workers" / source
    dest_dir = meight_home / "workers" / dest
    dest_dir.mkdir(parents=True, exist_ok=True)
    status_path = source_dir / "status.json"
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            status["name"] = dest
            (dest_dir / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            shutil.copy2(status_path, dest_dir / "status.json")
    for fname in ("result.md", "events.log"):
        source_path = source_dir / fname
        if source_path.exists():
            shutil.copy2(source_path, dest_dir / fname)


def _print_recovery_exhausted(name: str, decision: RecoveryDecision) -> None:
    print(
        "ERROR: worker "
        f"{name} recovery exhausted: terminal_category={decision.terminal_category} "
        f"failure_category={decision.category} reason={decision.reason}",
        file=sys.stderr,
    )


def _strip_fence(text: str) -> str:
    match = re.fullmatch(r"(?ms)\s*```[A-Za-z0-9_-]*\s*\n(.*?)\n```\s*", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_patch_body(result: str) -> str:
    marker = PATCH_BODY_RE.search(_clean_result_text(result))
    if not marker:
        return ""
    return _strip_fence(marker.group("body"))


def _patch_format(body: str) -> str:
    if re.search(r"(?m)^\*\*\* Begin Patch\s*$", body):
        return "apply_patch"
    if re.search(r"(?m)^(?:diff --git |--- |\+\+\+ )", body):
        return "unified"
    return ""


def _strip_diff_path_prefix(path_text: str) -> str:
    text = path_text.strip()
    if "\t" in text:
        text = text.split("\t", 1)[0].strip()
    if text in {"/dev/null", "dev/null"}:
        return ""
    if text.startswith(("a/", "b/")):
        return text[2:]
    return text


def _normalize_patch_path(path_text: str) -> str:
    text = _strip_diff_path_prefix(path_text)
    if not text:
        raise ValueError("PATCH_BODY path is empty")
    if "\\" in text:
        raise ValueError(f"PATCH_BODY path uses backslashes: `{text}`")
    path = PurePosixPath(text)
    if path.is_absolute():
        raise ValueError(f"PATCH_BODY uses absolute path: `{text}`")
    if ".." in path.parts:
        raise ValueError(f"PATCH_BODY uses path traversal: `{text}`")
    parts = [part for part in path.parts if part and part != "."]
    normalized = PurePosixPath(*parts).as_posix() if parts else ""
    if not normalized:
        raise ValueError("PATCH_BODY path is empty")
    return normalized


def _patch_paths(body: str) -> tuple[str, ...]:
    paths: list[str] = []
    if _patch_format(body) == "apply_patch":
        pattern = r"(?m)^\*\*\* (?:Add File|Delete File|Update File|Move to):\s*(.+?)\s*$"
        paths.extend(match.group(1) for match in re.finditer(pattern, body))
    else:
        for line in body.splitlines():
            if line.startswith("diff --git "):
                parts = line.split()
                if len(parts) >= 4:
                    paths.extend([parts[2], parts[3]])
                continue
            if line.startswith(("--- ", "+++ ")):
                paths.append(line[4:].strip())

    normalized: list[str] = []
    for path in paths:
        try:
            value = _normalize_patch_path(path)
        except ValueError as exc:
            if str(exc) == "PATCH_BODY path is empty":
                continue
            raise
        if value and value not in normalized:
            normalized.append(value)
    if not normalized:
        raise ValueError("PATCH_BODY has no recognizable file paths")
    return tuple(normalized)


def _scope_allows_child(scope: str, root: Path | None = None, *, explicit_dir: bool = False) -> bool:
    if explicit_dir:
        return True
    if root is None:
        return False
    return (root / scope).is_dir()

def _normalized_scope_entries(raw_scope: list[str], root: Path | None = None) -> tuple[tuple[str, bool], ...]:
    entries: list[tuple[str, bool]] = []
    seen: set[tuple[str, bool]] = set()
    for raw_path in raw_scope:
        explicit_dir = raw_path.strip().endswith("/")
        scope = _normalize_patch_path(raw_path)
        entry = (scope, _scope_allows_child(scope, root, explicit_dir=explicit_dir))
        if entry not in seen:
            entries.append(entry)
            seen.add(entry)
    return tuple(entries)

def _validate_patch_scope(worker: dict, paths: tuple[str, ...], cwd: Path | None = None) -> tuple[str, ...]:
    raw_scope = [path for path in worker.get("files", []) if path]
    if not raw_scope:
        raise ValueError("PATCH_BODY rejected: worker has no writable scope")
    allowed = _normalized_scope_entries(raw_scope, cwd)
    for path in paths:
        in_scope = False
        for scope, allow_child in allowed:
            if path == scope or (allow_child and path.startswith(scope + "/")):
                in_scope = True
                break
        if not in_scope:
            raise ValueError(f"PATCH_BODY path outside writable scope: `{path}`")
    return paths


def _snapshot_paths(cwd: Path, paths: tuple[str, ...]) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for rel_path in paths:
        path = cwd / rel_path
        try:
            snapshot[rel_path] = path.read_bytes()
        except OSError:
            snapshot[rel_path] = None
    return snapshot


def _changed_paths(cwd: Path, before: dict[str, bytes | None]) -> tuple[str, ...]:
    changed: list[str] = []
    for rel_path, old_bytes in before.items():
        path = cwd / rel_path
        try:
            new_bytes = path.read_bytes()
        except OSError:
            new_bytes = None
        if new_bytes != old_bytes:
            changed.append(rel_path)
    return tuple(changed)


def _patch_apply_command(body: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    if _patch_format(body) == "apply_patch":
        apply_patch = shutil.which("apply_patch")
        if not apply_patch:
            return subprocess.CompletedProcess(["apply_patch"], 127, "", "apply_patch command not found")
        return subprocess.run(
            [apply_patch],
            cwd=str(cwd),
            input=body,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    check_proc = subprocess.run(
        ["git", "apply", "--check", "--whitespace=nowarn", "-"],
        cwd=str(cwd),
        input=body,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check_proc.returncode != 0:
        return check_proc
    return subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "-"],
        cwd=str(cwd),
        input=body,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _record_patch_fallback_status(meight_home: Path, worker_name: str, paths: tuple[str, ...]) -> None:
    worker_dir = meight_home / "workers" / worker_name
    worker_dir.mkdir(parents=True, exist_ok=True)
    status_path = worker_dir / "status.json"
    status: dict = {}
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            status = {}
    changed = list(status.get("files_changed") or [])
    for path in paths:
        if path not in changed:
            changed.append(path)
    status.update(
        {
            "name": worker_name,
            "state": "completed",
            "files_changed": changed,
            "patch_body_fallback": True,
        }
    )
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")


def _apply_worker_patch_body(worker: dict, meight_home: Path, worker_name: str, cwd: Path, result: str) -> PatchFallbackResult:
    if worker.get("mode") == "review":
        return PatchFallbackResult()
    body = _extract_patch_body(result)
    if not body:
        return PatchFallbackResult()
    if not _patch_format(body):
        return PatchFallbackResult(category=CONTRACT_FAIL, reason="PATCH_BODY format is not supported")

    try:
        paths = _validate_patch_scope(worker, _patch_paths(body), cwd)
    except ValueError as exc:
        return PatchFallbackResult(category=CONTRACT_FAIL, reason=str(exc))

    before = _snapshot_paths(cwd, paths)
    proc = _patch_apply_command(body, cwd)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "patch does not apply").strip()
        return PatchFallbackResult(category=PATCH_CONTEXT, reason=f"PATCH_BODY apply failed: {detail}")

    changed = _changed_paths(cwd, before)
    if not changed:
        return PatchFallbackResult(category=CONTRACT_FAIL, reason="PATCH_BODY produced no file changes")

    _record_patch_fallback_status(meight_home, worker_name, changed)
    print(f"applied PATCH_BODY for {worker_name}: {', '.join(changed)}")
    return PatchFallbackResult(applied=True, paths=changed)


def _finish_worker_or_patch_failure(
    worker: dict,
    meight_home: Path,
    active_name: str,
    original_name: str,
    cwd: Path,
) -> PatchFallbackResult | None:
    result = _worker_result(meight_home, active_name)
    patch_result = _apply_worker_patch_body(worker, meight_home, active_name, cwd, result)
    if patch_result.category:
        return patch_result
    _copy_worker_outcome(meight_home, active_name, original_name)
    return None

def _worker_artifact_path(cwd: Path, worker: dict) -> Path | None:
    output = worker.get("output")
    if not output:
        return None
    path = Path(output)
    return path if path.is_absolute() else cwd / path

def _salvage_worker_artifact(worker: dict, cwd: Path, worker_name: str, result: str) -> None:
    artifact = _worker_artifact_path(cwd, worker)
    if not artifact or _artifact_exists(artifact):
        return
    body = (
        _review_artifact_body(worker_name, result)
        if worker.get("mode") == "review"
        else _implementation_artifact_body(worker_name, result)
    )
    if not body:
        return
    artifact.parent.mkdir(parents=True, exist_ok=True)
    artifact.write_text(body, encoding="utf-8")
    print(f"salvaged artifact: {artifact}")

def _repo_relative_contract_path(cwd: Path, path_text: str) -> str:
    path = Path(path_text)
    try:
        if path.is_absolute():
            path = path.resolve().relative_to(cwd.resolve())
    except (OSError, ValueError):
        pass
    return path.as_posix().lstrip("./")

def _contract_scope_entries(cwd: Path, paths: list[str]) -> tuple[tuple[str, bool], ...]:
    entries: list[tuple[str, bool]] = []
    seen: set[tuple[str, bool]] = set()
    for path in paths:
        explicit_dir = path.strip().endswith("/")
        scope_path = _repo_relative_contract_path(cwd, path)
        entry = (scope_path, _scope_allows_child(scope_path, cwd, explicit_dir=explicit_dir))
        if entry not in seen:
            entries.append(entry)
            seen.add(entry)
    return tuple(entries)

def _contract_path_in_scope(changed_path: str, scope_path: str, allow_child: bool) -> bool:
    changed = changed_path.rstrip("/")
    scope = scope_path.rstrip("/")
    return changed == scope or (allow_child and changed.startswith(scope + "/"))

def _completed_worker_contract_failure(worker: dict, cwd: Path, status: dict, result: str) -> PatchFallbackResult | None:
    artifact = _worker_artifact_path(cwd, worker)
    if artifact:
        if not artifact.exists():
            return PatchFallbackResult(category=CONTRACT_FAIL, reason=f"missing output artifact: {artifact}")
        try:
            artifact_text = artifact.read_text(encoding="utf-8")
        except OSError as exc:
            return PatchFallbackResult(category=CONTRACT_FAIL, reason=f"cannot read output artifact: {artifact}: {exc}")
        if not artifact_text.strip():
            return PatchFallbackResult(category=CONTRACT_FAIL, reason=f"empty output artifact: {artifact}")
        if BLOCKED_RE.search(artifact_text):
            return PatchFallbackResult(category=CONTRACT_FAIL, reason=f"output artifact reports blocked: {artifact}")
        if worker.get("mode") == "review" and _review_verdict(artifact_text) == "UNKNOWN":
            return PatchFallbackResult(category=CONTRACT_FAIL, reason=f"missing review verdict: {artifact}")

    if worker.get("mode") != "review":
        scope = _contract_scope_entries(cwd, [path for path in worker.get("files", []) if path])
        changed = [
            _repo_relative_contract_path(cwd, path)
            for path in status.get("files_changed") or []
            if path
        ]
        if scope and not any(
            _contract_path_in_scope(changed_path, scope_path, allow_child)
            for changed_path in changed
            for scope_path, allow_child in scope
        ):
            return PatchFallbackResult(
                category=CONTRACT_FAIL,
                reason=f"missing expected implementation evidence: no scoped files_changed for {[path for path, _ in scope]}",
            )
    return None


def _wait_worker_with_recovery(
    worker: dict,
    meight_home: Path,
    cwd: Path,
    meight: str,
    timeout: int,
    *,
    same_worker_restarts: int = 1,
    fresh_worker_restarts: int = 1,
) -> int:
    original_name = worker["name"]
    active_name = original_name
    follow_attempted = False
    same_restarts = 0
    fresh_restarts = 0

    while True:
        wait_code = _wait_worker_once(active_name, meight_home, cwd, meight, timeout)
        if wait_code == 0:
            patch_failure = _finish_worker_or_patch_failure(worker, meight_home, active_name, original_name, cwd)
            result = _worker_result(meight_home, original_name)
            _salvage_worker_artifact(worker, cwd, original_name, result)
            contract_failure = _completed_worker_contract_failure(
                worker,
                cwd,
                _worker_status(meight_home, original_name, cwd, meight),
                result,
            )
            if patch_failure is None and contract_failure is None:
                return 0
            if patch_failure is None:
                patch_failure = contract_failure
            wait_code = 1
        else:
            patch_failure = None

        status = _worker_status(meight_home, active_name, cwd, meight)
        if status.get("state") in ACTIVE_WORKER_STATES and status.get("stalled"):
            reason = str(status.get("stalled_reason") or "active worker stalled")
            _run_worker_control(
                [meight, "steer", active_name, _steer_brief(original_name, reason)],
                meight_home,
                cwd,
            )
            wait_code = _wait_worker_once(active_name, meight_home, cwd, meight, timeout)
            if wait_code == 0:
                patch_failure = _finish_worker_or_patch_failure(worker, meight_home, active_name, original_name, cwd)
                result = _worker_result(meight_home, original_name)
                _salvage_worker_artifact(worker, cwd, original_name, result)
                contract_failure = _completed_worker_contract_failure(
                    worker,
                    cwd,
                    _worker_status(meight_home, original_name, cwd, meight),
                    result,
                )
                if patch_failure is None and contract_failure is None:
                    return 0
                if patch_failure is None:
                    patch_failure = contract_failure
                wait_code = 1
            if patch_failure is None and _run_worker_control([meight, "interrupt", active_name], meight_home, cwd) == 0:
                wait_code = _wait_worker_once(active_name, meight_home, cwd, meight, timeout)
            status = _worker_status(meight_home, active_name, cwd, meight)

        result = _worker_result(meight_home, active_name)
        if patch_failure is None:
            patch_result = _apply_worker_patch_body(worker, meight_home, active_name, cwd, result)
            if patch_result.applied:
                _copy_worker_outcome(meight_home, active_name, original_name)
                return 0
            if patch_result.category:
                patch_failure = patch_result

        category = patch_failure.category if patch_failure else classify_worker_failure(status=status, result=result)
        decision = recovery_decision(
            category,
            attempts=same_restarts + fresh_restarts,
            max_attempts=same_worker_restarts + fresh_worker_restarts,
        )
        if decision.action == RECOVERY_STOP:
            _print_recovery_exhausted(original_name, decision)
            return wait_code or 1

        if (
            not follow_attempted
            and category in RECOVERABLE_FAILURES
            and status.get("state") in (TERMINAL_WORKER_STATES | {"needs_input"})
        ):
            follow_attempted = True
            reason = patch_failure.reason if patch_failure else str(
                status.get("failure_detail")
                or status.get("needs_input_detail")
                or status.get("stalled_reason")
                or "terminal recoverable failure"
            )
            follow_code = _run_worker_control(
                [
                    meight,
                    "follow",
                    active_name,
                    "--brief",
                    _recovery_brief(original_name, category, reason),
                ],
                meight_home,
                cwd,
            )
            if follow_code == 0:
                continue

        if same_restarts < same_worker_restarts:
            same_restarts += 1
            active_name = original_name
            if status.get("state") in ACTIVE_WORKER_STATES:
                _run_worker_control([meight, "interrupt", active_name], meight_home, cwd)
                _wait_worker_once(active_name, meight_home, cwd, meight, timeout)
            _start_worker(worker, meight_home, cwd, meight, name=active_name)
            continue

        if fresh_restarts < fresh_worker_restarts:
            fresh_restarts += 1
            active_name = f"{original_name}-recovery-{fresh_restarts}"
            _start_worker(worker, meight_home, cwd, meight, name=active_name)
            continue

        exhausted = recovery_decision(category, attempts=1, max_attempts=1)
        _print_recovery_exhausted(original_name, exhausted)
        return wait_code or 1


def _wait_workers(
    manifest: dict,
    meight_home: Path,
    cwd: Path,
    meight: str,
    timeout: int,
    *,
    same_worker_restarts: int = 1,
    fresh_worker_restarts: int = 1,
) -> int:
    exit_code = 0
    for worker in manifest.get("workers", []):
        code = _wait_worker_with_recovery(
            worker,
            meight_home,
            cwd,
            meight,
            timeout,
            same_worker_restarts=same_worker_restarts,
            fresh_worker_restarts=fresh_worker_restarts,
        )
        if code != 0:
            exit_code = code
    return exit_code


def _worker_result(meight_home: Path, name: str) -> str:
    path = meight_home / "workers" / name / "result.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _validate(manifest_path: Path, meight_home: Path, cwd: Path) -> int:
    validator = Path(__file__).with_name("validate_wave.py")
    proc = subprocess.run(
        [sys.executable, str(validator), "--manifest", str(manifest_path), "--meight-home", str(meight_home)],
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.stdout:
        print(proc.stdout.strip())
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    return proc.returncode


def _manifest_wave(manifest_path: Path) -> str:
    manifest = _load_json(manifest_path)
    return str(manifest.get("wave") or "")


def _repo_path(manifest: dict, path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return _repo_root(Path(manifest["spec_dir"])) / path


def _artifact_exists(path: Path) -> bool:
    try:
        return path.exists() and path.read_text(encoding="utf-8").strip() != ""
    except OSError:
        return False


def _salvage_artifacts(manifest: dict, meight_home: Path) -> None:
    for worker in manifest.get("workers", []):
        if not worker.get("output"):
            continue
        artifact = _repo_path(manifest, worker["output"])
        result = _worker_result(meight_home, worker["name"]).strip()
        if not result:
            continue
        if worker.get("mode") == "review":
            body = _review_artifact_body(worker["name"], result)
        else:
            body = _implementation_artifact_body(worker["name"], result)
        if not body:
            continue
        if _artifact_exists(artifact):
            try:
                existing = artifact.read_text(encoding="utf-8")
            except OSError:
                existing = ""
            if "Salvaged-From-Worker:" not in existing:
                continue
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(body, encoding="utf-8")
        print(f"salvaged artifact: {artifact}")


def _clean_result_text(result: str) -> str:
    text = result.strip()
    turns = list(re.finditer(r"(?m)^##\s+Turn\s+\d+\b.*$", text))
    if turns:
        text = text[turns[-1].end() :].strip()
    text = re.sub(r"(?ms)\n?QUESTION:.*$", "", text).strip()
    return text


def _strip_artifact_fence(text: str) -> str:
    match = re.fullmatch(r"(?ms)\s*```(?:markdown|md)?\s*\n(.*?)\n```\s*", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_artifact_body(result: str) -> str:
    text = _clean_result_text(result)
    marker = ARTIFACT_BODY_RE.search(text)
    if marker:
        return _strip_artifact_fence(marker.group("body"))

    # Common fallback: a short blocked-write note followed by one complete
    # fenced Markdown artifact. Salvage the artifact, not the wrapper note.
    fences = re.findall(r"(?ms)```(?:markdown|md)?\s*\n(.*?)\n```", text)
    for body in reversed(fences):
        stripped = body.strip()
        if _review_verdict(stripped) in {"PASS", "FAIL"}:
            return stripped
        if re.search(r"(?mi)(changed files|verification|verified|residual risks|risks|summary)", stripped):
            return stripped
    return text


def _review_artifact_body(worker_name: str, result: str) -> str:
    if _review_verdict(result) not in {"PASS", "FAIL"}:
        return ""
    text = _extract_artifact_body(result)
    marker = re.search(r"(?mi)^Review result:\s*$", text)
    if marker:
        text = text[marker.end() :].strip()
    headings = {match.group(1).strip().lower() for match in HEADING_RE.finditer(text)}
    lines = [f"Salvaged-From-Worker: {worker_name}", ""]
    if "findings" not in headings:
        lines.extend(["### Findings"])
    lines.extend(text.splitlines())
    if "verification" not in headings and "tests" not in headings:
        lines.extend(["", "### Verification", "- See worker result; artifact was salvaged by run_wave.py after worker write failure."])
    return "\n".join(lines).rstrip() + "\n"


def _implementation_artifact_body(worker_name: str, result: str) -> str:
    text = _extract_artifact_body(result)
    if not text:
        return ""
    if re.search(r"(?mi)^\s*QUESTION\s*:", text):
        return ""
    if not re.search(r"(?mi)(changed files|verification|verified|residual risks|risks|summary)", text):
        return ""
    return f"Salvaged-From-Worker: {worker_name}\n\n{text.rstrip()}\n"


def _create_fix_waves(manifest: dict) -> list[str]:
    script = Path(__file__).with_name("create_fix_wave.py")
    spec_dir = Path(manifest["spec_dir"])
    waves: list[str] = []
    for worker in manifest.get("workers", []):
        if worker.get("mode") != "review" or not worker.get("output"):
            continue
        review_path = _repo_path(manifest, worker["output"])
        if not review_path.exists():
            continue
        proc = subprocess.run(
            [
                sys.executable,
                str(script),
                "--spec-dir",
                str(spec_dir),
                "--review",
                str(review_path),
                "--verify",
                worker.get("verify") or "rerun affected tests",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode == 0:
            message = (proc.stdout or "").strip()
            if message.startswith("existing fix wave: "):
                wave = message.split(": ", 1)[1]
                prefix = "fix wave"
            else:
                wave = message
                prefix = "created fix wave"
            if wave and wave not in waves:
                waves.append(wave)
            print(f"{prefix}: {message}")
    return waves


def _update_tasks(manifest: dict) -> None:
    tasks_path = Path(manifest["spec_dir"]) / "tasks.md"
    if not tasks_path.exists():
        return
    text = tasks_path.read_text(encoding="utf-8")
    for worker in manifest.get("workers", []):
        raw = worker.get("raw_task")
        if raw and raw in text:
            text = text.replace(raw, raw.replace("- [ ]", "- [x]", 1), 1)
    tasks_path.write_text(text, encoding="utf-8")


def _review_verdict(text: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = VERDICT_LINE_RE.match(line)
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
    return "UNKNOWN"


def _section_items(text: str, names: set[str]) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in text.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            title = heading.group(1).strip().lower()
            in_section = any(title.startswith(name) for name in names)
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if item.lower().rstrip(".") not in {"none", "n/a", "na"}:
                items.append(item)
    return items


def _inline_verification_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip().lstrip("-").strip()
        match = re.match(r"(?i)(verification|test|tests|result)\s*:\s*(.+)$", stripped)
        if match:
            item = match.group(2).strip()
            if item.lower().rstrip(".") not in {"none", "n/a", "na"}:
                items.append(item)
    return items


def _review_summary_entry(manifest: dict, worker: dict) -> str:
    output = worker.get("output") or ""
    artifact = _repo_path(manifest, output) if output else None
    if not artifact or not artifact.exists():
        return f"- `{worker['name']}` verdict=UNKNOWN critical=0 verification=missing artifact `{output}`"

    text = artifact.read_text(encoding="utf-8")
    verdict = _review_verdict(text)
    critical = len(_section_items(text, {"critical"}))
    verification_items = _section_items(text, {"verification", "tests"})
    if not verification_items or all("salvaged by run_wave.py" in item for item in verification_items):
        verification_items = _inline_verification_items(text) or verification_items
    verification = "; ".join(verification_items[:2]) if verification_items else "not reported"
    if len(verification) > 220:
        verification = verification[:217].rstrip() + "..."
    return (
        f"- `{worker['name']}` verdict={verdict} critical={critical} "
        f"verification={verification} artifact=`{output}`"
    )


def _write_review_summary(manifest: dict) -> None:
    review_workers = [worker for worker in manifest.get("workers", []) if worker.get("mode") == "review"]
    if not review_workers:
        return
    spec_dir = Path(manifest["spec_dir"])
    lines = [f"## {manifest.get('wave', 'Wave')}"]
    for worker in review_workers:
        lines.append(_review_summary_entry(manifest, worker))
    (spec_dir / "review-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _dry_run(manifest: dict) -> None:
    print(f"wave: {manifest.get('wave')}")
    for worker in manifest.get("workers", []):
        print(
            f"- {worker['name']} role={worker.get('role')} mode={worker.get('mode')} "
            f"sandbox={worker.get('sandbox')} effort={worker.get('effort')} "
            f"context_profile={worker.get('context_profile')} "
            f"files={', '.join(worker.get('files', []))} brief={worker.get('brief')}"
        )


def _new_home(cwd: Path) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"meight-{cwd.name}-"))


def _bounded_nonnegative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if parsed < 0 or parsed > 3:
        raise argparse.ArgumentTypeError("must be between 0 and 3")
    return parsed


def _meight_is_resolvable(meight: str) -> bool:
    path = Path(meight)
    if path.parent != Path("."):
        return path.is_file() and os.access(path, os.X_OK)
    return shutil.which(meight) is not None


def _manifest_has_implementation_worker(manifest: dict) -> bool:
    return any(worker.get("mode") != "review" for worker in manifest.get("workers", []))


def _preflight_manifest(manifest: dict, meight_home: Path, cwd: Path, meight: str, timeout: int) -> PreflightResult:
    if not _manifest_has_implementation_worker(manifest):
        return PreflightResult(True)
    if not _meight_is_resolvable(meight):
        return PreflightResult(False, TOOL_INFRA, f"meight executable not found: {meight}")

    try:
        meight_home.mkdir(parents=True, exist_ok=True)
        probe = meight_home / ".run_wave_preflight"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
    except OSError as exc:
        return PreflightResult(False, TOOL_INFRA, f"MEIGHT_HOME is not writable: {meight_home}: {exc}")

    env = os.environ.copy()
    env["MEIGHT_HOME"] = str(meight_home)
    try:
        proc = subprocess.run(
            [meight, "doctor", "--json"],
            cwd=str(cwd),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return PreflightResult(False, TOOL_INFRA, f"meight doctor timed out after {timeout}s")
    except OSError as exc:
        return PreflightResult(False, TOOL_INFRA, f"meight doctor failed to start: {exc}")

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "meight doctor failed").strip()
        return PreflightResult(False, TOOL_INFRA, detail)
    try:
        report = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        return PreflightResult(False, TOOL_INFRA, f"meight doctor returned invalid JSON: {exc}")

    if not report.get("codex_cli_found"):
        return PreflightResult(False, TOOL_INFRA, "codex CLI not found")
    if not report.get("openai_codex_import"):
        detail = report.get("openai_codex_error") or "openai_codex import failed"
        return PreflightResult(False, TOOL_INFRA, str(detail))
    missing_skills = report.get("missing_role_skills") or []
    if missing_skills:
        return PreflightResult(False, TOOL_INFRA, f"missing role skills: {', '.join(missing_skills)}")

    print("preflight ok: meight doctor, codex CLI, SDK import, role skills")
    return PreflightResult(True)


def _run_manifest(
    manifest_path: Path,
    *,
    meight: str,
    timeout: int,
    meight_home: Path | None,
    keep_home: bool,
    skip_validate: bool,
    update_tasks: bool,
    create_fix_waves: bool,
    same_worker_restarts: int = 1,
    fresh_worker_restarts: int = 1,
    preflight: bool = True,
    preflight_timeout: int = 30,
) -> tuple[int, dict, list[str]]:
    manifest = _load_json(manifest_path)
    cwd = _repo_root(Path(manifest["spec_dir"]))
    run_home = meight_home or _new_home(cwd)
    created_home = meight_home is None

    print(f"MEIGHT_HOME={run_home}")
    fix_waves: list[str] = []
    should_shutdown = False
    try:
        if preflight:
            preflight_result = _preflight_manifest(manifest, run_home, cwd, meight, preflight_timeout)
            if not preflight_result.ok:
                print(
                    "ERROR: preflight failed: "
                    f"terminal_category={TERMINAL_BY_FAILURE[TOOL_INFRA]} "
                    f"failure_category={preflight_result.category or TOOL_INFRA} "
                    f"reason={preflight_result.reason}",
                    file=sys.stderr,
                )
                return 1, manifest, fix_waves
        should_shutdown = True
        _start_workers(manifest, run_home, cwd, meight)
        wait_code = _wait_workers(
            manifest,
            run_home,
            cwd,
            meight,
            timeout,
            same_worker_restarts=same_worker_restarts,
            fresh_worker_restarts=fresh_worker_restarts,
        )
        _salvage_artifacts(manifest, run_home)
        validate_code = 0 if skip_validate else _validate(manifest_path, run_home, cwd)
        exit_code = wait_code or validate_code
        if update_tasks:
            _write_review_summary(manifest)
        if validate_code != 0 and create_fix_waves:
            fix_waves = _create_fix_waves(manifest)
        if exit_code == 0 and update_tasks:
            _update_tasks(manifest)
        return exit_code, manifest, fix_waves
    finally:
        if should_shutdown:
            _shutdown_workers(meight, run_home, cwd)
        if created_home and not keep_home:
            shutil.rmtree(run_home, ignore_errors=True)


def _auto_run_fix_loop(
    initial_manifest_path: Path,
    *,
    meight: str,
    timeout: int,
    profile: str,
    keep_home: bool,
    skip_validate: bool,
    update_tasks: bool,
    max_fix_cycles: int,
    same_worker_restarts: int = 1,
    fresh_worker_restarts: int = 1,
    preflight: bool = True,
    preflight_timeout: int = 30,
) -> int:
    review_manifest_path = initial_manifest_path
    cycles = 0
    while True:
        review_code, review_manifest, fix_waves = _run_manifest(
            review_manifest_path,
            meight=meight,
            timeout=timeout,
            meight_home=None,
            keep_home=keep_home,
            skip_validate=skip_validate,
            update_tasks=update_tasks,
            create_fix_waves=cycles < max_fix_cycles,
            same_worker_restarts=same_worker_restarts,
            fresh_worker_restarts=fresh_worker_restarts,
            preflight=preflight,
            preflight_timeout=preflight_timeout,
        )
        if review_code == 0:
            return 0
        if not fix_waves:
            if cycles >= max_fix_cycles:
                print(f"ERROR: max fix cycles exceeded ({max_fix_cycles})", file=sys.stderr)
            return review_code
        cycles += 1

        spec_dir = Path(review_manifest["spec_dir"])
        for fix_wave in fix_waves:
            fix_manifest_path = _prepare(spec_dir, fix_wave, profile)
            fix_code, _, _ = _run_manifest(
                fix_manifest_path,
                meight=meight,
                timeout=timeout,
                meight_home=None,
                keep_home=keep_home,
                skip_validate=skip_validate,
                update_tasks=update_tasks,
                create_fix_waves=False,
                same_worker_restarts=same_worker_restarts,
                fresh_worker_restarts=fresh_worker_restarts,
                preflight=preflight,
                preflight_timeout=preflight_timeout,
            )
            if fix_code != 0:
                return fix_code

        print(f"rerun review: {_manifest_wave(review_manifest_path)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare/run/validate a codex2codex wave with meight.")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--spec-dir", type=Path)
    parser.add_argument("--wave")
    parser.add_argument("--meight", default="meight")
    parser.add_argument("--profile", choices=ALLOWED_CONTEXT_PROFILES, default="role")
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--meight-home", type=Path)
    parser.add_argument("--keep-home", action="store_true")
    parser.add_argument("--skip-validate", action="store_true")
    parser.add_argument("--no-update-tasks", action="store_true")
    parser.add_argument("--no-fix-wave", action="store_true")
    parser.add_argument("--auto-run-fix", action="store_true")
    parser.add_argument("--max-fix-cycles", type=int, default=1)
    parser.add_argument("--same-worker-restarts", type=_bounded_nonnegative_int, default=1)
    parser.add_argument("--fresh-worker-restarts", type=_bounded_nonnegative_int, default=1)
    parser.add_argument("--no-preflight", action="store_true")
    parser.add_argument("--preflight-timeout", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.manifest:
        manifest_path = args.manifest
    elif args.spec_dir and args.wave:
        manifest_path = _prepare(args.spec_dir, args.wave, args.profile, include_completed=args.auto_run_fix)
    else:
        raise SystemExit("ERROR: provide --manifest or both --spec-dir and --wave")

    manifest = _load_json(manifest_path)
    if args.dry_run:
        _dry_run(manifest)
        return 0

    if args.auto_run_fix and not args.no_fix_wave:
        if args.meight_home:
            print("ERROR: --auto-run-fix cannot be combined with --meight-home", file=sys.stderr)
            return 2
        return _auto_run_fix_loop(
            manifest_path,
            meight=args.meight,
            timeout=args.timeout,
            profile=args.profile,
            keep_home=args.keep_home,
            skip_validate=args.skip_validate,
            update_tasks=not args.no_update_tasks,
            max_fix_cycles=args.max_fix_cycles,
            same_worker_restarts=args.same_worker_restarts,
            fresh_worker_restarts=args.fresh_worker_restarts,
            preflight=not args.no_preflight,
            preflight_timeout=args.preflight_timeout,
        )

    exit_code, _, fix_waves = _run_manifest(
        manifest_path,
        meight=args.meight,
        timeout=args.timeout,
        meight_home=args.meight_home,
        keep_home=args.keep_home,
        skip_validate=args.skip_validate,
        update_tasks=not args.no_update_tasks,
        create_fix_waves=not args.no_fix_wave,
        same_worker_restarts=args.same_worker_restarts,
        fresh_worker_restarts=args.fresh_worker_restarts,
        preflight=not args.no_preflight,
        preflight_timeout=args.preflight_timeout,
    )
    if args.no_fix_wave:
        return exit_code
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
