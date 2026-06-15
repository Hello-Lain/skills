#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: preflight.sh [--source ~/path/to/OpenHandsMCP]

Non-destructive local preflight for OpenHandsMCP readiness.
Checks commands, sockets, env shape, disk space, and secret presence.
Does not install packages, pull images, start Docker, or run OpenHandsMCP.
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

status=0
check_cmd() {
  local name="$1"
  if command -v "$name" >/dev/null 2>&1; then
    printf 'ok: command %s found\n' "$name"
  else
    printf 'warn: command %s not found\n' "$name"
    status=1
  fi
}

check_cmd python3
check_cmd git

if command -v docker >/dev/null 2>&1; then
  printf 'info: docker command found; socket access is high-risk and needs approval before use\n'
else
  printf 'warn: docker command not found\n'
  status=1
fi

if command -v podman >/dev/null 2>&1; then
  printf 'info: podman command found\n'
fi

for sock in /var/run/docker.sock /var/run/podman.sock "${XDG_RUNTIME_DIR:-}/podman/podman.sock"; do
  [[ -n "$sock" ]] || continue
  if [[ -S "$sock" ]]; then
    printf 'info: container socket exists: %s\n' "$sock"
    if [[ -w "$sock" ]]; then
      printf 'warn: socket writable by current user: %s (high risk)\n' "$sock"
    fi
  fi
done

printf 'info: disk free for cwd:\n'
df -h . | sed 's/^/  /'

if env | grep -q '^OPENHANDS_SECRET_'; then
  printf 'warn: OPENHANDS_SECRET_* variables are present; do not forward without explicit per-key approval\n'
else
  printf 'ok: no OPENHANDS_SECRET_* variables detected\n'
fi

if [[ -n "$source_path" ]]; then
  if [[ -f "$source_path/src/openhands_mcp_server/server.py" ]]; then
    printf 'ok: OpenHandsMCP source detected at %s\n' "$source_path"
  else
    printf 'warn: OpenHandsMCP server.py not found under %s\n' "$source_path"
    status=1
  fi
fi

printf 'backend_started: no\n'
exit "$status"
