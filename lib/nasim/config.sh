#!/usr/bin/env bash
# lib/nasim/config.sh — external configuration + defaults (AD-09)
# Precedence: CLI args / explicit env > config file > built-in defaults
# Simple zero-dep format: KEY=val lines (sourced safely after validation).
# Supports comments (#) and blank lines.
#
# nasim_config_load():
#   Called at source time. Establishes BLACK_HOST, DEFAULT_MODEL (now strong), ports, orders.
#   The guard in _defaults uses explicit "is unset or empty" checks so that `export VAR=foo; nasim_config_load`
#   (as done in tests) reliably wins over compiled defaults.

NASIM_CONFIG_DIR="${NASIM_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/nasim}"
NASIM_CONFIG_FILE="${NASIM_CONFIG_FILE:-$NASIM_CONFIG_DIR/nasim.conf}"

_nasim_config_defaults() {
    # Only default when truly unset (respect explicit env and prior exports reliably).
    if [[ -z "${BLACK_HOST+x}" || -z "$BLACK_HOST" ]]; then BLACK_HOST="black"; fi
    if [[ -z "${DEFAULT_MODEL+x}" || -z "$DEFAULT_MODEL" ]]; then
        # Strong reasoner + coding model that exists on black and works well for agentic use over native compat.
        # (Avoid qwen2.5* for claude-code style loops; see tip in launchers and research.)
        DEFAULT_MODEL="deepseek-r1:14b"
    fi
    if [[ -z "${DEFAULT_LOCAL_PORT+x}" || -z "$DEFAULT_LOCAL_PORT" ]]; then DEFAULT_LOCAL_PORT=11435; fi
    if [[ -z "${LITELLM_PORT+x}" || -z "$LITELLM_PORT" ]]; then LITELLM_PORT=4000; fi

    if [[ -z "${ACCESS_ORDER+x}" || -z "$ACCESS_ORDER" ]]; then ACCESS_ORDER="ssh-tunnel tailscale litellm"; fi
    if [[ -z "${AGENT_ORDER+x}" || -z "$AGENT_ORDER" ]]; then AGENT_ORDER="claude aider opencode terminal"; fi

    if [[ -z "${PROBE_TIMEOUT+x}" || -z "$PROBE_TIMEOUT" ]]; then PROBE_TIMEOUT=6; fi
    if [[ -z "${PROBE_CONNECT_TIMEOUT+x}" || -z "$PROBE_CONNECT_TIMEOUT" ]]; then PROBE_CONNECT_TIMEOUT=3; fi
    if [[ -z "${SSH_CONNECT_TIMEOUT+x}" || -z "$SSH_CONNECT_TIMEOUT" ]]; then SSH_CONNECT_TIMEOUT=8; fi
    if [[ -z "${SSH_SERVER_ALIVE_INTERVAL+x}" || -z "$SSH_SERVER_ALIVE_INTERVAL" ]]; then SSH_SERVER_ALIVE_INTERVAL=20; fi
}

_nasim_config_load_file() {
    local f="$1"
    [[ -f "$f" ]] || return 0

    # Safe load: only allow simple KEY=val or KEY="val", ignore comments/blank
    # We use a subshell + grep + while to avoid sourcing arbitrary code.
    while IFS='=' read -r key val; do
        # trim
        key="${key%%#*}"          # drop inline comments
        key="$(echo "$key" | xargs)" || true
        val="$(echo "$val" | xargs)" || true
        [[ -z "$key" ]] && continue

        # Only accept known safe keys (whitelist to prevent injection surprises)
        case "$key" in
            BLACK_HOST|DEFAULT_MODEL|DEFAULT_LOCAL_PORT|LITELLM_PORT| \
            ACCESS_ORDER|AGENT_ORDER|PROBE_TIMEOUT|PROBE_CONNECT_TIMEOUT| \
            SSH_CONNECT_TIMEOUT|SSH_SERVER_ALIVE_INTERVAL|NASIM_VERSION_OVERRIDE)
                # Strip surrounding quotes if present
                val="${val#\"}"; val="${val%\"}"
                val="${val#\'}"; val="${val%\'}"
                export "$key=$val"
                ;;
            *)
                # Unknown keys are ignored (or could warn in verbose mode)
                ;;
        esac
    done < <(grep -v '^[[:space:]]*#' "$f" | grep '=' || true)
}

nasim_config_load() {
    _nasim_config_defaults
    _nasim_config_load_file "$NASIM_CONFIG_FILE"
    # Re-apply defaults for anything that was not set by file (in case file was partial).
    # With the if-unset guards this no longer stomps a live env export.
    _nasim_config_defaults
}

nasim_config_path() {
    echo "$NASIM_CONFIG_FILE"
}

nasim_config_show() {
    echo "# Effective nasim configuration (precedence: explicit env > $NASIM_CONFIG_FILE > defaults)"
    echo "BLACK_HOST=$BLACK_HOST"
    echo "DEFAULT_MODEL=$DEFAULT_MODEL"
    echo "DEFAULT_LOCAL_PORT=$DEFAULT_LOCAL_PORT"
    echo "LITELLM_PORT=$LITELLM_PORT"
    echo "ACCESS_ORDER=$ACCESS_ORDER"
    echo "AGENT_ORDER=$AGENT_ORDER"
    echo "CONFIG_FILE=$NASIM_CONFIG_FILE"
    echo "# (other tunables: PROBE_*, SSH_* )"
}

nasim_config_edit() {
    local editor="${EDITOR:-${VISUAL:-nano}}"
    mkdir -p "$(dirname "$NASIM_CONFIG_FILE")"
    if [[ ! -f "$NASIM_CONFIG_FILE" ]]; then
        cat > "$NASIM_CONFIG_FILE" <<'EOF'
# nasim user configuration (KEY=val)
# This file is sourced (safely) at startup.
# Precedence: environment variables and CLI flags override this file.

BLACK_HOST=black
# Strong default (exists + good for agentic claude/opencode over native Ollama Anthropic/OpenAI compat).
# Run `nasim models` to see all; prefer deepseek-r1:*, qwen3*, gemma4* large GPU-resident ones.
DEFAULT_MODEL=deepseek-r1:14b
# DEFAULT_LOCAL_PORT=11435
# LITELLM_PORT=4000

# Interactive select presentation order
# ACCESS_ORDER="ssh-tunnel tailscale litellm"
# AGENT_ORDER="claude aider opencode terminal"
EOF
        echo "Created default config at $NASIM_CONFIG_FILE"
    fi
    "$editor" "$NASIM_CONFIG_FILE"
}

# Called early by the loader
nasim_config_load
