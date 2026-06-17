# Nasim — Project CLAUDE.md (Claude-native, parity with .grok/AGENTS.md via knowledge-sync)

Nasim is the living, search-first knowledge base + minimal tooling for getting maximum real-world benefit from local and remote LLM inference for frontier-style agentic coding (Claude Code, OpenCode, Aider, Continue, Grok CLI equivalents, etc.). 

This .claude/ tree is the Claude view; it is kept in exact mtime-driven peer parity with the sibling .grok/ tree in this project by `knowledge-sync.sh project-register` + `project-sync` (daemon watches). Sprint.md lives only here per global rules.

## Identity & Scope
- Primary: both `.grok/` and `.claude/` (this tree) at project root are sources of truth for knowledge. The project code (`bin/nasim`, tests, etc.) lives at the visible project root, outside the dot-knowledge dirs.
- New in this sprint (2026-06-16): full `nasim select` interactive + non-interactive support for **all** solutions (SSH tunnel, Tailscale, LiteLLM proxy) + all terminal frontends (claude native, aider, opencode, raw configured terminal). Every combo covered by CI matrix + live tests against black.
- Goal: On laptop, run the best available agentic coding experiences powered by strong models on remote "black" (Ollama + GPU). Use current ecosystem. Thin glue only (the selector/launcher + tests + CI). Never reinvent.
- Always search current solutions first. Update research on material ecosystem shifts.

## Style (project)
- Follow global (terse, single return where reasonable, conventional commits, etc.).
- Design chain + sprint.md (this side) for the work.
- .claude/ is **never** pushed to Bitbucket origin (gitignored); enriched only to personal gh-private via post-commit hook.

## Git (mandatory)
- Same as global + .grok/AGENTS.md.
- Work on feature/salim-hp.
- After changes (especially slices that have "CI test passed"): conventional commit then push.

## Key Principles (non-negotiable) — updated for v2
- Search first, use existing: official `ollama launch claude`, `ANTHROPIC_*` envs, Tailscale/SSH, LiteLLM, Aider `--model ollama/...` + `--ollama-api-base`, Continue baseUrl, etc.
- `nasim select` (or flags) is the single entry point for users to pick any combination of private remote Ollama access + frontier terminal agent. It handles transport bring-up, probe, env, launch.
- Remote Ollama access: secure by default (SSH tunnels first-class and live-testable; Tailscale when present; LiteLLM as optional proxy layer). No public exposure. P-Invariants in sprint.md enforced.
- Model fit: GPU-resident only for agent loops. nasim doctor/probe + recipes emphasize verification on black.
- CI/CD for each feature: new transport or agent support is only "complete" after addition to test matrix in .github/workflows/ci.yml, passing run of tests/nasim-features.sh (dry + live SSH where applicable), then commit.
- .grok/ + .claude/ parity via registration + project-sync + daemon. sprint.md (Claude side) tracks design state.
- Capability is model-bound. The selector makes all the good 2026 options trivial to use.

## Common Commands (see recipes/ and new select)
- `nasim select` — interactive (or flagged) chooser + launcher for any solution.
- `nasim claude`, `nasim aider` (legacy thin wrappers still work; now powered by the same modular code).
- `nasim status`, `nasim doctor` (probe reachability + model list on the remote).
- `nasim tunnel ...` — helpers for ad-hoc/persistent.
- Full details: `.grok/research/2026-06-16-...` (or .claude/research mirror), recipes/*, README.
- CI verification: the matrix jobs + local `tests/nasim-features.sh --all`.

See also global `~/.claude/CLAUDE.md` / `~/.grok/AGENTS.md`, the sprint.md in this .claude/rules/, and project .grok/AGENTS.md.

## Sprint
Active sprint and design layer status, ADs, ODs, P-Invariants: `.claude/rules/sprint.md`

This file + `.claude/` (and sibling .grok/) = the project brain for both agents. Keep high-signal and in parity.

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
Last project .grok<->.claude sync: 2026-06-17T01:11:28+04:00
