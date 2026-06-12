#!/usr/bin/env bash
# integration-test.sh — end-to-end tests for the deployed Nasim stack.
# Requires: bridge live on the server, nasim installed on this client.
set -uo pipefail

PORT="${NASIM_BRIDGE_PORT:-8080}"
BASE="http://127.0.0.1:$PORT"
PASS=0
FAIL=0

check() {
    local name="$1" ok="$2" detail="${3:-}"
    if [[ "$ok" == "0" ]]; then
        echo "  PASS  $name"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $name  $detail"
        FAIL=$((FAIL + 1))
    fi
}

echo "→ Bridge API tests ($BASE)"

HEALTH=$(curl -fsS --max-time 10 "$BASE/health" 2>&1)
[[ "$HEALTH" == *'"status":"ok"'* || "$HEALTH" == *'"status": "ok"'* ]]
check "health endpoint" $? "$HEALTH"

RESP=$(curl -fsS --max-time 120 "$BASE/v1/messages" \
    -H 'Content-Type: application/json' \
    -d '{"model":"naseem-sonnet-4-6","max_tokens":32,
         "messages":[{"role":"user","content":"Reply with exactly one word: bridgeok"}]}' 2>&1)
[[ "$RESP" == *bridgeok* && "$RESP" == *'"type":"message"'* ]]
check "non-streaming message" $? "$RESP"

STREAM=$(curl -fsS --max-time 120 -N "$BASE/v1/messages" \
    -H 'Content-Type: application/json' \
    -d '{"model":"naseem-sonnet-4-6","max_tokens":32,"stream":true,
         "messages":[{"role":"user","content":"Reply with exactly one word: streamok"}]}' 2>&1)
[[ "$STREAM" == *"event: message_start"* && "$STREAM" == *"event: message_stop"* ]]
check "streaming SSE shape" $? "$(echo "$STREAM" | head -2)"

TOOLS=$(curl -fsS --max-time 120 "$BASE/v1/messages" \
    -H 'Content-Type: application/json' \
    -d '{"model":"naseem-sonnet-4-6","max_tokens":256,
         "tools":[{"name":"read_file","description":"Read a file from disk",
                   "input_schema":{"type":"object","properties":{"path":{"type":"string"}},
                                   "required":["path"]}}],
         "messages":[{"role":"user","content":"Use the read_file tool to read src/main.py"}]}' 2>&1)
[[ "$TOOLS" == *'"type":"tool_use"'* && "$TOOLS" == *'"name":"read_file"'* ]]
check "tool calling" $? "$TOOLS"

COUNT=$(curl -fsS --max-time 10 "$BASE/v1/messages/count_tokens" \
    -H 'Content-Type: application/json' \
    -d '{"model":"x","messages":[{"role":"user","content":"hello world"}]}' 2>&1)
[[ "$COUNT" == *'"input_tokens"'* ]]
check "count_tokens" $? "$COUNT"

echo "→ CLI tests"

VERSION=$(nasim --version 2>&1)
[[ "$VERSION" == *Naseem* && "$VERSION" != *Claude* ]]
check "version banner renamed" $? "$VERSION"

PRINT=$(cd /tmp && nasim -p "Reply with exactly one word: cliok" 2>&1)
[[ "$PRINT" == *cliok* ]]
check "nasim -p end-to-end" $? "$PRINT"

[[ -d "$HOME/.nasim" ]]
check "~/.nasim exists" $?

[[ ! -e "$HOME/.nasim/.claude.json" ]]
check "no .claude.json under ~/.nasim" $?

echo
echo "Results: $PASS passed, $FAIL failed"
exit "$((FAIL > 0))"
