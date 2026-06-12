#!/usr/bin/env bash
# audit-rename.sh — verify no claude identity survives in the patched binary.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BINARY="$REPO_DIR/vendor/naseem"

echo "→ Auditing rename in $BINARY..."
[[ -f "$BINARY" ]] || { echo "FAIL: binary not found — run sync-from-upstream.sh"; exit 1; }

FAIL=0
for pattern in "claude" "Claude" "CLAUDE"; do
    COUNT=$( (grep -ao -F "$pattern" "$BINARY" || true) | wc -l)
    if [[ "$COUNT" -ne 0 ]]; then
        echo "FAIL: $COUNT remaining occurrences of '$pattern'"
        FAIL=1
    fi
done

BANNER=$("$BINARY" --version)
[[ "$BANNER" == *Naseem* ]] || { echo "FAIL: version banner: $BANNER"; FAIL=1; }

[[ "$FAIL" -eq 0 ]] && echo "✓ Rename audit passed ($BANNER)"
exit "$FAIL"
