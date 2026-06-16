# Nasim — Project AGENTS.md (Grok-native)

Nasim is the living, search-first knowledge base + minimal tooling for getting maximum real-world benefit from local and remote LLM inference for frontier-style agentic coding (Claude Code, OpenCode, Aider, Continue, Grok CLI equivalents, etc.).

## Identity & Scope
- Primary: `.grok/` (this tree) is the single source of truth for setup, recipes, model guidance, research logs, and rules.
- Goal: On laptop, run the best available agentic coding experiences (Claude Code UX or equivalents) powered by strong models on remote "black" (Ollama + GPU), using current ecosystem solutions. Never reinvent what Ollama, LiteLLM, Tailscale, Aider, Continue, OpenCode, official installers, etc. already do well.
- Always search current available solutions (web + X + GitHub + official docs) before writing code or docs. Update this knowledge on material changes.
- Thin glue/scripts only when they remove repeated toil (persistent tunnels, env wrappers, health, one-command status) and are themselves well-tested and minimal.

## Style (project)
- Terse. No emoji unless requested. No trailing summaries.
- Code comments only for non-obvious WHY.
- Single return per function; `(success, result)` tuples for fallible ops.
- Absolute paths in references when needed for clarity; otherwise relative to project root.
- Markdown tables, lists, code fences for recipes.
- Research logs live under `.grok/research/`. Recipes (actionable how-tos) under `.grok/recipes/`.
- Follow global Grok rules (conventional commits, knowledge-sync with sibling if present, zero public Bitbucket AI dirs, etc.).

## Git (mandatory)
- Conventional Commits only. Use `/conventional-commit` skill or `~/.grok/bin/auto-commit.sh`.
- Work on `feature/salim-hp` (or machine feature). Never direct to main/develop.
- After changes: commit → (optional push). Post-commit hook (if installed) handles private GitHub enrichment.
- Register project for daemon parity if using knowledge-sync across agents/machines.

## Key Principles (non-negotiable)
- Search first, use existing: official `ollama launch claude`, `ANTHROPIC_*` envs, Tailscale/SSH, LiteLLM, Aider `--model ollama/...`, Continue baseUrl, etc.
- Remote Ollama access: secure by default (Tailscale preferred; SSH tunnels with autossh; localhost-only on black + private network). No public exposure.
- Model fit: GPU-resident only for agent loops. Verify with `ollama ps` / API on black.
- Capability is model-bound under load. Plumbing (the old bridge) is solved; the frontier experience ceiling is the chosen model + context + agent scaffolding.
- .grok/ + recipes must stay current. Re-search before claiming "best" or implementing new helpers.

## Common Commands (see recipes/)
- Research source: `.grok/research/2026-06-16-frontier-agents-with-local-remote-ollama.md`
- Practical setups: `.grok/recipes/`
- Update knowledge: fresh web searches + edit here + conventional commit.

See also global `~/.grok/AGENTS.md` and project `.claude/` (if parity maintained via sync).

This file + `.grok/` = the project brain. Keep high-signal.
