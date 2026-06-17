#!/usr/bin/env bash
# lib/nasim/agents/claude.sh — Claude Code launcher (native Anthropic compat)
#
# launch_claude(url, model, [extra_args...]):
#   Sets ANTHROPIC_* env vars and execs claude with the given model.
#
#   Based on patterns from free-claude-code (ClaudeCliAdapter) for reliable
#   tool use and model sync: gateway discovery + tier mapping + compact window.
#
#   CRITICAL: Claude Code uses 4 internal model tiers (Opus/Sonnet/Haiku/Subagent).
#   We must map ALL FOUR to the user's chosen model, or Claude will
#   try to call Anthropic model names that Ollama doesn't recognize.
#
#   ALSO CRITICAL: Ollama's Anthropic compat auto-adds /v1 internally.
#   Do NOT append /v1 to the base URL — pass the raw Ollama URL.

launch_claude() {
    local url="$1" model="$2"

    # Ollama's Anthropic compatibility auto-routes to /v1 when it sees
    # Anthropic headers. Pass the RAW Ollama URL, not .../v1.
    # See: https://docs.ollama.com/api/anthropic-compatibility
    local base="${url%/}"

    log "launching claude -> $base model=$model (native Anthropic compat)"
    log "Note: mapping Opus/Sonnet/Haiku/Subagent tiers all to $model"

    if is_dry; then
        echo "DRY: ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=$base ANTHROPIC_API_KEY= ANTHROPIC_DEFAULT_HAIKU_MODEL=$model ANTHROPIC_DEFAULT_SONNET_MODEL=$model ANTHROPIC_DEFAULT_OPUS_MODEL=$model CLAUDE_CODE_SUBAGENT_MODEL=$model CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 DISABLE_TELEMETRY=1 claude --model $model"
        return 0
    fi

    log "Tip: Claude Code agentic quality depends heavily on the model. Use strong tool-calling coders (qwen3*, deepseek-r1*, gemma4* large) fully GPU-resident on black. Weak or old taggers like qwen2.5 often emit malformed JSON/Workflow instead of clean turns."
    log "Tip: If you get 'model not found', ensure the model is pulled on black: ssh black 'ollama pull $model'"

    # CRITICAL: All four model tiers must be mapped to the local model.
    # Claude Code internally routes different tasks to:
    #   - Opus (primary conversation, complex reasoning)
    #   - Sonnet (main coding, subagents)
    #   - Haiku (fast auxiliary, summaries, titles)
    #   - Subagent (CLAUDE_CODE_SUBAGENT_MODEL for agent teams)
    # If any tier is unmapped, it falls back to Anthropic model names
    # which Ollama rejects with 404.
    #
    # Additional vars from free-claude-code (ClaudeCliAdapter.build_launcher_env):
    #   - ENABLE_GATEWAY_MODEL_DISCOVERY: lets claude query endpoint for models and sync
    #     capabilities (tools, etc) properly instead of assuming official names.
    #   - AUTO_COMPACT_WINDOW: larger window for long coding agent sessions.
    ANTHROPIC_AUTH_TOKEN=ollama \
    ANTHROPIC_BASE_URL="$base" \
    ANTHROPIC_API_KEY="" \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="$model" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="$model" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="$model" \
    CLAUDE_CODE_SUBAGENT_MODEL="$model" \
    CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 \
    DISABLE_TELEMETRY=1 \
    exec claude --model "$model" "${@:3}"
}
