#!/bin/sh
# codex2codex installer: creates a local uv-managed venv and the `meight` CLI shim.
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${MEIGHT_BIN_DIR:-$HOME/.local/bin}"
SDK_PIN="openai-codex==0.1.0b3"
UV_INDEX="${UV_DEFAULT_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"

# 1. prerequisites
command -v codex >/dev/null 2>&1 || {
  echo "error: codex CLI not found. Install & authenticate it first:"
  echo "       https://developers.openai.com/codex"
  exit 1
}
command -v uv >/dev/null 2>&1 || {
  echo "error: uv not found. Install uv first; raw pip fallback is intentionally disabled."
  echo "       Example: curl -LsSf https://astral.sh/uv/install.sh | sh"
  exit 1
}
PY="${PYTHON:-}"
if [ -z "$PY" ]; then
  for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      PY="$(command -v "$candidate")"
      break
    fi
  done
fi
[ -n "$PY" ] || { echo "error: Python >= 3.10 not found"; exit 1; }
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' || {
  echo "error: Python >= 3.10 required (found $("$PY" -V)); set PYTHON=/path/to/python3.10+"; exit 1; }

# 2. venv + pinned SDK
if [ -x "$REPO_DIR/.venv/bin/python" ]; then
  echo "→ reusing venv at $REPO_DIR/.venv"
else
  echo "→ creating uv venv at $REPO_DIR/.venv"
  uv venv --python "$PY" "$REPO_DIR/.venv"
fi
echo "→ installing $SDK_PIN (prerelease enabled)"
UV_DEFAULT_INDEX="$UV_INDEX" uv pip install --python "$REPO_DIR/.venv/bin/python" \
  --prerelease allow "$SDK_PIN"
echo "→ validating environment"
"$REPO_DIR/.venv/bin/python" -m pip --version >/dev/null 2>&1 || \
  "$REPO_DIR/.venv/bin/python" -m ensurepip --upgrade
"$REPO_DIR/.venv/bin/python" -m pip check
uv pip check --python "$REPO_DIR/.venv/bin/python"
"$REPO_DIR/.venv/bin/python" -c 'import openai_codex; print("openai_codex import ok")'
"$REPO_DIR/.venv/bin/python" "$REPO_DIR/meight.py" --help >/dev/null
echo "→ installed and validated $SDK_PIN"

# 3. CLI shim
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/meight" <<SHIM
#!/bin/sh
SKILL_DIR="\${CODEX_HOME:-\$HOME/.codex}/skills/codex2codex"
PY="\$SKILL_DIR/.venv/bin/python"
if [ ! -x "\$PY" ] || ! "\$PY" -c 'import sys' >/dev/null 2>&1; then
  PY=python3
fi
exec "\$PY" "\$SKILL_DIR/meight.py" "\$@"
SHIM
chmod +x "$BIN_DIR/meight"
echo "→ installed $BIN_DIR/meight"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "note: $BIN_DIR is not in your PATH — add it to use \`meight\` directly." ;;
esac

# 4. recommend global gitignore for per-repo state dirs
if ! git config --global core.excludesfile >/dev/null 2>&1 || \
   ! grep -qs "^\.meight/$" "$(git config --global core.excludesfile 2>/dev/null)" 2>/dev/null; then
  echo "note: worker state lives in <repo>/.meight/ — add it to your global gitignore:"
  echo "      echo '.meight/' >> \"\$(git config --global core.excludesfile || echo ~/.config/git/ignore)\""
fi

echo "done. try: meight --help"
