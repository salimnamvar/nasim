#!/usr/bin/env bash
# lib/nasim/orchestration.sh — core select/launch coordination (main "service" layer)

choose_and_launch() {
    local access="${1:-ssh-tunnel}"
    local agent="${2:-claude}"
    local model="${3:-$DEFAULT_MODEL}"
    local url

    if is_dry; then
        url="http://127.0.0.1:${DEFAULT_LOCAL_PORT}"
        log "(dry) would setup access=$access (no real tunnel)"
    else
        url=$(setup_transport "$access")
    fi

    # Final sanity (defensive but non-fatal if setup already proved it)
    if ! is_dry && ! probe_url "$url"; then
        log "WARNING: final probe failed for $url (proceeding anyway — setup had succeeded)"
    fi

    # Always surface the models at the chosen endpoint right before handing to the agent.
    # This is a major part of fixing "models are not shown" under select/launch.
    if ! is_dry; then
        log "models at $url (for $agent):"
        curl -s --max-time 5 "$url/api/tags" | python3 -c '
import sys, json
try:
    d=json.load(sys.stdin)
    names=[m.get("name","?") for m in d.get("models",[])][:5]
    print("  " + " ".join(names), file=sys.stderr)
except: print("  (list failed)", file=sys.stderr)
' 2>/dev/null || true
        # Also the authoritative black list (no tunnel needed)
        nasim_models 2>/dev/null || true

        # Warn (but do not hard fail) if the requested model is unknown on black.
        # Covers the original "qwen3-coder:14b does not exist" class of "models not working with the clis".
        if ! model_exists_on_black "$model" 2>/dev/null; then
            log "WARNING: '$model' not found in black inventory (nasim models). The agent may fail or trigger a slow pull. Choose an exact tag from the list above."
        fi
    fi

    launch_agent "$agent" "$url" "$model" "${@:4}"
}

# Legacy thin paths (still supported)
legacy_claude() {
    local url="${NASIM_REMOTE_URL:-http://127.0.0.1:${DEFAULT_LOCAL_PORT}}"
    local model="${NASIM_MODEL:-$DEFAULT_MODEL}"
    if [[ -z "${NASIM_REMOTE_URL:-}" ]]; then
        log "no NASIM_REMOTE_URL; starting ad-hoc ssh tunnel for legacy claude..."
        url=$(setup_ssh_tunnel)
    fi
    launch_claude "$url" "$model" "$@"
}

legacy_aider() {
    local url="${NASIM_REMOTE_URL:-http://127.0.0.1:${DEFAULT_LOCAL_PORT}}"
    local model="${NASIM_MODEL:-ollama/${DEFAULT_MODEL}}"
    if [[ -z "${NASIM_REMOTE_URL:-}" ]]; then
        log "no NASIM_REMOTE_URL; starting ad-hoc ssh tunnel for legacy aider..."
        url=$(setup_ssh_tunnel)
    fi
    launch_aider "$url" "$model" "$@"
}
