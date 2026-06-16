#!/usr/bin/env bash

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$REPO_DIR/bin/nasim.sh"
OLD_TARGET="$HOME/.local/bin/nasim"

echo "Installing nasim..."

# 1. Clean up the old executable link if it exists
if [ -L "$OLD_TARGET" ] || [ -f "$OLD_TARGET" ]; then
  rm -f "$OLD_TARGET"
  echo "Removed old binary from $OLD_TARGET"
fi

# 2. Determine the active shell profile
SHELL_RC="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
  SHELL_RC="$HOME/.zshrc"
fi

# 3. Add the source command to the profile if it isn't there already
if grep -q "source .*bin/nasim.sh" "$SHELL_RC"; then
  echo "✔ nasim is already hooked in $SHELL_RC"
else
  echo "" >> "$SHELL_RC"
  echo "# nasim: Local Ollama toggle for Claude Code" >> "$SHELL_RC"
  echo "source \"$SRC\"" >> "$SHELL_RC"
  echo "✔ Added nasim hook to $SHELL_RC"
fi

echo "----------------------------------------"
echo "Installation complete!"
echo "To use it right now without restarting your terminal, run:"
echo "source $SHELL_RC"