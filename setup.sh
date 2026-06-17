#!/usr/bin/env bash
# setup.sh — Install nasim v3 to your system
#
# Usage: ./setup.sh [install-dir]
#   Default install-dir: ~/.local/bin (for nasim) + ~/.local/lib/nasim (for modules)
#
# This script:
#   1. Creates directory structure
#   2. Copies all modules to lib/nasim/
#   3. Copies entrypoint to bin/
#   4. Symlinks nasim to a PATH location
#   5. Creates default config if missing

set -euo pipefail

INSTALL_DIR="${1:-${HOME}/.local}"
BIN_DIR="$INSTALL_DIR/bin"
LIB_DIR="$INSTALL_DIR/lib/nasim"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/nasim"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Nasim v3 Setup ==="
echo "Install dir: $INSTALL_DIR"
echo ""

# Create directories
mkdir -p "$BIN_DIR"
mkdir -p "$LIB_DIR"
mkdir -p "$LIB_DIR/agents"
mkdir -p "$LIB_DIR/transports"
mkdir -p "$CONFIG_DIR"
mkdir -p "${HOME}/.local/share/nasim"

echo "[1/5] Installing nasim modules to $LIB_DIR ..."

# Copy all modules
cp -v "$SCRIPT_DIR/lib/nasim/rollback.sh"    "$LIB_DIR/rollback.sh"
cp -v "$SCRIPT_DIR/lib/nasim/daemon.sh"      "$LIB_DIR/daemon.sh"
cp -v "$SCRIPT_DIR/lib/nasim/context.sh"     "$LIB_DIR/context.sh"
cp -v "$SCRIPT_DIR/lib/nasim/kb.sh"          "$LIB_DIR/kb.sh"
cp -v "$SCRIPT_DIR/lib/nasim/vram.sh"       "$LIB_DIR/vram.sh"
cp -v "$SCRIPT_DIR/lib/nasim/session.sh"     "$LIB_DIR/session.sh"
cp -v "$SCRIPT_DIR/lib/nasim/code.sh"        "$LIB_DIR/code.sh"
cp -v "$SCRIPT_DIR/lib/nasim/config.sh"      "$LIB_DIR/config.sh"
cp -v "$SCRIPT_DIR/lib/nasim/fcc.sh"         "$LIB_DIR/fcc.sh" 2>/dev/null || true
cp -v "$SCRIPT_DIR/lib/nasim/probe.sh"       "$LIB_DIR/probe.sh"
cp -v "$SCRIPT_DIR/lib/nasim/transport.sh"     "$LIB_DIR/transport.sh"
cp -v "$SCRIPT_DIR/lib/nasim/agent.sh"       "$LIB_DIR/agent.sh"
cp -v "$SCRIPT_DIR/lib/nasim/ui.sh"          "$LIB_DIR/ui.sh"
cp -v "$SCRIPT_DIR/lib/nasim/orchestration.sh" "$LIB_DIR/orchestration.sh"
cp -v "$SCRIPT_DIR/lib/nasim/cli.sh"         "$LIB_DIR/cli.sh"

# Copy agent launchers
cp -v "$SCRIPT_DIR/lib/nasim/agents/claude.sh"   "$LIB_DIR/agents/claude.sh"
cp -v "$SCRIPT_DIR/lib/nasim/agents/grok.sh"     "$LIB_DIR/agents/grok.sh"
cp -v "$SCRIPT_DIR/lib/nasim/agents/aider.sh"    "$LIB_DIR/agents/aider.sh"
cp -v "$SCRIPT_DIR/lib/nasim/agents/opencode.sh" "$LIB_DIR/agents/opencode.sh"
cp -v "$SCRIPT_DIR/lib/nasim/agents/terminal.sh" "$LIB_DIR/agents/terminal.sh"

# Copy transport strategies
cp -v "$SCRIPT_DIR/lib/nasim/transports/ssh.sh"       "$LIB_DIR/transports/ssh.sh"
cp -v "$SCRIPT_DIR/lib/nasim/transports/tailscale.sh"  "$LIB_DIR/transports/tailscale.sh"
cp -v "$SCRIPT_DIR/lib/nasim/transports/litellm.sh"   "$LIB_DIR/transports/litellm.sh"

echo ""
echo "[2/5] Installing entrypoint to $BIN_DIR ..."
if [[ -f "$SCRIPT_DIR/bin/nasim" ]]; then
    cp -v "$SCRIPT_DIR/bin/nasim" "$BIN_DIR/nasim"
else
    # legacy fallback
    cp -v "$SCRIPT_DIR/bin/nasim.sh" "$BIN_DIR/nasim" 2>/dev/null || echo "WARNING: no bin/nasim or bin/nasim.sh found"
fi
chmod +x "$BIN_DIR/nasim" 2>/dev/null || true

echo ""
echo "[3/5] Creating default config (if missing) ..."
if [[ ! -f "$CONFIG_DIR/nasim.conf" ]]; then
    cat > "$CONFIG_DIR/nasim.conf" <<'EOF'
# nasim user configuration (KEY=val)
# This file is sourced (safely) at startup.
# Precedence: environment variables and CLI flags override this file.

BLACK_HOST=black
# Strong default for agentic coding on 1080Ti (11GB VRAM).
# deepseek-r1:14b fits well (~9.2GB) and has excellent reasoning.
# Other good options: qwen3:8b (~5.3GB), gemma4:9b (~5.9GB)
DEFAULT_MODEL=deepseek-r1:14b
# DEFAULT_LOCAL_PORT=11435
# LITELLM_PORT=4000

# Interactive select presentation order
# ACCESS_ORDER="ssh-tunnel tailscale litellm"
# AGENT_ORDER="claude aider opencode terminal"

# GPU VRAM limit for fit checking (GB)
# NASIM_GPU_VRAM_GB=11
EOF
    echo "Created: $CONFIG_DIR/nasim.conf"
else
    echo "Config already exists: $CONFIG_DIR/nasim.conf"
fi

echo ""
echo "[4/5] Checking PATH ..."
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "WARNING: $BIN_DIR is not in your PATH"
    echo "Add this to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
else
    echo "OK: $BIN_DIR is in PATH"
fi

echo ""
echo "[5/5] Verifying installation ..."
if "$BIN_DIR/nasim" version >/dev/null 2>&1; then
    echo "OK: nasim version $("$BIN_DIR/nasim" version)"
else
    echo "WARNING: nasim version check failed"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Quick start:"
echo "  1. nasim config edit       # Edit your config (set BLACK_HOST, etc.)"
echo "  2. nasim start             # Start persistent tunnel"
echo "  3. cd ~/your-project && nasim context --refresh"
echo "  4. nasim code              # Launch agent with full context"
echo "  5. nasim stop              # Tear down + restore env"
echo ""
echo "Safety: Your Claude/Grok/Aider cloud settings are NEVER permanently modified."
echo "        Run 'nasim env diff' to see current changes vs backup."
