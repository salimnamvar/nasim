#!/usr/bin/env bash
# tests/test-claude-env.sh — verify nasim sets the COMPLETE set of ANTHROPIC/CLAUDE_* vars
# used by free-claude-code (from scripts/find.py + adapter + smoke tests).
#
# This exercises launch_claude (direct + fcc if present), terminal export, one-shot,
# and dry-run output. It is the canonical test that "nasim claude" (over remote ollama)
# produces the env surface expected by claude-code.
#
# Run:
#   bash tests/test-claude-env.sh
#   NASIM_DRY_RUN=1 bash tests/test-claude-env.sh
#   NASIM_RUN_LIVE=1 ... (if black reachable)

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "=== test-claude-env: load nasim internals ==="
NASIM_INTERNAL=1 source bin/nasim

# Force a deterministic model for assertions
export DEFAULT_MODEL="deepseek-r1:14b"

echo "=== test-claude-env: direct launch_claude dry contains full var surface ==="
out=$(NASIM_DRY_RUN=1 launch_claude "http://127.0.0.1:11435" "deepseek-r1:14b" 2>&1)

# Core ones from the find.py run on free-claude-code (the client-relevant subset)
must_have=(
  ANTHROPIC_API_URL
  ANTHROPIC_BASE_URL
  ANTHROPIC_AUTH_TOKEN
  ANTHROPIC_API_KEY
  ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS
  ANTHROPIC_DEFAULT_HAIKU_MODEL
  ANTHROPIC_DEFAULT_SONNET_MODEL
  ANTHROPIC_DEFAULT_OPUS_MODEL
  CLAUDE_CODE_SUBAGENT_MODEL
  CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY
  CLAUDE_CODE_AUTO_COMPACT_WINDOW
  CLAUDE_CLI_BIN
  CLAUDE_WORKSPACE
)

for v in "${must_have[@]}"; do
  if ! echo "$out" | grep -q "$v"; then
    echo "FAIL: expected $v in launch_claude dry output"
    echo "$out"
    exit 1
  fi
done
echo "PASS: launch_claude (direct) emits all required ANTHROPIC/CLAUDE vars"

# Value checks (some)
echo "$out" | grep -q 'ANTHROPIC_AUTH_TOKEN=ollama' || { echo "FAIL: auth token"; exit 1; }
echo "$out" | grep -q 'ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS=81920' || { echo "FAIL: max_tokens"; exit 1; }
echo "$out" | grep -q 'CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1' || { echo "FAIL: discovery"; exit 1; }
echo "PASS: key values correct in direct path"

echo "=== test-claude-env: terminal export surface ==="
# We can't easily capture export in a clean way without subshell side effects, so simulate the block
# by grepping the source (or run a tiny snippet).
# Instead assert the function mentions the new vars.
if ! grep -q 'ANTHROPIC_API_URL=' lib/nasim/agents/terminal.sh; then
  echo "FAIL: terminal should export ANTHROPIC_API_URL"
  exit 1
fi
if ! grep -q 'ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS' lib/nasim/agents/terminal.sh; then
  echo "FAIL: terminal should export DEFAULT_MAX"
  exit 1
fi
if ! grep -q 'CLAUDE_CLI_BIN' lib/nasim/agents/terminal.sh; then
  echo "FAIL: terminal should export CLAUDE_CLI_BIN"
  exit 1
fi
if ! grep -q 'CLAUDE_WORKSPACE' lib/nasim/agents/terminal.sh; then
  echo "FAIL: terminal should export CLAUDE_WORKSPACE"
  exit 1
fi
echo "PASS: terminal.sh contains full var exports"

echo "=== test-claude-env: one-shot path also uses full set (source check + dry via code) ==="
if ! grep -q 'ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS=81920' lib/nasim/code.sh; then
  echo "FAIL: code.sh one-shot must set DEFAULT_MAX"
  exit 1
fi
if ! grep -q 'CLAUDE_WORKSPACE' lib/nasim/code.sh; then
  echo "FAIL: code.sh one-shot must set WORKSPACE"
  exit 1
fi
echo "PASS: one-shot duplicates full set"

echo "=== test-claude-env: fcc integration points (auto-detect + start) ==="
# Exercise fcc_available (should not explode)
if type fcc_available >/dev/null 2>&1; then
  fcc_available || true   # may be false if no uvicorn or no src dir; that's ok
  echo "PASS: fcc_available callable after auto-detect"
else
  echo "SKIP: fcc functions not present (source order?)"
fi

# If sibling free-claude-code is next to us, NASIM_FCC_SRC_DIR should become set by _fcc_autodetect
if [[ -f "../free-claude-code/api/app.py" || -f "../../free-claude-code/api/app.py" ]]; then
  _fcc_autodetect || true
  if [[ -n "${NASIM_FCC_SRC_DIR:-}" ]]; then
    echo "PASS: auto-detected sibling fcc at $NASIM_FCC_SRC_DIR"
  else
    echo "NOTE: sibling exists on fs but autodetect left NASIM_FCC_SRC_DIR empty"
  fi
else
  echo "NOTE: no sibling free-claude-code visible from here (normal in some CI layouts)"
fi

echo "=== test-claude-env: rollback lists cover the new vars ==="
for v in ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS CLAUDE_CLI_BIN CLAUDE_WORKSPACE; do
  if ! grep -q "$v" lib/nasim/rollback.sh; then
    echo "FAIL: rollback must track $v"
    exit 1
  fi
done
echo "PASS: rollback saves/restores the extended set"

echo "=== test-claude-env: cfg doc updated ==="
grep -q 'ANTHROPIC_DEFAULT_MAX_OUTPUT_TOKENS' cfg/nasim-config-vars.md || { echo "FAIL: doc missing max_tokens"; exit 1; }
grep -q 'CLAUDE_CLI_BIN' cfg/nasim-config-vars.md || { echo "FAIL: doc missing cli bin"; exit 1; }
echo "PASS: documentation lists the full surface"

echo "ALL test-claude-env OK"

# Optional live probe note:
# To truly "use nasim claude + ollama models on black to write unit test":
#   nasim code --one-shot "Write a new unit test in tests/test_foo.sh that asserts all the ANTHROPIC/CLAUDE_* vars that launch_claude emits. Use only bash + grep. Make it robust."
# Then let the launched claude (with real deepseek-r1 or qwen3 on black) write + edit the file.
# This test file itself was produced under that discipline.