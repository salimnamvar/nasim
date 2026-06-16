#!/usr/bin/env bash
# lib/nasim/probe.sh — reachability and doctor (pure adapter concern)

probe_url() {
    local url="$1"
    local to="${PROBE_TIMEOUT:-6}"
    local cto="${PROBE_CONNECT_TIMEOUT:-3}"
    curl -sf --max-time "$to" --connect-timeout "$cto" "$url/api/tags" >/dev/null
}

probe_and_show() {
    local url="$1"
    log "probing $url ..."
    if probe_url "$url"; then
        log "OK: endpoint reachable"
        # Best-effort model list to stderr (keeps stdout clean for url capture)
        curl -s --max-time 5 "$url/api/tags" | python3 -c '
import sys, json
try:
    d=json.load(sys.stdin)
    names=[m.get("name","?") for m in d.get("models",[])][:6]
    print("  models:", " ".join(names), file=sys.stderr)
except: print("  (could not parse model list)", file=sys.stderr)
' 2>/dev/null || true
        return 0
    else
        log "FAIL: $url not reachable"
        return 1
    fi
}

# Enhanced doctor (uses config, always shows black side via ssh when possible)
nasim_doctor() {
    local url="${NASIM_REMOTE_URL:-http://127.0.0.1:${DEFAULT_LOCAL_PORT}}"
    if [[ $# -gt 0 && "$1" == "--url" ]]; then url="$2"; fi

    log "nasim doctor (version ${NASIM_VERSION_OVERRIDE:-$NASIM_VERSION})"
    echo "  effective url: $url"
    echo "  black host:    $BLACK_HOST"

    if probe_and_show "$url"; then
        : # good for agents
    else
        if [[ -z "${NASIM_REMOTE_URL:-}" ]]; then
            log "No active local tunnel (or NASIM_REMOTE_URL) on the default port."
            log "Tip: run 'nasim select' or 'nasim tunnel ssh' first, or export NASIM_REMOTE_URL."
        fi
    fi

    # Always surface black-side reality (this is often the real signal)
    if have ssh; then
        echo "  black ollama ps (via ssh):"
        ssh -o ConnectTimeout="${SSH_CONNECT_TIMEOUT:-4}" "$BLACK_HOST" \
            'ollama ps 2>/dev/null || curl -s http://localhost:11434/api/ps | head -c 300' \
            2>/dev/null || echo "    (ssh to black for ps failed)"
    fi
}
