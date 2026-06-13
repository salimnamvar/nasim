#!/usr/bin/env bash
# Source this file — do not execute directly.
#
# nasim — toggle Claude Code between Anthropic cloud and a local Ollama backend
#         running on the `black` machine, reached over an SSH tunnel to the
#         Nasim Bridge (Anthropic Messages API <-> Ollama translator).
#
# Usage:
#   nasim start    — open SSH tunnel, point Claude Code at the bridge, inject
#                    Ollama models into the /model picker, select the default.
#   nasim stop     — kill tunnel, restore Claude Code to Anthropic cloud,
#                    eject every injected model, restore the original /model.
#   nasim status   — show backend, tunnel, bridge health, active model.
#   nasim models   — list Ollama models available through the bridge.
#
# Rollback guarantee: `nasim stop` returns the machine to the exact Claude Code
# defaults it had before `nasim start` — no tunnel, no env redirect, no Ollama
# models in the picker, and the original selected model restored. The only
# files touched are surgically reverted; session history in ~/.claude.json is
# never rewritten wholesale.

nasim() {
  # ── configuration ────────────────────────────────────────────────────────
  local _STATE_FILE="$HOME/.nasim_state"
  local _PID_FILE="$HOME/.nasim_tunnel.pid"
  local _SAVED_MODEL_FILE="$HOME/.nasim_saved_model"
  local _LOCAL_PORT="${NASIM_LOCAL_PORT:-18080}"
  local _REMOTE_HOST="${NASIM_REMOTE_HOST:-black}"
  local _REMOTE_PORT="${NASIM_REMOTE_PORT:-8080}"
  local _BASE_URL="http://localhost:${_LOCAL_PORT}"
  local _CLAUDE_JSON="$HOME/.claude.json"
  local _SETTINGS_JSON="$HOME/.claude/settings.json"
  local _NASIM_MARKER="_nasim"   # sentinel field stamped on injected entries

  # ── tunnel helpers ─────────────────────────────────────────────────────────
  _nasim_kill_tunnel() {
    if [ -f "$_PID_FILE" ]; then
      local pid
      pid=$(cat "$_PID_FILE")
      if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
      fi
      rm -f "$_PID_FILE"
    fi
    # Fallback: reap any lingering tunnel bound to this exact forward.
    pkill -f "ssh.*-L ${_LOCAL_PORT}:127\.0\.0\.1:${_REMOTE_PORT}" 2>/dev/null || true
  }

  _nasim_start_tunnel() {
    _nasim_kill_tunnel
    ssh -f -N -o BatchMode=yes -o ConnectTimeout=8 \
        -L "${_LOCAL_PORT}:127.0.0.1:${_REMOTE_PORT}" \
        "$_REMOTE_HOST" 2>/dev/null
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
      echo "ERROR: SSH tunnel to ${_REMOTE_HOST} failed (exit $exit_code)" >&2
      echo "       Ensure 'ssh ${_REMOTE_HOST}' works without a passphrase." >&2
      return 1
    fi
    sleep 0.4  # give the forward time to bind
    pgrep -n -f "ssh.*-L ${_LOCAL_PORT}:127\.0\.0\.1:${_REMOTE_PORT}" > "$_PID_FILE" 2>/dev/null || true
    return 0
  }

  _nasim_health() {
    curl -sf --connect-timeout 3 "${_BASE_URL}/health" 2>/dev/null
  }

  # ── model picker: inject Ollama models + select the bridge default ─────────
  # Marks every entry it adds with {"_nasim": true} so eject is exact and
  # idempotent regardless of how many times start runs.
  _nasim_inject_models() {
    local models_json default_model
    models_json=$(curl -sf --connect-timeout 3 "${_BASE_URL}/v1/models" 2>/dev/null)
    [ -z "$models_json" ] && return 1
    default_model="$1"

    python3 - "$_CLAUDE_JSON" "$_SETTINGS_JSON" "$_SAVED_MODEL_FILE" \
              "$_NASIM_MARKER" "$default_model" "$models_json" << 'PYEOF'
import sys, json, os

(claude_path, settings_path, saved_model_path,
 marker, default_model, models_json_str) = sys.argv[1:7]

# 1. Inject Ollama models into ~/.claude.json picker cache (marked).
try:
    with open(claude_path) as f:
        data = json.load(f)
except Exception:
    sys.exit(0)

try:
    bridge_models = json.loads(models_json_str).get("data", [])
except Exception:
    bridge_models = []

cache = data.get("additionalModelOptionsCache", [])
existing = {e.get("value") for e in cache}
for m in bridge_models:
    mid = m.get("id", "")
    if not mid or mid in existing:
        continue
    parts = mid.split(":", 1)
    name = parts[0].replace("-", " ").title()
    tag = parts[1] if len(parts) > 1 else ""
    label = (f"{name} {tag}".strip()) if tag else name
    cache.append({
        "value": mid,
        "label": label,
        "description": f"{mid} · Local Ollama (black) · nasim",
        marker: True,
    })
    existing.add(mid)
data["additionalModelOptionsCache"] = cache
with open(claude_path, "w") as f:
    json.dump(data, f, indent=2)

# 2. Back up the current selected model, then select the bridge default.
#    Only back up once per session (never overwrite a real backup with an
#    Ollama value on a repeated start).
try:
    with open(settings_path) as f:
        settings = json.load(f)
except Exception:
    settings = {}

if not os.path.exists(saved_model_path):
    original = settings.get("model", None)
    with open(saved_model_path, "w") as f:
        json.dump({"present": "model" in settings, "model": original}, f)

if default_model:
    settings["model"] = default_model
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
PYEOF
    return 0
  }

  # ── model picker: eject injected models + restore original selection ───────
  _nasim_eject_models() {
    python3 - "$_CLAUDE_JSON" "$_SETTINGS_JSON" "$_SAVED_MODEL_FILE" \
              "$_NASIM_MARKER" << 'PYEOF'
import sys, json, os

claude_path, settings_path, saved_model_path, marker = sys.argv[1:5]

# 1. Drop every nasim-marked entry from the picker cache.
try:
    with open(claude_path) as f:
        data = json.load(f)
    cache = data.get("additionalModelOptionsCache", [])
    data["additionalModelOptionsCache"] = [e for e in cache if not e.get(marker)]
    with open(claude_path, "w") as f:
        json.dump(data, f, indent=2)
except Exception:
    pass

# 2. Restore the model selection captured at start.
try:
    with open(saved_model_path) as f:
        saved = json.load(f)
    with open(settings_path) as f:
        settings = json.load(f)
    if saved.get("present"):
        settings["model"] = saved.get("model")
    else:
        settings.pop("model", None)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
except Exception:
    pass

# 3. Remove the backup marker so the next start re-captures cleanly.
try:
    os.remove(saved_model_path)
except OSError:
    pass
PYEOF
  }

  # ── commands ───────────────────────────────────────────────────────────────
  case "$1" in
    start)
      echo "Starting nasim tunnel → ${_REMOTE_HOST}:${_REMOTE_PORT} ..."
      if ! _nasim_start_tunnel; then
        return 1
      fi

      local health_json
      health_json=$(_nasim_health)
      if ! echo "$health_json" | grep -q '"status":"ok"'; then
        echo "ERROR: tunnel up but bridge health check failed — aborting." >&2
        echo "  Response: ${health_json:-<empty>}" >&2
        _nasim_kill_tunnel
        return 1
      fi

      # Resolve the bridge's default model for the active selection.
      local default_model models
      default_model=$(echo "$health_json" | python3 -c \
        "import sys,json; print(json.load(sys.stdin).get('default_model',''))" 2>/dev/null)
      models=$(echo "$health_json" | python3 -c \
        "import sys,json; print(', '.join(json.load(sys.stdin).get('available_models',[])))" \
        2>/dev/null || echo "unknown")

      _nasim_inject_models "$default_model"

      export ANTHROPIC_BASE_URL="$_BASE_URL"
      export ANTHROPIC_AUTH_TOKEN="nasim"
      export CLAUDE_CODE_MAX_OUTPUT_TOKENS="128000"
      export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
      export DISABLE_TELEMETRY="1"
      export DISABLE_ERROR_REPORTING="1"
      echo "ollama" > "$_STATE_FILE"

      echo "nasim STARTED — Claude Code → Ollama via bridge"
      echo "  Bridge  : ${_BASE_URL}"
      echo "  Models  : ${models}"
      echo "  Active  : ${default_model:-<bridge default>}"
      echo "  Tip     : launch 'claude' in THIS shell; use /model to switch"
      ;;

    stop)
      _nasim_kill_tunnel
      _nasim_eject_models
      unset ANTHROPIC_BASE_URL
      unset ANTHROPIC_AUTH_TOKEN
      unset CLAUDE_CODE_MAX_OUTPUT_TOKENS
      unset CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
      unset DISABLE_TELEMETRY
      unset DISABLE_ERROR_REPORTING
      echo "anthropic" > "$_STATE_FILE"
      echo "nasim STOPPED — Claude Code → Anthropic cloud (defaults restored)"
      ;;

    status)
      local state
      state=$(cat "$_STATE_FILE" 2>/dev/null || echo "anthropic")
      echo "Backend : $state"
      echo "Base URL: ${ANTHROPIC_BASE_URL:-(not set)}"

      local active_model
      active_model=$(python3 -c \
        "import json;print(json.load(open('$_SETTINGS_JSON')).get('model','(default)'))" 2>/dev/null \
        || echo "(unknown)")
      echo "Model   : $active_model"

      if [ "$state" = "ollama" ]; then
        local tunnel_alive="no"
        if [ -f "$_PID_FILE" ]; then
          local pid
          pid=$(cat "$_PID_FILE")
          [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null && tunnel_alive="yes (PID $pid)"
        fi
        echo "Tunnel  : $tunnel_alive"

        local health_json
        health_json=$(_nasim_health)
        if echo "$health_json" | grep -q '"status"'; then
          local bstatus
          bstatus=$(echo "$health_json" | python3 -c \
            "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null)
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

    ""|help|-h|--help)
      echo "Usage: nasim {start|stop|status|models}"
      echo "  start   open tunnel, route Claude Code to Ollama on ${_REMOTE_HOST}"
      echo "  stop    restore Claude Code to Anthropic cloud (full rollback)"
      echo "  status  show backend, tunnel, bridge health, active model"
      echo "  models  list Ollama models available through the bridge"
      ;;

    *)
      echo "Usage: nasim {start|stop|status|models}" >&2
      return 2
      ;;
  esac
}
