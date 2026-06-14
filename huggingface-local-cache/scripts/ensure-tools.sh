#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONDA_BIN="${CONDA_BIN:-$(command -v conda 2>/dev/null || true)}"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python 2>/dev/null || command -v python3 2>/dev/null || true)}"
PIP_BIN="${PIP_BIN:-$(command -v pip 2>/dev/null || command -v pip3 2>/dev/null || true)}"

log() {
  printf '[hf-tools] %s\n' "$*" >&2
}

have() {
  command -v "$1" >/dev/null 2>&1
}

conda_install() {
  if [[ -z "$CONDA_BIN" ]]; then
    return 1
  fi
  log "conda install: $*"
  "$CONDA_BIN" install -y -c conda-forge "$@"
}

pip_install() {
  if [[ -n "$PYTHON_BIN" ]]; then
    log "pip install via python: $*"
    "$PYTHON_BIN" -m pip install -U "$@"
    return
  fi
  if [[ -n "$PIP_BIN" ]]; then
    log "pip install: $*"
    "$PIP_BIN" install -U "$@"
    return
  fi
  return 1
}

ensure_python() {
  if [[ -n "$PYTHON_BIN" ]]; then
    return
  fi
  conda_install python || {
    printf 'python is required; conda install failed and no python executable exists\n' >&2
    exit 1
  }
  PYTHON_BIN="$(command -v python 2>/dev/null || command -v python3 2>/dev/null || true)"
}

ensure_curl() {
  if have curl; then
    return
  fi
  conda_install curl || {
    printf 'curl is required; conda install failed\n' >&2
    exit 1
  }
}

ensure_hf() {
  if have hf; then
    return
  fi
  conda_install huggingface_hub || pip_install 'huggingface_hub[cli]' || pip_install huggingface_hub || {
    printf 'hf CLI is required; conda/pip install failed\n' >&2
    exit 1
  }
  if have hf; then
    return
  fi
  cat > "$SCRIPT_DIR/hf" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
"${PYTHON_BIN:-python}" -m huggingface_hub.commands.huggingface_cli "$@"
EOF
  chmod +x "$SCRIPT_DIR/hf"
  export PATH="$SCRIPT_DIR:$PATH"
  have hf || {
    printf 'hf CLI is required; installed huggingface_hub but could not create hf wrapper\n' >&2
    exit 1
  }
}

ensure_aria2() {
  if [[ -x "$SCRIPT_DIR/aria2c" ]]; then
    "$SCRIPT_DIR/aria2c" --version >/dev/null 2>&1 && return
  fi

  if have aria2c; then
    return
  fi

  conda_install aria2 || true

  if have aria2c; then
    cat > "$SCRIPT_DIR/aria2c" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
exec aria2c "$@"
EOF
    chmod +x "$SCRIPT_DIR/aria2c"
    return
  fi

  local datapath_root
  datapath_root="${DATAPATH_ROOT:-$SKILL_DIR/../../../syncthing/DATAPATH}"

  if [[ -x "$datapath_root/.skill/bin/aria2c" ]]; then
    cat > "$SCRIPT_DIR/aria2c" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DATAPATH_ROOT="${DATAPATH_ROOT:-$SKILL_DIR/../../../syncthing/DATAPATH}"
exec "$DATAPATH_ROOT/.skill/bin/aria2c" "$@"
EOF
    chmod +x "$SCRIPT_DIR/aria2c"
    return
  fi

  if [[ -x "$datapath_root/.tools/aria2/usr/bin/aria2c" ]]; then
    mkdir -p "$SKILL_DIR/tools"
    cp -a "$datapath_root/.tools/aria2" "$SKILL_DIR/tools/" 2>/dev/null || true
    if [[ -x "$SKILL_DIR/tools/aria2/usr/bin/aria2c" ]]; then
      cat > "$SCRIPT_DIR/aria2c" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ARIA2_ROOT="$SKILL_DIR/tools/aria2"
export LD_LIBRARY_PATH="$ARIA2_ROOT/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$ARIA2_ROOT/usr/bin/aria2c" "$@"
EOF
      chmod +x "$SCRIPT_DIR/aria2c"
      return
    fi
  fi

  printf 'aria2c is required for accelerated large-file downloads; conda install failed\n' >&2
  exit 1
}

case "${1:-all}" in
  all)
    ensure_python
    ensure_curl
    ensure_hf
    ensure_aria2
    ;;
  python) ensure_python ;;
  curl) ensure_curl ;;
  hf) ensure_python; ensure_hf ;;
  aria2|aria2c) ensure_aria2 ;;
  *)
    printf 'Usage: ensure-tools.sh [all|python|curl|hf|aria2]\n' >&2
    exit 2
    ;;
esac
