#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATE_WAVE = SCRIPT_DIR / "validate_wave.py"
VALIDATE_RESULT = SCRIPT_DIR / "validate_result_contract.py"
os.environ.setdefault("MEIGHT_NO_BUNDLED_PYTHON", "1")
sys.path.insert(0, str(SCRIPT_DIR.parent))
from meight import PRE_FIRST_ITEM_STALL, classify_worker_stall, now_kst  # noqa: E402


class WorkerRecoveryContractsTest(unittest.TestCase):
    def _stale_worker_status(self, **overrides: object) -> dict:
        stale = (now_kst() - timedelta(seconds=30)).isoformat(timespec="seconds")
        status = {
            "state": "running",
            "turn_id": "turn-1",
            "updated_at": stale,
            "last_event_at": stale,
            "current_item": None,
            "current_item_started_at": None,
            "tokens": {"input": 0, "cached": 0, "output": 0},
        }
        status.update(overrides)
        return status

    def test_pre_first_item_stall_classification_has_priority(self) -> None:
        status = self._stale_worker_status()

        self.assertEqual(classify_worker_stall(status, 10), PRE_FIRST_ITEM_STALL)

    def test_item_started_is_not_pre_first_item_stall(self) -> None:
        status = self._stale_worker_status(current_item_started_at=now_kst().isoformat())

        self.assertNotEqual(classify_worker_stall(status, 10), PRE_FIRST_ITEM_STALL)

    def test_token_usage_is_not_pre_first_item_stall(self) -> None:
        status = self._stale_worker_status(tokens={"input": 1, "cached": 0, "output": 0})

        self.assertNotEqual(classify_worker_stall(status, 10), PRE_FIRST_ITEM_STALL)

    def test_current_item_is_not_pre_first_item_stall(self) -> None:
        status = self._stale_worker_status(current_item="tool call (12s)")

        self.assertNotEqual(classify_worker_stall(status, 10), PRE_FIRST_ITEM_STALL)

    def test_past_item_started_is_not_pre_first_item_stall(self) -> None:
        status = self._stale_worker_status(
            first_item_started_at=now_kst().isoformat(timespec="seconds")
        )

        self.assertNotEqual(classify_worker_stall(status, 10), PRE_FIRST_ITEM_STALL)

    def _repo(self, tmp: Path) -> Path:
        repo = tmp / "repo"
        (repo / ".codex" / "specs" / "worker-recovery").mkdir(parents=True)
        return repo

    def _write_worker(
        self,
        meight_home: Path,
        name: str,
        *,
        state: str = "completed",
        result: str = "Done",
        files_changed: list[str] | None = None,
    ) -> None:
        worker_dir = meight_home / "workers" / name
        worker_dir.mkdir(parents=True)
        (worker_dir / "status.json").write_text(
            json.dumps({"state": state, "files_changed": files_changed or []}),
            encoding="utf-8",
        )
        (worker_dir / "result.md").write_text(result, encoding="utf-8")

    def _write_manifest(self, repo: Path, workers: list[dict]) -> Path:
        manifest = repo / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "spec_dir": str(repo / ".codex" / "specs" / "worker-recovery"),
                    "workers": workers,
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def _validate_wave(self, manifest: Path, meight_home: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATE_WAVE), "--manifest", str(manifest), "--meight-home", str(meight_home)],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def _validate_result(self, artifact: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATE_RESULT), *args, str(artifact)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_blocked_salvaged_implementation_without_scoped_diff_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text(
                "Salvaged-From-Worker: coding-1\n\n## Summary\n- Claimed fix.\n\n## Verification\n- Not run.\n",
                encoding="utf-8",
            )
            self._write_worker(
                meight_home,
                "coding-1",
                state="needs_input",
                result="Blocked writing artifact: apply_patch backend unavailable.",
                files_changed=[],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("missing expected implementation evidence", proc.stderr)

    def test_implementation_artifact_that_reports_blocked_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("Blocked: cannot edit scoped file\n", encoding="utf-8")
            self._write_worker(
                meight_home,
                "coding-1",
                files_changed=["src/target.py"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("output artifact reports blocked", proc.stderr)

    def test_blocked_result_without_salvaged_artifact_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- Not useful.\n", encoding="utf-8")
            self._write_worker(
                meight_home,
                "coding-1",
                result="Blocked: apply_patch backend unavailable.",
                files_changed=["src/target.py"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("result reports blocked despite terminal state", proc.stderr)

    def test_missing_implementation_artifact_fails_with_distinct_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            self._write_worker(
                meight_home,
                "coding-1",
                files_changed=["src/target.py"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/missing.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("missing output artifact", proc.stderr)

    def test_implementation_with_scoped_diff_and_artifact_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- Fixed.\n\n## Verification\n- Tests passed.\n", encoding="utf-8")
            self._write_worker(
                meight_home,
                "coding-1",
                files_changed=["src/target.py"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("VALID", proc.stdout)

    def test_file_scope_child_path_does_not_satisfy_implementation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            (repo / "src").mkdir()
            (repo / "src" / "target.py").write_text("print('old')\n", encoding="utf-8")
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- Fixed.\n\n## Verification\n- Tests passed.\n", encoding="utf-8")
            self._write_worker(
                meight_home,
                "coding-1",
                files_changed=["src/target.py/child.txt"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src/target.py"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("missing expected implementation evidence", proc.stderr)

    def test_directory_scope_child_path_satisfies_implementation_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            (repo / "src").mkdir()
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "task.md"
            artifact.parent.mkdir()
            artifact.write_text("## Summary\n- Fixed.\n\n## Verification\n- Tests passed.\n", encoding="utf-8")
            self._write_worker(
                meight_home,
                "coding-1",
                files_changed=["src/target.py"],
            )
            manifest = self._write_manifest(
                repo,
                [
                    {
                        "name": "coding-1",
                        "mode": "implement",
                        "files": ["src"],
                        "output": "artifacts/task.md",
                    }
                ],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("VALID", proc.stdout)

    def test_review_artifact_without_verdict_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "review.md"
            artifact.parent.mkdir()
            artifact.write_text("## Findings\n- None.\n\n## Verification\n- Read only.\n", encoding="utf-8")
            self._write_worker(meight_home, "review-1")
            manifest = self._write_manifest(
                repo,
                [{"name": "review-1", "mode": "review", "output": "artifacts/review.md"}],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("missing review verdict", proc.stderr)

    def test_review_fail_verdict_fails_wave(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = self._repo(Path(temp))
            meight_home = Path(temp) / "meight"
            artifact = repo / "artifacts" / "review.md"
            artifact.parent.mkdir()
            artifact.write_text(
                "Verdict: FAIL\n\n## Findings\n- Bug.\n\n## Verification\n- Unit tests failed.\n",
                encoding="utf-8",
            )
            self._write_worker(meight_home, "review-1")
            manifest = self._write_manifest(
                repo,
                [{"name": "review-1", "mode": "review", "output": "artifacts/review.md"}],
            )

            proc = self._validate_wave(manifest, meight_home, repo)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("review verdict FAIL", proc.stderr)

    def test_result_contract_distinguishes_missing_review_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "review.md"
            artifact.write_text("## Findings\n- None.\n\n## Tests\n- Not run.\n", encoding="utf-8")

            proc = self._validate_result(artifact, "--require-review")

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("missing review verdict", proc.stderr)


if __name__ == "__main__":
    unittest.main()
