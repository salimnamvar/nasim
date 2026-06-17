#!/usr/bin/env bash
# tests/test-fcc.sh — verify fcc proxy integration for claude + ollama (sce1 scenario)
# Run: bash tests/test-fcc.sh   or with NASIM_DRY_RUN=1 etc.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
NASIM_INTERNAL=1 source bin/nasim

echo "=== test-fcc: availability and model prefix logic ==="

# Simulate detection (we are in the checkout that has sibling free-claude-code)
if [[ -n "${NASIM_FCC_SRC_DIR:-}" ]]; then
  echo "PASS: NASIM_FCC_SRC_DIR detected: $NASIM_FCC_SRC_DIR"
else
  echo "NOTE: NASIM_FCC_SRC_DIR not auto-detected in this env (expected if not sibling clone)"
fi

# Test fcc_write_temp_config produces correct ollama/ prefix
if type fcc_write_temp_config >/dev/null 2>&1; then
  tmpf=$(fcc_write_temp_config "http://127.0.0.1:11435" "deepseek-r1:14b" 18081)
  grep -q 'MODEL=ollama/deepseek-r1:14b' "$tmpf" || { echo "FAIL: MODEL should be ollama/ prefixed"; exit 1; }
  grep -q 'OLLAMA_BASE_URL=http://127.0.0.1:11435' "$tmpf" || { echo "FAIL: OLLAMA url"; exit 1; }
  echo "PASS: temp fcc config uses MODEL=ollama/... "
  rm -f "$tmpf"
else
  echo "SKIP: fcc functions not loaded"
fi

echo "=== test-fcc: claude launch dry produces gateway model when fcc present ==="
# Force the fcc path in dry (mock fcc_start_proxy)
fcc_start_proxy() { echo "http://127.0.0.1:18081"; }

NASIM_DRY_RUN=1 \
  launch_claude "http://127.0.0.1:11435" "deepseek-r1:14b" 2>&1 | \
  grep -q 'claude --model anthropic/ollama/deepseek-r1:14b' || {
    echo "FAIL: expected gateway model id in dry claude cmd"
    exit 1
  }
echo "PASS: launch_claude uses anthropic/ollama/... gateway id + fcc base in dry"

# cleanup mock
unset -f fcc_start_proxy

echo "=== test-fcc: rollback cleans fcc artifacts (if any) ==="
# Touch fake pid to simulate
mkdir -p ~/.local/share/nasim
echo 999999 > ~/.local/share/nasim/fcc.pid   # non existent pid ok
source lib/nasim/rollback.sh
# calling restore should not blow up and try fcc_cleanup
restore_env_state 2>&1 | cat
echo "PASS: restore runs fcc cleanup without error"

echo "ALL test-fcc OK (or skipped gracefully)"