#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: cleanup-openhands.sh [--sessions-dir DIR] [--archive-dir DIR] [--show-commands]

Dry-run cleanup reporter for OpenHandsMCP artifacts.
Default behavior reports candidate sessions, archives, and containers only.
It never stops/removes containers or deletes files.
EOF
}

sessions_dir="./sessions"
archive_dir="./archive"
show_commands=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --sessions-dir) sessions_dir="${2:-}"; shift 2 ;;
    --archive-dir) archive_dir="${2:-}"; shift 2 ;;
    --show-commands) show_commands=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

printf 'backend_cleanup_executed: no\n'
printf 'sessions_dir: %s\n' "$sessions_dir"
list_candidates() {
  local prefix="$1"
  local dir="$2"
  local found=0
  if [[ ! -d "$dir" ]]; then
    printf 'info: %s dir not found\n' "${prefix%_candidate}"
    return
  fi
  shopt -s nullglob
  local -a items=()
  local item
  for item in "$dir"/*; do
    [[ -d "$item" ]] && items+=("$item")
  done
  shopt -u nullglob
  if (( ${#items[@]} == 0 )); then
    printf 'info: no %s candidates\n' "${prefix%_candidate}"
    return
  fi
  printf '%s\n' "${items[@]}" | sort | sed "s#^#${prefix}: #"
}

list_candidates session_candidate "$sessions_dir"

printf 'archive_dir: %s\n' "$archive_dir"
list_candidates archive_candidate "$archive_dir"

if command -v docker >/dev/null 2>&1; then
  printf 'docker_container_candidates:\n'
  docker ps -a --format '{{.ID}} {{.Names}} {{.Status}}' 2>/dev/null \
    | grep -E 'openhands|all-hands' \
    | sed 's/^/  /' || true
else
  printf 'info: docker command not found\n'
fi

if (( show_commands )); then
  cat <<'EOF'
suggested_sequence_after_explicit_approval:
  1. Use OpenHandsMCP cleanup_coding_tasks(session_id).
  2. Use OpenHandsMCP teardown(session_id, archive_changes=true).
  3. Re-run this script and verify no candidates remain.
  4. Only then consider manual docker stop/rm for verified OpenHandsMCP containers.
EOF
fi
