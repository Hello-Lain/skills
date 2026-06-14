#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HF_CACHE_ROOT="${HF_CACHE_ROOT:-$SKILL_DIR/../../../.cache/huggingface}"
HF_CACHE_DIR="${HF_CACHE_DIR:-$HF_CACHE_ROOT/hub}"

export HF_HOME="$HF_CACHE_ROOT"
export HF_HUB_CACHE="$HF_CACHE_DIR"
export HUGGINGFACE_HUB_CACHE="$HF_CACHE_DIR"
export HF_DATASETS_CACHE="$HF_CACHE_DIR"
export HF_DATASETS_DOWNLOADED_DATASETS_PATH="$HF_CACHE_DIR"
export DATASETS_ROOT="$HF_CACHE_DIR"

mkdir -p "$HF_CACHE_DIR"

case "${1:-print}" in
  print)
    printf 'export HF_HOME=%q\n' "$HF_HOME"
    printf 'export HF_HUB_CACHE=%q\n' "$HF_HUB_CACHE"
    printf 'export HUGGINGFACE_HUB_CACHE=%q\n' "$HUGGINGFACE_HUB_CACHE"
    printf 'export HF_DATASETS_CACHE=%q\n' "$HF_DATASETS_CACHE"
    printf 'export HF_DATASETS_DOWNLOADED_DATASETS_PATH=%q\n' "$HF_DATASETS_DOWNLOADED_DATASETS_PATH"
    printf 'export DATASETS_ROOT=%q\n' "$DATASETS_ROOT"
    ;;
  env)
    env | sort | grep -E '^(HF_HOME|HF_HUB_CACHE|HUGGINGFACE_HUB_CACHE|HF_DATASETS_CACHE|HF_DATASETS_DOWNLOADED_DATASETS_PATH|DATASETS_ROOT)='
    ;;
  exec)
    shift
    exec "$@"
    ;;
  *)
    printf 'Usage: hf-env.sh [print|env|exec COMMAND ...]\n' >&2
    exit 2
    ;;
esac
