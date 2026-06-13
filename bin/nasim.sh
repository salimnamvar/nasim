#!/usr/bin/env bash
# Source this file — do not execute directly.
#
# Usage:
#   nasim start    — open SSH tunnel to bridge, redirect Claude Code to Ollama
#   nasim stop     — kill tunnel, restore Claude Code to Anthropic cloud
#   nasim status   — show current state and bridge health
#   nasim models   — list Ollama models available through the bridge

nasim() {
  local _STATE_FILE="$HOME/.nasim_state"
  local _PID_FILE="$HOME/.nasim_tunnel.pid"
  local _LOCAL_PORT="18080"
  local _REMOTE_HOST="black"
  local _REMOTE_PORT="8080"
  local _BASE_URL="http://localhost:${_LOCAL_PORT}"

  _nasim_kill_tunnel() {
    if [ -f "$_PID_FILE" ]; then
      local pid
      pid=$(cat "$_PID_FILE")
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
      fi
      rm -f "$_PID_FILE"
    fi
    # Fallback: kill any lingering tunnel on this port
    pkill -f "ssh.*-L ${_LOCAL_PORT}:127\.0\.0\.1:${_REMOTE_PORT}" 2>/dev/null || true
  }

  _nasim_start_tunnel() {
    _nasim_kill_tunnel
    ssh -f -N -o BatchMode=yes \
        -L "${_LOCAL_PORT}:127.0.0.1:${_REMOTE_PORT}" \
        "$_REMOTE_HOST" 2>/dev/null
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
      echo "ERROR: SSH tunnel to ${_REMOTE_HOST} failed (exit $exit_code)" >&2
      return 1
    fi
    sleep 0.4  # give tunnel time to bind
    # Record PID for clean shutdown
    pgrep -n -f "ssh.*-L ${_LOCAL_PORT}:127\.0\.0\.1:${_REMOTE_PORT}" > "$_PID_FILE" 2>/dev/null || true
    return 0
  }

  local _CLAUDE_JSON="$HOME/.claude.json"
  local _INJECTED_FILE="$HOME/.nasim_injected_models"

  _nasim_health() {
    curl -sf --connect-timeout 3 "${_BASE_URL}/health" 2>/dev/null
  }

  # Inject Ollama models from the bridge into Claude Code's model picker cache.
  _nasim_inject_models() {
    local models_json
    models_json=$(curl -sf --connect-timeout 3 "${_BASE_URL}/v1/models" 2>/dev/null)
    [ -z "$models_json" ] && return

    python3 - "$_CLAUDE_JSON" "$_INJECTED_FILE" "$models_json" << 'PYEOF'
import sys, json

claude_json_path, injected_path, models_json_str = sys.argv[1], sys.argv[2], sys.argv[3]

try:
    with open(claude_json_path) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)

try:
    bridge_models = json.loads(models_json_str).get("data", [])
except Exception:
    sys.exit(0)

cache = data.get("additionalModelOptionsCache", [])
existing_values = {e.get("value") for e in cache}
injected = []

for m in bridge_models:
    mid = m.get("id", "")
    if not mid or mid in existing_values:
        continue
    parts = mid.split(":", 1)
    name  = parts[0].replace("-", " ").title()
    tag   = parts[1] if len(parts) > 1 else ""
    label = f"{name} {tag}".strip() if tag else name
    desc  = f"{mid} · Local Ollama (black) · nasim"
    cache.append({"value": mid, "label": label, "description": desc})
    injected.append(mid)

data["additionalModelOptionsCache"] = cache

with open(claude_json_path, "w") as f:
    json.dump(data, f, indent=2)

with open(injected_path, "w") as f:
    json.dump(injected, f)
PYEOF
  }

  # Remove previously injected Ollama models from Claude Code's model picker cache.
  _nasim_eject_models() {
    [ ! -f "$_INJECTED_FILE" ] && return

    python3 - "$_CLAUDE_JSON" "$_INJECTED_FILE" << 'PYEOF'
import sys, json

claude_json_path, injected_path = sys.argv[1], sys.argv[2]

try:
    with open(claude_json_path) as f:
        data = json.load(f)
    with open(injected_path) as f:
        injected = set(json.load(f))
except Exception:
    sys.exit(0)

cache = [e for e in data.get("additionalModelOptionsCache", [])
         if e.get("value") not in injected]
data["additionalModelOptionsCache"] = cache

with open(claude_json_path, "w") as f:
    json.dump(data, f, indent=2)
PYEOF
    rm -f "$_INJECTED_FILE"
  }

  case "$1" in
    start)
      echo "Starting nasim tunnel → ${_REMOTE_HOST}:${_REMOTE_PORT} ..."
      if ! _nasim_start_tunnel; then
        return 1
      fi

      export ANTHROPIC_BASE_URL="$_BASE_URL"
      export ANTHROPIC_AUTH_TOKEN="nasim"
      export CLAUDE_CODE_MAX_OUTPUT_TOKENS="128000"
      export CLAUDE_CODE_DISABLE_THINKING="1"
      echo "ollama" > "$_STATE_FILE"

      local health_json
      health_json=$(_nasim_health)
      if echo "$health_json" | grep -q '"status":"ok"'; then
        local models
        models=$(echo "$health_json" | python3 -c \
          "import sys,json; d=json.load(sys.stdin); print(', '.join(d.get('available_models',[])))" \
          2>/dev/null || echo "unknown")
        _nasim_inject_models
        echo "nasim STARTED — Claude Code → Ollama via bridge"
        echo "  Bridge : ${_BASE_URL}"
        echo "  Models : ${models}"
        echo "  Tip    : use /model inside Claude Code to switch models"
      else
        echo "WARNING: tunnel up but bridge health check failed" >&2
        echo "  Response: ${health_json:-<empty>}" >&2
      fi
      ;;

    stop)
      _nasim_kill_tunnel
      _nasim_eject_models
      unset ANTHROPIC_BASE_URL
      unset ANTHROPIC_AUTH_TOKEN
      unset CLAUDE_CODE_MAX_OUTPUT_TOKENS
      unset CLAUDE_CODE_DISABLE_THINKING
      echo "anthropic" > "$_STATE_FILE"
      echo "nasim STOPPED — Claude Code → Anthropic cloud"
      ;;

    status)
      local state
      state=$(cat "$_STATE_FILE" 2>/dev/null || echo "anthropic")
      echo "Backend : $state"
      echo "Base URL: ${ANTHROPIC_BASE_URL:-(not set)}"

      if [ "$state" = "ollama" ]; then
        # Check tunnel process
        local tunnel_alive="no"
        if [ -f "$_PID_FILE" ]; then
          local pid
          pid=$(cat "$_PID_FILE")
          kill -0 "$pid" 2>/dev/null && tunnel_alive="yes (PID $pid)"
        fi
        echo "Tunnel  : $tunnel_alive"

        local health_json
        health_json=$(_nasim_health)
        if echo "$health_json" | grep -q '"status"'; then
          local bstatus
          bstatus=$(echo "$health_json" | python3 -c \
            "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'))" 2>/dev/null)
          echo "Bridge  : $bstatus"
        else
          echo "Bridge  : unreachable"
        fi
      fi
      ;;

    models)
      local health_json
      health_json=$(_nasim_health)
      if echo "$health_json" | grep -q '"available_models"'; then
        echo "Ollama models (via bridge):"
        echo "$health_json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
default = d.get('default_model', '')
fast    = d.get('fast_model', '')
for m in d.get('available_models', []):
    tags = []
    if m == default: tags.append('default')
    if m == fast:    tags.append('fast')
    suffix = '  [' + ', '.join(tags) + ']' if tags else ''
    print(f'  {m}{suffix}')
"
      else
        echo "Bridge not reachable — run: nasim start"
      fi
      ;;

    *)
      echo "Usage: nasim {start|stop|status|models}"
      ;;
  esac
}
