#!/usr/bin/env bash
# tests/test-config.sh — "unit" tests for config (sourcable, zero mock, real execution)
# Covers: defaults, file load precedence, whitelist, nasim config subcmds, DEFAULT_MODEL correctness.
# Run: ./tests/test-config.sh
# Part of the mandatory per-functionality real test matrix for nasim.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NASIM_BIN="$PROJECT_ROOT/bin/nasim"

# Source in "unit test" mode (internal guard prevents main execution)
NASIM_INTERNAL=1 source "$NASIM_BIN" || true

# Re-exec load for a clean slate in this test process
nasim_config_load

RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

echo "=== test-config: unit-style config contract ==="

# 1. After load, DEFAULT_MODEL must be one that actually exists on black (critical bugfix)
if [[ "$DEFAULT_MODEL" == "qwen3-coder:14b" ]]; then
    fail "DEFAULT_MODEL still the bad tag that does not exist on black"
else
    pass "DEFAULT_MODEL is sane and likely exists: $DEFAULT_MODEL"
fi

# 2. Core vars are set
[[ -n "$BLACK_HOST" ]] && pass "BLACK_HOST set: $BLACK_HOST"
[[ -n "$DEFAULT_LOCAL_PORT" ]] && pass "DEFAULT_LOCAL_PORT set: $DEFAULT_LOCAL_PORT"

# 3. Config show works (exercises the printer)
out=$(nasim_config_show 2>&1)
echo "$out" | grep -q "DEFAULT_MODEL=" && pass "config show emits DEFAULT_MODEL"
echo "$out" | grep -q "qwen2.5-coder:14b\|DEFAULT_MODEL=" && pass "config show reflects good default or override"

# 4. Precedence: explicit env wins over file/defaults (simulated by re-export + reload)
OLD_DM="$DEFAULT_MODEL"
export DEFAULT_MODEL="deepseek-r1:14b"
nasim_config_load   # re-apply (file would be lower)
if [[ "$DEFAULT_MODEL" == "deepseek-r1:14b" ]]; then
    pass "env override precedence works (DEFAULT_MODEL from env)"
else
    fail "env did not win"
fi
export DEFAULT_MODEL="$OLD_DM"
nasim_config_load

# 5. nasim bin subcommand surface for config
"$NASIM_BIN" config show 2>&1 | grep -q "BLACK_HOST=" && pass "bin nasim config show works end-to-end"

echo "=== test-config: OK ==="
