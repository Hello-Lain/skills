#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: classify-task.sh --task TEXT [--files N] [--risk low|medium|high|critical]

Dry-run classifier for whether a task is a candidate for OpenHandsMCP delegation.
It never starts OpenHandsMCP, Docker, Podman, or MCP servers.
EOF
}

task=""
files="0"
risk="medium"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task) task="${2:-}"; shift 2 ;;
    --files) files="${2:-0}"; shift 2 ;;
    --risk) risk="${2:-medium}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$task" ]]; then
  echo "error: --task is required" >&2
  usage >&2
  exit 2
fi

lower="$(printf '%s' "$task" | tr '[:upper:]' '[:lower:]')"
score=0
reasons=()
decision="do-not-delegate"
approval="not-required"

if [[ "$lower" =~ (large|complex|refactor|migration|multi-file|architecture|plan|long-running|massive|broad) ]]; then
  score=$((score + 2))
  reasons+=("complexity keywords present")
fi

if [[ "$files" =~ ^[0-9]+$ ]] && (( files >= 5 )); then
  score=$((score + 2))
  reasons+=("file count >= 5")
fi

if [[ "$lower" =~ (secret|token|password|credential|prod|production|billing|payment|destructive|delete|drop) ]]; then
  score=$((score - 3))
  reasons+=("sensitive or destructive keywords present")
fi

case "$risk" in
  low) ;;
  medium) ;;
  high|critical) score=$((score - 2)); reasons+=("risk level requires stronger approval") ;;
  *) echo "error: invalid --risk: $risk" >&2; exit 2 ;;
esac

if (( score >= 3 )); then
  decision="candidate-requires-approval"
  approval="required-before-backend-use"
elif (( score >= 1 )); then
  decision="maybe-use-main-codex-first"
  approval="required-if-delegating"
fi

printf 'decision: %s\n' "$decision"
printf 'risk: %s\n' "$risk"
printf 'score: %s\n' "$score"
printf 'approval: %s\n' "$approval"
printf 'backend_started: no\n'
printf 'rationale:\n'
if ((${#reasons[@]} == 0)); then
  printf '  - no delegation threshold met\n'
else
  for reason in "${reasons[@]}"; do
    printf '  - %s\n' "$reason"
  done
fi
