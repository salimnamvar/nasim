#!/usr/bin/env bash
# lib/nasim/daemon.sh — Persistent tunnel daemon + lifecycle (Option A)
#
# nasim start  -> background tunnel, write active-url, env isolated
# nasim stop   -> kill tunnel, restore env, cleanup
# nasim status -> show daemon state + tunnel health
#
# The daemon persists across terminal sessions. All agent calls reuse the
# same tunnel until `nasim stop`. Env vars are backed up before modification
# and restored on stop.

NASIM_STATE_DIR="${HOME}/.local/share/nasim"
NASIM_ACTIVE_URL_FILE="$NASIM_STATE_DIR/active-url"
NASIM_DAEMON_PID_FILE="$NASIM_STATE_DIR/daemon.pid"

# _daemon_ensure_state_dir():
#   Ensure runtime state directory exists.
_daemon_ensure_state_dir() {
    mkdir -p "$NASIM_STATE_DIR"
}

# daemon_start([access]):
#   Start persistent background tunnel.
#   Access defaults to ssh-tunnel, but can be tailscale or litellm.
#   Writes active-url for all subsequent agent calls to reuse.
#   Saves env state before any modification (rollback guarantee).
#   Returns 0 on success, 1 on failure.
daemon_start() {
    local access="${1:-ssh-tunnel}"
    _daemon_ensure_state_dir

    # Check if already running
    if daemon_is_running; then
        log "daemon already running ($(daemon_url))"
        echo "Run 'nasim stop' first, or 'nasim status' for details."
        return 0
    fi

    # CRITICAL: Save env BEFORE we modify anything
    save_env_state

    log "starting nasim daemon (access=$access)..."

    local url
    if is_dry; then
        url="http://127.0.0.1:${DEFAULT_LOCAL_PORT}"
        log "(dry) would start daemon with url=$url"
    else
        url=$(setup_transport "$access")
    fi

    if [[ -z "$url" ]]; then
        log "ERROR: failed to establish transport"
        restore_env_state
        return 1
    fi

    # Write state files
    echo "$url" > "$NASIM_ACTIVE_URL_FILE"

    # For ssh tunnels, also save the PID for later cleanup
    if [[ "$access" == "ssh-tunnel" || "$access" == "ssh" ]]; then
        # Find the ssh process we just started
        local ssh_pid
        ssh_pid=$(pgrep -f "ssh.*${DEFAULT_LOCAL_PORT}.*${BLACK_HOST}" | head -1 || true)
        if [[ -n "$ssh_pid" ]]; then
            echo "$ssh_pid" > "$NASIM_DAEMON_PID_FILE"
        fi
    fi

    # Export for current shell and future subshells
    export NASIM_REMOTE_URL="$url"
    export NASIM_ACTIVE=1

    log "daemon active — url=$url"
    log "all 'nasim code', 'nasim claude', 'nasim aider' calls will reuse this tunnel"
    echo "Run 'nasim status' for health, 'nasim stop' to tear down + restore env."

    # Auto-detect project context if in a git repo
    if [[ -d ".git" ]]; then
        log "git repo detected — run 'nasim context --refresh' to index project"
    fi
}

# daemon_stop():
#   Tear down tunnel, restore original env vars, clean state files.
#   This is the SAFE EXIT path — your cloud Claude/Grok settings come back.
daemon_stop() {
    _daemon_ensure_state_dir

    if ! daemon_is_running; then
        log "no active daemon"
        # Still try to restore env in case of stale state
        restore_env_state
        return 0
    fi

    log "stopping nasim daemon..."

    # Kill tunnel process if we tracked it
    if [[ -f "$NASIM_DAEMON_PID_FILE" ]]; then
        local pid
        pid=$(cat "$NASIM_DAEMON_PID_FILE" 2>/dev/null || true)
        if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
            log "terminating tunnel PID $pid"
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
        rm -f "$NASIM_DAEMON_PID_FILE"
    fi

    # Also kill any lingering ssh processes for this host/port
    pkill -f "ssh.*${DEFAULT_LOCAL_PORT}.*${BLACK_HOST}" 2>/dev/null || true

    # CRITICAL: Restore env vars before removing state
    restore_env_state

    # Clean state files
    rm -f "$NASIM_ACTIVE_URL_FILE"

    log "daemon stopped — env restored, cloud agents back to normal"
}

# daemon_status():
#   Show current daemon state: running/stopped, url, health, model list.
daemon_status() {
    _daemon_ensure_state_dir

    echo "nasim daemon status"
    echo "==================="

    if ! daemon_is_running; then
        echo "  state: STOPPED"
        echo "  tip: run 'nasim start' to connect to black"
        return 0
    fi

    local url
    url=$(daemon_url)
    echo "  state: RUNNING"
    echo "  url:   $url"
    echo "  host:  $BLACK_HOST"
    echo "  model: ${NASIM_MODEL:-$DEFAULT_MODEL}"

    # Health check
    echo ""
    echo "  health check:"
    if probe_and_show "$url"; then
        echo "  + endpoint reachable"
    else
        echo "  - endpoint NOT reachable (tunnel may be stale)"
    fi

    # Model list
    echo ""
    list_models_on_black

    # Context status
    echo ""
    if context_is_active; then
        echo "  project context: ACTIVE ($(context_file))"
    else
        echo "  project context: none (run 'nasim context --refresh' in a git repo)"
    fi

    # KB status
    echo ""
    if kb_is_indexed; then
        echo "  knowledge base:  indexed ($(kb_index_path))"
    else
        echo "  knowledge base:  not indexed"
    fi
}

# daemon_is_running():
#   True if active-url file exists and points to a reachable endpoint.
#   Also checks if the tunnel process is alive (for ssh).
daemon_is_running() {
    if [[ ! -f "$NASIM_ACTIVE_URL_FILE" ]]; then
        return 1
    fi
    local url
    url=$(cat "$NASIM_ACTIVE_URL_FILE" 2>/dev/null || true)
    [[ -n "$url" ]] || return 1

    # For ssh, also verify the process is alive
    if [[ -f "$NASIM_DAEMON_PID_FILE" ]]; then
        local pid
        pid=$(cat "$NASIM_DAEMON_PID_FILE" 2>/dev/null || true)
        if [[ -n "$pid" ]] && ! kill -0 "$pid" 2>/dev/null; then
            # PID dead but file exists — stale state
            return 1
        fi
    fi

    # Quick probe (optional — don't fail if probe times out, file existence is enough)
    return 0
}

# daemon_url():
#   Return the current active URL, or empty if not running.
daemon_url() {
    if [[ -f "$NASIM_ACTIVE_URL_FILE" ]]; then
        cat "$NASIM_ACTIVE_URL_FILE" 2>/dev/null || true
    fi
}

# daemon_ensure_running():
#   If daemon not running, auto-start it with default access.
#   Used by `nasim code` and other commands so user doesn't manually start.
daemon_ensure_running() {
    if ! daemon_is_running; then
        log "no active daemon — auto-starting..."
        daemon_start "ssh-tunnel"
    fi
}
