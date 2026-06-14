#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HF_CACHE_ROOT="${HF_CACHE_ROOT:-$SKILL_DIR/../../../.cache/huggingface}"
HF_CACHE_DIR="${HF_CACHE_DIR:-$HF_CACHE_ROOT/hub}"
REPO_ID=""
REPO_TYPE="model"
REVISION="main"
LOCAL_DIR=""
SOURCE="auto"
PROXY_MODE="auto"
NETWORK_POLICY="${HF_DOWNLOAD_NETWORK_POLICY:-save-vpn}"
SELECTED_SOURCE=""
SELECTED_PROXY_MODE=""
CANDIDATES=()
MAX_WORKERS=4
BENCHMARK_TIMEOUT=15
ARIA2_THRESHOLD="${HF_DOWNLOAD_ARIA2_THRESHOLD:-104857600}"
ARIA2_SPLIT="${HF_DOWNLOAD_ARIA2_SPLIT:-16}"
FILES=()

usage() {
  cat <<'EOF'
Usage:
  hf-download.sh --repo-id REPO_ID [options] [FILE ...]

Options:
  --repo-id REPO_ID      Hugging Face repo id, e.g. Qwen/Qwen2.5-7B-Instruct
  --repo-type TYPE       model | dataset | space. Default: model
  --revision REV         Branch, tag, or commit. Default: main
  --local-dir DIR        Materialize files outside cache only when explicitly needed
  --source MODE          auto | official | mirror. Default: auto
  --proxy-mode MODE      auto | keep | none. Default: auto
  --network-policy MODE  fastest | save-vpn | no-vpn. Default: save-vpn
  --benchmark-timeout N  Seconds per candidate. Default: 15
  --mirror               Alias: --source mirror
  --official             Alias: --source official
  --keep-proxy           Alias: --proxy-mode keep
  --no-proxy             Alias: --proxy-mode none
  --max-workers N        hf download workers. Default: 4
  --aria2-threshold N    Use aria2 for files >= N bytes. Default: 104857600
  --aria2-split N        aria2 split/connections. Default: 16
  -h, --help             Show help

Defaults:
  cache-dir: ${HF_CACHE_ROOT:-../../../.cache/huggingface}/hub
  network-policy: save-vpn

Policies:
  fastest   Benchmark all reachable source/proxy paths; choose lowest latency.
  save-vpn  Try no-proxy first; use proxy only after direct download fails.
  no-vpn    Never use proxy; fail if no direct path works.
EOF
}

has_proxy_env() {
  env | grep -Eiq '^(HTTP_PROXY|HTTPS_PROXY|ALL_PROXY|http_proxy|https_proxy|all_proxy)='
}

repo_prefix() {
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

endpoint_base() {
  case "$1" in
    official) printf 'https://huggingface.co' ;;
    mirror) printf 'https://hf-mirror.com' ;;
    *)
      printf 'unsupported source: %s\n' "$1" >&2
      return 1
      ;;
  esac
}

benchmark_url() {
  local source="$1"
  local base prefix file
  base="$(endpoint_base "$source")"
  if [[ "${#FILES[@]}" -gt 0 ]]; then
    prefix="$(repo_prefix)"
    file="${FILES[0]}"
    printf '%s/%s%s/resolve/%s/%s\n' "$base" "$prefix" "$REPO_ID" "$REVISION" "$file"
    return
  fi

  case "$REPO_TYPE" in
    model) printf '%s/api/models/%s/revision/%s\n' "$base" "$REPO_ID" "$REVISION" ;;
    dataset) printf '%s/api/datasets/%s/revision/%s\n' "$base" "$REPO_ID" "$REVISION" ;;
    space) printf '%s/api/spaces/%s/revision/%s\n' "$base" "$REPO_ID" "$REVISION" ;;
  esac
}

api_url() {
  local source="$1"
  local base
  base="$(endpoint_base "$source")"
  case "$REPO_TYPE" in
    model) printf '%s/api/models/%s/revision/%s?blobs=true\n' "$base" "$REPO_ID" "$REVISION" ;;
    dataset) printf '%s/api/datasets/%s/revision/%s?blobs=true\n' "$base" "$REPO_ID" "$REVISION" ;;
    space) printf '%s/api/spaces/%s/revision/%s?blobs=true\n' "$base" "$REPO_ID" "$REVISION" ;;
  esac
}

largest_repo_file() {
  local source="$1"
  local proxy_mode="$2"
  local url
  url="$(api_url "$source")"
  curl_env "$proxy_mode" curl -L -sS \
    --connect-timeout 5 --max-time "$BENCHMARK_TIMEOUT" \
    "$url" 2>/dev/null | "${PYTHON_BIN:-python}" -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
siblings = data.get("siblings") or []
files = [
    (item.get("size") or 0, item.get("rfilename") or "")
    for item in siblings
    if item.get("rfilename")
]
if not files:
    sys.exit(1)
print(max(files)[1])
'
}

curl_env() {
  local proxy_mode="$1"
  shift
  if [[ "$proxy_mode" == "none" ]]; then
    env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
      -u http_proxy -u https_proxy -u all_proxy \
      -u NO_PROXY -u no_proxy \
      GIT_CONFIG_GLOBAL=/dev/null \
      "$@"
  else
    env GIT_CONFIG_GLOBAL=/dev/null "$@"
  fi
}

run_transport_env() {
  local proxy_mode="$1"
  shift
  if [[ "$proxy_mode" == "none" ]]; then
    env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
      -u http_proxy -u https_proxy -u all_proxy \
      -u NO_PROXY -u no_proxy \
      GIT_CONFIG_GLOBAL=/dev/null \
      "$@"
  else
    env GIT_CONFIG_GLOBAL=/dev/null "$@"
  fi
}

benchmark_candidate() {
  local source="$1"
  local proxy_mode="$2"
  local url out code time speed exit_code largest prefix base
  if [[ "${#FILES[@]}" -eq 0 ]] && largest="$(largest_repo_file "$source" "$proxy_mode")"; then
    base="$(endpoint_base "$source")"
    prefix="$(repo_prefix)"
    url="${base}/${prefix}${REPO_ID}/resolve/${REVISION}/${largest}"
    printf '[hf-download] benchmark file: source=%s proxy=%s file=%s\n' "$source" "$proxy_mode" "$largest" >&2
  else
    url="$(benchmark_url "$source")"
  fi

  set +e
  if [[ "${#FILES[@]}" -gt 0 || -n "${largest:-}" ]]; then
    out="$(curl_env "$proxy_mode" curl -L -r 0-1048575 -o /dev/null -sS \
      --connect-timeout 5 --max-time "$BENCHMARK_TIMEOUT" \
      -w '%{http_code} %{time_total} %{speed_download}' "$url" 2>/dev/null)"
  else
    out="$(curl_env "$proxy_mode" curl -L -o /dev/null -sS \
      --connect-timeout 5 --max-time "$BENCHMARK_TIMEOUT" \
      -w '%{http_code} %{time_total} %{speed_download}' "$url" 2>/dev/null)"
  fi
  exit_code=$?
  set -e

  [[ "$exit_code" -eq 0 ]] || return 1
  read -r code time speed <<<"$out"
  [[ "$code" =~ ^(200|206|302|307)$ ]] || return 1
  awk -v t="$time" 'BEGIN { exit !(t > 0) }' || return 1
  printf '%s %s %s %s\n' "$time" "$speed" "$source" "$proxy_mode"
}

select_transport() {
  local sources=()
  local source proxy_mode result direct_lines="" proxy_lines="" all_lines=""

  if [[ "$SOURCE" == "auto" ]]; then
    sources=(official mirror)
  else
    sources=("$SOURCE")
  fi

  if [[ "$NETWORK_POLICY" == "no-vpn" && "$PROXY_MODE" == "keep" ]]; then
    printf 'invalid combination: --network-policy no-vpn cannot use --proxy-mode keep\n' >&2
    exit 2
  fi

  CANDIDATES=()

  if [[ "$PROXY_MODE" == "none" || "$PROXY_MODE" == "auto" ]]; then
    for source in "${sources[@]}"; do
      if result="$(benchmark_candidate "$source" "none")"; then
        printf '[hf-download] candidate: time=%s speed=%s source=%s proxy=%s\n' $result >&2
        direct_lines+="${result}"$'\n'
      else
        printf '[hf-download] candidate failed: source=%s proxy=none\n' "$source" >&2
      fi
    done
  fi

  if [[ "$NETWORK_POLICY" != "no-vpn" && ( "$PROXY_MODE" == "keep" || "$PROXY_MODE" == "auto" ) ]] && has_proxy_env; then
    for source in "${sources[@]}"; do
      if result="$(benchmark_candidate "$source" "keep")"; then
        printf '[hf-download] candidate: time=%s speed=%s source=%s proxy=%s\n' $result >&2
        proxy_lines+="${result}"$'\n'
      else
        printf '[hf-download] candidate failed: source=%s proxy=keep\n' "$source" >&2
      fi
    done
  fi

  direct_lines="$(printf '%s' "${direct_lines:-}" | sed '/^$/d' | sort -n || true)"
  proxy_lines="$(printf '%s' "${proxy_lines:-}" | sed '/^$/d' | sort -n || true)"

  case "$NETWORK_POLICY" in
    fastest)
      all_lines="$(printf '%s\n%s\n' "$direct_lines" "$proxy_lines" | sed '/^$/d' | sort -n || true)"
      ;;
    save-vpn)
      all_lines="$(printf '%s\n%s\n' "$direct_lines" "$proxy_lines" | sed '/^$/d' || true)"
      ;;
    no-vpn)
      all_lines="$direct_lines"
      ;;
  esac

  if [[ -n "$all_lines" ]]; then
    mapfile -t CANDIDATES <<<"$all_lines"
  fi

  if [[ "${#CANDIDATES[@]}" -eq 0 ]]; then
    printf '[hf-download] benchmark failed; fallback source=official proxy=none\n' >&2
    CANDIDATES=("999999 0 official none")
  fi

  result="${CANDIDATES[0]}"
  SELECTED_SOURCE="$(awk '{print $3}' <<<"$result")"
  SELECTED_PROXY_MODE="$(awk '{print $4}' <<<"$result")"
  printf '[hf-download] selected-first: source=%s proxy=%s policy=%s time=%s speed=%s candidates=%s\n' \
    "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" "$NETWORK_POLICY" "$(awk '{print $1}' <<<"$result")" "$(awk '{print $2}' <<<"$result")" "${#CANDIDATES[@]}" >&2
}

run_hf() {
  local -a env_args=(
    "HF_HOME=$HF_CACHE_ROOT"
    "HF_HUB_CACHE=$HF_CACHE_DIR"
    "HUGGINGFACE_HUB_CACHE=$HF_CACHE_DIR"
    "HF_DATASETS_CACHE=$HF_CACHE_DIR"
    "HF_DATASETS_DOWNLOADED_DATASETS_PATH=$HF_CACHE_DIR"
    "DATASETS_ROOT=$HF_CACHE_DIR"
  )

  if [[ "$SELECTED_SOURCE" == "mirror" ]]; then
    env_args+=("HF_ENDPOINT=https://hf-mirror.com")
  fi

  if [[ "$SELECTED_PROXY_MODE" == "none" ]]; then
    env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY \
      -u http_proxy -u https_proxy -u all_proxy \
      -u NO_PROXY -u no_proxy \
      GIT_CONFIG_GLOBAL=/dev/null \
      "${env_args[@]}" \
      "$@"
  else
    env "${env_args[@]}" "$@"
  fi
}

metadata_tsv() {
  local source="$1"
  local proxy_mode="$2"
  local url
  url="$(api_url "$source")"
  curl_env "$proxy_mode" curl -L -sS \
    --connect-timeout 5 --max-time 60 \
    "$url" 2>/dev/null | "${PYTHON_BIN:-python}" -c '
import json, sys, urllib.parse
data = json.load(sys.stdin)
sha = data.get("sha") or ""
if not sha:
    sys.exit("missing revision sha")
wanted = set(sys.argv[1:]) if len(sys.argv) > 1 else None
print("COMMIT\t" + sha)
for item in data.get("siblings") or []:
    name = item.get("rfilename") or ""
    if not name or (wanted is not None and name not in wanted):
        continue
    lfs = item.get("lfs") or {}
    key = lfs.get("sha256") or item.get("blobId") or ""
    size = item.get("size") or lfs.get("size") or 0
    if not key:
        continue
    encoded = urllib.parse.quote(name, safe="/")
    print(f"FILE\t{name}\t{key}\t{size}\t{encoded}")
' "${FILES[@]}"
}

download_url_for_file() {
  local source="$1"
  local encoded_file="$2"
  local base prefix
  base="$(endpoint_base "$source")"
  prefix="$(repo_prefix)"
  printf '%s/%s%s/resolve/%s/%s\n' "$base" "$prefix" "$REPO_ID" "$REVISION" "$encoded_file"
}

download_blob_curl() {
  local url="$1"
  local incomplete="$2"
  run_transport_env "$SELECTED_PROXY_MODE" curl -L --fail --continue-at - \
    --connect-timeout 10 --retry 3 --retry-delay 2 \
    -o "$incomplete" "$url"
}

download_blob_aria2() {
  local url="$1"
  local incomplete="$2"
  local dir out aria2
  aria2="$SCRIPT_DIR/aria2c"
  dir="$(dirname "$incomplete")"
  out="$(basename "$incomplete")"
  if [[ ! -x "$aria2" ]]; then
    return 127
  fi
  run_transport_env "$SELECTED_PROXY_MODE" "$aria2" \
    --continue=true \
    --max-connection-per-server="$ARIA2_SPLIT" \
    --split="$ARIA2_SPLIT" \
    --min-split-size=1M \
    --file-allocation=none \
    --auto-file-renaming=false \
    --allow-overwrite=true \
    --dir "$dir" \
    --out "$out" \
    "$url"
}

cache_download() {
  local meta_file commit cache_dir blobs_dir snapshot_dir refs_dir
  local kind name key size encoded url final incomplete actual rel target_dir
  meta_file="$(mktemp)"
  metadata_tsv "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" > "$meta_file"
  commit="$(awk -F '\t' '$1=="COMMIT"{print $2; exit}' "$meta_file")"
  if [[ -z "$commit" ]]; then
    rm -f "$meta_file"
    printf '[hf-download] metadata fetch failed\n' >&2
    return 1
  fi

  cache_dir="$(repo_cache_dir)"
  blobs_dir="$cache_dir/blobs"
  snapshot_dir="$cache_dir/snapshots/$commit"
  refs_dir="$cache_dir/refs"
  mkdir -p "$blobs_dir" "$snapshot_dir" "$refs_dir"
  printf '%s' "$commit" > "$refs_dir/$REVISION"

  while IFS=$'\t' read -r kind name key size encoded; do
    [[ "$kind" == "FILE" ]] || continue
    final="$blobs_dir/$key"
    incomplete="$final.incomplete"
    url="$(download_url_for_file "$SELECTED_SOURCE" "$encoded")"

    if [[ -f "$final" ]]; then
      actual="$(stat -c '%s' "$final")"
      if [[ "$actual" == "$size" ]]; then
        printf '[hf-download] cache hit: %s\n' "$name" >&2
      else
        printf '[hf-download] size mismatch, redownload: %s local=%s expected=%s\n' "$name" "$actual" "$size" >&2
        mv -f "$final" "$incomplete"
      fi
    fi

    if [[ ! -f "$final" ]]; then
      if [[ "$size" -ge "$ARIA2_THRESHOLD" ]]; then
        printf '[hf-download] aria2: %s size=%s split=%s\n' "$name" "$size" "$ARIA2_SPLIT" >&2
        download_blob_aria2 "$url" "$incomplete" || {
          printf '[hf-download] aria2 failed, curl fallback: %s\n' "$name" >&2
          download_blob_curl "$url" "$incomplete"
        }
      else
        printf '[hf-download] curl: %s size=%s\n' "$name" "$size" >&2
        download_blob_curl "$url" "$incomplete"
      fi

      if [[ ! -f "$incomplete" ]]; then
        rm -f "$meta_file"
        printf '[hf-download] missing downloaded file: %s\n' "$name" >&2
        return 1
      fi
      actual="$(stat -c '%s' "$incomplete")"
      if [[ "$actual" != "$size" ]]; then
        rm -f "$meta_file"
        printf '[hf-download] incomplete size: %s local=%s expected=%s\n' "$name" "$actual" "$size" >&2
        return 1
      fi
      mv -f "$incomplete" "$final"
    fi

    target_dir="$snapshot_dir/$(dirname "$name")"
    [[ "$target_dir" == "$snapshot_dir/." ]] && target_dir="$snapshot_dir"
    mkdir -p "$target_dir"
    rel="$("${PYTHON_BIN:-python}" - "$name" <<'PY'
import os, sys
name = sys.argv[1]
depth = len(name.split("/")) - 1
print("../" * (depth + 2) + "blobs")
PY
)"
    ln -sfn "$rel/$key" "$snapshot_dir/$name"
  done < "$meta_file"

  rm -f "$meta_file"
}

repo_cache_dir() {
  local safe_id="${REPO_ID//\//--}"
  printf '%s/%ss--%s\n' "$HF_CACHE_DIR" "$REPO_TYPE" "$safe_id"
}

expected_file_count() {
  local source="$1"
  local proxy_mode="$2"
  local url
  url="$(api_url "$source")"
  curl_env "$proxy_mode" curl -L -sS \
    --connect-timeout 5 --max-time "$BENCHMARK_TIMEOUT" \
    "$url" 2>/dev/null | "${PYTHON_BIN:-python}" -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(1)
print(len(data.get("siblings") or []))
'
}

verify_download() {
  local cache_dir expected actual
  cache_dir="$(repo_cache_dir)"

  if find "$cache_dir" -name '*.incomplete' -print -quit 2>/dev/null | grep -q .; then
    printf '[hf-download] verify failed: incomplete files remain in %s\n' "$cache_dir" >&2
    return 1
  fi

  if [[ "${#FILES[@]}" -gt 0 ]]; then
    return 0
  fi

  expected="$(expected_file_count "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" || true)"
  if [[ -z "$expected" || "$expected" == "0" ]]; then
    printf '[hf-download] verify warning: could not fetch expected file count\n' >&2
    return 0
  fi

  actual="$(find "$cache_dir/snapshots" -maxdepth 2 -type l 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$actual" -lt "$expected" ]]; then
    printf '[hf-download] verify failed: snapshot has %s/%s files\n' "$actual" "$expected" >&2
    return 1
  fi
}

run_download() {
  if [[ -n "$LOCAL_DIR" ]]; then
    run_hf "${cmd[@]}"
    return
  fi
  cache_download
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-id)
      REPO_ID="${2:-}"
      shift 2
      ;;
    --repo-type)
      REPO_TYPE="${2:-}"
      shift 2
      ;;
    --revision)
      REVISION="${2:-}"
      shift 2
      ;;
    --local-dir)
      LOCAL_DIR="${2:-}"
      shift 2
      ;;
    --source)
      SOURCE="${2:-}"
      shift 2
      ;;
    --proxy-mode)
      PROXY_MODE="${2:-}"
      shift 2
      ;;
    --network-policy)
      NETWORK_POLICY="${2:-}"
      shift 2
      ;;
    --mirror)
      SOURCE="mirror"
      shift
      ;;
    --official)
      SOURCE="official"
      shift
      ;;
    --keep-proxy)
      PROXY_MODE="keep"
      shift
      ;;
    --no-proxy)
      PROXY_MODE="none"
      shift
      ;;
    --max-workers)
      MAX_WORKERS="${2:-}"
      shift 2
      ;;
    --aria2-threshold)
      ARIA2_THRESHOLD="${2:-}"
      shift 2
      ;;
    --aria2-split)
      ARIA2_SPLIT="${2:-}"
      shift 2
      ;;
    --benchmark-timeout)
      BENCHMARK_TIMEOUT="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      printf 'unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

while [[ $# -gt 0 ]]; do
  FILES+=("$1")
  shift
done

if [[ -z "$REPO_ID" ]]; then
  usage >&2
  exit 2
fi

case "$SOURCE" in
  auto|official|mirror) ;;
  *) printf 'invalid --source: %s\n' "$SOURCE" >&2; exit 2 ;;
esac

case "$PROXY_MODE" in
  auto|keep|none) ;;
  *) printf 'invalid --proxy-mode: %s\n' "$PROXY_MODE" >&2; exit 2 ;;
esac

case "$NETWORK_POLICY" in
  fastest|save-vpn|no-vpn) ;;
  *) printf 'invalid --network-policy: %s\n' "$NETWORK_POLICY" >&2; exit 2 ;;
esac

mkdir -p "$HF_CACHE_DIR"

cmd=(
  hf download
  --repo-type "$REPO_TYPE"
  --revision "$REVISION"
  --cache-dir "$HF_CACHE_DIR"
  --max-workers "$MAX_WORKERS"
)

if [[ -n "$LOCAL_DIR" ]]; then
  mkdir -p "$LOCAL_DIR"
  cmd+=(--local-dir "$LOCAL_DIR")
fi

cmd+=("$REPO_ID")

if [[ "${#FILES[@]}" -gt 0 ]]; then
  cmd+=("${FILES[@]}")
fi

"$SCRIPT_DIR/hf-env.sh" exec true >/dev/null
source "$SCRIPT_DIR/ensure-tools.sh" all
export PATH="$SCRIPT_DIR:$PATH"
select_transport

last_status=1
for candidate in "${CANDIDATES[@]}"; do
  SELECTED_SOURCE="$(awk '{print $3}' <<<"$candidate")"
  SELECTED_PROXY_MODE="$(awk '{print $4}' <<<"$candidate")"
  printf '[hf-download] attempt: source=%s proxy=%s policy=%s\n' \
    "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" "$NETWORK_POLICY" >&2

  set +e
  run_download
  last_status=$?
  set -e

  if [[ "$last_status" -eq 0 ]]; then
    if verify_download; then
      printf '[hf-download] completed: source=%s proxy=%s\n' "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" >&2
      exit 0
    fi
    last_status=1
  fi

  printf '[hf-download] failed: source=%s proxy=%s exit=%s; trying next available path with same cache\n' \
    "$SELECTED_SOURCE" "$SELECTED_PROXY_MODE" "$last_status" >&2
done

exit "$last_status"
