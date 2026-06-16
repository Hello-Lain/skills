#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: smoke-openhands-mcp-runtime.sh --source ~/path/to/OpenHandsMCP [--allow-server-smoke]

Verifies an OpenHandsMCP checkout and its uv-managed .venv.
Default mode does not start OpenHandsMCP, Docker, Podman, or MCP tasks.

With --allow-server-smoke, starts the MCP server over HTTP, calls only
initialize/list_tools, verifies expected tool names, then exits.
EOF
}

source_path=""
allow_server_smoke=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) source_path="${2:-}"; shift 2 ;;
    --allow-server-smoke) allow_server_smoke=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$source_path" ]]; then
  echo "error: --source is required" >&2
  usage >&2
  exit 2
fi

source_path="$(cd "$source_path" && pwd)"
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python_bin="$source_path/.venv/bin/python"
server_bin="$source_path/.venv/bin/openhands-mcp-server"
git_bin="$(command -v git || true)"

if [[ ! -x "$python_bin" ]]; then
  echo "error: venv python not found: $python_bin" >&2
  exit 1
fi

"$script_dir/check-openhands-mcp-tools.sh" --source "$source_path"

if command -v uv >/dev/null 2>&1; then
  uv pip check --python "$python_bin"
else
  echo "warn: uv not found; skipping uv pip check"
fi

"$python_bin" - <<'PY'
import importlib.metadata as md
import openhands_mcp_server.server as server

print("package:", md.version("openhands-mcp-server"))
print("server_module:", server.__file__)
print("has_main:", hasattr(server, "main"))
print("has_mcp:", hasattr(server, "mcp"))
print("mcp_type:", type(getattr(server, "mcp", None)).__name__)
PY

if (( allow_server_smoke == 0 )); then
  printf 'server_smoke_started: no\n'
  printf 'backend_started: no\n'
  exit 0
fi

if [[ ! -x "$server_bin" ]]; then
  echo "error: server entrypoint not found: $server_bin" >&2
  exit 1
fi

if [[ -z "$git_bin" ]]; then
  echo "error: git executable not found on PATH" >&2
  exit 1
fi

"$python_bin" - "$server_bin" "$source_path" "$git_bin" <<'PY'
import anyio
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

server_bin = Path(sys.argv[1])
source_path = Path(sys.argv[2])
git_bin = Path(sys.argv[3])
expected = {
    "start_session",
    "code",
    "git",
    "teardown",
    "coding_task_status",
    "cleanup_coding_tasks",
}

def pick_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])

def wait_for_port(port: int, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    last_error: OSError | None = None
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError as exc:
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f"MCP HTTP server did not open port {port}: {last_error}")

async def main() -> None:
    port = pick_port()
    env = {
        **os.environ,
        "PATH": f"{server_bin.parent}{os.pathsep}{os.environ.get('PATH', '')}",
        "GIT_PYTHON_GIT_EXECUTABLE": str(git_bin),
        "MCP_HTTP_HOST": "127.0.0.1",
        "MCP_HTTP_PORT": str(port),
    }
    proc = subprocess.Popen(
        [str(server_bin)],
        cwd=str(source_path),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_port(port)
        async with streamable_http_client(f"http://127.0.0.1:{port}/mcp") as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                with anyio.fail_after(10):
                    await session.initialize()
                    result = await session.list_tools()
                names = {tool.name for tool in result.tools}
                print("server_smoke_started: yes")
                print(f"server_url: http://127.0.0.1:{port}/mcp")
                print("tools:")
                for name in sorted(names):
                    print(f"  - {name}")
                missing = sorted(expected - names)
                extra = sorted(names - expected)
                print(f"missing_expected: {missing}")
                print(f"extra_observed: {extra}")
                if missing or extra:
                    raise SystemExit(1)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

anyio.run(main)
PY
printf 'backend_started: mcp-server-only\n'
