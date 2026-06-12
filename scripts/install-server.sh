#!/usr/bin/env bash
# install-server.sh — deploy Ollama + the Nasim Bridge to the model server.
# Run from the client (salim-hp); everything executes on the server via SSH.
#
# Usage: ./scripts/install-server.sh [host]
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${1:-black}"
DEFAULT_MODEL="${NASIM_DEFAULT_MODEL:-qwen2.5-coder:14b}"
FAST_MODEL="${NASIM_FAST_MODEL:-qwen2.5-coder:7b}"
NUM_CTX="${NASIM_NUM_CTX:-32768}"

echo "→ Checking SSH access to $HOST..."
ssh -o BatchMode=yes "$HOST" "echo ok" > /dev/null
REMOTE_USER=$(ssh "$HOST" whoami)
REMOTE_HOME=$(ssh "$HOST" 'echo $HOME')
REMOTE_DIR="$REMOTE_HOME/nasim-bridge"

echo "→ Installing Ollama (idempotent)..."
ssh "$HOST" "command -v ollama > /dev/null || curl -fsSL https://ollama.com/install.sh | sh"
ssh "$HOST" "sudo systemctl enable --now ollama"

echo "→ Pulling models ($DEFAULT_MODEL, $FAST_MODEL)..."
ssh "$HOST" "ollama pull $DEFAULT_MODEL && ollama pull $FAST_MODEL"

echo "→ Copying bridge source..."
ssh "$HOST" "mkdir -p $REMOTE_DIR"
scp -q "$REPO_DIR"/bridge/server.py "$REPO_DIR"/bridge/translator.py \
    "$REPO_DIR"/bridge/requirements.txt "$HOST:$REMOTE_DIR/"

echo "→ Creating venv and installing dependencies..."
ssh "$HOST" "cd $REMOTE_DIR && python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && .venv/bin/pip install -q -r requirements.txt"

echo "→ Installing systemd service..."
ssh "$HOST" "sudo tee /etc/systemd/system/nasim-bridge.service > /dev/null" << EOF
[Unit]
Description=Nasim Bridge — Anthropic API proxy to Ollama
After=network.target ollama.service
Requires=ollama.service

[Service]
Type=simple
User=$REMOTE_USER
WorkingDirectory=$REMOTE_DIR
ExecStart=$REMOTE_DIR/.venv/bin/uvicorn server:app --host 127.0.0.1 --port 8080
Restart=on-failure
RestartSec=5
Environment=OLLAMA_URL=http://localhost:11434
Environment=DEFAULT_MODEL=$DEFAULT_MODEL
Environment=FAST_MODEL=$FAST_MODEL
Environment=BRIDGE_NUM_CTX=$NUM_CTX

[Install]
WantedBy=multi-user.target
EOF
ssh "$HOST" "sudo systemctl daemon-reload && sudo systemctl enable nasim-bridge && sudo systemctl restart nasim-bridge"

sleep 2
echo "→ Health check..."
ssh "$HOST" "curl -fsS http://localhost:8080/health"
echo
echo "✓ Server install complete on $HOST."
