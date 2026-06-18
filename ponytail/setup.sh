#!/usr/bin/env bash
set -euo pipefail

PONY_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${CODEX_HOME:-$HOME/.codex}/skills"
TARGET="$SKILLS_DIR/ponytail"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/ponytail"
CONFIG_FILE="$CONFIG_DIR/config.json"

usage() {
  cat <<'EOF'
Usage: ./setup.sh [--mode lite|full|ultra] [--disable]

Installs/restores the Ponytail Codex skill after moving this directory.
Defaults: --mode full
EOF
}

MODE="full"
ENABLED="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) MODE="$2"; shift 2 ;;
    --disable) ENABLED="false"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

# Ensure target location
mkdir -p "$SKILLS_DIR" "$CONFIG_DIR"
if [[ "$(dirname "$PONY_DIR")" != "$SKILLS_DIR" ]]; then
  rm -f "$TARGET" 2>/dev/null
  ln -sf "$PONY_DIR" "$TARGET"
fi

# Init config
if [ ! -f "$CONFIG_FILE" ]; then
  python3 "$PONY_DIR/scripts/config.py" on "$MODE" >/dev/null
fi

if [[ "$ENABLED" != "true" ]]; then
  python3 "$PONY_DIR/scripts/config.py" off >/dev/null
fi

echo "Ponytail installed:"
echo "  skill:  $TARGET"
echo "  config: $CONFIG_FILE"
echo "  mode:   $MODE"
echo "  status: $(python3 "$PONY_DIR/scripts/config.py" status)" | head -1
