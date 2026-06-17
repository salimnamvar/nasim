#!/usr/bin/env bash
# lib/nasim/agents/grok.sh — Grok Code launcher (if available)
#
# launch_grok(url, model):
#   Sets GROK_API_BASE + GROK_API_KEY and execs grok CLI.
#   Grok CLI (if it exists) typically uses OpenAI-compatible endpoints.

launch_grok() {
    local url="$1" model="$2"
    local base="${url%/}/v1"

    log "launching grok -> $base model=$model (OpenAI compat)"

    if is_dry; then
        echo "DRY: GROK_API_BASE=$base GROK_API_KEY=ollama grok --model $model"
        return 0
    fi

    if ! have grok; then
        log "grok CLI not found. Install with: pip install grok-cli (or similar)"
        log "falling back to terminal mode..."
        launch_terminal "$url" "$model"
        return 0
    fi

    # Grok typically uses OpenAI-compatible API
    export GROK_API_BASE="$base"
    export GROK_API_KEY="ollama"
    # Some versions may use different env names
    export OPENAI_BASE_URL="$base"
    export OPENAI_API_KEY="ollama"

    exec grok --model "$model" "${@:3}"
}
