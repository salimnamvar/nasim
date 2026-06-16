#!/usr/bin/env bash

set -e

OLD_TARGET="$HOME/.local/bin/nasim"
NASIM_STATE_FILE="$HOME/.nasim_state"

echo "Uninstalling nasim..."

# 1. Clean up old binary symlinks if they still exist anywhere
if [ -L "$OLD_TARGET" ] || [ -f "$OLD_TARGET" ]; then
  rm -f "$OLD_TARGET"
  echo "✔ Removed binary from $OLD_TARGET"
fi

# 2. Clean up the state tracking file
if [ -f "$NASIM_STATE_FILE" ]; then
  rm -f "$NASIM_STATE_FILE"
  echo "✔ Removed state file at $NASIM_STATE_FILE"
fi

# 3. Clean up shell profiles (.bashrc and .zshrc)
clean_profile() {
  local PROFILE="$1"
  if [ -f "$PROFILE" ]; then
    # Create a temporary file
    local TMP_FILE
    TMP_FILE=$(mktemp)
    
    # Remove the comment line and the source line matching the pattern
    sed '/# nasim: Local Ollama toggle/d; /source .*bin\/nasim\.sh/d' "$PROFILE" > "$TMP_FILE"
    
    # Check if lines were actually removed
    if ! cmp -s "$PROFILE" "$TMP_FILE"; then
      mv "$TMP_FILE" "$PROFILE"
      echo "✔ Cleaned up nasim references from $PROFILE"
    else
      rm -f "$TMP_FILE"
    fi
  fi
}

clean_profile "$HOME/.bashrc"
clean_profile "$HOME/.zshrc"

# 4. Clean up any active environment variables in the current session
unset ANTHROPIC_BASE_URL
unset ANTHROPIC_AUTH_TOKEN

echo "----------------------------------------"
echo "Uninstallation complete!"
echo "To fully clear the nasim command from your current active window, run:"
echo "unset -f nasim"