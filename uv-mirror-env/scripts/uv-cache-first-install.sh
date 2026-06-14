#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR="${UV_MIRROR:-https://pypi.tuna.tsinghua.edu.cn/simple}"

if [[ "$#" -eq 0 ]]; then
  cat >&2 <<'EOF'
Usage:
  uv-cache-first-install.sh [uv pip install options] PACKAGE...

Example:
  uv-cache-first-install.sh --python .venv/bin/python --torch-backend cu121 torch==2.4.0
EOF
  exit 2
fi

echo "[uv-cache-first] trying uv cache/offline first" >&2
set +e
"$SCRIPT_DIR/uv-no-proxy.sh" uv pip install --offline "$@"
status=$?
set -e

if [[ "$status" -eq 0 ]]; then
  echo "[uv-cache-first] installed from existing cache" >&2
  exit 0
fi

echo "[uv-cache-first] cache miss; using mirror: $MIRROR" >&2
UV_DEFAULT_INDEX="$MIRROR" "$SCRIPT_DIR/uv-no-proxy.sh" uv pip install "$@"
