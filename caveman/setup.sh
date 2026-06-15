#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./setup.sh [--codex-home PATH] [--mode MODE] [--savings N] [--provider auto|codex|anthropic|claude] [--disable] [--copy]

Installs/restores the local Caveman Codex skill after moving this directory.

Defaults:
  --codex-home  ${CODEX_HOME:-$HOME/.codex}
  --mode        full
  --savings     50
  --provider    auto

Examples:
  ./setup.sh
  ./setup.sh --mode ultra --savings 75
  ./setup.sh --provider codex --copy
  ./setup.sh --disable
EOF
}

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
MODE="full"
SAVINGS="50"
PROVIDER="auto"
ENABLED="true"
LINK_MODE="symlink"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --codex-home) CODEX_HOME="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --savings) SAVINGS="${2%\%}"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --disable) ENABLED="false"; shift ;;
    --copy) LINK_MODE="copy"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1" >&2; usage >&2; exit 2 ;;
  esac
done

case "$MODE" in
  lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra) ;;
  *) echo "Invalid --mode: $MODE" >&2; exit 2 ;;
esac

case "$PROVIDER" in
  auto|codex|anthropic|claude) ;;
  *) echo "Invalid --provider: $PROVIDER" >&2; exit 2 ;;
esac

if ! [[ "$SAVINGS" =~ ^[0-9]+$ ]] || (( SAVINGS < 0 || SAVINGS > 90 )); then
  echo "--savings must be 0..90" >&2
  exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$CODEX_HOME/skills"
TARGET="$SKILLS_DIR/caveman"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/caveman"
CONFIG_FILE="$CONFIG_DIR/config.json"
INSTRUCTIONS_FILE="$CODEX_HOME/instructions.md"

mkdir -p "$SKILLS_DIR" "$CONFIG_DIR"

if [[ "$SCRIPT_DIR" != "$TARGET" ]]; then
  rm -rf "$TARGET"
  if [[ "$LINK_MODE" == "copy" ]]; then
    cp -a "$SCRIPT_DIR" "$TARGET"
  else
    ln -s "$SCRIPT_DIR" "$TARGET"
  fi
fi

python3 "$SCRIPT_DIR/scripts/config.py" on "$MODE" >/dev/null
python3 "$SCRIPT_DIR/scripts/config.py" set --savings "$SAVINGS" --provider "$PROVIDER" >/dev/null
if [[ "$ENABLED" != "true" ]]; then
  python3 "$SCRIPT_DIR/scripts/config.py" off >/dev/null
fi

if [[ ! -x "$SCRIPT_DIR/scripts/caveman" ]]; then
  chmod +x "$SCRIPT_DIR/scripts/caveman" 2>/dev/null || true
fi

mkdir -p "$(dirname "$INSTRUCTIONS_FILE")"
touch "$INSTRUCTIONS_FILE"
if ! grep -q '<!-- caveman-global-default -->' "$INSTRUCTIONS_FILE"; then
  cat >>"$INSTRUCTIONS_FILE" <<'EOF'

<!-- caveman-global-default -->
If `~/.config/caveman/config.json` exists and has `"enabled": true`, apply the local
Caveman response style by default for every conversation, without requiring the user
to mention `/caveman`.

Default behavior:
- Read intent from config: `defaultMode` controls intensity; `targetSavings` is the
  approximate token-saving target.
- `full`: concise fragments OK; remove filler, pleasantries, hedging, redundant prose.
- Preserve exact code, commands, file paths, URLs, API names, symbols, errors, dates,
  numbers, and the user's dominant language.
- Do not announce Caveman mode.
- Temporarily use normal clarity for security warnings, irreversible actions, exact
  multi-step ordering, or when compression would create ambiguity.
- User can disable with "关闭 caveman", "stop caveman", "normal mode", or `/caveman off`.
<!-- /caveman-global-default -->
EOF
fi

echo "Caveman skill installed:"
echo "  skill:    $TARGET"
echo "  config:   $CONFIG_FILE"
echo "  global:   $INSTRUCTIONS_FILE"
echo "  enabled:  $ENABLED"
echo "  mode:     $MODE"
echo "  savings:  $SAVINGS%"
echo "  provider: $PROVIDER"

if ! command -v codex >/dev/null 2>&1; then
  echo "Warning: codex not found; auto provider will fall back to Anthropic/Claude if available." >&2
fi
