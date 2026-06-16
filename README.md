# Nasim

**Nasim** is your practical, search-first setup for running frontier AI coding agents (Claude Code, OpenCode, Aider, Continue, Grok CLI-style, etc.) on your laptop while using powerful local models served by Ollama on a remote machine ("black").

## Philosophy
- **Search current solutions first.** We document what actually exists and works in 2026 (native Anthropic compat in Ollama, Tailscale for remote, LiteLLM when you need routing, mature open agents like Aider/Continue/OpenCode). We only add thin, high-value glue.
- **.grok/ is the source of truth.** Living research, recipes, rules, and model guidance live here. Update it by re-searching before changes.
- Real agentic coding (read/write/edit files, bash, multi-step, sub-agents) executes on the laptop where you run the agent. The remote model (on black) only decides *what* to do via tool calls.
- Maximize local benefit: strong GPU-resident models on black + secure always-on access + the best agent frontends.

## Quick Start — Claude Code on Laptop + Ollama on black (Native Path)
Ollama (v0.14+) speaks the Anthropic Messages API directly. The official Claude Code CLI just works.

1. On **black** (the server):
   - Ollama installed and running (`ollama serve` or systemd).
   - Pull a strong coding model that fits the GPU fully, e.g.:
     ```bash
     ollama pull qwen3-coder:14b   # or qwen3-coder, gemma4:xx, deepseek-coder-v2:16b, etc.
     ```
   - Verify it stays on GPU: `ollama ps` (or the API `/api/ps`).

2. Secure access from laptop to black:11434 (choose one):
   - **Preferred (set-and-forget):** Tailscale on both machines. Access via MagicDNS (e.g. `http://black:11434`).
   - **Simple persistent:** `autossh` or systemd user service doing `ssh -N -L 11435:localhost:11434 black`.

3. On **laptop** (in the shell where you will run the agent):
   ```bash
   # Point Claude Code at the forwarded/remote Ollama
   export ANTHROPIC_AUTH_TOKEN=ollama
   export ANTHROPIC_BASE_URL=http://127.0.0.1:11435   # or http://black:11434 via Tailscale
   export ANTHROPIC_API_KEY=""

   # Run the real Claude Code binary against a model on black
   claude --model qwen3-coder:14b
   ```
   Or if available on your setup:
   ```bash
   ollama launch claude --model qwen3-coder:14b
   ```

Full details, persistent tunnel recipes, Tailscale setup, model selection, GPU-fit checks, and fallbacks: see `.grok/recipes/` and the research log.

## Other High-Value Agents (All Work With Remote Ollama)
- **OpenCode (opencode)**: Excellent open-source Claude Code alternative. Native multi-provider + Ollama support.
- **Aider**: `aider --model ollama/qwen3-coder:14b` (or configure remote base URL). Mature git-centric workflow.
- **Continue.dev**: VS Code / JetBrains. Set `baseUrl` to your tunneled/remote Ollama in `config.json`.
- **Cline / Roo Code / Kilo Code**: Agentic VS Code experiences with full local model support.
- **grok-cli variants**: For xAI Grok API primarily; some accept Ollama as provider for local equivalent feel.

See `.grok/recipes/` for exact remote configs.

## Current Research Snapshot (as of 2026-06-16)
See `.grok/research/2026-06-16-frontier-agents-with-local-remote-ollama.md` for:
- Why the old custom bridge is obsolete (Ollama native compat).
- Remote access patterns (Tailscale > SSH tunnel > LiteLLM).
- "Grok Code" options (grok-code-fast-1 in supported IDE agents + grok-cli; local equivalents via strong open models in flexible agents).
- Model recommendations (Qwen3-Coder series, GLM-5.1, DeepSeek V4, Gemma 4 — size to GPU, verify no CPU spill for agent loops).
- Anti-patterns and security.

## Project Structure
- `.grok/` — everything important (AGENTS.md, research logs, recipes, rules).
- `README.md` — this file (points at .grok).
- Thin optional `bin/` or scripts only for real convenience (documented in recipes).

## Getting the Most Benefit
- Reproduce real work: multi-file edits, bash execution, planning → write loops.
- Keep models GPU-resident on black.
- Use large context (64k+ where possible).
- Hybrid: fast local model for exploration + heavy remote for synthesis.
- Re-search the ecosystem before adding features or claiming superiority.

## Contributing / Updating Knowledge
- Always start with fresh searches for "claude code ollama", "opencode ollama remote", "best ollama agentic coding models", Tailscale/WireGuard remote LLM patterns, etc.
- Edit under `.grok/`.
- Conventional commit.
- Keep this practical and current.

Start here: `.grok/research/2026-06-16-frontier-agents-with-local-remote-ollama.md` and `.grok/recipes/`.

Zero cost. Maximum privacy. Frontier agent experience on your hardware + remote GPU.
