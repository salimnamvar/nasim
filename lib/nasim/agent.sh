#!/usr/bin/env bash
# lib/nasim/agent.sh — Agent launch orchestration + pluggable strategies

# Source all agent launchers (discovery for scalability)
for a in "$NASIM_LIB_DIR"/agents/*.sh; do
    [[ -f "$a" ]] && source "$a"
done

# Maps logical agent name to launch function
launch_agent() {
    local agent="$1" url="$2" model="$3"
    shift 3 || true   # remaining args passed to the agent

    case "$agent" in
        claude|code)      launch_claude "$url" "$model" "$@" ;;
        aider)            launch_aider  "$url" "$model" "$@" ;;
        opencode|open)    launch_opencode "$url" "$model" "$@" ;;
        terminal|shell)   launch_terminal "$url" "$model" ;;
        *)
            log "unknown agent '$agent' — falling back to terminal shell"
            launch_terminal "$url" "$model" ;;
    esac
}
