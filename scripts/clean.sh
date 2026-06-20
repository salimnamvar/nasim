#!/usr/bin/env bash
# Environment / build artifact cleanser for nasim.
#
# Removes temporary generated files that pollute the tree or VS Code.
# Safe to run anytime. Does not touch source under nasim/, your conda env, or
# committed research data unless they match temp patterns.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="${1:-}"

log() { printf 'clean: %s\n' "$*" >&2; }
do_rm() {
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "  (dry) rm -rf $*"
  else
    rm -rf "$@"
  fi
}

cd "${PROJECT_ROOT}"

log "Cleaning temporary python/build artifacts (scoped to nasim)..."

# Bytecode
find . -type d -name '__pycache__' -exec sh -c 'for d; do [ -d "$d" ] && do_rm "$d"; done' sh {} + 2>/dev/null || true
find . -type f \( -name '*.py[co]' -o -name '*$.py.class' \) -delete 2>/dev/null || true

# Packaging
find . -type d -name '*.egg-info' -exec sh -c 'for d; do [ -d "$d" ] && do_rm "$d"; done' sh {} + 2>/dev/null || true
do_rm -rf nasim.egg-info .eggs/ MANIFEST 2>/dev/null || true

# Build
do_rm -rf build/ dist/ 2>/dev/null || true

# Tool caches
do_rm -rf .ruff_cache/ .pytest_cache/ .mypy_cache/ .hypothesis/ .nox/ .tox/ 2>/dev/null || true

# Coverage
do_rm -f .coverage .coverage.* coverage.xml htmlcov/ 2>/dev/null || true

# Other temp
do_rm -rf .cache/ *.tmp 2>/dev/null || true

log "Clean complete."
if [[ "$DRY_RUN" != "--dry-run" ]]; then
  log "Tip: re-run 'pip install -e \"[dev]\"' if you want fresh metadata."
fi
