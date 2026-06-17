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

# Smart launch (auto-detect agent, reuse tunnel, inject project context)
nasim start && nasim code        # ... work ... then:  nasim stop

# Non-interactive (CI, scripts, or when you know the choice)
nasim launch --access ssh-tunnel --agent claude --model deepseek-r1:14b
nasim launch --access litellm --agent aider --model qwen3:8b
nasim launch --access tailscale --agent opencode --model deepseek-r1:32b   # falls back gracefully if no ts

# After setup you are dropped straight into the interactive frontier agent (or a branded terminal shell).
```

The `nasim` CLI (Python package `src/nasim`, launched by `bin/nasim`) supports **every** solution from the research:
- Transports: ssh-tunnel (primary, ad-hoc with trap cleanup, free port), tailscale (MagicDNS + detection), litellm (proxy layer + config).
- Agents: claude (native ANTHROPIC_BASE_URL), aider (OLLAMA_API_BASE), opencode, terminal (full-env branded shell so you can run anything).
- Plus: `nasim doctor` (probe + black GPU state), `nasim tunnel install-systemd` (persistent autossh user unit), legacy `nasim claude` / `nasim aider` still work.

All combinations are covered by `python -m pytest test/` (including the gating clean-toggle safety tests) and the GHA matrix in `.github/workflows/ci.yml` (pytest + dry-run access×agent matrix). Live checks against real black (SSH) + models (gemma4, qwen3, deepseek-r1, etc.) run locally via `nasim doctor` / `nasim models`.

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

## Environment safety — the clean toggle

When nasim closes — cleanly, via Ctrl-C, or on a crash — Claude Code returns to
**100% defaults**: no leftover Ollama models in the `/model` picker and your original
active model restored. This is enforced two ways:

- **Scoped env.** Agents launch as child processes whose `ANTHROPIC_*` environment is
  passed only to that child, so your shell is never modified.
- **Reversible Claude config.** The chosen Ollama model is injected into Claude's
  `/model` picker (`~/.claude.json`, stamped `{"_nasim": true}`) and the active model
  in `~/.claude/settings.json` is backed up. On exit, every marked entry is removed and
  the original model restored — a full inject→eject round-trip is byte-for-byte
  identical. The same cleanup runs from `atexit`/signal handlers and on the next nasim
  run, so a crash never strands an Ollama selection in plain `claude`.

Verify with `nasim env diff`.

## Project Structure (Python)
- `bin/nasim` — thin launcher; resolves the package and hands off argv.
- `src/nasim/` — the implementation (layered: controller → service → adapters):
  - `config.py` — external config (defaults < file < env < CLI)
  - `claude_settings.py` + `rollback.py` — the clean-toggle safety core
  - `transport/` — pluggable access strategies (`ssh`, `tailscale`, `litellm`)
  - `agents/` — pluggable agent launchers (`claude`, `aider`, `opencode`, `grok`, `terminal`)
  - `probe.py`, `fcc.py`, `daemon.py`, `code.py`, `select.py`, `orchestration.py`, `cli.py`
  - `vram.py`, `context.py`, `kb.py`, `session.py` — feature modules
- `test/` — pytest suite, including the gating clean-toggle safety tests.
- `pyproject.toml` — package metadata + the `nasim` console script.
- `.grok/` / `.claude/` — knowledge surfaces only. Code lives at the visible root.
- `.github/workflows/ci.yml` — pytest + shim + dry-run access×agent matrix.

Install: `./setup.sh` (or `./setup.sh --dev` for an editable install). Run the suite
with `python -m pytest test/`.

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
