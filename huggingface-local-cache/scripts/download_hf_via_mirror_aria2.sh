#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_ARIA2_BIN="$SKILL_DIR/tools/aria2/usr/bin/aria2c"
HF_CACHE_ROOT="${HF_CACHE_ROOT:-$SKILL_DIR/../../../.cache/huggingface}"
HF_CACHE_DIR="${HF_CACHE_DIR:-$HF_CACHE_ROOT/hub}"
REPO_ID=""
REPO_TYPE="model"
REVISION="main"
OUTPUT_DIR="$HF_CACHE_DIR"
ARIA2_BIN="${ARIA2_BIN:-}"
MAX_CONNECTIONS=16
SPLIT=16
MIN_SPLIT_SIZE="1M"
USE_HF_FALLBACK=1
FILES=()

usage() {
  cat <<'EOF'
Usage:
  download_hf_via_mirror_aria2.sh --repo-id REPO_ID [options] FILE [FILE ...]

Options:
  --repo-id REPO_ID       Hugging Face repo id
  --repo-type TYPE        model | dataset | space. Default: model
  --revision REV          Branch, tag, or commit. Default: main
  --output-dir DIR        Target dir for materialized files. Default: ${HF_CACHE_ROOT:-../../../.cache/huggingface}/hub
  --aria2-bin PATH        aria2c executable path
  --max-connections N     aria2 max connections per server. Default: 16
  --split N               aria2 split count. Default: 16
  --min-split-size SIZE   aria2 min split size. Default: 1M
  --no-hf-fallback        Fail instead of falling back to hf download
  -h, --help              Show help
EOF
}

log() {
  printf '[hf-mirror-aria2] %s\n' "$*"
}

run_no_proxy() {
  env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
    -u http_proxy -u https_proxy -u all_proxy \
    -u NO_PROXY -u no_proxy \
    GIT_CONFIG_GLOBAL=/dev/null \
    HF_HOME="$HF_CACHE_ROOT" \
    HF_HUB_CACHE="$HF_CACHE_DIR" \
    HUGGINGFACE_HUB_CACHE="$HF_CACHE_DIR" \
    HF_DATASETS_CACHE="$HF_CACHE_DIR" \
    HF_DATASETS_DOWNLOADED_DATASETS_PATH="$HF_CACHE_DIR" \
    DATASETS_ROOT="$HF_CACHE_DIR" \
    "$@"
}

mirror_prefix() {
  case "$REPO_TYPE" in
    model) printf '' ;;
    dataset) printf 'datasets/' ;;
    space) printf 'spaces/' ;;
    *)
      printf 'unsupported repo type: %s\n' "$REPO_TYPE" >&2
      return 1
      ;;
  esac
}

resolve_signed_url() {
  local file="$1"
  local prefix mirror_url location
  prefix="$(mirror_prefix)"
  mirror_url="https://hf-mirror.com/${prefix}${REPO_ID}/resolve/${REVISION}/${file}"
  location="$(run_no_proxy curl -m 20 -sSI "$mirror_url" | awk 'BEGIN{IGNORECASE=1} /^location: /{sub(/^location: /,""); sub(/\r$/,""); print}' | tail -n1)"
  if [[ -n "$location" ]]; then
    if [[ "$location" == /* ]]; then
      printf 'https://hf-mirror.com%s\n' "$location"
      return 0
    fi
    printf '%s\n' "$location"
  else
    printf '%s\n' "$mirror_url"
  fi
}

remote_size() {
  local url="$1"
  run_no_proxy curl -m 20 -sSI "$url" | awk 'BEGIN{IGNORECASE=1} /^content-length: /{sub(/^content-length: /,""); sub(/\r$/,""); print}' | tail -n1
}

local_target_path() {
  local file="$1"
  printf '%s/%s\n' "$OUTPUT_DIR" "$file"
}

download_with_aria2() {
  local file="$1"
  local signed_url="$2"
  local target_dir target_name
  target_dir="$(dirname "$(local_target_path "$file")")"
  target_name="$(basename "$file")"
  mkdir -p "$target_dir"
  log "aria2: $file"
  run_no_proxy "$ARIA2_BIN" \
    --continue=true \
    --max-connection-per-server="$MAX_CONNECTIONS" \
    --split="$SPLIT" \
    --min-split-size="$MIN_SPLIT_SIZE" \
    --file-allocation=none \
    --auto-file-renaming=false \
    --dir "$target_dir" \
    --out "$target_name" \
    "$signed_url"
}

download_with_hf() {
  local file="$1"
  log "hf fallback: $file"
  run_no_proxy env HF_ENDPOINT="https://hf-mirror.com" \
    hf download \
      --repo-type "$REPO_TYPE" \
      --revision "$REVISION" \
      --cache-dir "$HF_CACHE_DIR" \
      --local-dir "$OUTPUT_DIR" \
      --max-workers 4 \
      "$REPO_ID" \
      "$file"
}

ensure_downloaded() {
  local file="$1"
  local target signed_url size local_size
  target="$(local_target_path "$file")"
  signed_url="$(resolve_signed_url "$file")"
  size="$(remote_size "$signed_url" || true)"

  if [[ -f "$target" && -n "$size" ]]; then
    local_size="$(stat -c '%s' "$target")"
    if [[ "$local_size" == "$size" ]]; then
      log "skip complete file: $file"
      return 0
    fi
  fi

  if [[ -z "$ARIA2_BIN" ]]; then
    if [[ "$USE_HF_FALLBACK" -eq 1 ]]; then
      download_with_hf "$file"
      return 0
    fi
    printf 'aria2c is unavailable and hf fallback is disabled\n' >&2
    return 1
  fi

  if download_with_aria2 "$file" "$signed_url"; then
    return 0
  fi

  if [[ "$USE_HF_FALLBACK" -eq 1 ]]; then
    download_with_hf "$file"
    return 0
  fi

  return 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-id) REPO_ID="${2:-}"; shift 2 ;;
    --repo-type) REPO_TYPE="${2:-}"; shift 2 ;;
    --revision) REVISION="${2:-}"; shift 2 ;;
    --output-dir) OUTPUT_DIR="${2:-}"; shift 2 ;;
    --aria2-bin) ARIA2_BIN="${2:-}"; shift 2 ;;
    --max-connections) MAX_CONNECTIONS="${2:-}"; shift 2 ;;
    --split) SPLIT="${2:-}"; shift 2 ;;
    --min-split-size) MIN_SPLIT_SIZE="${2:-}"; shift 2 ;;
    --no-hf-fallback) USE_HF_FALLBACK=0; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) printf 'unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
    *) FILES+=("$1"); shift ;;
  esac
done

while [[ $# -gt 0 ]]; do
  FILES+=("$1")
  shift
done

if [[ -z "$REPO_ID" || "${#FILES[@]}" -eq 0 ]]; then
  usage >&2
  exit 2
fi

if [[ -z "$ARIA2_BIN" && -x "$DEFAULT_ARIA2_BIN" ]]; then
  ARIA2_BIN="$DEFAULT_ARIA2_BIN"
elif [[ -z "$ARIA2_BIN" ]] && command -v aria2c >/dev/null 2>&1; then
  ARIA2_BIN="$(command -v aria2c)"
fi

mkdir -p "$OUTPUT_DIR" "$HF_CACHE_DIR"

for file in "${FILES[@]}"; do
  ensure_downloaded "$file"
done
