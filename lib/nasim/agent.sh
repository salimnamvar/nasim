#!/usr/bin/env bash
# lib/nasim/agent.sh — Agent launch orchestration + pluggable strategies
#
# launch_agent(agent, url, model, ...):
#   Strategy map. Each concrete launcher in agents/*.sh receives the effective remote url (from transport)
#   + the exact model tag the user chose, plus any extra args (e.g. -p "..." for claude one-shot).
#   Sourcing all *.sh at load time gives the "drop a new agent/*.sh" extensibility (AD-08).

# Source all agent launchers (discovery for scalability)
for a in "$NASIM_LIB_DIR"/agents/*.sh; do
    [[ -f "$a" ]] && source "$a"
done

# launch_agent(agent, url, model, ...):
#   Dispatch to the right launch_*. Remaining args flow through to the concrete exec.
launch_agent() {
    local agent="$1" url="$2" model="$3"
    shift 3 || true   # remaining args passed to the agent

    case "$agent" in
        claude|code)      launch_claude "$url" "$model" "$@" ;;
        grok)             launch_grok "$url" "$model" "$@" ;;
        aider)            launch_aider  "$url" "$model" "$@" ;;
        opencode|open)    launch_opencode "$url" "$model" "$@" ;;
        terminal|shell)   launch_terminal "$url" "$model" ;;
        *)
            log "unknown agent '$agent' — falling back to terminal shell"
            launch_terminal "$url" "$model" ;;
    esac
}
