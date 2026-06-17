#!/usr/bin/env bash
# lib/nasim/transports/tailscale.sh — Tailscale transport adapter (graceful degrade strategy)
#
# setup_tailscale():
#   If tailscale present and `tailscale status` ok, try MagicDNS "black:11434" then probe.
#   If not, ssh to black to discover its tailscale IP and try that.
#   Returns 1 on any failure so transport.sh falls back to ssh-tunnel.

setup_tailscale() {
    if is_dry; then
        echo "http://black:11434"
        return 0
    fi
    if ! have tailscale || ! tailscale status >/dev/null 2>&1; then
        log "Tailscale not running or not installed on this machine. Falling back or choose another access."
        return 1
    fi

    local url="http://black:11434"
    if probe_and_show "$url"; then
        echo "$url"
        return 0
    fi

    # Fallback: ask black its ts ip via ssh (we know ssh works)
    if have ssh; then
        local tsip
        tsip=$(ssh -o ConnectTimeout=5 "$BLACK_HOST" 'tailscale ip -4 2>/dev/null | head -1' || true)
        if [[ -n "$tsip" ]]; then
            url="http://${tsip}:11434"
            if probe_and_show "$url"; then
                echo "$url"
                return 0
            fi
        fi
    fi

    log "Tailscale present but could not reach black:11434. Is black in the same tailnet and ollama listening?"
    return 1
}
