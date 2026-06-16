# Nasim

**Nasim** is your practical, search-first setup for running frontier AI coding agents (Claude Code, OpenCode, Aider, Continue, Grok CLI-style, etc.) on your laptop while using powerful local models served by Ollama on a remote machine ("black").

## Philosophy
- **Search current solutions first.** We document what actually exists and works in 2026 (native Anthropic compat in Ollama, Tailscale for remote, LiteLLM when you need routing, mature open agents like Aider/Continue/OpenCode). We only add thin, high-value glue.
- **.grok/ is the source of truth.** Living research, recipes, rules, and model guidance live here. Update it by re-searching before changes.
- Real agentic coding (read/write/edit files, bash, multi-step, sub-agents) executes on the laptop where you run the agent. The remote model (on black) only decides *what* to do via tool calls.
- Maximize local benefit: strong GPU-resident models on black + secure always-on access + the best agent frontends.

## Quick Start — `nasim select` (all solutions, 2026-06-16)

```bash
# Interactive (picks transport + agent + model, brings up private path, probes, launches the CLI)
./bin/nasim select

# Manage configuration (no more hard-coded values)
./bin/nasim config edit
./bin/nasim config show

# Agentic self-audit (the primary test method): launch a strong model and task it with auditing nasim
NASIM_RUN_SELF_AUDIT=1 ./tests/nasim-features.sh --self-audit
# Inside the agent: "Read all of nasim (bin/ + lib/), sprint, research. Find errors, improve modularity, update docs."

# Non-interactive (CI, scripts, or when you know the choice)
nasim launch --access ssh-tunnel --agent claude --model deepseek-r1:14b
nasim launch --access litellm --agent aider --model qwen3:8b
nasim launch --access tailscale --agent opencode --model deepseek-r1:32b   # falls back gracefully if no ts

# After setup you are dropped straight into the interactive frontier agent (or a branded terminal shell).
```

The `nasim` CLI (in `bin/nasim`) now supports **every** solution from the research:
- Transports: ssh-tunnel (primary, ad-hoc with trap cleanup, free port), tailscale (MagicDNS + detection), litellm (proxy layer + config).
- Agents: claude (native ANTHROPIC_BASE_URL), aider (OLLAMA_API_BASE), opencode, terminal (full-env branded shell so you can run anything).
- Plus: `nasim doctor` (probe + black GPU state), `nasim tunnel install-systemd` (persistent autossh user unit), legacy `nasim claude` / `nasim aider` still work.

All combinations are covered by the test harness (`tests/nasim-features.sh --all`) and the GHA matrix in `.github/workflows/ci.yml`. Live tests against real black (SSH) + models (gemma4, qwen2.5-coder, deepseek-r1 etc.) pass before every slice commit.

See `.grok/recipes/` (or .claude mirror), the research log, and `.claude/rules/sprint.md` (design state + P-Invariants).

## Classic manual path (still valid)
(Old quick-start steps for Claude Code etc. remain below for reference — `nasim select` is the recommended way now.)

(Previous manual export + ssh -L or Tailscale steps still work and are used internally by nasim.)

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

## Project Structure (Phase 2 — modular)
- `bin/nasim` — thin loader + entrypoint only.
- `lib/nasim/` — real implementation (separation of concerns):
  - `config.sh` — external config (AD-09)
  - `transport.sh` + `transports/*.sh` — pluggable access strategies (ssh, tailscale, litellm)
  - `agent.sh` + `agents/*.sh` — pluggable agent launchers
  - `probe.sh`, `orchestration.sh`, `ui.sh`, `cli.sh`
- `tests/nasim-features.sh` — comprehensive real (no-mock) tests + `--self-audit` meta tests that launch strong models via nasim to audit the project itself (the best always-followed test scenario).
- `.grok/` — knowledge surfaces only (research, recipes, sprint, design). Code lives at visible root.
- `README.md`, `.github/workflows/ci.yml` — docs + CI matrix enforcing the above.

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
