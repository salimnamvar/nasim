#!/usr/bin/env bash
# lib/nasim/agents/claude.sh — Claude Code launcher (native Anthropic compat + fcc gateway)
#
# launch_claude(url, model, [extra_args...]):
#   Sets the FULL set of ANTHROPIC_* + CLAUDE_* env vars used by free-claude-code
#   (and its claude adapter) and execs the claude binary.
#
#   When NASIM_FCC_SRC_DIR (auto-detected for sibling checkout or explicit) is usable:
#     starts an isolated fcc proxy sidecar and points claude at the proxy
#     (richer model discovery, request translation, SSE, thinking support).
#
#   Direct path (ollama native): tier-maps all 4 internal claude tiers + sets both
#   BASE_URL and API_URL so claude works either way.

launch_claude() {
    local url="$1" model="$2"
    shift 2 || true

    local base="${url%/}"
    local target_base="$base"
    local target_api_url="${base%/}/v1"
    local using_fcc=0

    if ! is_dry && fcc_available 2>/dev/null; then
        log "fcc proxy available — starting isolated free-claude-code gateway for claude"
        local proxy_url
        # fcc_start_proxy returns the url on success (stdout) or falls back
        if proxy_url=$(fcc_start_proxy "$base" "$model"); then
            target_base="$proxy_url"
            target_api_url="${proxy_url%/}/v1"
            using_fcc=1
        else
            log "fcc proxy did not start; using direct ollama compat url"
        fi
    elif is_dry && fcc_available 2>/dev/null; then
        log "(dry) would attempt fcc proxy start for richer gateway"
    fi

    log "launching claude -> $target_base model=$model (using_fcc=$using_fcc)"

    # Ensure workspace exists for CLAUDE_WORKSPACE (used by fcc + claude for sessions/plans)
    local ws="${CLAUDE_WORKSPACE:-$HOME/.fcc/agent_workspace}"
    mkdir -p "$ws" 2>/dev/null || true

    if is_dry; then
        echo "DRY: ANTHROPIC_API_URL=$target_api_url ANTHROPIC_BASE_URL=$target_base ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY= ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS=81920 ANTHROPIC_DEFAULT_HAIKU_MODEL=$model ANTHROPIC_DEFAULT_SONNET_MODEL=$model ANTHROPIC_DEFAULT_OPUS_MODEL=$model CLAUDE_CODE_SUBAGENT_MODEL=$model CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 CLAUDE_CLI_BIN=${CLAUDE_CLI_BIN:-claude} CLAUDE_WORKSPACE=$ws TERM=dumb PYTHONIOENCODING=utf-8 DISABLE_TELEMETRY=1 claude --model $model"
        return 0
    fi

    log "Tip: For best tool use with claude-code + ollama use strong tool-calling models (deepseek-r1:*, qwen3*). fcc proxy provides full gateway translation when available."
    log "Tip: If 'model not found', ssh black 'ollama pull $model'"

    # All variables referenced by free-claude-code (from find.py + adapter + smoke + settings)
    # that affect the launched claude CLI client:
    #   ANTHROPIC_API_URL, ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, ANTHROPIC_API_KEY,
    #   ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS,
    #   + tier maps + CLAUDE_CODE_* discovery/compact/subagent,
    #   CLAUDE_CLI_BIN, CLAUDE_WORKSPACE
    #
    # Tier maps kept even under fcc (harmless; gateway discovery takes precedence).
    ANTHROPIC_API_URL="$target_api_url" \
    ANTHROPIC_BASE_URL="$target_base" \
    ANTHROPIC_AUTH_TOKEN=ollama \
    ANTHROPIC_API_KEY="" \
    ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS=81920 \
    ANTHROPIC_DEFAULT_HAIKU_MODEL="$model" \
    ANTHROPIC_DEFAULT_SONNET_MODEL="$model" \
    ANTHROPIC_DEFAULT_OPUS_MODEL="$model" \
    CLAUDE_CODE_SUBAGENT_MODEL="$model" \
    CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1 \
    CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000 \
    CLAUDE_CLI_BIN="${CLAUDE_CLI_BIN:-claude}" \
    CLAUDE_WORKSPACE="$ws" \
    TERM=dumb \
    PYTHONIOENCODING=utf-8 \
    DISABLE_TELEMETRY=1 \
    exec claude --model "$model" "$@"
}
