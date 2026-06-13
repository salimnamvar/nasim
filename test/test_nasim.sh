#!/usr/bin/env bash
# Nasim integration + rollback test suite.
#
# Verifies start/stop/status/models AND the hard rollback guarantee: after
# `nasim stop` the machine is byte-for-byte back to Claude Code defaults —
# no tunnel, no env redirect, no injected Ollama models, original /model
# selection restored.
#
# Prerequisites:
#   - SSH key access to 'black' without a passphrase
#   - nasim-bridge.service running on black (port 8080)
#   - curl + python3 available locally
#
# Run: bash test/test_nasim.sh
# Exit 0 = all passed; non-zero = at least one failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NASIM_SH="$SCRIPT_DIR/../bin/nasim.sh"

CLAUDE_JSON="$HOME/.claude.json"
SETTINGS_JSON="$HOME/.claude/settings.json"
LOCAL_PORT="18080"

# ── test framework ────────────────────────────────────────────────────────────
PASS=0; FAIL=0; ERRORS=()

pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL  $1: $2"; FAIL=$((FAIL + 1)); ERRORS+=("$1: $2"); }

assert_eq()       { [ "$2" = "$3" ] && pass "$1" || fail "$1" "expected '$3', got '$2'"; }
assert_contains() { echo "$2" | grep -qF "$3" && pass "$1" || fail "$1" "expected '$3' in output"; }
assert_empty()    { [ -z "$1" ] && pass "$2" || fail "$2" "expected empty, got '$1'"; }
assert_file()     { [ -f "$1" ] && pass "$2" || fail "$2" "expected file $1 to exist"; }
assert_no_file()  { [ ! -f "$1" ] && pass "$2" || fail "$2" "expected file $1 to be absent"; }

# Count nasim-marked entries in the picker cache.
_marked_count() {
  python3 -c "
import json
try:
    d=json.load(open('$CLAUDE_JSON'))
    print(sum(1 for e in d.get('additionalModelOptionsCache',[]) if e.get('_nasim')))
except Exception:
    print(-1)
"
}

# Current selected model in settings.json (or NONE).
_settings_model() {
  python3 -c "
import json
try:
    print(json.load(open('$SETTINGS_JSON')).get('model','NONE'))
except Exception:
    print('NONE')
"
}

# ── setup / teardown ─────────────────────────────────────────────────────────
setup() {
  bash -c "source '$NASIM_SH'; nasim stop" >/dev/null 2>&1 || true
  rm -f "$HOME/.nasim_state" "$HOME/.nasim_tunnel.pid" "$HOME/.nasim_saved_model"
}

teardown() {
  nasim stop >/dev/null 2>&1 || true
}

# ── TC01: bridge reachable on black via SSH ───────────────────────────────────
tc01_bridge_ssh_reachable() {
  echo "TC01: bridge reachable on black via SSH"
  local out
  out=$(ssh black "curl -sf http://127.0.0.1:8080/health" 2>/dev/null)
  assert_contains "TC01 bridge status ok" "$out" '"status":"ok"'
  assert_contains "TC01 ollama connected" "$out" '"ollama":"connected"'
}

# ── TC02: nasim start opens tunnel and sets env vars ─────────────────────────
tc02_start() {
  echo "TC02: nasim start opens tunnel and sets env vars"
  setup

  local _out; _out=$(mktemp)
  nasim start > "$_out" 2>&1
  grep -q "STARTED" "$_out" && pass "TC02 start output" || fail "TC02 start output" "STARTED not in output ($(cat "$_out"))"
  rm -f "$_out"

  assert_eq   "TC02 ANTHROPIC_BASE_URL"   "${ANTHROPIC_BASE_URL:-}"   "http://localhost:${LOCAL_PORT}"
  assert_eq   "TC02 ANTHROPIC_AUTH_TOKEN" "${ANTHROPIC_AUTH_TOKEN:-}" "nasim"
  assert_eq   "TC02 nonessential traffic disabled" "${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-}" "1"
  assert_file "$HOME/.nasim_tunnel.pid"   "TC02 pid file"
  assert_file "$HOME/.nasim_state"        "TC02 state file"
  assert_file "$HOME/.nasim_saved_model"  "TC02 saved-model backup file"
  assert_eq   "TC02 state file content"   "$(cat "$HOME/.nasim_state")" "ollama"

  local pid; pid=$(cat "$HOME/.nasim_tunnel.pid")
  kill -0 "$pid" 2>/dev/null && pass "TC02 tunnel process alive" || fail "TC02 tunnel process alive" "PID $pid not running"
}

# ── TC03: bridge health through tunnel ───────────────────────────────────────
tc03_health_through_tunnel() {
  echo "TC03: bridge health through tunnel"
  local out
  out=$(curl -sf --connect-timeout 5 "http://localhost:${LOCAL_PORT}/health" 2>/dev/null)
  assert_contains "TC03 health ok" "$out" '"status":"ok"'
}

# ── TC04: model list through tunnel ──────────────────────────────────────────
tc04_models() {
  echo "TC04: model list through tunnel"
  local out
  out=$(curl -sf --connect-timeout 5 "http://localhost:${LOCAL_PORT}/v1/models" 2>/dev/null)
  assert_contains "TC04 data array" "$out" '"data"'
  assert_contains "TC04 qwen model" "$out" "qwen"
}

# ── TC05: Anthropic API message round-trip through bridge ────────────────────
tc05_message_roundtrip() {
  echo "TC05: message round-trip (non-streaming)"
  local payload='{"model":"qwen2.5-coder:7b","max_tokens":32,"messages":[{"role":"user","content":"Reply with the single word: pong"}]}'
  local out
  out=$(curl -sf --connect-timeout 60 \
        -H "Content-Type: application/json" \
        -H "x-api-key: nasim" \
        -d "$payload" \
        "http://localhost:${LOCAL_PORT}/v1/messages" 2>/dev/null)
  assert_contains "TC05 type message" "$out" '"type":"message"'
  assert_contains "TC05 content block" "$out" '"type":"text"'
}

# ── TC06: Ollama models injected into the /model picker cache ─────────────────
tc06_models_injected() {
  echo "TC06: Ollama models injected into picker cache"
  local count; count=$(_marked_count)
  [ "$count" -ge 1 ] && pass "TC06 injected marked entries ($count)" || fail "TC06 injected marked entries" "expected >=1, got $count"

  # Every injected entry must be present in the picker cache by value.
  local has_qwen
  has_qwen=$(python3 -c "
import json
d=json.load(open('$CLAUDE_JSON'))
vals=[e.get('value','') for e in d.get('additionalModelOptionsCache',[]) if e.get('_nasim')]
print('yes' if any('qwen' in v for v in vals) else 'no')
")
  assert_eq "TC06 qwen in picker cache" "$has_qwen" "yes"
}

# ── TC07: start selects the bridge default model in settings.json ────────────
tc07_default_model_selected() {
  echo "TC07: start selects bridge default model"
  local default_model
  default_model=$(curl -sf "http://localhost:${LOCAL_PORT}/health" 2>/dev/null | \
    python3 -c "import sys,json;print(json.load(sys.stdin).get('default_model',''))" 2>/dev/null)
  assert_eq "TC07 active model is bridge default" "$(_settings_model)" "$default_model"
}

# ── TC08: nasim status reflects running state ────────────────────────────────
tc08_status_running() {
  echo "TC08: nasim status (running)"
  local out; out=$(nasim status 2>&1)
  assert_contains "TC08 backend ollama" "$out" "ollama"
  assert_contains "TC08 url present"    "$out" "localhost:${LOCAL_PORT}"
}

# ── TC09: user picks a specific Ollama model via /model (simulated) ──────────
# Simulates the Claude Code /model picker writing a colon-tagged Ollama model
# into settings.json. This is the dangling-reference risk that stop must heal.
tc09_user_selects_ollama_model() {
  echo "TC09: simulate /model selecting an Ollama tag"
  python3 -c "
import json
s=json.load(open('$SETTINGS_JSON'))
s['model']='gemma4:latest'
json.dump(s,open('$SETTINGS_JSON','w'),indent=2)
"
  assert_eq "TC09 settings model is ollama tag" "$(_settings_model)" "gemma4:latest"
}

# ── TC10: nasim stop — full rollback ─────────────────────────────────────────
tc10_stop_rollback() {
  echo "TC10: nasim stop — full rollback"
  local pid; pid=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "")

  local _out; _out=$(mktemp)
  nasim stop > "$_out" 2>&1
  grep -q "STOPPED" "$_out" && pass "TC10 stop output" || fail "TC10 stop output" "STOPPED not in output ($(cat "$_out"))"
  rm -f "$_out"

  assert_empty "${ANTHROPIC_BASE_URL:-}"   "TC10 ANTHROPIC_BASE_URL unset"
  assert_empty "${ANTHROPIC_AUTH_TOKEN:-}" "TC10 ANTHROPIC_AUTH_TOKEN unset"
  assert_empty "${CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:-}" "TC10 nonessential traffic unset"
  assert_no_file "$HOME/.nasim_tunnel.pid"  "TC10 pid file removed"
  assert_no_file "$HOME/.nasim_saved_model" "TC10 saved-model backup removed"
  assert_eq "TC10 state file content" "$(cat "$HOME/.nasim_state")" "anthropic"

  # No nasim-marked models left in the picker.
  assert_eq "TC10 zero injected models left" "$(_marked_count)" "0"

  # Original model restored (the pre-start value), NOT the ollama tag we set.
  local restored; restored=$(_settings_model)
  [ "$restored" != "gemma4:latest" ] && pass "TC10 ollama selection healed" || fail "TC10 ollama selection healed" "settings still on gemma4:latest"
  assert_eq "TC10 original model restored" "$restored" "$ORIGINAL_MODEL"

  if [ -n "$pid" ]; then
    kill -0 "$pid" 2>/dev/null && fail "TC10 tunnel process stopped" "PID $pid still running" || pass "TC10 tunnel process stopped"
  fi
}

# ── TC11: bridge unreachable after stop ──────────────────────────────────────
tc11_bridge_gone_after_stop() {
  echo "TC11: bridge unreachable after stop"
  local out
  out=$(curl -sf --connect-timeout 2 "http://localhost:${LOCAL_PORT}/health" 2>/dev/null || echo "")
  assert_empty "$out" "TC11 no bridge after stop"
}

# ── TC12: nasim status reflects stopped state ────────────────────────────────
tc12_status_stopped() {
  echo "TC12: nasim status (stopped)"
  local out; out=$(nasim status 2>&1)
  assert_contains "TC12 backend anthropic" "$out" "anthropic"
}

# ── TC13: double start is idempotent and keeps tracking intact ───────────────
tc13_double_start() {
  echo "TC13: double start is idempotent (no orphan tunnels, no lost tracking)"
  setup
  nasim start >/dev/null 2>&1
  local pid1 count1; pid1=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "0"); count1=$(_marked_count)
  nasim start >/dev/null 2>&1
  local pid2 count2; pid2=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "0"); count2=$(_marked_count)

  kill -0 "$pid1" 2>/dev/null && fail "TC13 old tunnel killed" "PID $pid1 still alive" || pass "TC13 old tunnel killed"
  kill -0 "$pid2" 2>/dev/null && pass "TC13 new tunnel alive" || fail "TC13 new tunnel alive" "PID $pid2 not running"
  # No duplicate injection on second start.
  assert_eq "TC13 no duplicate injected models" "$count1" "$count2"

  nasim stop >/dev/null 2>&1
  # After stop, second-start tracking still fully ejected.
  assert_eq "TC13 clean eject after double start" "$(_marked_count)" "0"
}

# ── TC14: idempotent stop (stop when already stopped is safe) ─────────────────
tc14_double_stop() {
  echo "TC14: double stop is safe"
  nasim stop >/dev/null 2>&1
  local out; out=$(nasim stop 2>&1)
  assert_contains "TC14 stop still reports STOPPED" "$out" "STOPPED"
  assert_eq "TC14 model unchanged on extra stop" "$(_settings_model)" "$ORIGINAL_MODEL"
}

# ── TC15: usage/help on bad verb ─────────────────────────────────────────────
tc15_usage() {
  echo "TC15: usage on unknown verb"
  local out; out=$(nasim bogus 2>&1)
  assert_contains "TC15 usage line" "$out" "Usage: nasim"
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
  echo "=== Nasim test suite ==="
  echo ""

  setup
  source "$NASIM_SH"

  # Capture the genuine pre-nasim model so rollback assertions are exact.
  ORIGINAL_MODEL="$(_settings_model)"
  echo "  (baseline /model selection: ${ORIGINAL_MODEL})"
  echo ""

  tc01_bridge_ssh_reachable
  tc02_start
  tc03_health_through_tunnel
  tc04_models
  tc05_message_roundtrip
  tc06_models_injected
  tc07_default_model_selected
  tc08_status_running
  tc09_user_selects_ollama_model
  tc10_stop_rollback
  tc11_bridge_gone_after_stop
  tc12_status_stopped
  tc13_double_start
  tc14_double_stop
  tc15_usage

  teardown

  # Final safety net: confirm the baseline model is intact after the whole run.
  echo ""
  assert_eq "FINAL baseline model intact" "$(_settings_model)" "$ORIGINAL_MODEL"

  echo ""
  echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
  if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "Failures:"
    for e in "${ERRORS[@]}"; do echo "  - $e"; done
  fi
  [ $FAIL -eq 0 ]
}

main "$@"
