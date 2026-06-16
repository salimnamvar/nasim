# Sprint — Nasim Remote Ollama + Frontier Agents

This is the project sprint file (per global rules/software-design/sprint.md). Single source of truth for current work state, design layers, ADs/ODs/invariants.

## Current Sprint

**Name:** Nasim v2 — Universal `nasim select` for all remote Ollama solutions on black + full CI/CD per feature + .claude/.grok parity + global sync

**Status:** Active. Sprint setup + design layers initialized. Core implementation (select UX, SSH transport, claude/aider/opencode/terminal launchers, test harness, initial CI matrix) in progress. Incremental "implement feature slice → add CI test → run & verify → commit" flow. All solutions from research (Tailscale, SSH tunnels, LiteLLM, native agents) being made first-class selectable. Live testing against real black via SSH. Final: register project for knowledge-sync, propagate to ~/.grok + ~/.claude, full E2E verification.

**Target branch:** feature/salim-hp (machine feature; conventional commits; auto-merge via GitHub Actions to develop on push)

**Started:** 2026-06-16
**Owner:** Salim (salim-hp)

## Design Layer Status

| Layer | Location | Status | Notes |
| ----- | -------- | ------ | ----- |
| C4 | `.claude/docs/C4/` + `.grok/docs/C4/` | In Progress | Context diagram (laptop nasim selector → transports → black Ollama + agent frontends on client). Container level for the CLI tool. |
| UC | `.claude/docs/UC/` + `.grok/docs/UC/` | In Progress | UC-01 Select & Launch; UC-02 Manage Tunnel; 1-2 more for doctor/probe + persistent setup. |
| SM | `.claude/docs/SM/` | Not Started | States: tunnel-up / endpoint-verified / agent-running / error. Optional for v2. |
| SQ | (inline in recipes or docs/SQ) | Not Started | Sequence: user select → transport setup → probe reachability → env export → exec agent. |
| DATA Contracts | N/A (thin CLI + env vars + yaml for litellm) | Not Started | Simple; env contracts documented in recipes. |
| ERD | N/A | Not Started | No persistent data model. |
| Class Diagram | N/A (bash functions) | Not Started | Modular functions in nasim script act as "units". |
| API Spec | N/A | Not Started | None (CLI + env + subprocess). |
| Implementation | `.grok/bin/nasim` + `.claude/bin/nasim` + `tests/nasim-features.sh` + `.github/workflows/ci.yml` + docs updates | Current (Phase 1-2) | Slices: core select+ssh+claude (with CI), then agents, transports, litellm/persistent, full matrix. Tests prove each. |
| Sprint / Knowledge | `.claude/rules/sprint.md` + `.grok/AGENTS.md` + `.claude/CLAUDE.md` + research/ + recipes/ | In Progress | This file + parity sync via knowledge-sync project-register + daemon. |

## Versioning Policy

Nasim "releases" are knowledge + script bumps in the repo (no strict semver on the CLI yet; treat as internal tool).
- Document major UX or contract changes (new required env, removed transport) in AD + research log.
- Bump informal version in research header and README on significant deliveries.
- Sprint labels internal only.

## Key Architectural Decisions

### AD-01: Pure-bash single-file (or minimal) `nasim` CLI with zero mandatory external runtime deps for core select/launch
Chose this (over Python/Go rewrite) to match existing thin philosophy, work in any minimal terminal on salim-hp/black, easy to test in CI with only bash+curl+ssh. Optional nice-to-haves (fzf/gum) detected at runtime. All logic (transports, env builders, probes) as functions for testability via sourcing in harness.

### AD-02: Matrix-per-feature CI + executable test harness exercising every (access x agent) combo
"Use CI/CD for each feature and test it then go ahead." Implemented as .github/workflows/ci.yml with strategy.matrix.include + tests/nasim-features.sh that supports targeted + full runs. Dry-run mode + live SSH probe mode (real black reachable). Syntax (bash -n), env capture assertions, reachability curls. Run locally before commit; workflow runs on push for the gh-private side.

### AD-03: SSH tunnel as primary always-testable transport; Tailscale/LiteLLM as first-class but graceful-degrade options
Black is reliably reachable via plain SSH from salim-hp (no Tailscale on either at snapshot). All "test them all work" guarantees use SSH for live E2E. Select offers Tailscale (with runtime check `tailscale status`), falls back with clear message. LiteLLM treated as "proxy layer" on top of a base transport.

### AD-04: Project maintains both .grok/ and .claude/ at root for agent parity; sprint.md lives only under .claude/rules/
Per global sprint rule and knowledge-sync contract. .claude/ is gitignored on BB (enriched only to gh-private). knowledge-sync project-register + project-sync (daemon) keeps the two trees' shared surfaces (recipes, research, bin, rules) in mtime peer parity locally. New generalizable patterns elevated to globals via harvest/sync.

### AD-05: "cli terminal provided" means either direct exec of chosen frontier agent REPL or a branded configured shell
After transport ready + probe pass, `nasim select` either execs the specific agent (claude --model ..., aider ...) with correct envs (user stays in the agent until exit), or for "terminal" choice drops into interactive bash with NASIM_* and PS1 branding so user can manually invoke any supported agent or raw commands. Supports both "agent provided" and "terminal provided".

## Open Decisions

| ID | Decision | Status |
| -- | -------- | ------ |
| OD-01 | Exact command/flag surface for opencode with remote Ollama (OpenAI compat base vs native ollama provider vs `ollama launch opencode`). Default to setting OPENAI_BASE_URL style + model tag; verify on run. | Open (implement then confirm) |
| OD-02 | Should `nasim select` auto-start litellm proxy in background for the session (with trap kill) or require separate `nasim litellm start` + user manages? | Open (lean toward per-session helper for simplicity in select) |
| OD-03 | Add a small persistent config (~/.config/nasim/config.toml or env file) for default transport/agent/model + last-used? Or stay pure env + flags for now. | Open (start stateless, add later if toil) |
| OD-04 | How deep to go on persistent tunnel install (systemd user unit generation + enable) vs just print the autossh one-liner. | Open (generate both the cmd and a file the user can install) |

## Resolved Decisions

| ID | Decision | Resolution |
| -- | -------- | ---------- |
| (none yet in sprint; prior research ADs carried in 2026-06-16 research doc: native Ollama Anthropic compat obsoletes custom bridges; Tailscale > SSH > LiteLLM priority) | - | See research/2026-06-16... and recipes/ |

## P-Invariants

- **P01 (Private access only):** No nasim code path, recipe, or generated config ever sets OLLAMA_HOST=0.0.0.0 on black in a way that + firewall allows public internet, or uses plain port-forward without encryption (SSH/Tailscale only). All solutions enforce private network path.
- **P02 (Verify before launch):** Every launch path must attempt a reachability probe (curl <url>/api/tags or /api/ps) and succeed (or offer explicit bypass + warning) before exec'ing the frontier agent. Prevents silent "connected to wrong ollama".
- **P03 (Agent on laptop, inference on black):** File system ops, bash execution, sub-agent loops etc. always execute in the context of the machine running `nasim` (salim-hp laptop). The remote only serves model tokens via the API. (Enforced by construction: we only forward the *model* endpoint.)
- **P04 (Testable slices):** Every added transport or agent frontend must have a corresponding entry in the CI test matrix + passing harness run (dry + live where transport allows) before the slice is considered "done" and committed.
- **P05 (Parity surfaces):** After any material change to recipes/research/bin under .grok/, a project-sync (or daemon) must be runnable to reconcile into .claude/ (and vice-versa). sprint.md only mutated on .claude side.

---

Next actions tracked in this sprint file + todo (internal). Update tables/status immediately on decisions or layer progress. Re-search ecosystem on any external shift before claiming "all solutions".

Sources: global sprint rule, existing Nasim research 2026-06-16, recipes, connectivity (SSH to black confirmed 2026-06-16).