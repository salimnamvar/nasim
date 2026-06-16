#!/usr/bin/env bash
# lib/nasim/agents/aider.sh

launch_aider() {
    local url="$1" model="$2"
    local m="ollama/${model}"
    log "launching aider -> $url model=$m"
    if is_dry; then
        echo "DRY: OLLAMA_API_BASE=$url aider --model $m"
        return 0
    fi
    export OLLAMA_API_BASE="$url"
    exec aider --model "$m" "${@:3}"
}
