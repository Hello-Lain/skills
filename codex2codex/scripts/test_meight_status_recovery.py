#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MEIGHT = SCRIPT_DIR.parent / "meight.py"


def load_meight_module():
    os.environ["MEIGHT_NO_BUNDLED_PYTHON"] = "1"
    spec = importlib.util.spec_from_file_location("meight_under_test", MEIGHT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


meight = load_meight_module()


class MeightStatusRecoveryTest(unittest.TestCase):
    def test_wait_state_mapping_distinguishes_terminal_active_and_question(self) -> None:
        self.assertEqual(meight.classify_wait_state({"state": "completed"}), 0)
        self.assertEqual(meight.classify_wait_state({"state": "failed"}), 2)
        self.assertEqual(meight.classify_wait_state({"state": "interrupted"}), 2)
        self.assertEqual(
            meight.classify_wait_state({"state": "needs_input", "needs_input_source": "question"}),
            3,
        )
        self.assertIsNone(
            meight.classify_wait_state({"state": "needs_input", "needs_input_source": "tool"})
        )
        self.assertIsNone(meight.classify_wait_state({"state": "running"}))

    def test_worker_diagnostics_marks_stalled_active_worker_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            stale = (meight.now_kst() - timedelta(seconds=120)).isoformat(timespec="seconds")
            recent = meight.now_kst().isoformat(timespec="seconds")
            self._write_status(
                home,
                "active-stalled",
                {
                    "name": "active-stalled",
                    "state": "running",
                    "updated_at": stale,
                    "last_event_at": stale,
                    "current_item_started_at": stale,
                },
            )
            self._write_status(
                home,
                "failed-old",
                {
                    "name": "failed-old",
                    "state": "failed",
                    "updated_at": stale,
                    "last_event_at": stale,
                    "failure_detail": "provider timeout",
                },
            )
            self._write_status(
                home,
                "tool-wait",
                {
                    "name": "tool-wait",
                    "state": "needs_input",
                    "needs_input_source": "tool",
                    "updated_at": recent,
                    "last_event_at": recent,
                },
            )

            diagnostics, corrupt = meight.worker_diagnostics(home, stall_warn_sec=60)
            by_name = {item["name"]: item for item in diagnostics}

            self.assertEqual(corrupt, 0)
            self.assertTrue(by_name["active-stalled"]["stalled"])
            self.assertEqual(
                by_name["active-stalled"]["stall_classification"],
                meight.GENERIC_WORKER_STALL,
            )
            self.assertIn("no worker activity", by_name["active-stalled"]["stalled_reason"])
            self.assertFalse(by_name["failed-old"]["stalled"])
            self.assertEqual(by_name["failed-old"]["failure_detail"], "provider timeout")
            self.assertFalse(by_name["tool-wait"]["stalled"])
            self.assertEqual(by_name["tool-wait"]["needs_input_source"], "tool")

    def test_worker_diagnostics_reports_pre_first_item_stall_classification(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            stale = (meight.now_kst() - timedelta(seconds=120)).isoformat(timespec="seconds")
            self._write_status(
                home,
                "pre-first-item",
                {
                    "name": "pre-first-item",
                    "state": "running",
                    "turn_id": "turn-1",
                    "updated_at": stale,
                    "last_event_at": stale,
                    "current_item": None,
                    "current_item_started_at": None,
                    "first_item_started_at": None,
                    "tokens": {"input": 0, "cached": 0, "output": 0},
                },
            )

            diagnostics, corrupt = meight.worker_diagnostics(home, stall_warn_sec=60)

            self.assertEqual(corrupt, 0)
            self.assertEqual(diagnostics[0]["stall_classification"], meight.PRE_FIRST_ITEM_STALL)

    def test_worker_diagnostics_preserves_question_need_input_detail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            now = meight.now_kst().isoformat(timespec="seconds")
            self._write_status(
                home,
                "question",
                {
                    "name": "question",
                    "state": "needs_input",
                    "needs_input_source": "question",
                    "needs_input_detail": "QUESTION: choose API shape",
                    "updated_at": now,
                    "last_event_at": now,
                },
            )

            diagnostics, corrupt = meight.worker_diagnostics(home, stall_warn_sec=60)

            self.assertEqual(corrupt, 0)
            self.assertEqual(diagnostics[0]["needs_input_source"], "question")
            self.assertEqual(diagnostics[0]["needs_input_detail"], "QUESTION: choose API shape")
            self.assertFalse(diagnostics[0]["stalled"])

    def _write_status(self, home: Path, name: str, status: dict) -> None:
        worker_dir = home / "workers" / name
        worker_dir.mkdir(parents=True)
        (worker_dir / "status.json").write_text(json.dumps(status), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
