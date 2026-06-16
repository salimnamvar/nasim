#!/usr/bin/env bash
# lib/nasim/agents/opencode.sh — OpenCode (prefers OpenAI compat base for broadest support)

launch_opencode() {
    local url="$1" model="$2"
    log "launching opencode -> $url model=$model (OpenAI compat; prefers /v1 + ollama launch helper if present)"
    if is_dry; then
        echo "DRY: OPENAI_BASE_URL=${url}/v1 OPENAI_API_KEY=ollama opencode --model $model (or: ollama launch opencode --model $model)"
        return 0
    fi
    # 2026 reality (from search): ollama launch opencode is the blessed one-command path on hosts with ollama.
    # For pure remote forward we set OpenAI-compat (many opencode builds use /v1). Try several surfaces.
    # We do not exec the ollama launch here (it would ignore our forwarded url); we set the envs the binary respects.
    export OPENAI_BASE_URL="${url%/}/v1"
    export OPENAI_API_KEY="ollama"
    # Also common for some builds
    export OLLAMA_API_BASE="$url"
    # Try explicit model flag, then fallback without (config-driven) or direct binary name
    exec opencode --model "$model" "${@:3}" 2>/dev/null || \
    exec opencode "${@:3}" || \
    exec opencode --provider ollama --model "$model" "${@:3}" 2>/dev/null || true
    # If none of the execs replaced the process, we fall through (rare); the caller will have seen logs.
}
