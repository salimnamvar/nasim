# LiteLLM When You Need More Than Direct Ollama

Use the native path (remote-claude-code.md) when you just want Claude Code ↔ Ollama on black.

Use LiteLLM on the laptop (or on black) when you want:

- One `ANTHROPIC_BASE_URL` for Claude Code that can route "sonnet" to local big model on black, "haiku" to fast local, and fall back to OpenRouter / xAI / Anthropic cloud for hard problems.
- Logging, cost tracking, or auth layer in front of the remote Ollama.
- Support for providers that don't speak Anthropic natively (point LiteLLM at them, then point Claude Code at LiteLLM).
- OpenAI-compatible front for tools that prefer `/v1/chat/completions` while still serving Anthropic-shaped requests.

Quick laptop setup (tunnel/Tailscale to black already up):
```bash
pip install 'litellm[proxy]'
```

Minimal config for "black primary + cloud fallback":
```yaml
# litellm_config.yaml
model_list:
  - model_name: black-default
    litellm_params:
      model: ollama/qwen3-coder:14b
      api_base: "http://127.0.0.1:11435"

  - model_name: black-fast
    litellm_params:
      model: ollama/qwen3-coder:7b
      api_base: "http://127.0.0.1:11435"

  # Example cloud for reference quality
  - model_name: reference-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY
```

Run:
```bash
litellm --config litellm_config.yaml --port 4000
```

Point Claude Code:
```bash
export ANTHROPIC_BASE_URL=http://localhost:4000
export ANTHROPIC_AUTH_TOKEN=sk-litellm   # whatever you set as master key if any
claude --model black-default
```

See LiteLLM docs for full routing, fallbacks, caching, and the Anthropic passthrough mode.

LiteLLM is the standard "don't build your own proxy" answer in 2026 searches.
