#!/usr/bin/env bash
# lib/nasim/probe.sh — reachability and doctor (pure adapter concern)
#
# probe_url / probe_and_show / list_models_on_black / nasim_doctor / nasim_models / model_exists_on_black:
#   The "models are shown + verify before launch" layer (P02 invariant).
#   list_models_on_black + nasim_models use direct ssh to black (no tunnel) so discovery always works.
#   probe_and_show used to swallow output with 2>/dev/null on the python print — fixed.
#   doctor and pre-launch in orchestration always call the ssh list.

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
        # Best-effort model list — do NOT swallow the print we want to show the user.
        # 2>/dev/null only for python errors; the "  models:" goes to stderr on purpose.
        if curl -sf --max-time 5 "$url/api/tags" -o /tmp/nasim-tags.$$.json 2>/dev/null; then
            python3 -c '
import sys, json
try:
    with open("/tmp/nasim-tags.$$.json") as f: d=json.load(f)
    names=[m.get("name","?") for m in d.get("models",[])][:8]
    print("  models:", " ".join(names), file=sys.stderr)
except Exception: print("  (could not parse model list)", file=sys.stderr)
' 2>/dev/null || echo "  (model list parse error)" >&2
            rm -f /tmp/nasim-tags.$$.json
        else
            echo "  (could not fetch /api/tags for model list)" >&2
        fi
        return 0
    else
        log "FAIL: $url not reachable"
        return 1
    fi
}

# list_models_on_black():
#   SSH to BLACK_HOST, run curl localhost:11434/api/tags, pretty print with sizes/quants.
#   This is the single source of truth for "what tags actually exist" and is used by doctor, pre-launch warn, and nasim models (no --url).
#   Never depends on a local tunnel.

# List models directly from black via SSH (no tunnel required). Always works for discovery.
list_models_on_black() {
    if ! have ssh; then
        echo "  (ssh not available; cannot list black models)"
        return 1
    fi
    echo "  models available on black (via ssh to ${BLACK_HOST}:11434):"
    ssh -o ConnectTimeout="${SSH_CONNECT_TIMEOUT:-5}" "$BLACK_HOST" '
        curl -s --max-time 8 http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    for m in d.get(\"models\", []):
        name = m.get(\"name\", \"?\")
        psize = m.get(\"details\", {}).get(\"parameter_size\", \"?\")
        q = m.get(\"details\", {}).get(\"quantization_level\", \"?\")
        print(\"    - \" + name + \" (\" + psize + \", \" + q + \")\")
except Exception as e:
    print(\"    (parse error: \" + str(e) + \")\")
" 2>/dev/null || echo "    (failed to fetch/parse tags on black)"
    ' 2>/dev/null || echo "    (ssh to black for /api/tags failed)"
}

# nasim_doctor([--url U]):
#   Prints effective url, black host, probe result + models at that url (if ollama style),
#   then always the full authoritative ssh black inventory + black `ollama ps`.
#   The key "models not shown" fix surface.
nasim_doctor() {
    local url="${NASIM_REMOTE_URL:-http://127.0.0.1:${DEFAULT_LOCAL_PORT}}"
    if [[ $# -gt 0 && "$1" == "--url" ]]; then url="$2"; fi

    log "nasim doctor (version ${NASIM_VERSION_OVERRIDE:-$NASIM_VERSION})"
    echo "  effective url: $url"
    echo "  black host:    $BLACK_HOST"

    if probe_and_show "$url"; then
        : # good for agents (also printed models if reachable)
    else
        if [[ -z "${NASIM_REMOTE_URL:-}" ]]; then
            log "No active local tunnel (or NASIM_REMOTE_URL) on the default port."
            log "Tip: run 'nasim select' or 'nasim tunnel ssh' first, or export NASIM_REMOTE_URL."
        fi
    fi

    # Always surface authoritative black model inventory (this solves "models are not shown")
    list_models_on_black

    # black-side runtime
    if have ssh; then
        echo "  black ollama ps (via ssh):"
        ssh -o ConnectTimeout="${SSH_CONNECT_TIMEOUT:-4}" "$BLACK_HOST" \
            'ollama ps 2>/dev/null || curl -s http://localhost:11434/api/ps | head -c 300' \
            2>/dev/null || echo "    (ssh to black for ps failed)"
    fi
}

# nasim_models([--url U]):
#   First-class command (nasim models). When --url given uses that (for a forwarded endpoint);
#   otherwise delegates to list_models_on_black (ssh, always works).
nasim_models() {
    local url=""
    if [[ $# -gt 0 && "$1" == "--url" ]]; then
        url="$2"
        echo "Models via provided url $url :"
        curl -s --max-time 6 "$url/api/tags" | python3 -c '
import sys, json
try:
    d=json.load(sys.stdin)
    for m in d.get("models",[]):
        print("  - " + m.get("name","?"))
except: print("  (error)")
' 2>/dev/null || echo "  (failed)"
    else
        list_models_on_black
    fi
}

# model_exists_on_black(want):
#   Fast ssh query to black for exact tag presence in /api/tags names.
#   Used in choose_and_launch to emit pre-launch WARNING so user sees "that tag is not there".
#   Returns 0 if present.
model_exists_on_black() {
    local want="$1"
    # Fast path: ask black directly over ssh (no tunnel)
    if have ssh; then
        ssh -o ConnectTimeout=4 "$BLACK_HOST" "
            curl -s --max-time 5 http://localhost:11434/api/tags 2>/dev/null | python3 -c '
import sys, json
d=json.load(sys.stdin)
names=[m.get(\"name\",\"\") for m in d.get(\"models\",[])]
print(\"yes\" if \"${want}\" in names else \"no\")
' 2>/dev/null
        " 2>/dev/null | grep -q yes && return 0
    fi
    return 1
}
