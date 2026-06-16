#!/usr/bin/env bash
set -euo pipefail

source_path="${OPENHANDS_MCP_SOURCE:-/data/lcq/.codex/tools/OpenHandsMCP}"
python_bin="$source_path/.venv/bin/python"
git_bin="$(command -v git || true)"

if [[ ! -x "$python_bin" ]]; then
  echo "error: venv python not found: $python_bin" >&2
  exit 1
fi

if [[ -z "$git_bin" ]]; then
  echo "error: git executable not found on PATH" >&2
  exit 1
fi

export PATH="$source_path/.venv/bin:$PATH"
export GIT_PYTHON_GIT_EXECUTABLE="$git_bin"

cd "$source_path"
exec "$python_bin" -c 'from openhands_mcp_server.server import mcp; mcp.run(transport="stdio")'
