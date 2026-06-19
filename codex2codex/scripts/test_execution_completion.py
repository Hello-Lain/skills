#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE_EXECUTION = SCRIPT_DIR / "validate_execution_complete.py"

sys.path.insert(0, str(SCRIPT_DIR))
import run_wave
import run_plan


def _run_validator(spec_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATE_EXECUTION), str(spec_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _write_state(spec_dir: Path, state: dict) -> None:
    (spec_dir / "execution-state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


class ExecutionCompletionGateTest(unittest.TestCase):
    def test_compile_only_state_is_not_a_quality_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            _write_state(
                spec_dir,
                {
                    "version": 1,
                    "spec_dir": str(spec_dir),
                    "plan": {
                        "status": "compiled",
                        "dry_run": True,
                        "waves": ["Wave 1"],
                        "tasks_path": str(spec_dir / "tasks.md"),
                    },
                    "waves": {},
                },
            )

            proc = _run_validator(spec_dir)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("dry-run", proc.stderr)
        self.assertIn("missing execution receipt for wave: Wave 1", proc.stderr)

    def test_implementation_without_review_pass_fails_final_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            artifact = spec_dir / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- done\n\n## Verification\n- ok\n", encoding="utf-8")
            summary = spec_dir / "runs" / "wave-1" / "coding-1" / "summary.json"
            summary.parent.mkdir(parents=True)
            summary.write_text('{"exit_code": 0}\n', encoding="utf-8")
            _write_state(
                spec_dir,
                {
                    "version": 1,
                    "spec_dir": str(spec_dir),
                    "plan": {"status": "compiled", "dry_run": False, "waves": ["Wave 1"]},
                    "waves": {
                        "Wave 1": {
                            "status": "success",
                            "exit_code": 0,
                            "cleanup": {"shutdown_attempted": True, "shutdown_ok": True},
                            "workers": [
                                {
                                    "name": "coding-1",
                                    "mode": "implement",
                                    "output": str(artifact),
                                    "summary_path": str(summary),
                                }
                            ],
                        }
                    },
                },
            )

            proc = _run_validator(spec_dir)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("missing required review PASS", proc.stderr)

    def test_reviewed_execution_passes_final_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            task_artifact = spec_dir / "artifacts" / "task.md"
            review_artifact = spec_dir / "review.md"
            task_summary = spec_dir / "runs" / "wave-1" / "coding-1" / "summary.json"
            review_summary = spec_dir / "runs" / "wave-2" / "review-1" / "summary.json"
            task_artifact.parent.mkdir()
            task_summary.parent.mkdir(parents=True)
            review_summary.parent.mkdir(parents=True)
            task_artifact.write_text("## Summary\n- done\n\n## Verification\n- ok\n", encoding="utf-8")
            review_artifact.write_text("Verdict: PASS\n\n## Findings\n- None\n\n## Verification\n- ok\n", encoding="utf-8")
            task_summary.write_text('{"exit_code": 0}\n', encoding="utf-8")
            review_summary.write_text('{"exit_code": 0}\n', encoding="utf-8")
            _write_state(
                spec_dir,
                {
                    "version": 1,
                    "spec_dir": str(spec_dir),
                    "plan": {"status": "compiled", "dry_run": False, "waves": ["Wave 1", "Wave 2"]},
                    "waves": {
                        "Wave 1": {
                            "status": "success",
                            "exit_code": 0,
                            "cleanup": {"shutdown_attempted": True, "shutdown_ok": True},
                            "workers": [
                                {
                                    "name": "coding-1",
                                    "mode": "implement",
                                    "output": str(task_artifact),
                                    "summary_path": str(task_summary),
                                }
                            ],
                        },
                        "Wave 2": {
                            "status": "success",
                            "exit_code": 0,
                            "cleanup": {"shutdown_attempted": True, "shutdown_ok": True},
                            "workers": [
                                {
                                    "name": "review-1",
                                    "mode": "review",
                                    "output": str(review_artifact),
                                    "summary_path": str(review_summary),
                                }
                            ],
                        },
                    },
                },
            )

            proc = _run_validator(spec_dir)

        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("VALID", proc.stdout)

    def test_dry_run_output_warns_that_it_is_not_quality_gate(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            run_wave._dry_run({"wave": "Wave 1", "workers": []})

        self.assertIn("COMPILE ONLY - NOT A QUALITY GATE", stdout.getvalue())

    def test_run_plan_records_compile_and_result_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            plan_path = spec_dir / "plan.md"
            tasks_path = spec_dir / "tasks.md"
            plan_path.write_text("# Plan\n", encoding="utf-8")
            tasks_path.write_text("# Tasks\n", encoding="utf-8")

            original_compile = run_plan._compile_plan
            original_run_wave = run_plan._run_wave
            run_plan._compile_plan = lambda *args, **kwargs: {
                "spec_dir": str(spec_dir),
                "tasks_path": str(tasks_path),
                "waves": ["Wave 1"],
            }
            run_plan._run_wave = lambda *args, **kwargs: 0
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = run_plan.main_with_args([str(plan_path), "--spec-dir", str(spec_dir)])
            finally:
                run_plan._compile_plan = original_compile
                run_plan._run_wave = original_run_wave

            state = json.loads((spec_dir / "execution-state.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(state["plan"]["status"], "success")
        self.assertFalse(state["plan"]["dry_run"])
        self.assertEqual(state["plan"]["waves"], ["Wave 1"])

    def test_run_manifest_records_wave_receipt_and_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            spec_dir = Path(temp)
            manifest_path = spec_dir / "manifest.json"
            artifact = spec_dir / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- done\n\n## Verification\n- ok\n", encoding="utf-8")
            manifest_path.write_text(
                json.dumps(
                    {
                        "spec_dir": str(spec_dir),
                        "wave": "Wave 1",
                        "workers": [
                            {
                                "name": "coding-1",
                                "mode": "implement",
                                "role": "coding",
                                "output": str(artifact),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            original_start = run_wave._start_workers
            original_wait = run_wave._wait_workers
            original_validate = run_wave._validate
            original_shutdown = run_wave._shutdown_workers
            def fake_wait(manifest, home, cwd, meight, timeout, **kwargs):
                worker_dir = kwargs["run_dir"] / "coding-1"
                worker_dir.mkdir(parents=True, exist_ok=True)
                (worker_dir / "summary.json").write_text('{"exit_code": 0}\n', encoding="utf-8")
                return 0
            run_wave._start_workers = lambda *args, **kwargs: ["coding-1"]
            run_wave._wait_workers = fake_wait
            run_wave._validate = lambda *args, **kwargs: 0
            run_wave._shutdown_workers = lambda *args, **kwargs: True
            try:
                code, _, _ = run_wave._run_manifest(
                    manifest_path,
                    meight="meight",
                    timeout=5,
                    meight_home=spec_dir / "meight",
                    keep_home=True,
                    skip_validate=False,
                    update_tasks=False,
                    create_fix_waves=False,
                    preflight=False,
                )
            finally:
                run_wave._start_workers = original_start
                run_wave._wait_workers = original_wait
                run_wave._validate = original_validate
                run_wave._shutdown_workers = original_shutdown

            state = json.loads((spec_dir / "execution-state.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(state["waves"]["Wave 1"]["status"], "success")
        self.assertTrue(state["waves"]["Wave 1"]["cleanup"]["shutdown_ok"])
        self.assertEqual(state["waves"]["Wave 1"]["workers"][0]["name"], "coding-1")


if __name__ == "__main__":
    unittest.main()
