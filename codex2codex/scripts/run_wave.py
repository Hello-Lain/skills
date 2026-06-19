#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from roles import ALLOWED_CONTEXT_PROFILES, DEFAULT_EFFORT, ROLE_MODE

HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")
VERDICT_LINE_RE = re.compile(r"^\s*(?:-\s*)?(?:#{1,6}\s*)?Verdict\s*:?\s*`?(PASS|FAIL)?`?\.?\s*$", re.I)
ARTIFACT_BODY_RE = re.compile(r"(?mis)^ARTIFACT_BODY:\s*\n(?P<body>.*)$")


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


def _start_workers(manifest: dict, meight_home: Path, cwd: Path, meight: str) -> list[str]:
    names: list[str] = []
    for worker in manifest.get("workers", []):
        name = worker["name"]
        names.append(name)
        cmd = [
            meight,
            "start",
            name,
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
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr or proc.stdout or "")
            raise SystemExit(f"ERROR: failed to start worker {name}")
        print((proc.stdout or "").strip())
    return names


def _wait_workers(names: list[str], meight_home: Path, cwd: Path, meight: str, timeout: int) -> int:
    exit_code = 0
    for name in names:
        proc = _run([meight, "wait", name, "--timeout", str(timeout)], meight_home, cwd, capture=True)
        if proc.stdout:
            print(proc.stdout.strip())
        if proc.stderr:
            sys.stderr.write(proc.stderr)
        if proc.returncode != 0:
            print(f"ERROR: worker {name} wait exit {proc.returncode}", file=sys.stderr)
            exit_code = proc.returncode or 1
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
) -> tuple[int, dict, list[str]]:
    manifest = _load_json(manifest_path)
    cwd = _repo_root(Path(manifest["spec_dir"]))
    run_home = meight_home or _new_home(cwd)
    created_home = meight_home is None

    print(f"MEIGHT_HOME={run_home}")
    fix_waves: list[str] = []
    try:
        names = _start_workers(manifest, run_home, cwd, meight)
        wait_code = _wait_workers(names, run_home, cwd, meight, timeout)
        _salvage_artifacts(manifest, run_home)
        validate_code = 0 if skip_validate else _validate(manifest_path, run_home, cwd)
        exit_code = validate_code if wait_code == 3 and validate_code == 0 else wait_code or validate_code
        if update_tasks:
            _write_review_summary(manifest)
        if validate_code != 0 and create_fix_waves:
            fix_waves = _create_fix_waves(manifest)
        if exit_code == 0 and update_tasks:
            _update_tasks(manifest)
        return exit_code, manifest, fix_waves
    finally:
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
    )
    if args.no_fix_wave:
        return exit_code
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
