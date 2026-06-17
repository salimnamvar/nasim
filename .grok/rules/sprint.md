# Sprint — Nasim Remote Ollama + Frontier Agents

This is the project sprint file (per global rules/software-design/sprint.md). Single source of truth for current work state, design layers, ADs/ODs/invariants.

## Current Sprint

**Name:** Nasim v2 — Universal `nasim select` for all remote Ollama solutions on black + full CI/CD per feature + .claude/.grok parity + global sync

**Status:** Core slice delivered + tested. Phase 2 started: major refactor to modular layered design (SoC, DRY, pluggable adapters), external config, and primary testing via agentic self-audit (real black + frontier models launched by nasim itself used to audit/document the project and find/fix errors). "Use the tool to improve the tool with real models" is now the canonical test scenario. All previous combos + new meta-audits must pass real (no-mock) harness runs before slices.

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
| Class Diagram | N/A (bash modules + strategies) | In Progress | lib/nasim/*.sh with clear concerns (config, transport adapters, agent launchers, probes, ui, cli dispatch). "OOP" via function namespaces + strategy registration for pluggable transports/agents. Thin loader in bin/nasim. |
| API Spec | N/A | Not Started | None (CLI + env + subprocess). |
| Implementation | `bin/nasim` (Python launcher) + `src/nasim/` package (config, claude_settings, rollback, probe, fcc, transport/*, agents/*, daemon, code, select, orchestration, cli, vram, context, kb, session) + `pyproject.toml` + `test/` pytest + `.github/workflows/ci.yml` | Python rewrite (AD-11) | Full 1:1 parity translation from `lib/nasim/*.sh` to Python, plus the verifiable clean Claude Code toggle (byte-identical inject→eject on the real `~/.claude.json`; crash-safe via atexit/signals). 14 pytest pass (6 gating safety + 8 parity); dry-run access×agent matrix green; live `nasim models` lists black inventory. Bash `lib/nasim/*.sh` retained as legacy reference. |
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
Delivered and tested.

### AD-06: Test harness + GHA matrix as the enforcement mechanism for "CI/CD for each feature"
tests/nasim-features.sh + .github/workflows/ci.yml matrix.include now the contract. Local run with NASIM_RUN_LIVE_PROBE=1 gives real black proof; GHA exercises all dry paths + syntax for both .grok and .claude bins. Slice only complete after green run.

### AD-07: .claude/ + .grok/ dual trees + knowledge-sync project registration
Full mirror bootstrapped (cp of recipes/research + hand-written CLAUDE.md + sprint only on claude side + force-add for enrichment). `knowledge-sync.sh project-register nasim <root>` + `project-sync` keeps parity on this machine (daemon) and surfaces the new nasim selector knowledge for globals via harvest. .claude/ gitignored on BB.
After transport ready + probe pass, `nasim select` either execs the specific agent (claude --model ..., aider ...) with correct envs (user stays in the agent until exit), or for "terminal" choice drops into interactive bash with NASIM_* and PS1 branding so user can manually invoke any supported agent or raw commands. Supports both "agent provided" and "terminal provided".

### AD-08: Layered modular bash design (SoC, DRY, pluggable, scalable) — CSR spirit adapted for CLI
Moved from single-file monolith to thin `bin/nasim` loader + sourced `lib/nasim/` modules with clear boundaries:
- CLI/Controller layer (dispatch, menus, arg parsing, user I/O — kept very thin).
- Orchestration/"Service" layer (select flow, choose_and_launch coordination, env injection).
- Adapters (transports as strategies: ssh, tailscale, litellm; agents as strategies; config loader; probe/state; cleanup).
This gives separation of concerns and DRY (shared probe, port allocation, pid management, env builders) while staying pure-bash, sourceable for tests, zero mandatory deps. "OOP" via namespaced functions + runtime registration of strategies for easy extension (new transport/agent = drop-in file). "Repository" concerns = config + runtime state (pidfiles, active tunnels). Scalable vision: plugins, multiple profiles, future remote nasim control. CSR web terminology not applied literally (no HTTP, no DB aggregates) — project-specific adaptation recorded here to avoid anti-pattern bloat.

### AD-09: External configuration (resolves OD-03)
All previously hardcoded values (BLACK_HOST, ports, default model, litellm port, preferred orders, etc.) loaded from `~/.config/nasim/nasim.conf` (simple KEY=val or sourced env style, zero-dep parser) + ENV + CLI flags, with clear precedence (CLI/env override > config file > compiled defaults). Supports `nasim config edit | show | path`. Enables per-machine / per-user customization without editing code. Config changes are the primary way to scale/adapt without forking logic.

### AD-10: Agentic self-audit as the primary "all options" test scenario (meta-testing with real black + models)
The best and always-followed test method for nasim is to use nasim itself to launch frontier agents (claude, opencode, etc.) against strong models on black, then task those agents with auditing the nasim source, tests, sprint, research, recipes; finding feature errors/bugs; suggesting refactors for modularity; generating docs, additional test cases, and sprint updates. The test harness gains a `--self-audit` / meta target that exercises full launch paths (real probe + tunnel) + captures the agent's output as artifacts. "Test your all options" means every transport + every agent must be usable in such an agentic audit loop. No mocks for core paths; live black SSH + real model inference required for full green. This also serves as continuous documentation and forces the tool to be good enough for real heavy agent work on its own codebase.

### AD-11: Python rewrite (`src/nasim/`) + verifiable clean Claude Code toggle (2026-06-17)
The whole tool was translated from bash (`lib/nasim/*.sh`) to a layered Python package
`src/nasim/` (controller→service→adapters), following the global Python standards
(`a_` params, dataclasses, type hints, Google docstrings). `bin/nasim` became a thin
launcher that prefers the installed package and falls back to the in-repo `src/`.
Drivers: testability (pytest replaces the bash harness), maintainability, and a
**provable clean toggle**.

Clean toggle (resolves the user requirement "when I close nasim, Claude Code returns
to default and I don't see Ollama models in original Claude Code"):
- New `claude_settings.py` injects the chosen Ollama tag into Claude's `/model` picker
  (`~/.claude.json` `additionalModelOptionsCache`, each entry stamped `{"_nasim": true}`)
  and snapshots `~/.claude/settings.json` `"model"`. On stop/exit it ejects **all**
  marked entries (marker-based, idempotent) and restores the original model exactly
  (removing the key if it was originally absent). `sanitize()` runs on start AND stop to
  heal stray entries from a crashed/old session. Atomic writes preserve each file's
  newline style + UTF-8, so a full inject→eject is **byte-for-byte identical** (verified
  against a copy of the real 60KB `~/.claude.json`).
- Agents launch as child processes with a **scoped** `ANTHROPIC_*` env (parent shell
  never modified), via `subprocess.run`+wait (not `exec`) so a `try/finally` ejects after
  the agent exits. `rollback.EnvGuard` wires the same cleanup into `atexit` + SIGINT/
  SIGTERM/SIGHUP for crash safety.
- Gating pytest (`test/test_claude_settings.py`) asserts inject→eject removes all marked
  entries, restores/removes the model, is idempotent, and heals a stray entry without a
  backup. CI runs pytest + a dry-run access×agent matrix. Bash `lib/nasim/*.sh` retained
  as legacy reference (no longer the entrypoint); removal deferred to a follow-up.

## Open Decisions

| ID | Decision | Status |
| -- | -------- | ------ |
| OD-01 | Exact command/flag surface for opencode with remote Ollama (OpenAI compat base vs native ollama provider vs `ollama launch opencode`). Default to setting OPENAI_BASE_URL style + model tag; verify on run. | Open (implement then confirm) |
| OD-02 | Should `nasim select` auto-start litellm proxy in background for the session (with trap kill) or require separate `nasim litellm start` + user manages? | Open (lean toward per-session helper for simplicity in select) |
| OD-03 | Add a small persistent config (~/.config/nasim/config.toml or env file) for default transport/agent/model + last-used? Or stay pure env + flags for now. | Resolved by AD-09 (config file + precedence implemented; simple KEY=val format for zero-dep). |
| OD-04 | How deep to go on persistent tunnel install (systemd user unit generation + enable) vs just print the autossh one-liner. | Open (generate both the cmd and a file the user can install) |

## Resolved Decisions

| ID | Decision | Resolution |
| -- | -------- | ---------- |
| (none yet in sprint; prior research ADs carried in 2026-06-16 research doc: native Ollama Anthropic compat obsoletes custom bridges; Tailscale > SSH > LiteLLM priority) | - | See research/2026-06-16... and recipes/ |
| RD-01 (2026-06-16) | Serious user-reported breakage: no models shown under any select/doctor/launch, no models working with any clis (claude/aider/opencode), wrong defaults, probe output swallowed. | Fixed in one slice: corrected DEFAULT_MODEL everywhere (source + auto-created user conf), fixed probe_and_show output suppression, added first-class `nasim models` (ssh-direct, always works, no tunnel), emit full lists in doctor + before every launch, pre-launch existence warn on black inventory, expanded tests/ to 6+ dedicated real (no-mock) scripts exercising *every* access/agent/model combo + live inference. Real black models (via nasim transports) used to generate the root-cause analysis and code suggestions that informed/validated the fixes (see tests/audits/). Verified real claude binary reaches models over nasim url+envs. Full harness --all + --real-reasoning green repeatedly. |

## Current Status Note (2026-06-16 serious fix)
- `nasim models`, `nasim doctor`, launch flows now reliably surface the 13 models on black.
- All 4 agents x 3 accesses x multiple real models (including the ones that matter for agentic coding) have dedicated real test coverage + live black inference "OK" responses.
- AD-10 live: test-inference-reasoning.sh + --self-audit use qwen2.5-coder + deepseek-r1 etc. on black (launched via nasim ssh transport) to read symptoms, propose exact patches for probe/config/cli/ui/launchers, and generate helper code. Artifacts persisted. This is now the canonical way to evolve nasim.
- The suite (tests/nasim-features.sh --all / --real-reasoning / --self-audit) + individual test-*.sh is the "never done" mechanism. Re-run after any edit; they use the tool (real ollama on black) to improve the tool.
- P-invariants held (private ssh only, probe before launch, agent on laptop, testable slices).

## P-Invariants

- **P01 (Private access only):** No nasim code path, recipe, or generated config ever sets OLLAMA_HOST=0.0.0.0 on black in a way that + firewall allows public internet, or uses plain port-forward without encryption (SSH/Tailscale only). All solutions enforce private network path.
- **P02 (Verify before launch):** Every launch path must attempt a reachability probe (curl <url>/api/tags or /api/ps) and succeed (or offer explicit bypass + warning) before exec'ing the frontier agent. Prevents silent "connected to wrong ollama".
- **P03 (Agent on laptop, inference on black):** File system ops, bash execution, sub-agent loops etc. always execute in the context of the machine running `nasim` (salim-hp laptop). The remote only serves model tokens via the API. (Enforced by construction: we only forward the *model* endpoint.)
- **P04 (Testable slices):** Every added transport or agent frontend must have a corresponding entry in the CI test matrix + passing harness run (dry + live where transport allows) before the slice is considered "done" and committed.
- **P05 (Parity surfaces):** After any material change to recipes/research/bin under .grok/, a project-sync (or daemon) must be runnable to reconcile into .claude/ (and vice-versa). sprint.md only mutated on .claude side.

---

Next actions tracked in this sprint file + todo (internal). Update tables/status immediately on decisions or layer progress. Re-search ecosystem on any external shift before claiming "all solutions".

Sources: global sprint rule, existing Nasim research 2026-06-16, recipes, connectivity (SSH to black confirmed 2026-06-16).