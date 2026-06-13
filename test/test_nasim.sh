#!/usr/bin/env bash
# Nasim integration test suite.
#
# Prerequisites:
#   - SSH key access to 'black' without a passphrase
#   - nasim-bridge.service running on black (port 8080)
#   - curl available on the local machine
#
# Run: bash test/test_nasim.sh
# Exit 0 = all passed; non-zero = at least one failure.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NASIM_SH="$SCRIPT_DIR/../bin/nasim.sh"

# ── test framework ────────────────────────────────────────────────────────────
PASS=0; FAIL=0; ERRORS=()

pass() { echo "  PASS  $1"; PASS=$((PASS + 1)); }
fail() { echo "  FAIL  $1: $2"; FAIL=$((FAIL + 1)); ERRORS+=("$1: $2"); }

assert_eq()  { [ "$2" = "$3" ] && pass "$1" || fail "$1" "expected '$3', got '$2'"; }
assert_contains() { echo "$2" | grep -qF "$3" && pass "$1" || fail "$1" "expected '$3' in output"; }
assert_empty()    { [ -z "$1" ] && pass "$2" || fail "$2" "expected empty, got '$1'"; }
assert_file()     { [ -f "$1" ] && pass "$2" || fail "$2" "expected file $1 to exist"; }
assert_no_file()  { [ ! -f "$1" ] && pass "$2" || fail "$2" "expected file $1 to be absent"; }

# Source nasim into a subshell helper
_run_nasim() {
  bash -c "source '$NASIM_SH'; nasim $*" 2>&1
}

# ── setup / teardown ─────────────────────────────────────────────────────────
setup() {
  # Ensure clean state
  bash -c "source '$NASIM_SH'; nasim stop" >/dev/null 2>&1 || true
  rm -f "$HOME/.nasim_state" "$HOME/.nasim_tunnel.pid"
}

teardown() {
  bash -c "source '$NASIM_SH'; nasim stop" >/dev/null 2>&1 || true
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

  # Run start in current shell (no pipe — pipes create subshells, losing env var side-effects)
  local _out
  _out=$(mktemp)
  nasim start > "$_out" 2>&1
  grep -q "STARTED" "$_out" && pass "TC02 start output" || fail "TC02 start output" "STARTED not in output ($(cat "$_out"))"
  rm -f "$_out"

  assert_eq   "TC02 ANTHROPIC_BASE_URL" "${ANTHROPIC_BASE_URL:-}" "http://localhost:18080"
  assert_eq   "TC02 ANTHROPIC_AUTH_TOKEN" "${ANTHROPIC_AUTH_TOKEN:-}" "nasim"
  assert_file "$HOME/.nasim_tunnel.pid"  "TC02 pid file"
  assert_file "$HOME/.nasim_state"       "TC02 state file"
  assert_eq   "TC02 state file content" "$(cat "$HOME/.nasim_state")" "ollama"

  # Tunnel process alive
  local pid
  pid=$(cat "$HOME/.nasim_tunnel.pid")
  kill -0 "$pid" 2>/dev/null && pass "TC02 tunnel process alive" || fail "TC02 tunnel process alive" "PID $pid not running"
}

# ── TC03: bridge health through tunnel ───────────────────────────────────────
tc03_health_through_tunnel() {
  echo "TC03: bridge health through tunnel"
  local out
  out=$(curl -sf --connect-timeout 5 http://localhost:18080/health 2>/dev/null)
  assert_contains "TC03 health ok" "$out" '"status":"ok"'
}

# ── TC04: model list through tunnel ──────────────────────────────────────────
tc04_models() {
  echo "TC04: model list through tunnel"
  local out
  out=$(curl -sf --connect-timeout 5 http://localhost:18080/v1/models 2>/dev/null)
  assert_contains "TC04 data array" "$out" '"data"'
  assert_contains "TC04 qwen model" "$out" "qwen"
}

# ── TC05: Anthropic API message round-trip through bridge ────────────────────
tc05_message_roundtrip() {
  echo "TC05: message round-trip (non-streaming)"
  local payload='{"model":"qwen2.5-coder:7b","max_tokens":32,"messages":[{"role":"user","content":"Reply with the single word: pong"}]}'
  local out
  out=$(curl -sf --connect-timeout 30 \
        -H "Content-Type: application/json" \
        -H "x-api-key: nasim" \
        -d "$payload" \
        http://localhost:18080/v1/messages 2>/dev/null)
  assert_contains "TC05 type message" "$out" '"type":"message"'
  assert_contains "TC05 content block" "$out" '"type":"text"'
}

# ── TC06: nasim status reflects running state ────────────────────────────────
tc06_status_running() {
  echo "TC06: nasim status (running)"
  local out
  out=$(nasim status 2>&1)
  assert_contains "TC06 backend ollama" "$out" "ollama"
  assert_contains "TC06 url present"    "$out" "localhost:18080"
}

# ── TC07: nasim stop kills tunnel and unsets env ─────────────────────────────
tc07_stop() {
  echo "TC07: nasim stop"
  local pid
  pid=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "")

  local _out
  _out=$(mktemp)
  nasim stop > "$_out" 2>&1
  grep -q "STOPPED" "$_out" && pass "TC07 stop output" || fail "TC07 stop output" "STOPPED not in output ($(cat "$_out"))"
  rm -f "$_out"

  assert_empty "${ANTHROPIC_BASE_URL:-}"    "TC07 ANTHROPIC_BASE_URL unset"
  assert_empty "${ANTHROPIC_AUTH_TOKEN:-}"  "TC07 ANTHROPIC_AUTH_TOKEN unset"
  assert_no_file "$HOME/.nasim_tunnel.pid" "TC07 pid file removed"
  assert_eq "TC07 state file content" "$(cat "$HOME/.nasim_state")" "anthropic"

  if [ -n "$pid" ]; then
    kill -0 "$pid" 2>/dev/null && fail "TC07 tunnel process stopped" "PID $pid still running" || pass "TC07 tunnel process stopped"
  fi
}

# ── TC08: bridge unreachable after stop ──────────────────────────────────────
tc08_bridge_gone_after_stop() {
  echo "TC08: bridge unreachable after stop"
  local out
  out=$(curl -sf --connect-timeout 2 http://localhost:18080/health 2>/dev/null || echo "")
  assert_empty "$out" "TC08 no bridge after stop"
}

# ── TC09: nasim status reflects stopped state ────────────────────────────────
tc09_status_stopped() {
  echo "TC09: nasim status (stopped)"
  local out
  out=$(nasim status 2>&1)
  assert_contains "TC09 backend anthropic" "$out" "anthropic"
}

# ── TC10: idempotent start (second start replaces tunnel) ────────────────────
tc10_double_start() {
  echo "TC10: double start is idempotent"
  nasim start >/dev/null 2>&1
  local pid1
  pid1=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "0")
  nasim start >/dev/null 2>&1
  local pid2
  pid2=$(cat "$HOME/.nasim_tunnel.pid" 2>/dev/null || echo "0")

  # First tunnel must be dead
  kill -0 "$pid1" 2>/dev/null && fail "TC10 old tunnel killed" "PID $pid1 still alive" || pass "TC10 old tunnel killed"
  # New tunnel must be alive
  kill -0 "$pid2" 2>/dev/null && pass "TC10 new tunnel alive" || fail "TC10 new tunnel alive" "PID $pid2 not running"
  # Stop to clean up
  nasim stop >/dev/null 2>&1
}

# ── main ─────────────────────────────────────────────────────────────────────
main() {
  echo "=== Nasim test suite ==="
  echo ""

  setup

  # Source nasim into current shell so env-var tests work
  source "$NASIM_SH"

  tc01_bridge_ssh_reachable
  tc02_start
  tc03_health_through_tunnel
  tc04_models
  tc05_message_roundtrip
  tc06_status_running
  tc07_stop
  tc08_bridge_gone_after_stop
  tc09_status_stopped

  # Re-start for double-start test
  nasim start >/dev/null 2>&1
  tc10_double_start

  teardown

  echo ""
  echo "=== Results: ${PASS} passed, ${FAIL} failed ==="
  if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "Failures:"
    for e in "${ERRORS[@]}"; do echo "  - $e"; done
  fi
  [ $FAIL -eq 0 ]
}

main "$@"
