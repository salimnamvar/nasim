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
| D7 | Recommended agentic model = `qwen2.5-coder:14b` | Strongest tool-use, but on an 11 GB GPU it spills to CPU (~5 min/turn). See D9. |
| D8 | **Pin a low temperature (0.0) for tool-bearing requests** when the client sets none (`bridge.tool_temperature`) | Captured payloads carried no temperature; qwen at ~0.7 emitted empty/placeholder tool templates. At 0 it emits clean, complete calls. Client-set temperature is always respected. |
| D9 | **e2e runs in an isolated minimal HOME + GPU-resident model** (`NASIM_E2E_MODEL`/`models.fast`) | A 200 KB global `CLAUDE.md` overflows `num_ctx` and makes a small model pick the wrong tool; the 14b spills to CPU. The e2e isolates the *pipeline*, not a developer's personal context. On 11 GB, 7b fits fully and completes reliably. |

## Diagnosis (resolved — evidence captured 2026-06-13)

Captured real `claude` payloads via a gated bridge dump (`BRIDGE_DEBUG_DUMP`) and
replayed them directly to Ollama. Findings:

1. **The model never emits native Ollama `tool_calls` under load** — it writes the
   call as markdown-fenced JSON text. `tool_salvage` already recovers that; this
   is the load-bearing path, not a fallback.
2. **No temperature in the request → qwen ran at ~0.7 → empty/placeholder
   templates** (`{"name":"","arguments":{}}`, `<function-name>`), which are
   correctly unsalvageable. Pinning temp 0 (D8) yields clean, complete calls the
   bridge streams as valid `tool_use` (`stop_reason: tool_use`, full args).
3. **The pipeline is sound end-to-end** — `stream-json` showed claude receiving
   `tool_use`, executing it, and returning `tool_result`. Failures were the model
   picking the wrong tool when drowned in a 200 KB global `CLAUDE.md` (context
   overflow) and the 14b spilling to CPU.

With a controlled context + GPU-resident model, **E01–E05 write/edit/read/bash/
multi-file all land on disk** — the user's "nothing happens" bug is closed. The
ceiling is the local model + 11 GB GPU, never the bridge.

## Capability matrix status (2026-06-13 — green)

Legend: ✅ green · 🟡 model-bound · ⬜ not yet. IDs defined in `rules/testing.md`.

| Group | Status | Evidence |
| --- | --- | --- |
| B01–B18 (bridge-guaranteed) | ✅ | unit (translator/server) + integration (live) + capability (live) |
| T01–T09 (rollback) | ✅ | live start/stop contract, isolated temp home + dedicated port |
| E01–E05 (e2e) | ✅ | real `claude` binary, minimal HOME, GPU-resident model — files on disk |
| X01–X06 (exhaustive surface) | ✅ transport · 🟡 reliability | tool families relayed verbatim (unit); reliability is model-bound |

Counts: 96 unit · 5 integration · 3 capability · 7 rollback · 8 surface · 5 e2e.

## Phase progress

| Phase | Task | Status |
| --- | --- | --- |
| Knowledge base | #1 `.claude/` policies | done |
| Loop | #2 methodology + runner | done |
| Config | #3 `cfg/` + `config.py` | done |
| Bridge | #4 decomposed + `schema_coerce` + `tool_temperature`, deployed | done |
| Runtime | #5 OOP toggle + shim | done |
| Tests | #6–#8 unit / integration+capability / e2e+surface | done |
| Docs | #9 install/uninstall + README + docs | in progress |
| Loop to green | #10 iterate + commit | in progress |

## Open items

- Confirm a self-hosted CI runner path (or document local-only loop) — `docs/runbook.md`.
- Hardware ceiling: 11 GB GPU cannot run 14b + a 20k+ context fully on GPU. If
  agentic quality on `7b` proves marginal for real work, the lever is better
  hardware or a fully-GPU-resident mid model — not a bridge change.

## Model compatibility findings (2026-06-15)

`docs/ollama-models.md` added: full Ollama library survey + per-model GPU fit table.

New model tested: `llama3.1:8b` (4.9 GB, installed on black).
- Bridge protocol test: ✅ — `stop_reason: tool_use`, correct `Write` args on direct API call.
- e2e with Claude Code: ❌ — under the full Claude Code system prompt the model emits
  bash-style `/tool cat …` pseudo-calls in text instead of JSON tool_use. E01–E05 fail.
  `tool_salvage` cannot recover this format. Not suitable for agentic use.

Documentation test run with `qwen2.5-coder:7b` (proven): claude read `request.py` and
wrote `translator-docs.md` with correct module overview, function signature, and
translation rules — the full read→synthesize→write pipeline confirmed working.
