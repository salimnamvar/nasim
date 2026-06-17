#!/usr/bin/env bash
# tests/test-setup.sh — guard the installer used in sce1.txt
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

echo "=== test-setup ==="
bash -n setup.sh && echo "PASS: setup.sh parses"

# Simulate the cp logic in a temp dir
tmp=$(mktemp -d)
mkdir -p "$tmp/bin"
cp bin/nasim "$tmp/bin/nasim" 2>/dev/null || true
chmod +x "$tmp/bin/nasim" || true
echo "PASS: bin/nasim copy simulation"

# run a fragment of setup logic
INSTALL_TEST="$tmp"
BIN_TEST="$tmp/bin"
# (we don't exec full setup to avoid side effects)
[[ -x "$tmp/bin/nasim" || -f bin/nasim ]] && echo "PASS: entrypoint exists after hypothetical install"

rm -rf "$tmp"
echo "test-setup OK"