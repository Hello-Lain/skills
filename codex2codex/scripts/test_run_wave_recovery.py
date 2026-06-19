#!/usr/bin/env python3
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_plan
import run_wave


class RunWaveRecoveryTaxonomyTest(unittest.TestCase):
    def test_provider_strings_map_to_transient_api(self) -> None:
        fixtures = [
            "provider timeout while waiting for response",
            "No active credentials for provider: openai-compatible",
            "app-server socket disconnect",
            "HTTP 503 service unavailable",
            "gateway timeout from API server",
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(run_wave.classify_failure_text(fixture), run_wave.TRANSIENT_API)

    def test_tool_strings_map_to_tool_infra(self) -> None:
        fixtures = [
            "worker tool backend failure",
            "approval backend failure",
            "apply_patch backend unavailable",
            "meight daemon socket drift",
            "tool call failed before completion",
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(run_wave.classify_failure_text(fixture), run_wave.TOOL_INFRA)

    def test_hunk_and_context_failures_map_to_patch_context(self) -> None:
        fixtures = [
            "stale hunk in PATCH_BODY",
            "target changed before patch could apply",
            "patch context mismatch",
            "Failed to find expected lines in file",
            "hunk failed at line 42",
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(run_wave.classify_failure_text(fixture), run_wave.PATCH_CONTEXT)

    def test_contract_failures_map_to_contract_fail(self) -> None:
        fixtures = [
            "missing output artifact artifacts/task.md",
            "blocked artifact written by worker",
            "missing review verdict",
            "no verdict in review result",
            "missing expected file change",
            "no scoped diff for implementation worker",
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(run_wave.classify_failure_text(fixture), run_wave.CONTRACT_FAIL)

    def test_question_and_repo_ambiguity_map_to_task_blocker(self) -> None:
        fixtures = [
            "QUESTION: choose API shape",
            "ambiguous requirement between CLI and library behavior",
            "design conflict requires user decision",
            "writable-scope conflict blocks implementation",
            "repo-unanswerable question",
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(run_wave.classify_failure_text(fixture), run_wave.TASK_BLOCKER)

    def test_status_question_maps_to_task_blocker(self) -> None:
        status = {
            "state": "needs_input",
            "needs_input_source": "question",
            "needs_input_detail": "QUESTION: narrow scope",
        }

        self.assertEqual(run_wave.classify_worker_failure(status=status), run_wave.TASK_BLOCKER)

    def test_status_failure_detail_maps_to_tool_infra(self) -> None:
        status = {"state": "failed", "failure_detail": "approval backend failure"}

        self.assertEqual(run_wave.classify_worker_failure(status=status), run_wave.TOOL_INFRA)

    def test_contract_signal_helper_maps_any_gate_failure_to_contract_fail(self) -> None:
        fixtures = [
            {"artifact_missing": True},
            {"missing_verdict": True},
            {"missing_diff": True},
            {"blocked_artifact": True},
        ]

        for fixture in fixtures:
            with self.subTest(fixture=fixture):
                self.assertEqual(
                    run_wave.classify_contract_failure(**fixture),
                    run_wave.CONTRACT_FAIL,
                )

    def test_recoverable_failure_retries_while_budget_remains(self) -> None:
        decision = run_wave.recovery_decision(
            run_wave.TRANSIENT_API,
            attempts=0,
            max_attempts=1,
        )

        self.assertEqual(decision.action, run_wave.RECOVERY_RETRY)
        self.assertIsNone(decision.terminal_category)

    def test_recoverable_failure_stops_with_terminal_category_after_budget(self) -> None:
        fixtures = [
            (run_wave.TRANSIENT_API, run_wave.INFRA_FAILED),
            (run_wave.TOOL_INFRA, run_wave.INFRA_FAILED),
            (run_wave.PATCH_CONTEXT, run_wave.CONTRACT_FAILED),
            (run_wave.CONTRACT_FAIL, run_wave.CONTRACT_FAILED),
        ]

        for category, terminal in fixtures:
            with self.subTest(category=category):
                decision = run_wave.recovery_decision(category, attempts=1, max_attempts=1)
                self.assertEqual(decision.action, run_wave.RECOVERY_STOP)
                self.assertEqual(decision.terminal_category, terminal)

    def test_task_blocker_stops_without_consuming_recovery_budget(self) -> None:
        decision = run_wave.recovery_decision(
            run_wave.TASK_BLOCKER,
            attempts=0,
            max_attempts=3,
        )

        self.assertEqual(decision.action, run_wave.RECOVERY_STOP)
        self.assertEqual(decision.terminal_category, run_wave.TASK_BLOCKED)


class RunWavePatchBodyFallbackTest(unittest.TestCase):
    def test_unified_add_patch_ignores_dev_null_path(self) -> None:
        body = """diff --git a/new.txt b/new.txt
new file mode 100644
--- /dev/null
+++ b/new.txt
@@ -0,0 +1 @@
+hello
"""

        self.assertEqual(run_wave._patch_paths(body), ("new.txt",))

    def test_dotfile_path_is_not_stripped(self) -> None:
        self.assertEqual(
            run_wave._normalize_patch_path("./.github/workflows/ci.yml"),
            ".github/workflows/ci.yml",
        )

    def test_absolute_and_traversal_paths_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "absolute path"):
            run_wave._patch_paths("*** Begin Patch\n*** Update File: /tmp/out.txt\n")
        with self.assertRaisesRegex(ValueError, "path traversal"):
            run_wave._patch_paths("*** Begin Patch\n*** Update File: ../out.txt\n")

    def test_in_scope_apply_patch_body_is_applied_and_recorded(self) -> None:
        result = """Tooling failed, runner may apply fallback.

PATCH_BODY:
*** Begin Patch
*** Update File: scoped.txt
@@
-old
+new
*** End Patch
"""

        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "scoped.txt").write_text("old\n", encoding="utf-8")
            home = cwd / "meight"

            patch_result = run_wave._apply_worker_patch_body(
                {"name": "coding-1", "mode": "implement", "files": ["scoped.txt"]},
                home,
                "coding-1",
                cwd,
                result,
            )

            status = json.loads((home / "workers" / "coding-1" / "status.json").read_text(encoding="utf-8"))

        self.assertTrue(patch_result.applied)
        self.assertEqual(patch_result.paths, ("scoped.txt",))
        self.assertEqual(status["files_changed"], ["scoped.txt"])
        self.assertTrue(status["patch_body_fallback"])

    def test_out_of_scope_patch_body_is_contract_failure(self) -> None:
        result = """PATCH_BODY:
*** Begin Patch
*** Update File: other.txt
@@
-old
+new
*** End Patch
"""

        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "other.txt").write_text("old\n", encoding="utf-8")
            patch_result = run_wave._apply_worker_patch_body(
                {"name": "coding-1", "mode": "implement", "files": ["scoped.txt"]},
                cwd / "meight",
                "coding-1",
                cwd,
                result,
            )

        self.assertFalse(patch_result.applied)
        self.assertEqual(patch_result.category, run_wave.CONTRACT_FAIL)
        self.assertIn("outside writable scope", patch_result.reason)

    def test_directory_scope_allows_nested_patch_body_path(self) -> None:
        result = """PATCH_BODY:
*** Begin Patch
*** Update File: src/scoped.txt
@@
-old
+new
*** End Patch
"""

        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "src").mkdir()
            (cwd / "src" / "scoped.txt").write_text("old\n", encoding="utf-8")
            patch_result = run_wave._apply_worker_patch_body(
                {"name": "coding-1", "mode": "implement", "files": ["src"]},
                cwd / "meight",
                "coding-1",
                cwd,
                result,
            )

        self.assertTrue(patch_result.applied)
        self.assertEqual(patch_result.paths, ("src/scoped.txt",))

    def test_file_scope_rejects_child_patch_body_path(self) -> None:
        result = """PATCH_BODY:
*** Begin Patch
*** Update File: src/target.py/child.txt
@@
-old
+new
*** End Patch
"""

        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "src").mkdir()
            (cwd / "src" / "target.py").write_text("print('old')\n", encoding="utf-8")
            patch_result = run_wave._apply_worker_patch_body(
                {"name": "coding-1", "mode": "implement", "files": ["src/target.py"]},
                cwd / "meight",
                "coding-1",
                cwd,
                result,
            )

        self.assertFalse(patch_result.applied)
        self.assertEqual(patch_result.category, run_wave.CONTRACT_FAIL)
        self.assertIn("outside writable scope", patch_result.reason)

    def test_patch_apply_failure_is_sent_to_worker_follow(self) -> None:
        calls: list[list[str]] = []
        follow_briefs: list[str] = []
        wait_count = 0

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            nonlocal wait_count
            calls.append(cmd)
            if cmd[1] == "wait":
                wait_count += 1
                worker_dir = meight_home / "workers" / cmd[2]
                worker_dir.mkdir(parents=True, exist_ok=True)
                if wait_count == 1:
                    (worker_dir / "result.md").write_text(
                        """PATCH_BODY:
*** Begin Patch
*** Update File: scoped.txt
@@
-missing
+new
*** End Patch
""",
                        encoding="utf-8",
                    )
                else:
                    (worker_dir / "result.md").write_text("Changed files\nVerification: ok\n", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            if cmd[1] == "status":
                status = {"name": cmd[2], "state": "completed"}
                if wait_count > 1:
                    status["files_changed"] = ["scoped.txt"]
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(status), stderr="")
            if cmd[1] == "follow":
                follow_briefs.append(cmd[4])
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                cwd = Path(temp)
                (cwd / "scoped.txt").write_text("old\n", encoding="utf-8")
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        {"name": "coding-1", "brief": "brief.md", "mode": "implement", "files": ["scoped.txt"]},
                        cwd / "meight",
                        cwd,
                        "meight",
                        5,
                        same_worker_restarts=1,
                        fresh_worker_restarts=0,
                        same_thread_continues=1,
                    )
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status", "status", "follow", "wait", "status"])
        self.assertIn("PATCH_BODY apply failed", follow_briefs[0])


class RunWaveRecoveryLoopTest(unittest.TestCase):
    def test_stalled_active_worker_is_steered_before_interrupt(self) -> None:
        calls: list[list[str]] = []
        wait_codes = [1, 0]
        statuses = [
            {
                "name": "coding-1",
                "state": "running",
                "stalled": True,
                "stalled_reason": "no worker activity for 120s",
            },
            {"name": "coding-1", "state": "completed"},
        ]

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            calls.append(cmd)
            if cmd[1] == "wait":
                return subprocess.CompletedProcess(cmd, wait_codes.pop(0), stdout="", stderr="")
            if cmd[1] == "status":
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(statuses.pop(0)), stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        Path(temp),
                        Path(temp),
                        "meight",
                        5,
                        same_worker_restarts=0,
                        fresh_worker_restarts=0,
                        same_thread_continues=0,
                    )
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status", "steer", "wait", "status"])
        self.assertIn("no worker activity", calls[2][3])

    def test_terminal_transient_failure_follows_before_same_worker_restart(self) -> None:
        calls: list[list[str]] = []
        wait_codes = [2, 2, 0]
        statuses = [
            {"name": "coding-1", "state": "failed", "failure_detail": "provider timeout"},
            {"name": "coding-1", "state": "failed", "failure_detail": "provider timeout"},
            {"name": "coding-1", "state": "completed"},
        ]

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            calls.append(cmd)
            if cmd[1] == "wait":
                return subprocess.CompletedProcess(cmd, wait_codes.pop(0), stdout="", stderr="")
            if cmd[1] == "status":
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(statuses.pop(0)), stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        Path(temp),
                        Path(temp),
                        "meight",
                        5,
                        same_worker_restarts=1,
                        fresh_worker_restarts=0,
                        same_thread_continues=1,
                    )
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status", "follow", "wait", "status", "start", "wait", "status"])
        self.assertEqual(calls[5][2], "coding-1")

    def test_active_wait_failure_interrupts_before_same_name_restart(self) -> None:
        calls: list[list[str]] = []
        wait_codes = [1, 2, 0]

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            calls.append(cmd)
            if cmd[1] == "wait":
                return subprocess.CompletedProcess(cmd, wait_codes.pop(0), stdout="", stderr="")
            if cmd[1] == "status":
                status = {"name": "coding-1", "state": "running", "stalled": False}
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(status), stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        Path(temp),
                        Path(temp),
                        "meight",
                        5,
                        same_worker_restarts=1,
                        fresh_worker_restarts=0,
                    )
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status", "interrupt", "wait", "start", "wait", "status"])

    def test_completed_review_without_verdict_recovers_before_validation(self) -> None:
        calls: list[list[str]] = []
        wait_count = 0

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            nonlocal wait_count
            calls.append(cmd)
            if cmd[1] == "wait":
                wait_count += 1
                worker_dir = meight_home / "workers" / cmd[2]
                worker_dir.mkdir(parents=True, exist_ok=True)
                if wait_count == 1:
                    (worker_dir / "result.md").write_text(
                        "ARTIFACT_BODY:\n# Review\n\n## Findings\n\nNo issues.\n",
                        encoding="utf-8",
                    )
                else:
                    (worker_dir / "result.md").write_text(
                        "ARTIFACT_BODY:\n# Review\n\nVerdict: PASS\n\n## Findings\n\nNo issues.\n",
                        encoding="utf-8",
                    )
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            if cmd[1] == "status":
                return subprocess.CompletedProcess(
                    cmd,
                    0,
                    stdout=json.dumps({"name": cmd[2], "state": "completed"}),
                    stderr="",
                )
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                cwd = Path(temp)
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        {
                            "name": "review-1",
                            "brief": "brief.md",
                            "mode": "review",
                            "output": "review.md",
                        },
                        cwd / "meight",
                        cwd,
                        "meight",
                        5,
                        same_worker_restarts=1,
                        fresh_worker_restarts=0,
                    )
                artifact = (cwd / "review.md").read_text(encoding="utf-8")
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status", "status", "follow", "wait", "status"])
        self.assertIn("Verdict: PASS", artifact)

    def test_fresh_worker_success_is_mirrored_to_original_worker_for_validation(self) -> None:
        calls: list[list[str]] = []
        first_wait = True

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            nonlocal first_wait
            calls.append(cmd)
            if cmd[1] == "wait" and first_wait:
                first_wait = False
                return subprocess.CompletedProcess(cmd, 2, stdout="", stderr="")
            if cmd[1] == "wait":
                worker_dir = meight_home / "workers" / cmd[2]
                worker_dir.mkdir(parents=True, exist_ok=True)
                (worker_dir / "status.json").write_text(
                    json.dumps(
                        {
                            "name": cmd[2],
                            "state": "completed",
                            "files_changed": ["codex2codex/scripts/run_wave.py"],
                        }
                    ),
                    encoding="utf-8",
                )
                (worker_dir / "result.md").write_text("Changed files\nVerification: ok\n", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")
            if cmd[1] == "status":
                status = {"name": "coding-1", "state": "failed", "failure_detail": "provider timeout"}
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(status), stderr="")
            if cmd[1] == "follow":
                return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="follow failed")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                home = Path(temp)
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        home,
                        home,
                        "meight",
                        5,
                        same_worker_restarts=0,
                        fresh_worker_restarts=1,
                    )
                original_status = json.loads((home / "workers" / "coding-1" / "status.json").read_text(encoding="utf-8"))
                original_result = (home / "workers" / "coding-1" / "result.md").read_text(encoding="utf-8")
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 0)
        self.assertIn(["start", "coding-1-recovery-1"], [cmd[1:3] for cmd in calls])
        self.assertEqual(original_status["name"], "coding-1")
        self.assertEqual(original_status["state"], "completed")
        self.assertIn("Verification: ok", original_result)

    def test_recovery_exhaustion_reports_terminal_category(self) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            calls.append(cmd)
            if cmd[1] == "wait":
                return subprocess.CompletedProcess(cmd, 2, stdout="", stderr="")
            if cmd[1] == "status":
                status = {"name": "coding-1", "state": "failed", "failure_detail": "provider timeout"}
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(status), stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        Path(temp),
                        Path(temp),
                        "meight",
                        5,
                        same_worker_restarts=0,
                        fresh_worker_restarts=0,
                        same_thread_continues=0,
                    )
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 2)
        self.assertEqual([cmd[1] for cmd in calls], ["wait", "status"])
        self.assertIn("terminal_category=INFRA_FAILED", stderr.getvalue())
        self.assertIn("reason=recovery budget exhausted", stderr.getvalue())

    def test_preflight_rejects_missing_meight_before_starting_workers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            manifest = {"workers": [{"name": "coding-1", "mode": "implement"}]}
            result = run_wave._preflight_manifest(
                manifest,
                cwd / "meight-home",
                cwd,
                str(cwd / "missing-meight"),
                5,
            )

        self.assertFalse(result.ok)
        self.assertEqual(result.category, run_wave.TOOL_INFRA)
        self.assertIn("meight executable not found", result.reason)

    def test_preflight_uses_doctor_and_requires_worker_readiness(self) -> None:
        calls: list[list[str]] = []

        def fake_run(*args, **kwargs):
            calls.append(args[0])
            return subprocess.CompletedProcess(
                args[0],
                0,
                stdout=json.dumps(
                    {
                        "codex_cli_found": True,
                        "openai_codex_import": True,
                        "missing_role_skills": [],
                    }
                ),
                stderr="",
            )

        original_run = run_wave.subprocess.run
        original_resolvable = run_wave._meight_is_resolvable
        run_wave.subprocess.run = fake_run
        run_wave._meight_is_resolvable = lambda meight: True
        try:
            with tempfile.TemporaryDirectory() as temp:
                cwd = Path(temp)
                result = run_wave._preflight_manifest(
                    {"workers": [{"name": "coding-1", "mode": "implement"}]},
                    cwd / "meight-home",
                    cwd,
                    "meight",
                    5,
                )
        finally:
            run_wave.subprocess.run = original_run
            run_wave._meight_is_resolvable = original_resolvable

        self.assertTrue(result.ok)
        self.assertEqual(calls, [["meight", "doctor", "--json"]])

    def test_preflight_skips_review_only_waves(self) -> None:
        result = run_wave._preflight_manifest(
            {"workers": [{"name": "review-1", "mode": "review"}]},
            Path("/missing"),
            Path("/missing"),
            "/missing/meight",
            5,
        )

        self.assertTrue(result.ok)

    def test_run_manifest_does_not_turn_question_exit_into_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps({"spec_dir": str(root), "workers": [{"name": "coding-1"}]}),
                encoding="utf-8",
            )

            original_start = run_wave._start_workers
            original_wait = run_wave._wait_workers
            original_validate = run_wave._validate
            original_shutdown = run_wave._shutdown_workers
            run_wave._start_workers = lambda *args, **kwargs: ["coding-1"]
            run_wave._wait_workers = lambda *args, **kwargs: 3
            run_wave._validate = lambda *args, **kwargs: 0
            run_wave._shutdown_workers = lambda *args, **kwargs: None
            try:
                code, _, _ = run_wave._run_manifest(
                    manifest_path,
                    meight="meight",
                    timeout=5,
                    meight_home=root / "meight",
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

        self.assertEqual(code, 3)

    def test_default_same_thread_continuation_budget_is_three_and_writes_ledger(self) -> None:
        calls: list[list[str]] = []
        wait_codes = [2, 2, 2, 2]

        def fake_run(cmd: list[str], meight_home: Path, cwd: Path, capture: bool = False):
            calls.append(cmd)
            if cmd[1] == "wait":
                return subprocess.CompletedProcess(cmd, wait_codes.pop(0), stdout="", stderr="")
            if cmd[1] == "status":
                status = {"name": "coding-1", "state": "failed", "failure_detail": "provider timeout"}
                return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(status), stderr="")
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

        original_run = run_wave._run
        run_wave._run = fake_run
        try:
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                run_dir = root / "runs" / "wave-1"
                with contextlib.redirect_stderr(io.StringIO()):
                    code = run_wave._wait_worker_with_recovery(
                        self._worker(),
                        root / "meight",
                        root,
                        "meight",
                        5,
                        same_worker_restarts=0,
                        fresh_worker_restarts=0,
                        run_dir=run_dir,
                        wave="Wave 1",
                    )
                attempts = [
                    json.loads(line)
                    for line in (run_dir / "coding-1" / "attempts.jsonl").read_text(encoding="utf-8").splitlines()
                ]
                summary = json.loads((run_dir / "coding-1" / "summary.json").read_text(encoding="utf-8"))
        finally:
            run_wave._run = original_run

        self.assertEqual(code, 2)
        self.assertEqual([cmd[1] for cmd in calls].count("follow"), 3)
        self.assertEqual([item["continue_attempt"] for item in attempts if item["action"] == "continue"], [1, 2, 3])
        self.assertTrue(all(item["wave"] == "Wave 1" for item in attempts))
        self.assertEqual(summary["terminal_category"], run_wave.INFRA_FAILED)

    def test_review_infra_failure_is_review_unavailable_and_no_fix_wave(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "spec_dir": str(root),
                        "wave": "Wave 2",
                        "workers": [{"name": "review-1", "mode": "review", "output": "review.md"}],
                    }
                ),
                encoding="utf-8",
            )

            original_start = run_wave._start_workers
            original_wait = run_wave._wait_workers
            original_validate = run_wave._validate
            original_fix = run_wave._create_fix_waves
            original_shutdown = run_wave._shutdown_workers
            run_wave._start_workers = lambda *args, **kwargs: ["review-1"]
            run_wave._wait_workers = lambda manifest, home, cwd, meight, timeout, **kwargs: (
                run_wave._write_wave_summary(
                    kwargs["run_dir"],
                    manifest,
                    [{"worker": "review-1", "exit_code": 2, "terminal_category": run_wave.REVIEW_UNAVAILABLE}],
                )
                or 2
            )
            run_wave._validate = lambda *args, **kwargs: 1
            run_wave._create_fix_waves = lambda *args, **kwargs: ["unexpected-fix-wave"]
            run_wave._shutdown_workers = lambda *args, **kwargs: None
            try:
                code, _, fix_waves = run_wave._run_manifest(
                    manifest_path,
                    meight="meight",
                    timeout=5,
                    meight_home=root / "meight",
                    keep_home=True,
                    skip_validate=False,
                    update_tasks=False,
                    create_fix_waves=True,
                    preflight=False,
                )
            finally:
                run_wave._start_workers = original_start
                run_wave._wait_workers = original_wait
                run_wave._validate = original_validate
                run_wave._create_fix_waves = original_fix
                run_wave._shutdown_workers = original_shutdown

        self.assertEqual(code, 2)
        self.assertEqual(fix_waves, [])

    def test_pass_review_marks_existing_fix_wave_obsolete(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            review = root / "review.md"
            review.write_text("Verdict: PASS\n\n## Findings\n- None.\n\n## Verification\n- ok.\n", encoding="utf-8")
            tasks = root / "tasks.md"
            tasks.write_text(
                f"# Tasks\n\n## Wave 3: fix review findings\n- [ ] [coding] Fix review findings from `{review}` | `src/app.py` | Verify: tests\n",
                encoding="utf-8",
            )

            run_wave._mark_obsolete_fix_waves_for_pass_reviews(
                {"spec_dir": str(root), "workers": [{"name": "review-1", "mode": "review", "output": str(review)}]}
            )

            text = tasks.read_text(encoding="utf-8")

        self.assertIn("- [x] [coding] Fix review findings", text)
        self.assertIn("fix-wave-obsolete", text)

    def test_completed_contract_failure_rejects_file_scope_child_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "src").mkdir()
            (cwd / "src" / "target.py").write_text("print('old')\n", encoding="utf-8")
            artifact = cwd / "artifact.md"
            artifact.write_text("## Summary\n- Fixed.\n\n## Verification\n- ok.\n", encoding="utf-8")

            failure = run_wave._completed_worker_contract_failure(
                {
                    "name": "coding-1",
                    "mode": "implement",
                    "files": ["src/target.py"],
                    "output": "artifact.md",
                },
                cwd,
                {"state": "completed", "files_changed": ["src/target.py/child.txt"]},
                "Changed files\nVerification: ok\n",
            )

        self.assertIsNotNone(failure)
        self.assertEqual(failure.category, run_wave.CONTRACT_FAIL)
        self.assertIn("missing expected implementation evidence", failure.reason)

    def test_completed_contract_failure_accepts_directory_scope_child_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            cwd = Path(temp)
            (cwd / "src").mkdir()
            artifact = cwd / "artifact.md"
            artifact.write_text("## Summary\n- Fixed.\n\n## Verification\n- ok.\n", encoding="utf-8")

            failure = run_wave._completed_worker_contract_failure(
                {
                    "name": "coding-1",
                    "mode": "implement",
                    "files": ["src"],
                    "output": "artifact.md",
                },
                cwd,
                {"state": "completed", "files_changed": ["src/target.py"]},
                "Changed files\nVerification: ok\n",
            )

        self.assertIsNone(failure)

    def test_recovery_budget_parser_is_bounded(self) -> None:
        self.assertEqual(run_wave._bounded_nonnegative_int("0"), 0)
        self.assertEqual(run_wave._bounded_nonnegative_int("3"), 3)
        with self.assertRaisesRegex(run_wave.argparse.ArgumentTypeError, "between 0 and 3"):
            run_wave._bounded_nonnegative_int("4")

    def _worker(self) -> dict:
        return {
            "name": "coding-1",
            "brief": "brief.md",
            "role": "coding",
            "sandbox": "ws",
            "effort": "high",
        }


class RunPlanRecoveryControlsTest(unittest.TestCase):
    def test_run_plan_forwards_recovery_controls_to_run_wave(self) -> None:
        calls: list[list[str]] = []

        def fake_run(cmd: list[str], text: bool = False, check: bool = False):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0)

        args = argparse.Namespace(
            profile="role",
            timeout=99,
            meight="meight",
            dry_run=False,
            keep_home=False,
            skip_validate=False,
            no_update_tasks=False,
            no_fix_wave=False,
            auto_run_fix=True,
            max_fix_cycles=2,
            same_worker_restarts=2,
            fresh_worker_restarts=0,
            same_thread_continues=3,
            no_preflight=True,
            preflight_timeout=7,
        )

        original_run = run_plan.subprocess.run
        run_plan.subprocess.run = fake_run
        try:
            code = run_plan._run_wave(Path("spec"), "Wave 1", args)
        finally:
            run_plan.subprocess.run = original_run

        self.assertEqual(code, 0)
        command = calls[0]
        self.assertIn("--same-worker-restarts", command)
        self.assertEqual(command[command.index("--same-worker-restarts") + 1], "2")
        self.assertIn("--fresh-worker-restarts", command)
        self.assertEqual(command[command.index("--fresh-worker-restarts") + 1], "0")
        self.assertIn("--same-thread-continues", command)
        self.assertEqual(command[command.index("--same-thread-continues") + 1], "3")
        self.assertIn("--no-preflight", command)
        self.assertIn("--preflight-timeout", command)
        self.assertEqual(command[command.index("--preflight-timeout") + 1], "7")


if __name__ == "__main__":
    unittest.main()
