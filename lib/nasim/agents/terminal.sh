#!/usr/bin/env bash
# lib/nasim/agents/terminal.sh — drop into branded shell so user can run any agent manually
#
# launch_terminal(url, model):
#   Exports the full set of vars (ANTHROPIC_*, OLLAMA_*, NASIM_*) + branded PS1, then execs interactive $SHELL.
#   This is the escape hatch / "manual any agent or raw curl" mode. Also the path used by --self-audit for interactive work.

launch_terminal() {
    local url="$1" model="$2"
    log "dropping into configured shell (all envs set). Run your agents manually."
    if is_dry; then
        echo "DRY: export ANTHROPIC_BASE_URL=$url ANTHROPIC_DEFAULT_*=$model CLAUDE_CODE_*=... OLLAMA_API_BASE=$url NASIM_REMOTE_URL=$url"
        echo "DRY: PS1=\"nasim[black:${model}] $ \" ; exec \$SHELL -i"
        return 0
    fi
    export ANTHROPIC_AUTH_TOKEN=ollama
    # Raw base (no /v1) for claude-code anthropic compat (ollama auto-routes); see claude.sh
    export ANTHROPIC_BASE_URL="${url%/}"
    export ANTHROPIC_API_KEY=""
    # Full tier mapping + FCC-derived discovery flags so that manual `claude` (or claude --model)
    # inside this shell gets correct tool-calling sync with the remote ollama model.
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="$model"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="$model"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="$model"
    export CLAUDE_CODE_SUBAGENT_MODEL="$model"
    export CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1
    export CLAUDE_CODE_AUTO_COMPACT_WINDOW=190000
    export DISABLE_TELEMETRY=1
    export OLLAMA_API_BASE="$url"
    export NASIM_REMOTE_URL="$url"
    export NASIM_MODEL="$model"
    export NASIM_ACTIVE=1
    export PS1="nasim[black:${model}] \$ "

    echo "nasim: remote env active in this shell (branded prompt)."
    echo "  Running 'claude', 'aider', etc. here will use Ollama models on black."
    echo "  Type 'exit' to leave and return to normal shells (default real APIs)."
    exec "${SHELL:-/bin/bash}" -i
}
