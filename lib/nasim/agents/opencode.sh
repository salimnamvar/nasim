#!/usr/bin/env bash
# lib/nasim/agents/opencode.sh — OpenCode (prefers OpenAI compat base for broadest support)

launch_opencode() {
    local url="$1" model="$2"
    log "launching opencode -> $url model=$model (OpenAI compat base)"
    if is_dry; then
        echo "DRY: OPENAI_BASE_URL=$url OPENAI_API_KEY=ollama opencode (or ollama launch opencode) model=$model"
        return 0
    fi
    # Common pattern (OD-01 still open for exact surface)
    OPENAI_BASE_URL="$url" OPENAI_API_KEY="ollama" \
    exec opencode --model "$model" "${@:3}" 2>/dev/null || \
    OPENAI_BASE_URL="$url" exec opencode "${@:3}"
}
