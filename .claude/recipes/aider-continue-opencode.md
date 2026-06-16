# Aider, Continue.dev, OpenCode with Remote Ollama on black

These are mature, first-class ways to get agentic (or near-agentic) coding against your remote models. Often lower friction than routing everything through the Anthropic-shaped Claude Code path.

## Aider (terminal, git-centric)
Install (laptop):
```bash
pip install aider-chat
```

Remote Ollama (after tunnel or Tailscale up):
```bash
# OpenAI-compatible endpoint that Ollama exposes
aider --model ollama/qwen3-coder:14b \
      --ollama-api-base http://127.0.0.1:11435   # or black:11434
```

Or set env and use shorter:
```bash
export OLLAMA_API_BASE=http://127.0.0.1:11435
aider --model ollama/qwen3-coder:14b
```

Strengths: repo map, excellent for multi-file refactors, / commands, works great with local models in practice.

## Continue.dev (VS Code / JetBrains)
In `~/.continue/config.json` (or project-level):
```json
{
  "models": [
    {
      "title": "Black Qwen Coder",
      "provider": "ollama",
      "model": "qwen3-coder:14b",
      "baseUrl": "http://127.0.0.1:11435"
    }
  ],
  "tabAutocompleteModel": { ... same pattern ... }
}
```

Restart Continue. Use the chat sidebar or Cmd/Ctrl+I for inline edits. Supports custom context, commands, agents.

For remote: just the baseUrl change. Works with both SSH tunnel and Tailscale.

## OpenCode (opencode) — Open-Source Claude Code Alternative
- Install per current docs (often `npm` or direct binary; check GitHub anomalyco/opencode or official).
- Config supports Ollama / OpenAI-compatible providers directly.
- Point at your forwarded/remote endpoint (standard OpenAI or Anthropic compat if available).
- Many 2026 comparisons position it as the flexible, local-first choice when you don't want to be locked to one provider's binary.

Example (typical): in its config or env, set provider to ollama + base URL + model tag.

Advantages: multi-provider (local + any cloud), no Anthropic tax, explicit cost/token visibility, good agentic UX.

## When to Choose Which
- Want the exact "Claude Code" UX and features (MCP, sub-agents in its specific way, plan mode, official Anthropic tools): use real `claude` binary + native Ollama Anthropic compat (remote-claude-code.md).
- Daily driver, heavy git work, want something that "just works" great with local models today: **Aider**.
- Live in VS Code and want autocomplete + powerful chat/agent inside editor: **Continue**.
- Want one flexible open agent binary that can route to anything (local Ollama, Grok, Claude cloud, etc.) without lock-in: **OpenCode**.
- Specific "Grok Code Fast" speed profile: use the IDEs/agents that integrated grok-code-fast-1 (Cline, Roo, Cursor, opencode, etc.) against xAI, or use strong local models in the above for the local equivalent.

All of them work with the same remote Ollama access layer (tunnel/Tailscale/LiteLLM). Choose the frontend that matches your workflow; the model on black does the heavy lifting.

See research doc for links and 2026 context.
