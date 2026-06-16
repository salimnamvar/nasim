#!/usr/bin/env bash
# lib/nasim/transport.sh — Transport orchestration (Service-like layer)
#
# setup_transport(access [, model]):
#   Strategy dispatcher. ssh-tunnel and tailscale are direct ollama forwards.
#   litellm starts an inner ssh then a litellm proxy on top (with dynamic model registration).
#   All strategies return the http://127.0.0.1:port (or host:port for ts) that the agent launchers should point at.
#   free_port + cleanup_tunnel are shared.

# Source all concrete transport strategies (pluggable / scalable)
for t in "$NASIM_LIB_DIR"/transports/*.sh; do
    [[ -f "$t" ]] && source "$t"
done

# free_port([base]):
#   Find next free TCP >= base by checking ss/netstat. Used by ssh tunnel to avoid "address in use".
#   Dies if no port in +100 range.
free_port() {
    local base="${1:-$DEFAULT_LOCAL_PORT}"
    local p=$base
    while ss -ltn 2>/dev/null | grep -q ":$p " || netstat -ltn 2>/dev/null | grep -q ":$p "; do
        p=$((p+1))
        [[ $p -gt $((base+100)) ]] && die "no free port found near $base"
    done
    echo "$p"
}

cleanup_tunnel() {
    local pidfile="${1:-}"
    if [[ -n "$pidfile" && -f "$pidfile" ]]; then
        local pid
        pid=$(cat "$pidfile" 2>/dev/null || true)
        if [[ -n "$pid" ]]; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
        rm -f "$pidfile"
    fi
}

# setup_transport(access [, model]):
#   Returns the URL the chosen agent should talk to.
#   Side effects: may start ssh -L (background), litellm bg process + its config file + pidfile.
#   For litellm the inner ssh is started first, then proxy; the returned url is the litellm port.
setup_transport() {
    local access="${1:-ssh-tunnel}"
    local model_for_litellm="${2:-}"

    case "$access" in
        ssh-tunnel|ssh)
            setup_ssh_tunnel ;;
        tailscale|ts)
            setup_tailscale || { log "Tailscale unavailable — trying ssh-tunnel"; setup_ssh_tunnel; } ;;
        litellm|llm)
            local inner
            inner=$(setup_ssh_tunnel)
            setup_litellm "$inner" "$model_for_litellm" ;;
        *)
            die "unknown access: $access (ssh-tunnel | tailscale | litellm)" ;;
    esac
}
