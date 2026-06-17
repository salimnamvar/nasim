#!/usr/bin/env bash
# lib/nasim/agents/claude.sh — Claude Code launcher (native Anthropic compat)
#
# launch_claude(url, model, [extra_args...]):
#   Sets ANTHROPIC_* env vars and execs claude with the given model.
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
    # Anthropic headers. Pass the RAW url, not .../v1.
    local base="${url%/}"

    log "launching claude -> $base model=$model (native Anthropic compat)"
    log "Note: mapping Opus/Sonnet/Haiku/Subagent tiers all to $model"

    if is_dry; then
        echo "DRY: ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_BASE_URL=$base ANTHROPIC_API_KEY= ANTHROPIC_DEFAULT_HAIKU_MODEL=$model ANTHROPIC_DEFAULT_SONNET_MODEL=$model ANTHROPIC_DEFAULT_OPUS_MODEL=$model CLAUDE_CODE_SUBAGENT_MODEL=$model CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 TERM=dumb claude --model $model"
        return 0
    fi

    log "Tip: For best tool use with claude-code + ollama use strong tool-calling models (deepseek-r1:*, qwen3*). Use 'nasim launch --access litellm --agent claude' if litellm is installed for extra normalization."
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
    # Additional vars known to help claude-code with local backends (discovery + large context for agent sessions).
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
    exec claude --model "$model" "${@:3}"
}
