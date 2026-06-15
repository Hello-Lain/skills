#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: check-openhands-mcp-tools.sh --source ~/path/to/OpenHandsMCP

Verifies the registered FastMCP tool names from a local OpenHandsMCP checkout.
No network access. No MCP server startup. No Docker/OpenHands execution.
EOF
}

source_path=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) source_path="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$source_path" ]]; then
  echo "error: --source is required" >&2
  usage >&2
  exit 2
fi

server_py="$source_path/src/openhands_mcp_server/server.py"
if [[ ! -f "$server_py" ]]; then
  echo "error: not found: $server_py" >&2
  exit 1
fi

python3 - "$server_py" <<'PY'
import ast
import sys
from pathlib import Path

server_py = Path(sys.argv[1])
tree = ast.parse(server_py.read_text(encoding="utf-8"))
tools = []
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for deco in node.decorator_list:
            if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Attribute):
                if deco.func.attr == "tool":
                    tool_name = node.name
                    for kw in deco.keywords:
                        if kw.arg == "name" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                            tool_name = kw.value.value
                    tools.append(tool_name)

expected = {
    "start_session",
    "code",
    "git",
    "teardown",
    "coding_task_status",
    "cleanup_coding_tasks",
}
print("tools:")
for tool in tools:
    print(f"  - {tool}")
missing = sorted(expected - set(tools))
extra = sorted(set(tools) - expected)
print(f"missing_expected: {missing}")
print(f"extra_observed: {extra}")
print("list_sessions_present:", "list_sessions" in tools)
sys.exit(0 if not missing and not extra else 1)
PY
printf 'backend_started: no\n'
