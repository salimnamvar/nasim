#!/usr/bin/env bash
# lib/nasim/transports/litellm.sh — LiteLLM proxy as a transport layer on top of a base

setup_litellm() {
    local inner_url="$1"   # already verified real ollama (ssh or ts)
    if is_dry; then
        echo "http://127.0.0.1:${LITELLM_PORT}"
        return 0
    fi

    local cfg="/tmp/nasim-litellm-$$.yaml"
    local pidfile="/tmp/nasim-litellm-$$.pid"

    cat > "$cfg" <<EOF
model_list:
  - model_name: black-default
    litellm_params:
      model: ollama/${DEFAULT_MODEL}
      api_base: ${inner_url}
  - model_name: black-fast
    litellm_params:
      model: ollama/llama3.1:8b
      api_base: ${inner_url}
EOF

    log "litellm config: $cfg (inner: $inner_url)"

    if ! have litellm; then
        log "litellm not installed. pip install 'litellm[proxy]' then re-run, or use direct transport."
        echo "http://127.0.0.1:${LITELLM_PORT}"
        return 0
    fi

    litellm --config "$cfg" --port "$LITELLM_PORT" --num_workers 1 >/tmp/nasim-litellm-$$.log 2>&1 &
    local lpid=$!
    echo "$lpid" > "$pidfile"
    sleep 1.2

    local url="http://127.0.0.1:${LITELLM_PORT}"
    if probe_and_show "$url"; then
        echo "$url"
        return 0
    fi
    # Non-fatal for some agents
    echo "$url"
}
