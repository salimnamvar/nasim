# Nasim — Project AGENTS.md (Grok-native)

Nasim is the living, search-first knowledge base + minimal tooling for getting maximum real-world benefit from local and remote LLM inference for frontier-style agentic coding (Claude Code, OpenCode, Aider, Continue, Grok CLI equivalents, etc.).

## Identity & Scope
- Primary: `.grok/` (this tree) is the single source of truth for setup, recipes, model guidance, research logs, and rules. The sibling `.claude/` (registered via knowledge-sync) is kept in parity for Claude sessions (sprint.md lives only on .claude side per global rule).
- Goal: On laptop, run the best available agentic coding experiences (Claude Code UX or equivalents) powered by strong models on remote "black" (Ollama + GPU), using current ecosystem solutions. Never reinvent what Ollama, LiteLLM, Tailscale, Aider, Continue, OpenCode, official installers, etc. already do well.
- **v2 (this sprint):** `nasim select` makes **every** documented solution (SSH tunnel, Tailscale, LiteLLM) + every terminal frontier agent first-class and choosable from one command. Full CI/CD matrix "for each feature", live tests against black, automatic cleanup, doctor/probe. Then hand the user the interactive CLI (agent or configured terminal shell).
- Always search current available solutions (web + X + GitHub + official docs) before writing code or docs. Update this knowledge on material changes.
- Thin glue/scripts only when they remove repeated toil (persistent tunnels, env wrappers, the selector, health, one-command status) and are themselves well-tested and minimal.

## Style (project)
- Terse. No emoji unless requested. No trailing summaries.
- Code comments only for non-obvious WHY.
- Single return per function; `(success, result)` tuples for fallible ops.
- Absolute paths in references when needed for clarity; otherwise relative to project root.
- Markdown tables, lists, code fences for recipes.
- Research logs live under `.grok/research/`. Recipes under `.grok/recipes/`.
- Follow global Grok rules (conventional commits, knowledge-sync with sibling + globals, zero public Bitbucket AI dirs, .claude/ gitignored on BB, enriched to gh-private, etc.).
- Use design chain + sprint (on .claude side) for ambitious changes.

## Git (mandatory)
- Conventional Commits only. Use `/conventional-commit` skill or `~/.grok/bin/auto-commit.sh "..." [--push]`.
- Work on `feature/salim-hp` (or machine feature). Never direct to main/develop.
- After changes (especially after a feature slice + its CI test passes): commit → (optional push). Post-commit hook handles private GitHub enrichment.
- Register project for daemon parity: `knowledge-sync.sh project-register nasim <root>` (done in this sprint). Daemon + project-sync keep .grok/.claude surfaces live in parity on this machine.

## Key Principles (non-negotiable)
- Search first, use existing: official `ollama launch claude`, `ANTHROPIC_*` envs, Tailscale/SSH, LiteLLM, Aider `--model ollama/...`, Continue baseUrl, etc.
- `nasim select` (interactive or `nasim launch --access X --agent Y`) is the user-facing way to pick any private remote Ollama on black + any frontier terminal agent. It brings up the transport, probes, sets envs, launches (or provides branded terminal).
- Remote Ollama access: secure by default (SSH tunnels primary for testing here; Tailscale when available; LiteLLM as proxy on top). No public exposure. Enforce P-Invariants from sprint.
- Model fit: GPU-resident only for agent loops. Verify with `ollama ps` / API on black (nasim doctor helps).
- **CI/CD for each feature:** Add support for a new transport or agent only together with updates to the test harness + matrix in .github/workflows/ci.yml. Run the tests (local + CI job), verify, *then* go ahead and commit the slice.
- .grok/ + .claude/ in the project + registration = both agents see the same project brain instantly (daemon). Elevate generalizable patterns (e.g. new tunnel recipes) to globals.
- Capability is model-bound under load. Plumbing is solved (native + simple private paths); the frontier experience ceiling is the chosen model + context + agent scaffolding.
- .grok/ + recipes must stay current. Re-search before claiming "all solutions".

## Common Commands (see recipes/ + sprint)
- `nasim select` — the main thing (this sprint). Picks access + agent + model → secure path → probe → launch interactive CLI.
- Legacy thin still supported: `nasim claude`, `nasim aider`.
- `nasim status` / `nasim doctor` — quick + probing checks (used by tests).
- `nasim tunnel ...` — ad-hoc and persistent helpers.
- Core knowledge (always search-updated):
  - `.grok/research/2026-06-16-frontier-agents-with-local-remote-ollama.md` (and later dated entries)
  - `.grok/recipes/` (remote-claude-code.md, tunnel-setup.md, models.md, aider-continue-opencode.md, litellm-for-mixing.md, and new select-usage if extracted)
- CI: `.github/workflows/ci.yml` + `tests/nasim-features.sh` (matrix of every combo; must pass before slice "done").

See also global `~/.grok/AGENTS.md` (and sibling ~/.claude), project `.claude/CLAUDE.md` + `.claude/rules/sprint.md` (design state, layers, ADs/ODs/P-Invariants for this work).

## Sprint
The active sprint (C4/UC status, ADs, invariants, "test each then go ahead" tracking) lives in the .claude side (`.claude/rules/sprint.md`). Both sides stay in sync for recipes/research/bin.

This file + `.grok/` = the project brain. Keep high-signal. After changes run project knowledge sync.

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
Last project .grok<->.claude sync: 2026-06-16T20:56:41+04:00
