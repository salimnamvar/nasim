#!/usr/bin/env bash
# Nasim CI/CD loop runner — plan→code→build→test→release→deploy→operate→monitor.
# The discipline is documented in .claude/rules/cicd-loop.md; this is the artifact.
#
# Stages, in order:
#   1 lint         ruff + black --check + import smoke        (gating)
#   2 unit         pytest test/unit (no network)             (gating)
#   3 deploy       push bridge to the server, await /health   (gating for live)
#   4 integration  pytest -m integration (live bridge)        (report)
#   5 capability   pytest -m capability  (API matrix)         (report)
#   6 rollback     pytest -m rollback    (start/stop)         (report)
#   7 e2e          pytest -m e2e (real claude binary)         (report, opt-in E2E=1)
#
# Gating stages stop the loop on failure (no point testing live against broken
# code). Report stages all run so you see the whole matrix in one pass.
#
# Usage:  bash bin/loop.sh            # stages 1–6
#         E2E=1 bash bin/loop.sh      # also stage 7
#         bash bin/loop.sh --no-deploy   # skip deploy (test the already-running bridge)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
export PYTHONPATH="src:${PYTHONPATH:-}"

E2E="${E2E:-0}"
DO_DEPLOY=1
[ "${1:-}" = "--no-deploy" ] && DO_DEPLOY=0

REMOTE_HOST="$(python3 -c 'from nasim.config import Config; print(Config.load().remote_host)' 2>/dev/null || echo black)"

names=()
results=()
record() { names+=("$1"); results+=("$2"); }

hr() { printf '%s\n' "────────────────────────────────────────────────────────────"; }
banner() { echo; hr; echo "▶ $1"; hr; }

# A gating stage: on failure, print the matrix and exit non-zero.
gate() {
    local label="$1"; shift
    banner "$label"
    if "$@"; then
        record "$label" PASS
    else
        record "$label" FAIL
        echo "✗ gating stage '$label' failed — stopping loop." >&2
        report
        exit 1
    fi
}

# A report stage: run, record, continue regardless.
report_stage() {
    local label="$1"; shift
    banner "$label"
    if "$@"; then
        record "$label" PASS
    else
        record "$label" FAIL
    fi
}

skip_stage() {
    record "$1" "SKIP ($2)"
    banner "$1"
    echo "⏭  skipped: $2"
}

ssh_reachable() {
    timeout 12 ssh -o BatchMode=yes -o ConnectTimeout=8 "$REMOTE_HOST" true 2>/dev/null
}

report() {
    echo
    hr
    echo "  NASIM CI/CD LOOP — RESULT MATRIX"
    hr
    local i
    for i in "${!names[@]}"; do
        printf "  %-14s %s\n" "${names[$i]}" "${results[$i]}"
    done
    hr
    local fails=0
    for r in "${results[@]}"; do [[ "$r" == FAIL* ]] && fails=$((fails + 1)); done
    if [ "$fails" -eq 0 ]; then
        echo "  ✓ all run stages green"
    else
        echo "  ✗ $fails stage(s) failed"
    fi
    hr
}

echo "Nasim loop @ $(date '+%F %T')  server=${REMOTE_HOST}  e2e=${E2E}  deploy=${DO_DEPLOY}"

# ── gating: lint + unit ─────────────────────────────────────────────────────
gate "lint" make lint
gate "unit" make unit

# ── live stages: require the server ─────────────────────────────────────────
if ssh_reachable; then
    if [ "$DO_DEPLOY" -eq 1 ]; then
        gate "deploy" make deploy
    else
        skip_stage "deploy" "--no-deploy"
    fi
    report_stage "integration" make integration
    report_stage "capability" make capability
    report_stage "rollback" make rollback
    if [ "$E2E" -eq 1 ]; then
        report_stage "e2e" make e2e
    else
        skip_stage "e2e" "set E2E=1 to run"
    fi
else
    for s in deploy integration capability rollback e2e; do
        skip_stage "$s" "server ${REMOTE_HOST} unreachable"
    done
fi

report

# Exit non-zero if any stage failed (for CI).
for r in "${results[@]}"; do [[ "$r" == FAIL* ]] && exit 1; done
exit 0
