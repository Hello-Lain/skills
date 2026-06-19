#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ensure-codegraph-index.sh [repo]

Ensures CodeGraph can serve a repo by running status, then sync or init.
Defaults to git root, else current directory.

Environment:
  CODEGRAPH_BIN="codegraph"   Override command. Supports shell words, e.g. "npx --yes @colbymchenry/codegraph".
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

repo="${1:-}"
if [[ -z "$repo" ]]; then
  repo="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

if [[ ! -d "$repo" ]]; then
  echo "not a directory: $repo" >&2
  exit 2
fi

if [[ -n "${CODEGRAPH_BIN:-}" ]]; then
  # shellcheck disable=SC2206
  cg=($CODEGRAPH_BIN)
elif command -v codegraph >/dev/null 2>&1; then
  cg=(codegraph)
elif command -v npx >/dev/null 2>&1; then
  cg=(npx --yes @colbymchenry/codegraph)
else
  echo "codegraph unavailable: install @colbymchenry/codegraph or provide CODEGRAPH_BIN" >&2
  exit 127
fi

echo "repo: $repo"
echo "codegraph: ${cg[*]}"

status_file="$(mktemp)"
trap 'rm -f "$status_file"' EXIT

if "${cg[@]}" status --json "$repo" >"$status_file" 2>&1 && grep -q '"initialized":true' "$status_file"; then
  cat "$status_file"
  "${cg[@]}" sync "$repo" || "${cg[@]}" index "$repo"
else
  cat "$status_file" >&2 || true
  "${cg[@]}" init "$repo"
fi

"${cg[@]}" status "$repo"
