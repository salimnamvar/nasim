#!/usr/bin/env bash
# lib/nasim/agents/claude.sh — Claude Code launcher (native Anthropic compat)

launch_claude() {
    local url="$1" model="$2"
    log "launching claude -> $url model=$model (native Anthropic compat)"
    if is_dry; then
        echo "DRY: ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=$url ANTHROPIC_API_KEY= CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 claude --model $model"
        return 0
    fi
    log "Tip: Claude Code agentic quality depends heavily on the model. Use strong tool-calling coders (qwen3-coder*, glm-5*, deepseek-coder-v* etc) fully GPU-resident on black. Weak or old taggers like qwen2.5 often emit malformed JSON/Workflow instead of clean turns. See .grok/recipes/models.md"
    ANTHROPIC_AUTH_TOKEN=ollama \
    ANTHROPIC_BASE_URL="$url" \
    ANTHROPIC_API_KEY="" \
    CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
    exec claude --model "$model" "${@:3}"
}
