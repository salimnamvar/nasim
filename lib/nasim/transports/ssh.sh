#!/usr/bin/env bash
# lib/nasim/transports/ssh.sh — SSH tunnel transport adapter (strategy)

setup_ssh_tunnel() {
    if is_dry; then
        echo "http://127.0.0.1:${DEFAULT_LOCAL_PORT}"
        return 0
    fi

    local lport
    lport=$(free_port "$DEFAULT_LOCAL_PORT")
    local pidfile="/tmp/nasim-ssh-tunnel-$$.pid"

    log "starting SSH tunnel: $lport -> $BLACK_HOST:11434"

    ssh -o ConnectTimeout="${SSH_CONNECT_TIMEOUT:-8}" \
        -o ServerAliveInterval="${SSH_SERVER_ALIVE_INTERVAL:-20}" \
        -o ServerAliveCountMax=3 \
        -o ExitOnForwardFailure=yes -f -N -L "${lport}:localhost:11434" "$BLACK_HOST"

    sleep 0.6
    pgrep -f "ssh.*${lport}.*${BLACK_HOST}" | head -1 > "$pidfile" || true

    local url="http://127.0.0.1:${lport}"

    if ! probe_and_show "$url"; then
        cleanup_tunnel "$pidfile"
        die "SSH tunnel came up but probe failed. Is ollama running on black?"
    fi

    log "SSH forward active (pidfile $pidfile). It will stay until killed (see 'nasim tunnel status' or pkill)."
    echo "$url"
}
