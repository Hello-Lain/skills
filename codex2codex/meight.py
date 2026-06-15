#!/usr/bin/env python3
"""codex2codex: Harness for running multiple Codex workers in parallel. See SPEC.md for the contract.

Run: .venv/bin/python meight.py <cmd>
Observe by pulling disk digests, steer mid-turn, and push only through wait.
"""

from __future__ import annotations

import argparse
import shutil
import fcntl
import json
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
DEBUG_EVENTS = os.environ.get("MEIGHT_DEBUG") == "1"
TERMINAL_STATES = {"completed", "failed", "interrupted"}
ACTIVE_STATES = {"starting", "running", "needs_input"}
SOCKET_TIMEOUT_SEC = 60.0  # start/follow may take several seconds for thread_start+turn RPCs
STATUS_THROTTLE_SEC = 2.0
EVENT_LINE_MAX = 300
HEARTBEAT_SEC = 5.0
STALL_WARN_SEC = 600.0

# Bidirectional workers: automatically prepend this before start/follow briefs (disable with --no-preamble)
PREAMBLE = """[Harness protocol — applies on top of the task below]
- Never run `git commit` or `git push`. Leave all changes in the working tree.
- You are a teammate on this work, not a tool that only executes. If you see a better approach, the brief rests on a wrong assumption, or there's a tradeoff worth weighing before a direction is locked in, don't silently comply or guess — raise it in a final paragraph starting with `QUESTION:` and the orchestrator will discuss and adjust direction with you. Judge by the bar: raise it when the call could change direction — scope, approach, or risk — and just decide local implementation choices yourself, noting them as judgment calls in your report.
- Likewise, when you are genuinely blocked on a decision or missing information that only the orchestrator can provide, end with a `QUESTION:` paragraph stating exactly what you need instead of guessing. Either way you receive the answer as a follow-up turn in this same thread.
"""

SANDBOX_MAP = {
    "ws": "workspace_write",
    "workspace_write": "workspace_write",
    "workspace-write": "workspace_write",
    "ro": "read_only",
    "read_only": "read_only",
    "read-only": "read_only",
    "full": "full_access",
    "full_access": "full_access",
    "full-access": "full_access",
}


# ── Common Utilities ───────────────────────────────────────────────────────

def now_kst() -> datetime:
    return datetime.now(KST)


def now_iso() -> str:
    return now_kst().isoformat(timespec="seconds")


def state_home() -> Path:
    env = os.environ.get("MEIGHT_HOME")
    if env:
        return Path(env)
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        if root:
            return Path(root) / ".meight"
    except Exception:
        pass
    return Path.cwd() / ".meight"


def atomic_write_json(path: Path, obj: dict) -> None:
    # Include pid+thread id in tmp names so concurrent writers cannot steal each other's tmp files.
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError, ValueError):
        return False
    except OSError:
        return False


def read_daemon_pid(home: Path) -> int | None:
    try:
        return int((home / "daemon.pid").read_text().strip())
    except (OSError, ValueError):
        return None

def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None

def age_seconds_from_iso(value: str | None) -> int | None:
    dt = parse_iso(value)
    if dt is None:
        return None
    return max(0, int((now_kst() - dt).total_seconds()))

def activity_age_seconds(st: dict) -> int | None:
    """Age of the newest observed worker activity, including retry/error events."""
    ages = [
        age_seconds_from_iso(st.get("updated_at")),
        age_seconds_from_iso(st.get("last_event_at")),
    ]
    ages = [a for a in ages if a is not None]
    return min(ages) if ages else None

def file_age_seconds(path: Path) -> int | None:
    try:
        return max(0, int(time.time() - path.stat().st_mtime))
    except OSError:
        return None

def redact_env_presence() -> dict[str, bool]:
    keys = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
            "http_proxy", "https_proxy", "all_proxy", "no_proxy",
            "UV_DEFAULT_INDEX")
    return {k: k in os.environ for k in keys}

def recent_event_tail(worker_dir: Path) -> str | None:
    path = worker_dir / "events.log"
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if line.strip():
            return truncate(line, 220)
    return None


def probe_daemon_socket(sock_path: Path, timeout: float = 3.0) -> bool:
    """Ping meight.sock to confirm the daemon is alive and avoid false positives from pid reuse."""
    if not sock_path.exists():
        return False
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(str(sock_path))
        s.sendall(b'{"cmd":"ping"}\n')
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(4096)
            if not chunk:
                return False
            buf += chunk
        return json.loads(buf.split(b"\n", 1)[0]).get("ok") is True
    except (OSError, json.JSONDecodeError):
        return False
    finally:
        s.close()


def truncate(text: str, limit: int) -> str:
    text = text.replace("\n", " ").strip()
    return text if len(text) <= limit else text[: limit - 1] + "…"


def dig(d: object, *keys: str, default=None):
    """Chained dict.get helper for missing beta SDK payload fields."""
    cur = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k)
    return default if cur is None else cur


# ── Worker (Inside Daemon) ─────────────────────────────────────────────────

def describe_item(item: dict) -> str:
    itype = item.get("type", "unknown")
    if itype == "commandExecution":
        return f"commandExecution: {truncate(item.get('command', ''), 120)}"
    if itype == "agentMessage":
        return "agentMessage"
    if itype == "reasoning":
        return "reasoning"
    if itype == "fileChange":
        paths = [dig(c, "path", default="?") for c in item.get("changes") or []]
        return f"fileChange: {truncate(', '.join(str(p) for p in paths), 150)}"
    if itype == "mcpToolCall":
        return f"mcpToolCall: {item.get('server', '?')}/{item.get('tool', '?')}"
    if itype == "webSearch":
        return f"webSearch: {truncate(item.get('query', ''), 100)}"
    return itype


def files_from_diff(diff: str) -> list[str]:
    files: list[str] = []
    for line in diff.splitlines():
        m = re.match(r"^diff --git a/(.+?) b/(.+)$", line)
        if m:
            files.append(m.group(2).strip())
            continue
        m = re.match(r"^\+\+\+ (?:b/)?(.+)$", line)
        if m and m.group(1).strip() != "/dev/null":
            files.append(m.group(1).strip())
    seen: dict[str, None] = {}
    for f in files:
        seen.setdefault(f, None)
    return list(seen.keys())


class Worker:
    """One worker = one Codex Thread plus a digest file set."""

    def __init__(self, name: str, home: Path, cwd: str, sandbox: str,
                 model: str | None, effort: str, service_tier: str | None = None):
        self.name = name
        self.dir = home / "workers" / name
        self.cwd = cwd
        self.sandbox = sandbox  # normalized key such as "workspace_write"
        self.model = model
        self.effort = effort
        self.service_tier = service_tier  # None -> inherit ~/.codex/config.toml; else override per worker
        self.thread = None       # openai_codex.Thread (kept while daemon lives -> reused for follow)
        self.handle = None       # TurnHandle
        self.consumer: threading.Thread | None = None
        self.interrupt_requested = False
        self.lock = threading.Lock()       # serialize status/event handling
        self.ctl_lock = threading.Lock()   # serialize control calls such as steer/interrupt
        self.generation = 0                # turn generation; ignores late events from old streams
        self._last_status_write = 0.0
        self._agent_msg_buf = ""       # accumulated in-flight agentMessage deltas
        self._last_agent_msg = ""      # last finalized agentMessage
        self._current_item_label: str | None = None
        self._current_item_since: float | None = None
        # The public status.json field needs_input_source is the SSOT for needs_input:
        # "question" (final QUESTION; wait exits 3) | "tool" (mid-turn wait; treated as active)
        self.status: dict = {}

    # ── status.json ──

    def init_status(self, thread_id: str | None, turns: int = 1) -> None:
        with self.lock:
            self._init_status_locked(thread_id, turns)

    def _init_status_locked(self, thread_id: str | None, turns: int) -> None:
        self.status = {
            "name": self.name,
            "thread_id": thread_id,
            "turn_id": None,
            "state": "starting",
            "started_at": now_iso(),
            "updated_at": now_iso(),
            "cwd": self.cwd,
            "sandbox": self.sandbox.replace("_", "-"),
            "model": self.model,
            "effort": self.effort,
            "service_tier": self.service_tier,
            "current_item": None,
            "current_item_started_at": None,
            "plan": [],
            "files_changed": [],
            "tokens": {"input": 0, "cached": 0, "output": 0},
            "last_message_tail": "",
            "last_event_at": None,
            "last_event": None,
            "stalled": False,
            "stalled_reason": None,
            "needs_input_detail": None,
            "needs_input_source": None,
            "failure_detail": None,
            "turns": turns,
        }
        self.write_status(force=True)

    def write_status(self, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last_status_write < STATUS_THROTTLE_SEC:
            return
        self._last_status_write = now
        self.status["updated_at"] = now_iso()
        if self._current_item_label and self._current_item_since is not None:
            elapsed = int(time.monotonic() - self._current_item_since)
            self.status["current_item"] = f"{self._current_item_label} ({elapsed}s)"
        else:
            self.status["current_item"] = None
            self.status["current_item_started_at"] = None
        atomic_write_json(self.dir / "status.json", self.status)

    def log_event(self, method: str, summary: str) -> None:
        line = f"{now_iso()} [{method}] {truncate(summary, EVENT_LINE_MAX - 60)}"
        with open(self.dir / "events.log", "a", encoding="utf-8") as f:
            f.write(line[:EVENT_LINE_MAX] + "\n")
        self.status["last_event_at"] = now_iso()
        self.status["last_event"] = truncate(f"{method}: {summary}", 220)

    # ── Event Handling ──

    def consume_stream(self, daemon: "Daemon", gen: int, handle) -> None:
        try:
            for note in handle.stream():
                try:
                    self.on_event(note, daemon, gen)
                except Exception as e:  # one event handler failure must not kill the worker
                    daemon.log(f"worker={self.name} event handler error: {e!r}")
            self.on_stream_end(gen)
        except Exception as e:
            with self.lock:
                state = self.status.get("state")
                question_final = (state == "needs_input"
                                  and self.status.get("needs_input_source") == "question")
                if gen == self.generation and state not in TERMINAL_STATES and not question_final:
                    self.status["state"] = "interrupted" if self.interrupt_requested else "failed"
                    self.status["needs_input_detail"] = None
                    self.status["needs_input_source"] = None
                    self.log_event("stream/exception", f"{type(e).__name__}: {e}")
                    self.write_status(force=True)
            daemon.log(f"worker={self.name} stream exception: {traceback.format_exc(limit=3)}")

    def on_event(self, note, daemon: "Daemon", gen: int) -> None:
        method = note.method
        payload = note.payload
        # mode="json": enum -> value strings, Path -> str (avoid exposing raw beta SDK enums)
        p = payload.model_dump(mode="json") if hasattr(payload, "model_dump") else (
            payload if isinstance(payload, dict) else {})

        if DEBUG_EVENTS:
            try:
                with open(self.dir / "debug-events.log", "a", encoding="utf-8") as f:
                    f.write(f"{now_iso()} {method} {json.dumps(p, ensure_ascii=False, default=str)[:4000]}\n")
            except Exception:
                pass

        with self.lock:
            if gen != self.generation:
                return  # late event from an old turn; prevents status/result contamination
            self._handle_event(method, p)

    def _handle_event(self, method: str, p: dict) -> None:
        if method == "turn/started":
            self.status["turn_id"] = dig(p, "turn", "id")
            if self.status["state"] == "starting":
                self.status["state"] = "running"
            self.log_event(method, f"turn={self.status['turn_id']}")
            self.write_status(force=True)

        elif method == "item/started":
            item = p.get("item") or {}
            self._current_item_label = describe_item(item)
            self._current_item_since = time.monotonic()
            self.status["current_item_started_at"] = now_iso()
            if item.get("type") == "agentMessage":
                self._agent_msg_buf = ""
            if self.status["state"] in ("starting", "needs_input"):
                self.status["state"] = "running"
                self.status["needs_input_detail"] = None
                self.status["needs_input_source"] = None
            self.write_status(force=True)

        elif method == "item/agentMessage/delta":
            self._agent_msg_buf += p.get("delta") or ""
            self.status["last_message_tail"] = self._agent_msg_buf[-500:]
            self.write_status()  # throttled

        elif method == "item/completed":
            self._on_item_completed(p.get("item") or {})

        elif method == "turn/plan/updated":
            marker = {"completed": "[done]", "inProgress": "[active]", "pending": "[ ]"}
            self.status["plan"] = [
                f"{marker.get(dig(s, 'status', default=''), '[?]')} {dig(s, 'step', default='')}"
                for s in p.get("plan") or []
            ]
            self.write_status(force=True)

        elif method == "turn/diff/updated":
            files = files_from_diff(p.get("diff") or "")
            if files:
                self.status["files_changed"] = files
            self.write_status()

        elif method == "thread/tokenUsage/updated":
            total = dig(p, "token_usage", "total", default={})
            self.status["tokens"] = {
                "input": dig(total, "input_tokens", default=0),
                "cached": dig(total, "cached_input_tokens", default=0),
                "output": dig(total, "output_tokens", default=0),
            }
            self.write_status()

        elif method == "turn/completed":
            self._on_turn_completed(p.get("turn") or {})

        elif method == "error":
            msg = dig(p, "error", "message", default="unknown error")
            will_retry = bool(p.get("will_retry"))
            self.log_event(method, f"{msg} (will_retry={will_retry})")
            if not will_retry:
                self.status["state"] = "failed"
                self.status["needs_input_detail"] = None
                self.status["needs_input_source"] = None
                self.status["failure_detail"] = truncate(msg, 500)
                self.write_status(force=True)
            else:
                # Retry errors are still live activity. Persist them so wait/doctor do not
                # misclassify a reconnecting worker as stalled due to an old updated_at.
                self.write_status(force=True)

        elif method == "tool/requestUserInput" or method.endswith("/requestApproval"):
            # With config approval=never this should not happen; defensive handling only (v1: no auto-reply).
            self.status["state"] = "needs_input"
            self.status["needs_input_detail"] = truncate(json.dumps(p, ensure_ascii=False, default=str), 500)
            self.status["needs_input_source"] = "tool"  # mid-turn wait, not final; wait treats it as active
            self.log_event(method, self.status["needs_input_detail"])
            self.write_status(force=True)

        elif method in ("item/commandExecution/outputDelta",
                        "item/reasoning/textDelta",
                        "item/reasoning/summaryTextDelta",
                        "item/reasoning/summaryPartAdded",
                        "item/fileChange/outputDelta",
                        "item/plan/delta"):
            self.write_status()  # deltas only refresh throttled status without logging (elapsed update)

        else:
            pass  # ignore unknown or irrelevant events

    def _on_item_completed(self, item: dict) -> None:
        itype = item.get("type", "unknown")
        if itype == "agentMessage":
            text = item.get("text") or self._agent_msg_buf
            self._last_agent_msg = text
            self.status["last_message_tail"] = text[-500:]
            self.log_event("item/completed", f"agentMessage: {truncate(text, 150)}")
        elif itype == "commandExecution":
            self.log_event(
                "item/completed",
                f"commandExecution: {truncate(item.get('command', ''), 150)}"
                f" → exit {item.get('exit_code')}",
            )
        elif itype == "fileChange":
            paths = [str(dig(c, "path", default="?")) for c in item.get("changes") or []]
            for path in paths:
                if path not in self.status["files_changed"]:
                    self.status["files_changed"].append(path)
            self.log_event("item/completed",
                           f"fileChange ({item.get('status')}): {', '.join(paths)}")
        elif itype == "mcpToolCall":
            self.log_event("item/completed",
                           f"mcpToolCall: {item.get('server')}/{item.get('tool')}"
                           f" → {item.get('status')}")
        elif itype == "webSearch":
            self.log_event("item/completed", f"webSearch: {truncate(item.get('query', ''), 150)}")
        # Other item types such as reasoning are noise, so do not log them.
        self._current_item_label = None
        self._current_item_since = None
        self.write_status(force=True)

    def _extract_question(self) -> str | None:
        """Return the final paragraph if the final agent message ends with a QUESTION: block."""
        msg = (self._last_agent_msg or self._agent_msg_buf).strip()
        if not msg:
            return None
        paragraphs = [blk.strip() for blk in re.split(r"\n\s*\n", msg) if blk.strip()]
        if paragraphs and paragraphs[-1].startswith("QUESTION:"):
            return paragraphs[-1]
        return None

    def _on_turn_completed(self, turn: dict) -> None:
        turn_status = turn.get("status")  # completed | interrupted | failed | (future SDK values)
        prior = self.status.get("state")
        # Priority: preserve existing failed/interrupted > promote QUESTION > completed
        if prior in ("failed", "interrupted"):
            # A late completed event must not overwrite a failure already set by a non-retry error.
            self.log_event("turn/completed",
                           f"turn status {turn_status!r} ignored — state already {prior}")
        elif turn_status == "interrupted":
            self.status["state"] = "interrupted"
            if not self.status.get("failure_detail"):
                self.status["failure_detail"] = "interrupted"
        elif turn_status == "completed":
            # Promote QUESTION only for normally completed turns so it cannot conflict with interrupted/failed.
            question = self._extract_question()
            if question:
                self.status["state"] = "needs_input"
                self.status["needs_input_detail"] = question if len(question) <= 500 else question[:499] + "…"
                self.status["needs_input_source"] = "question"
                self.log_event("question", question)
            else:
                self.status["state"] = "completed"
        elif turn_status == "failed":
            self.status["state"] = "failed"
            err = dig(turn, "error", "message")
            if err:
                self.status["failure_detail"] = truncate(err, 500)
                self.log_event("turn/completed", f"failed: {truncate(err, 200)}")
        else:
            # Mapping unknown/missing statuses to completed would violate the wait contract.
            self.status["state"] = "interrupted" if self.interrupt_requested else "failed"
            self.status["failure_detail"] = f"unexpected turn status {turn_status!r}"
            self.log_event("turn/completed",
                           f"unexpected turn status {turn_status!r} → {self.status['state']}")
        # Clear stale tool wait details for every non-question terminal state (failed/interrupted/completed).
        if self.status["state"] != "needs_input":
            self.status["needs_input_detail"] = None
            self.status["needs_input_source"] = None
        self._current_item_label = None
        self._current_item_since = None
        self.write_result()
        self.log_event("turn/completed", f"state={self.status['state']}")
        self.write_status(force=True)

    def on_stream_end(self, gen: int) -> None:
        with self.lock:
            if gen != self.generation:
                return
            state = self.status.get("state")
            if state == "needs_input":
                if self.status.get("needs_input_source") == "question":
                    return  # final QUESTION; keep waiting for a follow-up answer
                # Stream ended while waiting on tool/approval without a terminal event = failure, not hidden.
                self.status["state"] = "interrupted" if self.interrupt_requested else "failed"
                self.status["needs_input_detail"] = None
                self.status["needs_input_source"] = None
                self.status["failure_detail"] = "stream ended while awaiting tool/approval"
                self.log_event("stream/ended",
                               f"stream ended while awaiting tool/approval → {self.status['state']}")
                self.write_result()
                self.write_status(force=True)
                return
            if state not in TERMINAL_STATES:
                self.status["state"] = "interrupted" if self.interrupt_requested else "failed"
                self.status["failure_detail"] = "stream ended without terminal event"
                self.log_event("stream/ended", f"stream ended without terminal event → {self.status['state']}")
                self.write_result()
                self.write_status(force=True)

    def write_result(self) -> None:
        msg = self._last_agent_msg or self._agent_msg_buf
        if not msg:
            msg = "(no agent message)"
            if self.status.get("failure_detail"):
                msg += f"\n\nFailure: {self.status['failure_detail']}"
        header = ""
        if self.status.get("turns", 1) > 1:
            header = f"\n\n---\n## Turn {self.status['turns']} ({now_iso()})\n\n"
        with open(self.dir / "result.md", "a", encoding="utf-8") as f:
            f.write(header + msg + "\n")

    # ── Reset For Follow ──

    def reset_for_follow(self, brief: str) -> None:
        with self.lock:
            self.generation += 1  # after this point, all old stream events are ignored
            self.interrupt_requested = False
            self._agent_msg_buf = ""
            self._last_agent_msg = ""
            self._current_item_label = None
            self._current_item_since = None
            turns = int(self.status.get("turns", 1)) + 1
            sep = f"\n\n---\n## Turn {turns} ({now_iso()})\n\n"
            with open(self.dir / "brief.md", "a", encoding="utf-8") as f:
                f.write(sep + brief + "\n")
            with open(self.dir / "events.log", "a", encoding="utf-8") as f:
                f.write(f"--- turn {turns} ({now_iso()}) ---\n")
            self.status.update({
                "turn_id": None,
                "state": "starting",
                "started_at": now_iso(),
                "current_item": None,
                "current_item_started_at": None,
                "plan": [],
                "files_changed": [],
                "last_message_tail": "",
                "last_event_at": None,
                "last_event": None,
                "stalled": False,
                "stalled_reason": None,
                "needs_input_detail": None,
                "needs_input_source": None,
                "failure_detail": None,
                "turns": turns,
            })
            self.write_status(force=True)

    def current_state(self) -> str:
        with self.lock:
            return self.status.get("state", "unknown")

    def mark_failed(self, reason: str) -> None:
        with self.lock:
            self.status["state"] = "failed"
            self.log_event("daemon/error", reason)
            self.write_status(force=True)

    def consumer_finished(self, join_timeout: float = 3.0) -> bool:
        if self.consumer is None:
            return True
        self.consumer.join(timeout=join_timeout)
        return not self.consumer.is_alive()


# ── Daemon ─────────────────────────────────────────────────────────────────

class Daemon:
    def __init__(self, home: Path):
        self.home = home
        self.sock_path = home / "meight.sock"
        self.pid_path = home / "daemon.pid"
        self.log_path = home / "daemon.log"
        self.heartbeat_path = home / "daemon.heartbeat.json"
        self.codex = None
        self.workers: dict[str, Worker] = {}
        self.reg_lock = threading.Lock()
        self.shutting_down = threading.Event()
        self.server: socket.socket | None = None
        self.lock_file = None  # flock handle kept while the daemon is alive
        self.heartbeat_thread: threading.Thread | None = None

    def log(self, msg: str) -> None:
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"{now_iso()} {msg}\n")
        except OSError:
            pass

    # ── Startup/Cleanup ──

    def run(self) -> int:
        self.home.mkdir(parents=True, exist_ok=True)
        (self.home / "workers").mkdir(exist_ok=True)

        # Singleton guard 1: flock blocks concurrent startup regardless of pid file presence/reuse.
        self.lock_file = open(self.home / "daemon.lock", "w")
        try:
            fcntl.flock(self.lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            print("daemon already running (daemon.lock held)", file=sys.stderr)
            return 1
        # Singleton guard 2: never unlink an existing socket if it is alive.
        if probe_daemon_socket(self.sock_path):
            print(f"daemon already running (live socket at {self.sock_path})", file=sys.stderr)
            return 1
        # From here on the state is confirmed stale, so clean up leftovers.
        for p in (self.sock_path, self.pid_path):
            try:
                p.unlink()
            except FileNotFoundError:
                pass

        from openai_codex import Codex
        self.codex = Codex()

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(str(self.sock_path))
        self.server.listen(16)
        self.server.settimeout(1.0)
        self.pid_path.write_text(str(os.getpid()) + "\n")

        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)

        self.log(f"daemon started pid={os.getpid()} home={self.home}")
        print(f"codex2codex daemon listening on {self.sock_path} (pid {os.getpid()})", flush=True)
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True,
                                                 name="meight-heartbeat")
        self.heartbeat_thread.start()

        try:
            while not self.shutting_down.is_set():
                try:
                    conn, _ = self.server.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break  # socket closed = shutdown
                threading.Thread(target=self._handle_conn, args=(conn,), daemon=True).start()
        finally:
            self._cleanup()
        return 0

    def _heartbeat_loop(self) -> None:
        while not self.shutting_down.is_set():
            with self.reg_lock:
                active = [n for n, w in self.workers.items() if w.current_state() in ACTIVE_STATES]
            try:
                atomic_write_json(self.heartbeat_path, {
                    "pid": os.getpid(),
                    "home": str(self.home),
                    "updated_at": now_iso(),
                    "active_workers": active,
                    "worker_count": len(self.workers),
                })
            except OSError as e:
                self.log(f"heartbeat write failed: {e!r}")
            self.shutting_down.wait(HEARTBEAT_SEC)

    def _on_signal(self, signum, frame) -> None:
        self.log(f"signal {signum} received → shutdown")
        threading.Thread(target=self._shutdown_now, daemon=True).start()

    def _shutdown_now(self) -> None:
        if self.shutting_down.is_set():
            return
        self.shutting_down.set()
        with self.reg_lock:
            workers = list(self.workers.values())
        for w in workers:
            with w.ctl_lock:
                if w.current_state() in ACTIVE_STATES and w.handle is not None:
                    w.interrupt_requested = True
                    try:
                        w.handle.interrupt()
                    except Exception as e:
                        self.log(f"interrupt {w.name} failed: {e!r}")
        deadline = time.monotonic() + 10
        for w in workers:
            if w.consumer is not None:
                w.consumer.join(timeout=max(0.1, deadline - time.monotonic()))
        try:
            if self.server is not None:
                self.server.close()
        except OSError:
            pass

    def _cleanup(self) -> None:
        try:
            if self.codex is not None:
                self.codex.close()
        except Exception as e:
            self.log(f"codex.close() error: {e!r}")
        for p in (self.sock_path, self.pid_path):
            try:
                p.unlink()
            except FileNotFoundError:
                pass
        try:
            self.heartbeat_path.unlink()
        except FileNotFoundError:
            pass
        if self.lock_file is not None:
            try:
                self.lock_file.close()  # release flock
            except OSError:
                pass
        self.log("daemon stopped")

    # ── Socket Handling ──

    def _handle_conn(self, conn: socket.socket) -> None:
        try:
            conn.settimeout(SOCKET_TIMEOUT_SEC)
            buf = b""
            while b"\n" not in buf:
                chunk = conn.recv(65536)
                if not chunk:
                    return
                buf += chunk
            req = json.loads(buf.split(b"\n", 1)[0].decode("utf-8"))
            resp = self._dispatch(req)
            should_shutdown = bool(resp.pop("_shutdown", False))
            conn.sendall((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
            if should_shutdown:
                self._shutdown_now()
        except Exception as e:
            self.log(f"conn error: {e!r}")
            try:
                conn.sendall((json.dumps({"ok": False, "error": str(e)}) + "\n").encode("utf-8"))
            except OSError:
                pass
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def _dispatch(self, req: dict) -> dict:
        cmd = req.get("cmd")
        try:
            if cmd == "ping":
                return {"ok": True, "pid": os.getpid()}
            if cmd == "start":
                return self.cmd_start(req)
            if cmd == "follow":
                return self.cmd_follow(req)
            if cmd == "steer":
                return self.cmd_steer(req)
            if cmd == "interrupt":
                return self.cmd_interrupt(req)
            if cmd == "shutdown":
                return self.cmd_shutdown(req)
            return {"ok": False, "error": f"unknown cmd: {cmd}"}
        except Exception as e:
            self.log(f"cmd={cmd} error: {traceback.format_exc(limit=5)}")
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    # ── Command Implementations ──

    def cmd_start(self, req: dict) -> dict:
        from openai_codex import Sandbox

        name = req["name"]
        brief = req["brief"]
        use_preamble = not req.get("no_preamble")
        turn_input = f"{PREAMBLE}\n{brief}" if use_preamble else brief
        file_brief = f"{PREAMBLE}\n---\n\n{brief}" if use_preamble else brief
        cwd = req.get("cwd") or os.getcwd()
        sandbox_key = SANDBOX_MAP.get(req.get("sandbox") or "ws")
        if sandbox_key is None:
            return {"ok": False, "error": f"invalid sandbox: {req.get('sandbox')}"}
        model = req.get("model")
        effort = req.get("effort") or "medium"
        service_tier = req.get("service_tier")

        with self.reg_lock:
            existing = self.workers.get(name)
            if existing is not None:
                if existing.current_state() in ACTIVE_STATES:
                    return {"ok": False,
                            "error": f"worker '{name}' is already active ({existing.current_state()})"}
                # Even in a terminal state, reject reuse while the old consumer may still be writing files.
                if not existing.consumer_finished():
                    return {"ok": False,
                            "error": f"worker '{name}' previous stream is still finishing — retry shortly"}

            w = Worker(name, self.home, cwd, sandbox_key, model, effort, service_tier)
            w.dir.mkdir(parents=True, exist_ok=True)
            # Restarting the same name creates a new worker, so reset prior outputs.
            for fname in ("events.log", "result.md", "debug-events.log"):
                try:
                    (w.dir / fname).unlink()
                except FileNotFoundError:
                    pass
            (w.dir / "brief.md").write_text(file_brief + "\n", encoding="utf-8")

            w.init_status(thread_id=None)
            try:
                thread = self.codex.thread_start()
                w.thread = thread
                with w.lock:
                    w.status["thread_id"] = thread.id
                w.handle = thread.turn(
                    turn_input, cwd=cwd, sandbox=getattr(Sandbox, sandbox_key),
                    model=model, effort=effort, service_tier=service_tier,
                )
            except Exception as e:
                # If SDK failure leaves a starting zombie, wait polls until timeout.
                w.mark_failed(f"start failed: {type(e).__name__}: {e}")
                self.workers[name] = w
                self.log(f"start worker={name} failed: {e!r}")
                return {"ok": False, "error": f"start failed: {type(e).__name__}: {e}"}

            w.generation = 1
            w.consumer = threading.Thread(
                target=w.consume_stream, args=(self, w.generation, w.handle), daemon=True,
                name=f"worker-{name}",
            )
            w.consumer.start()
            self.workers[name] = w

        self.log(f"start worker={name} thread={thread.id} cwd={cwd} sandbox={sandbox_key}")
        return {"ok": True, "thread_id": thread.id}

    def cmd_follow(self, req: dict) -> dict:
        from openai_codex import Sandbox

        name = req["name"]
        brief = req["brief"]
        use_preamble = not req.get("no_preamble")
        turn_input = f"{PREAMBLE}\n{brief}" if use_preamble else brief
        file_brief = f"{PREAMBLE}\n---\n\n{brief}" if use_preamble else brief
        with self.reg_lock:
            w = self.workers.get(name)
            if w is None:
                if (self.home / "workers" / name / "status.json").exists():
                    return {"ok": False, "error":
                            f"worker '{name}' exists on disk but not in this daemon "
                            "(daemon restarted?). follow across daemon restarts is out of scope in v1 — "
                            "use 'start' with a new name instead."}
                return {"ok": False, "error": f"unknown worker: {name}"}
            prev_state = w.current_state()
            # needs_input (waiting on QUESTION) can also follow; send the answer as a new turn on the same thread.
            if prev_state not in TERMINAL_STATES and prev_state != "needs_input":
                return {"ok": False, "error":
                        f"worker '{name}' is not in a terminal state ({prev_state})"}
            if w.thread is None:
                return {"ok": False, "error":
                        f"worker '{name}' has no codex thread (start failed earlier) — use 'start' instead"}
            # Reject follow until the old consumer fully exits (first guard against late-event contamination).
            if not w.consumer_finished():
                return {"ok": False,
                        "error": f"worker '{name}' previous stream is still finishing — retry shortly"}

            w.reset_for_follow(file_brief)  # generation+1; also ignores any leftover old events (second guard)
            try:
                w.handle = w.thread.turn(
                    turn_input, cwd=w.cwd, sandbox=getattr(Sandbox, w.sandbox),
                    model=w.model, effort=w.effort, service_tier=w.service_tier,
                )
            except Exception as e:
                w.mark_failed(f"follow turn failed (was {prev_state}): {type(e).__name__}: {e}")
                self.log(f"follow worker={name} failed: {e!r}")
                return {"ok": False, "error": f"follow failed: {type(e).__name__}: {e}"}
            with w.lock:
                gen = w.generation
                turns = w.status["turns"]
                thread_id = w.status["thread_id"]
            w.consumer = threading.Thread(
                target=w.consume_stream, args=(self, gen, w.handle), daemon=True,
                name=f"worker-{name}-t{turns}",
            )
            w.consumer.start()

        self.log(f"follow worker={name} thread={thread_id} turn#{turns}")
        return {"ok": True, "thread_id": thread_id, "turns": turns}

    def cmd_steer(self, req: dict) -> dict:
        name = req["name"]
        with self.reg_lock:
            w = self.workers.get(name)
        if w is None:
            return {"ok": False, "error": f"unknown worker: {name}"}
        with w.ctl_lock:  # serialize concurrent steer/interrupt and re-check state inside the lock
            state = w.current_state()
            if state != "running":
                return {"ok": False, "error": f"worker '{name}' is not running ({state})"}
            w.handle.steer(req["text"])
            w.log_event("steer", truncate(req["text"], 200))
        self.log(f"steer worker={name}")
        return {"ok": True}

    def cmd_interrupt(self, req: dict) -> dict:
        name = req["name"]
        with self.reg_lock:
            w = self.workers.get(name)
        if w is None:
            return {"ok": False, "error": f"unknown worker: {name}"}
        with w.ctl_lock:
            state = w.current_state()
            if state in TERMINAL_STATES:
                return {"ok": True, "note": f"already terminal ({state})"}  # idempotent
            if state not in ACTIVE_STATES:
                return {"ok": False, "error": f"worker '{name}' is not active ({state})"}
            if w.interrupt_requested:
                return {"ok": True, "note": "interrupt already requested"}  # idempotent
            w.interrupt_requested = True
            try:
                w.handle.interrupt()
            except Exception as e:
                # Interrupt may fail right after a turn ends; keep the requested flag.
                w.log_event("interrupt", f"request failed: {type(e).__name__}: {e}")
                self.log(f"interrupt worker={name} sdk error: {e!r}")
                return {"ok": True, "note": f"interrupt call failed ({type(e).__name__}) — turn may have ended"}
            w.log_event("interrupt", "requested by client")
        self.log(f"interrupt worker={name}")
        return {"ok": True}

    def cmd_shutdown(self, req: dict) -> dict:
        force = bool(req.get("force"))
        with self.reg_lock:
            active = [n for n, w in self.workers.items()
                      if w.current_state() in ACTIVE_STATES]
        if active and not force:
            return {"ok": False,
                    "error": f"active workers: {', '.join(active)} — use --force to interrupt and shut down"}
        self.log(f"shutdown requested (force={force}, active={active})")
        return {"ok": True, "interrupted": active, "_shutdown": True}


# ── Client ─────────────────────────────────────────────────────────────────

def send_request(home: Path, req: dict, timeout: float = SOCKET_TIMEOUT_SEC) -> dict:
    sock_path = home / "meight.sock"
    if not sock_path.exists():
        raise SystemExit(f"daemon socket not found: {sock_path} (check that the daemon is running)")
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(str(sock_path))
        s.sendall((json.dumps(req, ensure_ascii=False) + "\n").encode("utf-8"))
        buf = b""
        while b"\n" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                raise SystemExit("daemon closed connection without response")
            buf += chunk
        return json.loads(buf.split(b"\n", 1)[0].decode("utf-8"))
    except socket.timeout:
        raise SystemExit(f"daemon response timed out after {timeout}s")
    finally:
        s.close()


def expect_ok(resp: dict) -> dict:
    if not resp.get("ok"):
        print(f"error: {resp.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)
    return resp


def read_brief(args) -> str:
    brief_file = getattr(args, "brief_file", None)
    if brief_file == "-":
        return sys.stdin.read()  # heredocs and similar inputs avoid shell quoting for long briefs
    if brief_file:
        return Path(brief_file).read_text(encoding="utf-8")
    if getattr(args, "brief", None):
        return args.brief
    raise SystemExit("--brief or --brief-file required")


def load_statuses(home: Path) -> list[dict]:
    out = []
    workers_dir = home / "workers"
    if not workers_dir.is_dir():
        return out
    for d in sorted(workers_dir.iterdir()):
        sj = d / "status.json"
        if sj.is_file():
            try:
                out.append(json.loads(sj.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                pass
    return out


def fmt_elapsed(st: dict) -> str:
    try:
        start = datetime.fromisoformat(st["started_at"])
        end = now_kst() if st.get("state") in ACTIVE_STATES else datetime.fromisoformat(st["updated_at"])
        sec = max(0, int((end - start).total_seconds()))
        if sec < 60:
            return f"{sec}s"
        return f"{sec // 60}m{sec % 60:02d}s"
    except (KeyError, ValueError):
        return "?"


def fmt_tokens(st: dict) -> str:
    t = st.get("tokens") or {}
    return f"in:{t.get('input', 0)} out:{t.get('output', 0)}"


def summary_line(st: dict) -> str:
    current = st.get("current_item") or "-"
    if st.get("stalled"):
        current = f"STALLED: {st.get('stalled_reason') or current}"
    return (f"{st.get('name', '?'):<14} {st.get('state', '?'):<12} {fmt_elapsed(st):>8} "
            f"files:{len(st.get('files_changed') or []):<3} {fmt_tokens(st):<22} "
            f"{truncate(current, 60)}")


def print_status_table(statuses: list[dict]) -> None:
    if not statuses:
        print("(no workers)")
        return
    print(f"{'NAME':<14} {'STATE':<12} {'ELAPSED':>8} {'FILES':<9} {'TOKENS':<22} CURRENT")
    for st in statuses:
        print(summary_line(st))


def read_json_file(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

def daemon_lock_state(home: Path) -> str:
    lock = home / "daemon.lock"
    if not lock.exists():
        return "absent"
    try:
        with open(lock, "r+") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f, fcntl.LOCK_UN)
                return "free"
            except OSError:
                return "held"
    except OSError:
        return "unknown"

def worker_diagnostics(home: Path, stall_warn_sec: float = STALL_WARN_SEC) -> tuple[list[dict], int]:
    out: list[dict] = []
    corrupt = 0
    workers_dir = home / "workers"
    if not workers_dir.is_dir():
        return out, corrupt
    for d in sorted(workers_dir.iterdir()):
        if not d.is_dir():
            continue
        st = read_json_file(d / "status.json")
        if st is None:
            corrupt += 1
            out.append({"name": d.name, "state": "corrupt-status"})
            continue
        updated_age = age_seconds_from_iso(st.get("updated_at"))
        active_age = activity_age_seconds(st)
        item_age = age_seconds_from_iso(st.get("current_item_started_at"))
        state = st.get("state", "unknown")
        stalled = state in ("starting", "running") and active_age is not None and active_age >= stall_warn_sec
        st["updated_age_sec"] = updated_age
        st["activity_age_sec"] = active_age
        st["current_item_age_sec"] = item_age
        st["stalled"] = stalled
        st["stalled_reason"] = (
            f"no worker activity for {active_age}s (threshold {int(stall_warn_sec)}s)"
            if stalled else None
        )
        if not st.get("last_event"):
            st["last_event"] = recent_event_tail(d)
        out.append(st)
    return out, corrupt

def doctor_report(home: Path) -> dict:
    pid = read_daemon_pid(home)
    sock_path = home / "meight.sock"
    heartbeat = read_json_file(home / "daemon.heartbeat.json")
    workers, corrupt_workers = worker_diagnostics(home)
    active = [w.get("name", "?") for w in workers if w.get("state") in ACTIVE_STATES]
    stale = [w.get("name", "?") for w in workers if w.get("stalled")]
    sdk_import = False
    sdk_error = None
    try:
        __import__("openai_codex")
        sdk_import = True
    except Exception as e:
        sdk_error = f"{type(e).__name__}: {e}"
    return {
        "home": str(home),
        "home_exists": home.exists(),
        "socket": str(sock_path),
        "socket_exists": sock_path.exists(),
        "socket_live": probe_daemon_socket(sock_path),
        "pid": pid,
        "pid_alive": pid_alive(pid) if pid is not None else False,
        "lock_state": daemon_lock_state(home),
        "heartbeat": heartbeat,
        "heartbeat_age_sec": file_age_seconds(home / "daemon.heartbeat.json"),
        "codex_cli_found": shutil.which("codex") is not None,
        "openai_codex_import": sdk_import,
        "openai_codex_error": sdk_error,
        "env_presence": redact_env_presence(),
        "worker_count": len(workers),
        "active_workers": active,
        "stalled_workers": stale,
        "corrupt_worker_statuses": corrupt_workers,
        "workers": workers,
    }

def print_doctor_report(report: dict) -> None:
    print(f"home: {report['home']}")
    print(f"socket_exists: {report['socket_exists']}")
    print(f"socket_live: {report['socket_live']}")
    print(f"pid: {report['pid']}")
    print(f"pid_alive: {report['pid_alive']}")
    print(f"lock_state: {report['lock_state']}")
    print(f"heartbeat_age_sec: {report['heartbeat_age_sec']}")
    print(f"codex_cli_found: {report['codex_cli_found']}")
    print(f"openai_codex_import: {report['openai_codex_import']}")
    if report.get("openai_codex_error"):
        print(f"openai_codex_error: {report['openai_codex_error']}")
    print(f"env_presence: {json.dumps(report['env_presence'], sort_keys=True)}")
    print(f"worker_count: {report['worker_count']}")
    print(f"active_workers: {', '.join(report['active_workers']) or '-'}")
    print(f"stalled_workers: {', '.join(report['stalled_workers']) or '-'}")
    print(f"corrupt_worker_statuses: {report['corrupt_worker_statuses']}")

def snapshot_recovery_files(home: Path, backup_root: Path | None = None) -> Path:
    stamp = now_kst().strftime("%Y%m%d-%H%M%S")
    dest = (backup_root or (home / "recovery-backups")) / stamp
    dest.mkdir(parents=True, exist_ok=False)
    candidates = [home / "daemon.pid", home / "daemon.log", home / "daemon.heartbeat.json"]
    workers_dir = home / "workers"
    if workers_dir.is_dir():
        for worker in workers_dir.iterdir():
            if not worker.is_dir():
                continue
            for name in ("status.json", "events.log", "result.md", "brief.md"):
                candidates.append(worker / name)
    for src in candidates:
        if not src.is_file():
            continue
        try:
            if src.stat().st_size > 1_000_000:
                continue
            rel = src.relative_to(home)
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
        except OSError:
            continue
    return dest

# ── CLI Commands ───────────────────────────────────────────────────────────

def cmd_daemon(args, home: Path) -> int:
    return Daemon(home).run()


def start_request(args, home: Path) -> dict:
    # --fast/--no-fast is the user-facing knob; map it to a codex service tier.
    # priority = Fast; default = a non-priority tier; None = inherit ~/.codex/config.toml.
    fast = getattr(args, "fast", None)
    service_tier = None if fast is None else ("priority" if fast else "default")
    return send_request(home, {
        "cmd": "start", "name": args.name, "brief": read_brief(args),
        "cwd": str(Path(args.cwd).resolve()) if args.cwd else os.getcwd(),
        "sandbox": args.sandbox, "model": args.model, "effort": args.effort,
        "service_tier": service_tier,
        "no_preamble": args.no_preamble,
    })


def cmd_start(args, home: Path) -> int:
    resp = expect_ok(start_request(args, home))
    print(f"started worker '{args.name}' thread={resp.get('thread_id')}")
    return 0


def cmd_follow(args, home: Path) -> int:
    resp = expect_ok(send_request(home, {
        "cmd": "follow", "name": args.name, "brief": read_brief(args),
        "no_preamble": args.no_preamble,
    }))
    print(f"follow turn #{resp.get('turns')} on worker '{args.name}' thread={resp.get('thread_id')}")
    return 0


def cmd_steer(args, home: Path) -> int:
    expect_ok(send_request(home, {"cmd": "steer", "name": args.name, "text": args.text}))
    print(f"steered '{args.name}'")
    return 0


def cmd_interrupt(args, home: Path) -> int:
    expect_ok(send_request(home, {"cmd": "interrupt", "name": args.name}))
    print(f"interrupt requested for '{args.name}'")
    return 0


def cmd_status(args, home: Path) -> int:
    name = getattr(args, "name", None)
    if name:
        sj = home / "workers" / name / "status.json"
        if not sj.is_file():
            print(f"no status for worker '{name}'", file=sys.stderr)
            return 1
        st = json.loads(sj.read_text(encoding="utf-8"))
        diag, _ = worker_diagnostics(home)
        for dst in diag:
            if dst.get("name") == name:
                st.update({k: v for k, v in dst.items()
                           if k in ("updated_age_sec", "activity_age_sec", "current_item_age_sec",
                                    "stalled", "stalled_reason", "last_event")})
                break
        if getattr(args, "json", False):
            print(json.dumps(st, ensure_ascii=False, indent=2))
        else:
            print(summary_line(st))
            for key in ("thread_id", "turn_id", "cwd", "sandbox", "model", "effort", "service_tier",
                        "started_at", "updated_at", "turns",
                        "updated_age_sec", "activity_age_sec", "current_item_age_sec",
                        "stalled", "stalled_reason",
                        "last_event", "needs_input_source", "needs_input_detail", "failure_detail"):
                print(f"  {key}: {st.get(key)}")
            if st.get("plan"):
                print("  plan:")
                for step in st["plan"]:
                    print(f"    {step}")
            if st.get("files_changed"):
                print("  files_changed:")
                for f in st["files_changed"]:
                    print(f"    {f}")
            if st.get("last_message_tail"):
                print(f"  last_message_tail: {truncate(st['last_message_tail'], 200)}")
        return 0
    statuses = load_statuses(home)
    diag, _ = worker_diagnostics(home)
    diag_by_name = {st.get("name"): st for st in diag}
    for st in statuses:
        st.update({k: v for k, v in diag_by_name.get(st.get("name"), {}).items()
                   if k in ("updated_age_sec", "activity_age_sec", "current_item_age_sec",
                            "stalled", "stalled_reason", "last_event")})
    if getattr(args, "json", False):
        print(json.dumps(statuses, ensure_ascii=False, indent=2))
    else:
        print_status_table(statuses)
    return 0


def cmd_result(args, home: Path) -> int:
    rp = home / "workers" / args.name / "result.md"
    if not rp.is_file():
        print(f"no result for worker '{args.name}'", file=sys.stderr)
        return 1
    print(rp.read_text(encoding="utf-8"), end="")
    return 0


def classify_wait_state(st: dict) -> int | None:
    """Map a status dict to a wait exit code. None means keep polling.
    needs_input exits 3 only when source=="question" (final QUESTION);
    tool/approval waits are treated as active until stream-end cleanup."""
    state = st.get("state")
    if state in TERMINAL_STATES:
        return 0 if state == "completed" else 2
    if state == "needs_input" and st.get("needs_input_source") == "question":
        return 3
    return None


def wait_for_worker(home: Path, name: str, timeout: float | None,
                    stall_timeout: float | None = None) -> int:
    sj = home / "workers" / name / "status.json"
    deadline = time.monotonic() + timeout if timeout else None
    dead_strikes = 0  # avoid false positives from transient ping failures while the daemon is busy
    while True:
        st = None
        if sj.is_file():
            try:
                st = json.loads(sj.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                st = None
        if st is not None:
            code = classify_wait_state(st)
            if code is not None:
                print(summary_line(st))
                return code
            if stall_timeout is not None:
                active_age = activity_age_seconds(st)
                if (st.get("state") in ("starting", "running")
                        and active_age is not None and active_age >= stall_timeout):
                    print(f"{name:<14} stall checkpoint after {active_age}s "
                          f"(state={st.get('state')}, threshold={stall_timeout}s)")
                    return 1
        # Daemon death check: ping success means definitely alive. pid alone is insufficient due to pid reuse.
        if probe_daemon_socket(home / "meight.sock"):
            dead_strikes = 0
        else:
            dead_strikes += 1
            pid = read_daemon_pid(home)
            pid_dead = pid is None or not pid_alive(pid)
            if pid_dead or dead_strikes >= 2:
                print(f"{name:<14} daemon-dead (pid={pid})")
                return 4
        if deadline is not None and time.monotonic() > deadline:
            print(f"{name:<14} timeout after {timeout}s "
                  f"(state={st.get('state') if st else 'unknown'})")
            return 1
        time.sleep(1)


def cmd_wait(args, home: Path) -> int:
    return wait_for_worker(home, args.name, args.timeout, args.stall_timeout)

def cmd_doctor(args, home: Path) -> int:
    report = doctor_report(home)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_doctor_report(report)
    return 0

def cmd_recover(args, home: Path) -> int:
    report = doctor_report(home)
    live = report["socket_live"] or report["lock_state"] == "held"
    if live:
        print("refused: live daemon/socket/lock detected; run shutdown first", file=sys.stderr)
        return 1
    targets = []
    for p in (home / "meight.sock", home / "daemon.pid", home / "daemon.heartbeat.json",
              home / "daemon.lock"):
        if p.exists():
            targets.append(p)
    if not targets:
        print("recover: no stale daemon artifacts found")
        return 0
    if args.dry_run or not args.force:
        print("recover dry-run: would snapshot and remove:")
        for p in targets:
            print(f"  {p}")
        print("rerun with --force to mutate")
        return 0
    backup = snapshot_recovery_files(home)
    for p in targets:
        try:
            p.unlink()
            print(f"removed: {p}")
        except FileNotFoundError:
            pass
    print(f"backup: {backup}")
    return 0


def ensure_daemon(home: Path) -> bool:
    """Auto-start the daemon detached after ping failure and poll until it responds."""
    if probe_daemon_socket(home / "meight.sock"):
        return True
    home.mkdir(parents=True, exist_ok=True)
    with open(home / "daemon.log", "a", encoding="utf-8") as log_f:
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "daemon"],
            stdout=log_f, stderr=log_f, stdin=subprocess.DEVNULL,
            start_new_session=True,
            env={**os.environ, "MEIGHT_HOME": str(home)},
        )
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        if probe_daemon_socket(home / "meight.sock"):
            return True
        time.sleep(0.25)
    return False


def cmd_dispatch(args, home: Path) -> int:
    """One-shot: auto-start daemon -> start -> wait -> print full result.md. Exit matches wait."""
    if not ensure_daemon(home):
        print("error: daemon auto-start failed — check daemon.log", file=sys.stderr)
        return 4
    resp = start_request(args, home)
    if not resp.get("ok"):
        print(f"error: {resp.get('error', 'unknown')}", file=sys.stderr)
        return 1
    print(f"started worker '{args.name}' thread={resp.get('thread_id')}", flush=True)
    code = wait_for_worker(home, args.name, args.timeout, args.stall_timeout)
    rp = home / "workers" / args.name / "result.md"
    if code in (0, 2, 3) and rp.is_file():
        print("--- result ---")
        print(rp.read_text(encoding="utf-8"), end="", flush=True)
    return code


def cmd_reply(args, home: Path) -> int:
    """One-shot reply: follow -> wait -> print only the latest turn result. For QUESTION (exit 3)."""
    resp = expect_ok(send_request(home, {
        "cmd": "follow", "name": args.name, "brief": read_brief(args),
        "no_preamble": args.no_preamble,
    }))
    print(f"reply turn #{resp.get('turns')} on worker '{args.name}'", flush=True)
    code = wait_for_worker(home, args.name, args.timeout, args.stall_timeout)
    rp = home / "workers" / args.name / "result.md"
    if code in (0, 2, 3) and rp.is_file():
        text = rp.read_text(encoding="utf-8")
        marker = "\n---\n## Turn "
        if marker in text:
            text = "## Turn " + text.rsplit(marker, 1)[1]
        print("--- result ---")
        print(text, end="", flush=True)
    return code


def cmd_shutdown(args, home: Path) -> int:
    resp = send_request(home, {"cmd": "shutdown", "force": args.force})
    if not resp.get("ok"):
        print(f"refused: {resp.get('error')}", file=sys.stderr)
        return 1
    interrupted = resp.get("interrupted") or []
    print("shutdown ok" + (f" (interrupted: {', '.join(interrupted)})" if interrupted else ""))
    return 0


def cmd_ping(args, home: Path) -> int:
    resp = expect_ok(send_request(home, {"cmd": "ping"}, timeout=10))
    print(f"pong (daemon pid {resp.get('pid')})")
    return 0


# ── argparse ───────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="meight", description="codex2codex: parallel Codex worker harness")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("daemon", help="foreground daemon").set_defaults(fn=cmd_daemon)
    sub.add_parser("ping", help="daemon health check").set_defaults(fn=cmd_ping)
    sp = sub.add_parser("doctor", help="passive health report; no state mutation")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_doctor)

    sp = sub.add_parser("recover", help="dry-run-first cleanup for stale daemon artifacts")
    sp.add_argument("--dry-run", action="store_true",
                    help="show stale artifacts only (default)")
    sp.add_argument("--force", action="store_true", help="snapshot then remove stale artifacts")
    sp.set_defaults(fn=cmd_recover)

    def add_start_options(sp):
        sp.add_argument("--brief-file", help="read from stdin when '-'")
        sp.add_argument("--brief")
        sp.add_argument("--cwd")
        sp.add_argument("--sandbox", default="ws", choices=sorted(SANDBOX_MAP.keys()))
        sp.add_argument("--model")
        sp.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh"])
        sp.add_argument("--fast", action=argparse.BooleanOptionalAction, default=None,
                        help="use the priority service tier (codex 'Fast'); --no-fast forces a non-priority tier for a cheaper run; omit to inherit ~/.codex/config.toml")
        sp.add_argument("--no-preamble", action="store_true", help="disable prepending the harness protocol preamble")

    sp = sub.add_parser("start", help="start a new worker")
    sp.add_argument("name")
    add_start_options(sp)
    sp.set_defaults(fn=cmd_start)

    sp = sub.add_parser("dispatch", help="one-shot: auto-start daemon + start + wait + print result")
    sp.add_argument("name")
    add_start_options(sp)
    sp.add_argument("--timeout", type=float, default=1800)
    sp.add_argument("--stall-timeout", type=float, default=None,
                    help="checkpoint if a running worker has no status update for SEC; does not interrupt")
    sp.set_defaults(fn=cmd_dispatch)

    sp = sub.add_parser("follow", help="new turn on the same thread for a terminal/QUESTION worker")
    sp.add_argument("name")
    sp.add_argument("--brief-file", help="read from stdin when '-'")
    sp.add_argument("--brief")
    sp.add_argument("--no-preamble", action="store_true")
    sp.set_defaults(fn=cmd_follow)

    sp = sub.add_parser("reply", help="one-shot reply: follow + wait + print latest turn result (for QUESTION)")
    sp.add_argument("name")
    sp.add_argument("--brief-file", help="read from stdin when '-'")
    sp.add_argument("--brief")
    sp.add_argument("--no-preamble", action="store_true")
    sp.add_argument("--timeout", type=float, default=1800)
    sp.add_argument("--stall-timeout", type=float, default=None,
                    help="checkpoint if a running worker has no status update for SEC; does not interrupt")
    sp.set_defaults(fn=cmd_reply)

    sp = sub.add_parser("steer", help="inject mid-turn text into a running turn")
    sp.add_argument("name")
    sp.add_argument("text")
    sp.set_defaults(fn=cmd_steer)

    sp = sub.add_parser("interrupt", help="interrupt a turn")
    sp.add_argument("name")
    sp.set_defaults(fn=cmd_interrupt)

    sp = sub.add_parser("status", help="worker status (daemon not required)")
    sp.add_argument("name", nargs="?")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_status)

    sp = sub.add_parser("list", help="status alias")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(fn=cmd_status, name=None)

    sp = sub.add_parser("result", help="print result.md")
    sp.add_argument("name")
    sp.set_defaults(fn=cmd_result)

    sp = sub.add_parser("wait", help="poll until terminal state")
    sp.add_argument("name")
    sp.add_argument("--timeout", type=float, default=None)
    sp.add_argument("--stall-timeout", type=float, default=None,
                    help="checkpoint if a running worker has no status update for SEC; does not interrupt")
    sp.set_defaults(fn=cmd_wait)

    sp = sub.add_parser("shutdown", help="shut down daemon")
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(fn=cmd_shutdown)

    return p


def main() -> int:
    args = build_parser().parse_args()
    home = state_home()
    return args.fn(args, home)


if __name__ == "__main__":
    sys.exit(main())
