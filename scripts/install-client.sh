#!/usr/bin/env bash
# install-client.sh — install the nasim command and seed ~/.nasim.
#
# Installs:
#   ~/.nasim/bin/naseem      identity-patched binary (from vendor/)
#   ~/.local/bin/nasim       wrapper (tunnel + env + exec)
#   ~/.local/bin/naseem      symlink to the wrapper
#   ~/.nasim/NASEEM.md       global context (seeded once, never overwritten)
#   ~/.nasim/.naseem.json    onboarding pre-seed   (seeded once)
#   ~/.nasim/settings.json   settings              (seeded once)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NASIM_HOME="${NASIM_HOME:-$HOME/.nasim}"
BIN_DIR="$HOME/.local/bin"

[[ -f "$REPO_DIR/vendor/naseem" ]] || { echo "vendor/naseem missing — run scripts/sync-from-upstream.sh first"; exit 1; }

echo "→ Installing binary to $NASIM_HOME/bin/naseem..."
mkdir -p "$NASIM_HOME/bin" "$BIN_DIR"
install -m 755 "$REPO_DIR/vendor/naseem" "$NASIM_HOME/bin/naseem"

echo "→ Installing wrapper to $BIN_DIR/nasim..."
install -m 755 "$REPO_DIR/bin/nasim" "$BIN_DIR/nasim"
ln -sf "$BIN_DIR/nasim" "$BIN_DIR/naseem"

if [[ ! -f "$NASIM_HOME/NASEEM.md" ]]; then
    echo "→ Seeding $NASIM_HOME/NASEEM.md..."
    cp "$REPO_DIR/NASEEM.md" "$NASIM_HOME/NASEEM.md"
fi

if [[ ! -f "$NASIM_HOME/.naseem.json" ]]; then
    echo "→ Seeding onboarding state..."
    cat > "$NASIM_HOME/.naseem.json" << 'EOF'
{
  "hasCompletedOnboarding": true,
  "theme": "dark",
  "autoUpdates": false
}
EOF
fi

if [[ ! -f "$NASIM_HOME/settings.json" ]]; then
    echo "→ Seeding settings.json..."
    cat > "$NASIM_HOME/settings.json" << 'EOF'
{
  "includeCoAuthoredBy": false
}
EOF
fi

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "NOTE: add $BIN_DIR to PATH" ;;
esac

echo "✓ Client install complete: $("$NASIM_HOME/bin/naseem" --version)"
echo "  Try: nasim --help"
