# Sprint — State, Decisions, Matrix Progress

Updated continuously during the build. This is the live status of the rebuild.

## Goal

`nasim start` → `claude` uses local Ollama models on a configurable server, with
all Claude Code capabilities working; `nasim stop` → full rollback to the
Anthropic cloud. Decoupled OOP package, config in `cfg/`, tests in `test/`,
docs in `docs/`, driven by the CI/CD loop.

## Locked decisions (2026-06-13)

| # | Decision | Rationale |
| --- | --- | --- |
| D1 | **Full clean-room rewrite** into `src/nasim/` package | User choice; cleanest decoupled design. Rollback contract re-proven from zero. |
| D2 | **Exhaustive capability scope** (API + agentic e2e + client surface) | User choice; bounds in `rules/testing.md`. |
| D3 | Keep a **thin sourced bash shim**; all logic in Python | Env export must happen in the calling shell; everything else is testable logic. |
| D4 | **`schema_coerce`** added as the real fix for "Invalid tool parameters" | Type coercion + drop-unknown + safe required-fill. |
| D5 | Runtime state consolidated under `~/.nasim/` | Cleaner than scattered `~/.nasim_*` dotfiles. |
| D6 | Config single-source `cfg/nasim.toml` → env overrides | Relocate the server without code changes. |
| D7 | Recommended agentic model = `qwen2.5-coder:14b` | Only model that holds up under full agentic load on this hardware. |

## Diagnosis carried forward

Bridge plumbing is sound: `14b` (and even `gemma4`) return correct `tool_use`
blocks for simple requests in streaming + non-streaming. The user's failure was
`gemma4` active under the full ~15-tool agentic load + translation not robust
enough. Fix = `schema_coerce` + model steering + exhaustive tests. Ceiling is the
local model's capability, not the bridge.

## Capability matrix status

Legend: ✅ green · 🟡 model-bound · ⬜ not yet. IDs defined in `rules/testing.md`.

| Group | Status |
| --- | --- |
| B01–B18 (bridge-guaranteed) | ⬜ rebuilding |
| T01–T09 (rollback) | ⬜ rebuilding |
| E01–E05 (e2e on `14b`) | ⬜ pending bridge+runtime |
| X01–X06 (exhaustive surface) | ⬜ pending |

## Phase progress

| Phase | Task | Status |
| --- | --- | --- |
| Knowledge base | #1 `.claude/` policies | in progress |
| Loop | #2 methodology + runner | pending |
| Config | #3 `cfg/` + `config.py` | pending |
| Bridge | #4 decomposed + `schema_coerce`, deploy | pending |
| Runtime | #5 OOP toggle + shim | pending |
| Tests | #6–#8 unit / integration+capability / e2e+surface | pending |
| Docs | #9 install/uninstall + README + docs | pending |
| Loop to green | #10 iterate + commit | pending |

## Open items

- Confirm a self-hosted CI runner path (or document local-only loop) — `docs/runbook.md`.
- Decide whether to pull a stronger model onto the server if 14B agentic
  reliability proves marginal for E05 (out of scope unless E2E demands it).
