# Tunnel & Remote Access Recipes for Ollama on black

## Goal
Reliable, secure, low-maintenance access from laptop to `black:11434` (Ollama) without exposing anything publicly.

## Tailscale (preferred)
1. `tailscale up` on both machines (same tailnet / ACLs).
2. On black, decide bind:
   - Keep default localhost + rely on Tailscale (clients connect to black's tailnet IP/name).
   - Or `sudo systemctl edit ollama` (or env file) + `Environment=OLLAMA_HOST=0.0.0.0`, restart, firewall only tailnet.
3. Optional: Tailscale Serve for HTTPS proxy to the API.
4. On laptop clients:
   ```bash
   export ANTHROPIC_BASE_URL=http://black:11434   # MagicDNS
   # or http://100.x.y.z:11434
   ```

Advantages: works from anywhere, no port forwards to manage, access control, MagicDNS.

## SSH + autossh (no extra mesh)
See `remote-claude-code.md` for the systemd user unit example.

One-liner background:
```bash
autossh -M 0 -f -N -o "ServerAliveInterval 30" -L 11435:localhost:11434 black
```

Kill: `pkill -f 'ssh.*11435.*black'`

## LiteLLM on laptop (as unified front)
Install:
```bash
pip install 'litellm[proxy]'
```

`litellm_config.yaml` (example for remote Ollama via tunnel/Tailscale):
```yaml
model_list:
  - model_name: black-qwen-coder
    litellm_params:
      model: ollama/qwen3-coder:14b
      api_base: http://127.0.0.1:11435   # or Tailscale black:11434
      # api_key: ""   # usually not needed for Ollama

  # Add cloud models for fallback as needed
```

Run:
```bash
litellm --config litellm_config.yaml --port 4000
```

Point agents at it:
```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
# (for pure OpenAI compat agents use the /v1 base)
```

LiteLLM gives you one place for auth, logging, fallbacks, and routing across local remote + cloud.

## Verification
- From laptop: `curl $ANTHROPIC_BASE_URL/api/tags` (Ollama) or the health/model list your agent uses.
- During a Claude Code run: watch black with `ollama ps`, `nvidia-smi` (or equiv), and journal.

Security reminder: black's Ollama should never be reachable from the public internet. Tailscale or localhost+SSH only.
