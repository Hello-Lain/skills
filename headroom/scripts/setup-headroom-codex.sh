#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: setup-headroom-codex.sh [options]

Install/configure Headroom for Codex on this machine.

Options:
  --yes              Non-interactive. Apply changes without prompt.
  --upgrade          Force package upgrade/reinstall where supported.
  --run              Launch "headroom wrap codex" after setup.
  --prepare-only     Prepare Codex config only. Default.
  --unwrap           Run "headroom unwrap codex" and exit.
  --mirror tuna      Use Tsinghua PyPI mirror.
  --mirror aliyun    Use Aliyun PyPI mirror.
  --mirror ustc      Use USTC PyPI mirror.
  --index-url URL    Use a custom Python package index URL.
  --no-proxy         Clear HTTP(S)/ALL proxy env vars for this script.
  --context-tool X   Set HEADROOM_CONTEXT_TOOL, e.g. rtk or lean-ctx.
  -h, --help         Show this help.

Examples:
  setup-headroom-codex.sh --yes
  setup-headroom-codex.sh --yes --mirror tuna --no-proxy
  setup-headroom-codex.sh --unwrap
USAGE
}

die() {
  echo "error: $*" >&2
  exit 1
}

have() {
  command -v "$1" >/dev/null 2>&1
}

YES=0
UPGRADE=0
RUN=0
UNWRAP=0
PREPARE_ONLY=1
INDEX_URL=""
NO_PROXY_MODE=0
CONTEXT_TOOL=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --yes)
      YES=1
      ;;
    --upgrade)
      UPGRADE=1
      ;;
    --run)
      RUN=1
      PREPARE_ONLY=0
      ;;
    --prepare-only)
      PREPARE_ONLY=1
      RUN=0
      ;;
    --unwrap)
      UNWRAP=1
      ;;
    --mirror)
      [ "$#" -ge 2 ] || die "--mirror requires a value"
      case "$2" in
        tuna)
          INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple"
          ;;
        aliyun)
          INDEX_URL="https://mirrors.aliyun.com/pypi/simple"
          ;;
        ustc)
          INDEX_URL="https://pypi.mirrors.ustc.edu.cn/simple"
          ;;
        *)
          die "unknown mirror: $2"
          ;;
      esac
      shift
      ;;
    --index-url)
      [ "$#" -ge 2 ] || die "--index-url requires a URL"
      INDEX_URL="$2"
      shift
      ;;
    --no-proxy)
      NO_PROXY_MODE=1
      ;;
    --context-tool)
      [ "$#" -ge 2 ] || die "--context-tool requires a value"
      CONTEXT_TOOL="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
  shift
done

if [ "$NO_PROXY_MODE" -eq 1 ]; then
  unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
  export NO_PROXY="*" no_proxy="*"
fi

if [ -n "$INDEX_URL" ]; then
  export PIP_INDEX_URL="$INDEX_URL"
  export UV_DEFAULT_INDEX="$INDEX_URL"
fi

if [ -n "$CONTEXT_TOOL" ]; then
  export HEADROOM_CONTEXT_TOOL="$CONTEXT_TOOL"
fi

if [ "$YES" -ne 1 ] && [ "$UNWRAP" -ne 1 ]; then
  echo "This will install/upgrade Headroom and run: headroom wrap codex --prepare-only"
  printf "Continue? [y/N] "
  read -r answer
  case "$answer" in
    y|Y|yes|YES)
      ;;
    *)
      echo "aborted"
      exit 0
      ;;
  esac
fi

install_with_pipx() {
  if [ "$UPGRADE" -eq 1 ]; then
    pipx install --force 'headroom-ai[all]'
  else
    pipx install 'headroom-ai[all]' || pipx upgrade headroom-ai
  fi
}

install_with_uv() {
  if [ "$UPGRADE" -eq 1 ]; then
    uv tool install --force 'headroom-ai[all]'
  else
    uv tool install 'headroom-ai[all]' || true
  fi
}

install_with_pip_user() {
  python3 -m pip install --user --upgrade 'headroom-ai[all]'
}

ensure_path_hint() {
  case ":$PATH:" in
    *":$HOME/.local/bin:"*)
      ;;
    *)
      echo "note: add $HOME/.local/bin to PATH if headroom is not found in new shells" >&2
      ;;
  esac
}

if [ "$UNWRAP" -eq 1 ]; then
  have headroom || die "headroom not found; install it first or run this script without --unwrap"
  headroom unwrap codex
  exit 0
fi

if ! have headroom || [ "$UPGRADE" -eq 1 ]; then
  if have pipx; then
    install_with_pipx
  elif have uv; then
    install_with_uv
  elif have python3; then
    install_with_pip_user
    ensure_path_hint
  else
    die "need one of: pipx, uv, python3"
  fi
fi

if ! have headroom; then
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

have headroom || die "headroom installed but not found on PATH"

headroom --version || true

if [ "$RUN" -eq 1 ]; then
  exec headroom wrap codex
fi

if [ "$PREPARE_ONLY" -eq 1 ]; then
  headroom wrap codex --prepare-only
fi

echo "Headroom for Codex configured."
echo "Start with: headroom wrap codex"
