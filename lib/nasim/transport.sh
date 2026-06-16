#!/usr/bin/env bash
# lib/nasim/transport.sh — Transport orchestration (Service-like layer)

# Source all concrete transport strategies (pluggable / scalable)
for t in "$NASIM_LIB_DIR"/transports/*.sh; do
    [[ -f "$t" ]] && source "$t"
done

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

# Main entry used by orchestration. Returns the effective URL on success.
setup_transport() {
    local access="${1:-ssh-tunnel}"

    case "$access" in
        ssh-tunnel|ssh)
            setup_ssh_tunnel ;;
        tailscale|ts)
            setup_tailscale || { log "Tailscale unavailable — trying ssh-tunnel"; setup_ssh_tunnel; } ;;
        litellm|llm)
            local inner
            inner=$(setup_ssh_tunnel)
            setup_litellm "$inner" ;;
        *)
            die "unknown access: $access (ssh-tunnel | tailscale | litellm)" ;;
    esac
}
