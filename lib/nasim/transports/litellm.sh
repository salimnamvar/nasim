#!/usr/bin/env bash
# lib/nasim/transports/litellm.sh — LiteLLM proxy as a transport layer on top of a base
#
# setup_litellm(inner_ollama_url [, chosen_model]):
#   Writes a temp litellm.yaml that registers the chosen model (and aliases), starts `litellm --config` in bg,
#   uses litellm-specific readiness (/health or /v1/models) instead of ollama /api/tags.
#   Returns the litellm port url even on soft probe fail (caller decides).
#   Fix for original symptom: litellm probes were using wrong endpoint + static config didn't know the runtime model tag.

setup_litellm() {
    local inner_url="$1"   # already verified real ollama (ssh or ts)
    local chosen_model="${2:-$DEFAULT_MODEL}"
    if is_dry; then
        echo "http://127.0.0.1:${LITELLM_PORT}"
        return 0
    fi

    local cfg="/tmp/nasim-litellm-$$.yaml"
    local pidfile="/tmp/nasim-litellm-$$.pid"
    local logf="/tmp/nasim-litellm-$$.log"

    # Dynamic: always register the user-chosen model under its exact tag so
    # `claude --model $chosen` or aider/opencode see a matching name at the proxy.
    # Also expose a stable default + a reasoner alias.
    cat > "$cfg" <<EOF
model_list:
  - model_name: ${chosen_model}
    litellm_params:
      model: ollama/${chosen_model}
      api_base: ${inner_url}
  - model_name: black-default
    litellm_params:
      model: ollama/${chosen_model}
      api_base: ${inner_url}
  - model_name: black-reasoner
    litellm_params:
      model: ollama/deepseek-r1:14b
      api_base: ${inner_url}
EOF

    log "litellm config: $cfg (inner: $inner_url, chosen: $chosen_model)"

    if ! have litellm; then
        log "litellm not installed. pip install 'litellm[proxy]' then re-run, or use direct transport."
        echo "http://127.0.0.1:${LITELLM_PORT}"
        return 0
    fi

    litellm --config "$cfg" --port "$LITELLM_PORT" --num_workers 1 >"$logf" 2>&1 &
    local lpid=$!
    echo "$lpid" > "$pidfile"
    sleep 1.5

    local url="http://127.0.0.1:${LITELLM_PORT}"

    # LiteLLM serves OpenAI compat at /v1 (and Anthropic passthrough). Do NOT use ollama /api/tags probe here.
    local litellm_ready=0
    for i in 1 2 3 4; do
        if curl -sf --max-time 3 "$url/health" >/dev/null 2>&1 || \
           curl -sf --max-time 3 "$url/v1/models" >/dev/null 2>&1 ; then
            litellm_ready=1
            break
        fi
        sleep 0.8
    done

    if [[ $litellm_ready -eq 1 ]]; then
        log "OK: litellm reachable at $url (OpenAI/Anthropic compat)"
        echo "$url"
        return 0
    fi

    log "WARNING: litellm did not respond on /health or /v1/models (see $logf). Proceeding with url anyway; agent may fail if proxy not ready."
    # Return url so orchestration can still surface ssh-based model list + warning.
    echo "$url"
}
