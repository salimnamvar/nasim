#!/usr/bin/env bash
# lib/nasim/agents/terminal.sh — drop into branded shell so user can run any agent manually

launch_terminal() {
    local url="$1" model="$2"
    log "dropping into configured shell (all envs set). Run your agents manually."
    if is_dry; then
        echo "DRY: export ANTHROPIC_BASE_URL=$url OLLAMA_API_BASE=$url NASIM_REMOTE_URL=$url"
        echo "DRY: PS1=\"nasim[black:${model}] $ \" ; exec \$SHELL -i"
        return 0
    fi
    export ANTHROPIC_AUTH_TOKEN=ollama
    export ANTHROPIC_BASE_URL="$url"
    export ANTHROPIC_API_KEY=""
    export OLLAMA_API_BASE="$url"
    export NASIM_REMOTE_URL="$url"
    export NASIM_MODEL="$model"
    export PS1="nasim[black:${model}] \$ "
    exec "${SHELL:-/bin/bash}" -i
}
