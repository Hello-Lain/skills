#!/usr/bin/env python3
"""Stream the original demo.rag.ac.cn chat response in real time."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any, Iterable


DEFAULT_BASE_URL = "https://demo.rag.ac.cn"
DEFAULT_TIMEOUT = 300
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class DemoChatError(RuntimeError):
    pass


def parse_sse_events(chunks: Iterable[bytes]) -> Iterable[dict[str, Any]]:
    buffer = ""
    for chunk in chunks:
        if not chunk:
            continue
        buffer += chunk.decode("utf-8", errors="replace").replace("\r\n", "\n")
        while "\n\n" in buffer:
            raw, buffer = buffer.split("\n\n", 1)
            yield from parse_sse_block(raw)
    if buffer.strip():
        yield from parse_sse_block(buffer)


def parse_sse_block(raw: str) -> Iterable[dict[str, Any]]:
    data_lines = []
    for line in raw.splitlines():
        if line.startswith("data: "):
            data_lines.append(line[6:])
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    if not data_lines:
        return
    payload = "\n".join(data_lines).strip()
    if not payload or payload == "[DONE]":
        return
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as exc:
        yield {"type": "parse_error", "message": str(exc), "raw": payload}
        return
    if isinstance(parsed, dict):
        yield parsed
    else:
        yield {"type": "data", "value": parsed}

def load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def read_history(path: str | None) -> list[dict[str, str]]:
    if not path:
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise DemoChatError("--history-json must contain a JSON list.")
    return data


def stream_chat(args: argparse.Namespace, token: str) -> dict[str, Any]:
    base_url = os.environ.get("RAG_DEMO_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
    url = f"{base_url.rstrip('/')}/api/chat/stream"
    body = json.dumps(
        {"query": args.query, "history": read_history(args.history_json), "effort": args.effort},
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )
    final_answer = ""
    answer_parts: list[str] = []
    steps: list[dict[str, Any]] = []
    events_count = 0
    event_file = open(args.jsonl_events, "w", encoding="utf-8") if args.jsonl_events else None
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            for event in parse_sse_events(response):
                events_count += 1
                if event_file:
                    event_file.write(json.dumps(event, ensure_ascii=False) + "\n")
                    event_file.flush()
                event_type = event.get("type")
                if event_type == "thinking":
                    print(f"\n[thinking round {event.get('round', '?')}]", file=sys.stderr, flush=True)
                elif event_type == "thinking_content" and args.show_thinking:
                    print(str(event.get("content", "")), end="", file=sys.stderr, flush=True)
                elif event_type == "sql_start":
                    steps.append(event)
                    print(f"\n[search] {event.get('task') or event.get('sql')}", file=sys.stderr, flush=True)
                elif event_type == "sql_retry":
                    steps.append(event)
                    print(f"\n[retry] {event.get('task')}: {event.get('error')}", file=sys.stderr, flush=True)
                elif event_type == "sql_done":
                    steps.append(event)
                    status = "error" if event.get("error") else "done"
                    rows = event.get("row_count")
                    suffix = f", rows={rows}" if rows is not None else ""
                    print(f"\n[{status}] {event.get('task') or event.get('sql')}{suffix}", file=sys.stderr, flush=True)
                elif event_type == "answer_start":
                    print("", flush=True)
                elif event_type == "token":
                    content = str(event.get("content", ""))
                    answer_parts.append(content)
                    print(content, end="", flush=True)
                elif event_type == "done":
                    answer = event.get("answer")
                    if isinstance(answer, str) and answer:
                        final_answer = answer
                elif event_type == "error":
                    print(f"\n[error] {event.get('message')}", file=sys.stderr, flush=True)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        if exc.code in {401, 403}:
            raise DemoChatError("Demo token invalid/expired. Need demo.rag.ac.cn browser localStorage.auth_token.") from exc
        if exc.code == 502:
            raise DemoChatError(
                "Demo stream returned 502 upstream error. Use a fresh demo.rag.ac.cn browser "
                "localStorage.auth_token, or retry if the demo backend is temporarily unavailable."
            ) from exc
        raise DemoChatError(f"HTTP {exc.code}: {detail or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise DemoChatError(f"Request failed: {exc.reason}") from exc
    finally:
        if event_file:
            event_file.close()
    if not final_answer:
        final_answer = "".join(answer_parts)
    print("", flush=True)
    result = {
        "query": args.query,
        "effort": args.effort,
        "answer": final_answer,
        "steps": steps,
        "events_count": events_count,
    }
    if args.transcript:
        with open(args.transcript, "w", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stream the original DeepXiv demo chat.")
    parser.add_argument("query", help="Chat query, e.g. 请帮我找到和resnet相关的24-26年的论文")
    parser.add_argument("--effort", choices=["quick", "balanced", "thorough"], default="thorough")
    parser.add_argument("--history-json", help="Optional JSON file: [{'role':'user|assistant','content':'...'}].")
    parser.add_argument("--jsonl-events", help="Write raw SSE events as JSONL.")
    parser.add_argument("--transcript", help="Write final answer/steps JSON transcript.")
    parser.add_argument("--clean-md", help="Legacy helper: after quality gate passes, write candidate Markdown to this path.")
    parser.add_argument("--candidates-json", help="Write extracted candidate papers JSON for agent verification.")
    parser.add_argument("--allow-unclean", action="store_true", help="Allow --clean-md even when assess_response.py fails.")
    parser.add_argument("--show-thinking", action="store_true", help="Also stream thinking_content to stderr.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    return parser.parse_args(argv)


def get_token() -> str:
    return (
        os.environ.get("RAG_DEMO_TOKEN")
        or os.environ.get("RAG_AC_CN_DEMO_TOKEN")
        or ""
    ).strip()


def main(argv: list[str] | None = None) -> int:
    load_dotenv(os.path.join(SKILL_DIR, ".env"))
    args = parse_args(argv or sys.argv[1:])
    token = get_token()
    if not token:
        print(
            "Missing demo token. Log in at https://demo.rag.ac.cn/login, then export "
            "localStorage.auth_token as RAG_DEMO_TOKEN.",
            file=sys.stderr,
        )
        return 2
    try:
        result = stream_chat(args, token)
    except DemoChatError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.clean_md:
        transcript = args.transcript
        if not transcript:
            transcript = os.path.join(os.getcwd(), "transcript.json")
            with open(transcript, "w", encoding="utf-8") as handle:
                json.dump(result, handle, ensure_ascii=False, indent=2)
        root, _ = os.path.splitext(args.clean_md)
        assessor = os.path.join(SKILL_DIR, "scripts", "assess_response.py")
        quality_report = f"{root}.quality.json"
        quality = subprocess.run(
            [sys.executable, assessor, "--transcript", transcript, "--output", quality_report],
            check=False,
        )
        if quality.returncode != 0 and not args.allow_unclean:
            print(
                f"Raw answer failed quality gate; see {quality_report}. "
                "Retry with the report's retry_prompt, or pass --allow-unclean for debugging only.",
                file=sys.stderr,
            )
            return quality.returncode
        cleaner = os.path.join(SKILL_DIR, "scripts", "clean_literature.py")
        cmd = [sys.executable, cleaner, "--transcript", transcript, "--output", args.clean_md]
        if args.jsonl_events:
            cmd.extend(["--events", args.jsonl_events])
        candidates_json = args.candidates_json
        if not candidates_json:
            candidates_json = f"{root}.candidates.json"
        cmd.extend(["--candidates-json", candidates_json])
        subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
