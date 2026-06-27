#!/usr/bin/env bash
# Scoped lint + format + strict type check for nasim only.
# Run from repo root or anywhere: bash scripts/lint.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

: "${BLACK:=$(command -v black || echo black)}"
: "${ISORT:=$(command -v isort || echo isort)}"
: "${RUFF:=$(command -v ruff || echo ruff)}"
: "${PYRIGHT:=$(command -v pyright || echo pyright)}"

SRC_DIR="${PROJECT_ROOT}/nasim"
SCRIPT_DIR_LINT="${PROJECT_ROOT}/scripts"

if [[ -x "${PROJECT_ROOT}/scripts/clean.sh" ]]; then
  "${PROJECT_ROOT}/scripts/clean.sh"
fi

echo "==> black (check) ${SRC_DIR} ${SCRIPT_DIR_LINT}"
"${BLACK}" --check --line-length 120 "${SRC_DIR}" "${SCRIPT_DIR_LINT}" || true

echo "==> isort (check-only)"
"${ISORT}" --check-only --profile google --line-length 120 "${SRC_DIR}" "${SCRIPT_DIR_LINT}" || true

echo "==> ruff check"
"${RUFF}" check "${SRC_DIR}" "${SCRIPT_DIR_LINT}" || true

echo "==> pyright (strict)"
( cd "${PROJECT_ROOT}" && "${PYRIGHT}" ) || true

echo "==> SQ enforcer (C4 fidelity + ref blocks)"
( cd "${PROJECT_ROOT}" && python docs/SQ/common/sq_enforce.py ) || true

echo "==> lint complete (some tools may have reported findings above)"
