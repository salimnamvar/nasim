#!/usr/bin/env bash
# setup.sh — Install the nasim Python package + the `nasim` launcher.
#
# Usage: ./setup.sh [--user|--dev] [bin-dir]
#   --user (default): pip install the package for the current user.
#   --dev:            pip install -e . (editable) so edits in src/ take effect live.
#   bin-dir:          where to place the `nasim` launcher symlink (default ~/.local/bin).
#
# After install, `nasim` resolves the importable package; if pip is unavailable the
# launcher still runs straight from this checkout's src/ tree.
set -euo pipefail

MODE="--user"
BIN_DIR="${HOME}/.local/bin"
for arg in "$@"; do
    case "$arg" in
        --user) MODE="--user" ;;
        --dev)  MODE="--dev" ;;
        *)      BIN_DIR="$arg" ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${NASIM_PYTHON:-python3}"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/nasim"

echo "=== Nasim (Python) Setup ==="
echo "Mode: $MODE | bin: $BIN_DIR"

mkdir -p "$BIN_DIR" "$CONFIG_DIR" "${HOME}/.local/share/nasim"

echo "[1/4] Installing package ..."
if "$PY" -m pip --version >/dev/null 2>&1; then
    if [[ "$MODE" == "--dev" ]]; then
        "$PY" -m pip install -e "$SCRIPT_DIR" || echo "pip editable install failed; launcher will fall back to src/"
    else
        "$PY" -m pip install --user "$SCRIPT_DIR" || echo "pip install failed; launcher will fall back to src/"
    fi
else
    echo "pip not available — skipping install; the launcher runs from src/ in this checkout."
fi

echo "[2/4] Installing launcher to $BIN_DIR/nasim ..."
ln -sf "$SCRIPT_DIR/bin/nasim" "$BIN_DIR/nasim"
chmod +x "$SCRIPT_DIR/bin/nasim"

echo "[3/4] Creating default config (if missing) ..."
if [[ ! -f "$CONFIG_DIR/nasim.conf" ]]; then
    cat > "$CONFIG_DIR/nasim.conf" <<'EOF'
# nasim user configuration (KEY=val). Env vars and CLI flags override this file.
BLACK_HOST=black
# Strong default for agentic coding (fits an 11GB GPU; good tool use).
DEFAULT_MODEL=deepseek-r1:14b
# DEFAULT_LOCAL_PORT=11435
# LITELLM_PORT=4000
# ACCESS_ORDER="ssh-tunnel tailscale litellm"
# AGENT_ORDER="claude aider opencode terminal"
# NASIM_FCC_SRC_DIR=$HOME/prj/salim/nasim/code/free-claude-code
# NASIM_GPU_VRAM_GB=11
EOF
    echo "Created: $CONFIG_DIR/nasim.conf"
else
    echo "Config already exists: $CONFIG_DIR/nasim.conf"
fi

echo "[4/4] Verifying ..."
if "$BIN_DIR/nasim" version >/dev/null 2>&1; then
    echo "OK: nasim $("$BIN_DIR/nasim" version)"
else
    echo "WARNING: nasim version check failed"
fi

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "NOTE: add to your shell rc:  export PATH=\"$BIN_DIR:\$PATH\""
fi

echo ""
echo "=== Setup Complete ==="
echo "Quick start: nasim config edit → nasim start → nasim code → nasim stop"
echo "Safety: nasim restores your Claude /model picker + env on stop/exit/crash."
