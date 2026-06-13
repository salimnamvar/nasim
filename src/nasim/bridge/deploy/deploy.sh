#!/usr/bin/env bash
# Deploy the Nasim bridge to the configured server and restart the service.
#
# Reads the server, port, and model settings from the single config source
# (cfg/nasim.toml + env), syncs the package and config, renders the systemd unit
# from its template, restarts the service, and waits for /health.
#
# Override the remote bridge directory with NASIM_BRIDGE_DIR (default
# /home/salim/nasim-bridge).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="src:${PYTHONPATH:-}"

REMOTE_DIR="${NASIM_BRIDGE_DIR:-/home/salim/nasim-bridge}"

# ── pull settings from the single config source ─────────────────────────────
read -r HOST PORT OLLAMA DEF FAST NUMCTX KEEP TIMEOUT LOGLVL < <(python3 - <<'PY'
from nasim.config import Config
c = Config.load()
print(c.remote_host, c.bridge_port, c.ollama_url, c.default_model, c.fast_model,
      c.num_ctx, c.keep_alive, c.request_timeout, c.log_level)
PY
)

echo "Deploying bridge → ${HOST}:${REMOTE_DIR}  (port ${PORT}, default ${DEF})"

# ── 1. sync the package + config ────────────────────────────────────────────
ssh "$HOST" "mkdir -p ${REMOTE_DIR}/src ${REMOTE_DIR}/cfg"
rsync -az --delete --exclude '__pycache__' --exclude '*.pyc' \
    src/ "${HOST}:${REMOTE_DIR}/src/"
rsync -az --exclude 'nasim.local.toml' cfg/ "${HOST}:${REMOTE_DIR}/cfg/"

# Remove the superseded flat modules from the old layout, if present.
ssh "$HOST" "rm -f ${REMOTE_DIR}/server.py ${REMOTE_DIR}/translator.py"

# ── 2. ensure venv dependencies ─────────────────────────────────────────────
ssh "$HOST" "${REMOTE_DIR}/.venv/bin/pip install -q --upgrade fastapi uvicorn httpx"

# ── 3. render + install the systemd unit ────────────────────────────────────
sed -e "s|@REMOTE_DIR@|${REMOTE_DIR}|g" \
    -e "s|@PORT@|${PORT}|g" \
    -e "s|@OLLAMA@|${OLLAMA}|g" \
    -e "s|@DEF@|${DEF}|g" \
    -e "s|@FAST@|${FAST}|g" \
    -e "s|@NUMCTX@|${NUMCTX}|g" \
    -e "s|@KEEP@|${KEEP}|g" \
    -e "s|@TIMEOUT@|${TIMEOUT}|g" \
    -e "s|@LOGLVL@|${LOGLVL}|g" \
    src/nasim/bridge/deploy/nasim-bridge.service \
    | ssh "$HOST" "sudo tee /etc/systemd/system/nasim-bridge.service >/dev/null"

# ── 4. reload + restart ─────────────────────────────────────────────────────
ssh "$HOST" "sudo systemctl daemon-reload && sudo systemctl restart nasim-bridge.service"

# ── 5. wait for health ──────────────────────────────────────────────────────
printf 'Waiting for /health '
for _ in $(seq 1 30); do
    if ssh "$HOST" "curl -sf http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
        echo " ok"
        ssh "$HOST" "curl -sf http://127.0.0.1:${PORT}/health"
        echo
        exit 0
    fi
    printf '.'
    sleep 0.5
done

echo " FAILED — recent journal:"
ssh "$HOST" "sudo journalctl -u nasim-bridge.service --no-pager -n 40"
exit 1
