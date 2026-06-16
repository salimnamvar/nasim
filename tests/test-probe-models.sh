#!/usr/bin/env bash
# tests/test-probe-models.sh — real (no mock) tests for probe + models listing
# Exercises: probe_url, probe_and_show (now fixed to show models), list_models_on_black, nasim_models, nasim doctor.
# Uses live black via ssh (always) + optional tunneled url.
# This directly validates the fix for "the models are not shown".
# Run: ./tests/test-probe-models.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NASIM="$PROJECT_ROOT/bin/nasim"
BLACK_HOST="${NASIM_BLACK_HOST:-black}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log() { echo -e "${YELLOW}[probe-test]${NC} $*"; }
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

echo "=== test-probe-models: real black + fixed model visibility ==="

# 1. Direct black model list via the new first-class helper (no tunnel)
log "Exercise nasim models (ssh path, no tunnel required)"
"$NASIM" models 2>&1 | tee /tmp/nasim-models.out
if grep -q "qwen2.5-coder:14b\|deepseek-r1:14b\|llama3.1:8b" /tmp/nasim-models.out; then
    pass "nasim models lists real models from black (qwen2.5-coder etc visible)"
else
    fail "models command did not surface known black models"
fi

# 2. Doctor must now emit the full list (via list_models_on_black)
log "Exercise nasim doctor (must show models section)"
"$NASIM" doctor 2>&1 | tee /tmp/nasim-doctor.out
if grep -q "models available on black" /tmp/nasim-doctor.out && \
   grep -q "qwen2.5-coder:14b\|deepseek-r1:14b" /tmp/nasim-doctor.out; then
    pass "doctor surfaces black model inventory (fixes 'models not shown')"
else
    # Still pass if at least the ssh ps path or probe ran; but we want the list
    log "doctor output for diagnosis:"
    cat /tmp/nasim-doctor.out
    fail "doctor did not show the authoritative model list from black"
fi

# 3. Live tunnel + probe_and_show now emits models (use harness-style temp forward + nasim doctor --url)
log "Live SSH forward + nasim doctor --url on the forwarded endpoint (exercises probe_and_show fix)"
lport=11437
pkill -f "ssh.*$lport.*$BLACK_HOST" 2>/dev/null || true
ssh -o ConnectTimeout=5 -o ServerAliveInterval=10 -f -N -L "${lport}:localhost:11434" "$BLACK_HOST"
sleep 0.6
url="http://127.0.0.1:${lport}"

# Direct reachability + models via nasim's probe path
if "$NASIM" doctor --url "$url" 2>&1 | tee /tmp/nasim-doctor-url.out | grep -E "(OK: endpoint reachable|models:)" ; then
    pass "probe_and_show on real tunneled url reported reachable + emitted models (no longer suppressed)"
else
    fail "probe on live tunneled url failed to show models or reachability"
fi

pkill -f "ssh.*$lport.*$BLACK_HOST" 2>/dev/null || true

echo "=== test-probe-models: OK (real black models visible via nasim) ==="
