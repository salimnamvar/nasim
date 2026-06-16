# Remote Claude Code + Ollama on "black" (Laptop Client)

This is the primary path for "frontier AI agent like Claude Code on my laptop, models on black".

## Prerequisites (black)
- Ollama installed and service running.
- A capable coding model pulled that **fits fully in GPU VRAM** (critical for agent loops).
  ```bash
  ollama pull qwen3-coder:14b
  # or qwen3-coder, gemma4:12b/26b (MoE), deepseek-coder-v2:16b, etc.
  ```
- Confirm GPU residency (no heavy CPU offload):
  ```bash
  curl http://localhost:11434/api/ps
  # or watch during a run; "VRAM: !!" style warnings in older tooling
  ```

Recommended context: 32k–128k+ (set via `OLLAMA_NUM_CTX` or Modelfile / API options).

## Secure Remote Access (laptop ↔ black)
**Option 1: Tailscale (recommended for daily use)**
- Install Tailscale on laptop + black.
- On black, keep Ollama on localhost (or `OLLAMA_HOST=0.0.0.0` + Tailscale ACLs/firewall allowing only your tailnet).
- Use MagicDNS name or Tailscale IP:
  ```bash
  export ANTHROPIC_BASE_URL=http://black:11434
  ```

**Option 2: Persistent SSH tunnel (autossh or systemd)**
Example systemd user unit on laptop (`~/.config/systemd/user/nasim-black-tunnel.service`):
```ini
[Unit]
Description=Persistent SSH tunnel to black Ollama (Anthropic port)
After=network.target

[Service]
ExecStart=/usr/bin/autossh -M 0 -N -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -L 11435:localhost:11434 black
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```
Enable:
```bash
systemctl --user daemon-reload
systemctl --user enable --now nasim-black-tunnel
```

One-off test:
```bash
ssh -L 11435:localhost:11434 black
```

Use port 11435 (or any free local) on laptop to avoid clashing with a local Ollama.

## Run Claude Code (laptop)
```bash
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_BASE_URL=http://127.0.0.1:11435   # or Tailscale http://black:11434
export ANTHROPIC_API_KEY=""
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1   # privacy (optional but good)

claude --model qwen3-coder:14b
```

Or the Ollama helper (if it respects the forwarded URL):
```bash
ANTHROPIC_BASE_URL=... ollama launch claude --model qwen3-coder:14b
```

**Install Claude Code (once):**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

## Switching / Hybrid
- To use real Anthropic cloud temporarily: unset the BASE_URL / AUTH_TOKEN (or use a different shell profile).
- For LiteLLM mixing (local on black + cloud fallbacks): run LiteLLM on laptop pointing at the tunneled Ollama, then point `ANTHROPIC_BASE_URL` at LiteLLM.

See also:
- `.grok/research/2026-06-16-frontier-agents-with-local-remote-ollama.md`
- `tunnel-setup.md` (more variants)
- `models.md`
- `litellm-for-mixing.md`

Test with a real task that mutates files (E01–E05 style from old matrix): the model must drive the full loop.
