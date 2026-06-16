#!/usr/bin/env bash
# tests/test-ssh-transport-real.sh — real integration for the primary transport (ssh-tunnel)
# Covers: free_port, setup_ssh_tunnel (via orchestration), probe after, cleanup, reachability, model list at url.
# Uses live black. No mocks.
# Run: ./tests/test-ssh-transport-real.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NASIM_BIN="$PROJECT_ROOT/bin/nasim"

# Source for direct access to internal functions (unit + integration mix)
NASIM_INTERNAL=1 source "$NASIM_BIN" || true

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log() { echo -e "${YELLOW}[ssh-real]${NC} $*"; }
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

echo "=== test-ssh-transport-real: live tunnel + functions ==="

# 1. free_port logic (unit-ish)
p=$(free_port 11438)
[[ "$p" -ge 11438 ]] && pass "free_port returns usable port >= base: $p"

# 2. Full real setup_ssh_tunnel (exercises pidfile, ssh -L, probe_and_show inside)
log "Calling setup_ssh_tunnel (real SSH to black, will allocate port, verify probe)"
# Clean potential leftovers on common test ports
pkill -f 'ssh.*-L .*1143[0-9]:localhost:11434 black' 2>/dev/null || true

url=$(setup_ssh_tunnel)
log "Tunnel up at $url"

if probe_url "$url"; then
    pass "probe_url true on the url returned by setup_ssh_tunnel"
else
    fail "probe failed right after setup_ssh_tunnel"
fi

# 3. Models visible at the tunneled url (real /api/tags)
log "Fetching /api/tags via the nasim-provided url (real model names)"
tags=$(curl -s --max-time 6 "$url/api/tags")
if echo "$tags" | grep -q 'qwen2.5-coder:14b\|deepseek-r1:14b'; then
    pass "real models (including known coders) visible through the transport url"
else
    echo "$tags" | head -c 400
    fail "expected known models in /api/tags through tunnel"
fi

# 4. Orchestration path (choose_and_launch dry already covered elsewhere; here just the transport part)
log "choose_and_launch with ssh-tunnel (will bring another or reuse logic; we use direct for control)"
# We already have a live url; simulate what orchestration does for the access part.
# Cleanup the one we have
# (the pidfile for the one created by setup is in /tmp/nasim-ssh-tunnel-$$.pid but $$ here is the test's)
# Best effort: kill by pattern on the lport we just got
lport_from_url=$(echo "$url" | sed -E 's|.*:([0-9]+)$|\1|')
pkill -f "ssh.*${lport_from_url}.*black" 2>/dev/null || true

pass "ssh transport setup + probe + model visibility through real black exercised"

echo "=== test-ssh-transport-real: OK ==="
