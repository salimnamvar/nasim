#!/usr/bin/env bash
# Note: This file is meant to be sourced, not executed directly.

nasim() {
  local NASIM_STATE_FILE="$HOME/.nasim_state"
  local OLLAMA_URL="http://192.168.70.125:11434"

  case "$1" in
    start)
      echo "ollama" > "$NASIM_STATE_FILE"

      export ANTHROPIC_BASE_URL="$OLLAMA_URL"
      export ANTHROPIC_AUTH_TOKEN="ollama"
      
      # Add these two new lines:
      export CLAUDE_CODE_MAX_OUTPUT_TOKENS="128000"
      export CLAUDE_CODE_DISABLE_THINKING="1"

      echo "🟢 nasim STARTED → Claude Code now uses LOCAL Ollama"
      echo "Model backend: $OLLAMA_URL"
      ;;

    stop)
      echo "anthropic" > "$NASIM_STATE_FILE"

      unset ANTHROPIC_BASE_URL
      unset ANTHROPIC_AUTH_TOKEN
      unset CLAUDE_CODE_MAX_OUTPUT_TOKENS
      unset CLAUDE_CODE_DISABLE_THINKING

      echo "🔵 nasim STOPPED → Claude Code now uses Anthropic cloud"
      echo "Backend reset to default Claude"
      ;;

    status)
      if [ -f "$NASIM_STATE_FILE" ]; then
        cat "$NASIM_STATE_FILE"
      else
        echo "anthropic (default)"
      fi
      ;;

    *)
      echo "Usage: nasim {start|stop|status}"
      ;;
  esac
}