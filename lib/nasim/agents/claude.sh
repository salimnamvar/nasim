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

    # Prefer an isolated free-claude-code proxy in front when available.
    # This gives claude-code the gateway model ids ("anthropic/ollama/..."),
    # correct tool streaming, thinking blocks (for deepseek-r1), and full
    # request shaping that direct ollama anthropic compat often lacks.
    # The fcc module (if sourced) starts a temp proxy pointing at the tunnel.
    local base="$url"
    local use_model="$model"
    if type fcc_start_proxy >/dev/null 2>&1; then
        local proxy
        proxy=$(fcc_start_proxy "$url" "$model" 2>/dev/null || true)
        if [[ -n "$proxy" && "$proxy" != "$url" ]]; then
            base="${proxy%/}"
            # Use the gateway-encoded form so claude discovers it via /v1/models
            # and treats it as a full-featured non-anthropic backend for tools.
            use_model="anthropic/ollama/${model#ollama/}"
            log "using fcc proxy at $base for claude (model advertised as $use_model)"
        fi
    fi

    # Ollama's Anthropic compatibility auto-routes to /v1 when it sees
    # Anthropic headers. Pass the RAW Ollama URL (or the fcc proxy root), not .../v1.
    base="${base%/}"

    via="direct"
    [[ "$base" != "$url" ]] && via="fcc proxy"
    log "launching claude -> $base model=$use_model (native Anthropic compat via $via)"
    log "Note: mapping Opus/Sonnet/Haiku/Subagent tiers all to $model"

    if is_dry; then
        echo "DRY: ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=$base ANTHROPIC_API_KEY= ANTHROPIC_DEFAULT_HAIKU_MODEL=$model ANTHROPIC_DEFAULT_SONNET_MODEL=$model ANTHROPIC_DEFAULT_OPUS_MODEL=$model CLAUDE_CODE_SUBAGENT_MODEL=$model CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 TERM=dumb fcc_proxy=${base} claude --model $use_model"
        return 0
    fi

    log "Tip: Using fcc proxy (or direct) + deepseek-r1 etc for tool use. Gateway discovery + tier mapping + thinking support from free-claude-code patterns."
    log "Tip: If 'model not found', ssh black 'ollama pull $model'"

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
    TERM=dumb \
    PYTHONIOENCODING=utf-8 \
    DISABLE_TELEMETRY=1 \
    exec claude --model "$use_model" "${@:3}"
}
