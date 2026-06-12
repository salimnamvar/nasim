#!/usr/bin/env bash
# sync-from-upstream.sh — pull the latest Claude Code release and rebuild Nasim.
#
# Claude Code is not open source: the npm package @anthropic-ai/claude-code
# ships a platform-native binary (bun-compiled ELF with the JS bundle embedded
# as text). Nasim is produced by downloading that binary and applying a
# same-length identity patch (see scripts/patch-binary.py).
#
# Usage: ./scripts/sync-from-upstream.sh [version]
#   version   npm version to sync (default: latest)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-latest}"
PLATFORM_PKG="@anthropic-ai/claude-code-linux-x64"
VENDOR_DIR="$REPO_DIR/vendor"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

echo "→ Resolving $PLATFORM_PKG@$VERSION..."
RESOLVED=$(npm view "$PLATFORM_PKG@$VERSION" version)
echo "  resolved: $RESOLVED"

if [[ -f "$VENDOR_DIR/.version" && "$(cat "$VENDOR_DIR/.version")" == "$RESOLVED" ]]; then
    echo "✓ Already on $RESOLVED — nothing to do."
    exit 0
fi

echo "→ Downloading..."
cd "$WORK_DIR"
npm pack "$PLATFORM_PKG@$RESOLVED" > /dev/null 2>&1
tar xzf anthropic-ai-claude-code-linux-x64-*.tgz package/claude

echo "→ Patching identity (claude → naseem, same-length binary patch)..."
mkdir -p "$VENDOR_DIR"
python3 "$REPO_DIR/scripts/patch-binary.py" package/claude "$VENDOR_DIR/naseem"

echo "→ Verifying patched binary..."
BANNER=$("$VENDOR_DIR/naseem" --version)
echo "  version banner: $BANNER"
case "$BANNER" in
    *Claude*) echo "FAIL: banner still mentions Claude"; exit 1 ;;
    *Naseem*) ;;
    *) echo "FAIL: unexpected banner"; exit 1 ;;
esac

echo "$RESOLVED" > "$VENDOR_DIR/.version"
date -u +%Y-%m-%dT%H:%M:%SZ > "$VENDOR_DIR/.sync-date"

"$REPO_DIR/scripts/audit-rename.sh"

echo "✓ Sync complete: Nasim is now Claude Code $RESOLVED (Naseem identity)."
echo "  Run scripts/install-client.sh to (re)install the nasim command."
