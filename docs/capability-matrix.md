# Capability Matrix

Every capability Claude Code depends on, the layer that proves it, and its
status. Each green cell is backed by a runnable assertion.

Legend: ✅ green · 🟡 model-bound (transport green, reliability depends on the
local model).

## Bridge-guaranteed (B) — fully in the bridge's control · all ✅

| ID | Capability | Proven by |
| --- | --- | --- |
| B01 | `/health` reports ok + model inventory | integration |
| B02 | `/v1/models` returns the picker list | integration |
| B03 | `/v1/messages/count_tokens` estimates input tokens | unit + integration |
| B04 | Non-streaming text round-trip | unit (server) + integration |
| B05 | Streaming text round-trip (correct SSE order) | unit + integration |
| B06 | Single `tool_use` — non-streaming | unit + capability |
| B07 | Single `tool_use` — streaming (valid `input_json_delta`) | unit + capability |
| B08 | Multiple `tool_use` blocks in one turn | unit |
| B09 | Multi-turn tool chain (`tool_use`→`tool_result`→continue) | capability |
| B10 | `tool_result` with `is_error` handled | unit |
| B11 | System prompt as string AND as block list | unit |
| B12 | `stop_reason` mapping (`end_turn`/`tool_use`/`max_tokens`) | unit |
| B13 | Error mapping: 400 / 502 / 503 | unit (server) |
| B14 | `model_map`: opus→default, haiku→fast, `:tag` passthrough | unit |
| B15 | `schema_coerce`: type coercion, drop-unknown, fill-required | unit |
| B16 | `tool_salvage`: `<tool_call>` tag form AND bare/fenced JSON | unit |
| B17 | Image block → `[image omitted]` (no crash) | unit |
| B18 | Sampling params + `stop_sequences` passthrough | unit |

## Client toggle / rollback (T) — all ✅

| ID | Capability | Proven by |
| --- | --- | --- |
| T01 | `start` opens tunnel, sets env, writes state, backs up model | rollback |
| T02 | `start` injects marked Ollama models into the picker | rollback |
| T03 | `start` selects the recommended model | rollback |
| T04 | `status` reflects running state | rollback |
| T05 | `stop` unsets env, kills tunnel, ejects all marked models | rollback |
| T06 | `stop` restores the exact pre-start model | rollback |
| T07 | Double `start` idempotent (no orphan tunnel, no duplicates) | rollback |
| T08 | Double `stop` safe | rollback |
| T09 | Baseline `/model` selection intact after a full cycle | rollback |

## End-to-end (E) — real `claude` binary writes to disk · all ✅

Run in an isolated minimal HOME against a GPU-resident model
(see [model-guidance.md](model-guidance.md)).

| ID | Capability | Proven by |
| --- | --- | --- |
| E01 | Write a new file → file exists with correct content | e2e |
| E02 | Edit an existing file → change applied on disk | e2e |
| E03 | Read + report → correct content surfaced | e2e |
| E04 | Bash command executed, output observed | e2e |
| E05 | Multi-step task mutates ≥2 files → all on disk | e2e |

## Exhaustive surface (X) — transport ✅, reliability 🟡

Client-side features. The bridge relays the tool definitions and tool calls
verbatim; whether the model *drives* the feature is model-bound.

| ID | Capability | Guarantee |
| --- | --- | --- |
| X01 | MCP tool invocation | schema + calls relayed verbatim |
| X02 | Sub-agents (`Task`) | Task tool + nested calls relayed |
| X03 | Plan mode | plan tools relayed; exit-plan round-trips |
| X04 | Hooks | client-side; the bridge carries no hook concept |
| X05 | Skills / slash commands | skill tool calls relayed |
| X06 | `WebFetch` / `WebSearch` | tools relayed; execution is client-side |

## Counts

96 unit · 5 integration · 3 capability · 7 rollback · 8 surface · 5 e2e.

## Running

```bash
make test                       # unit only (fast, no network)
make integration                # B01–B05 live
make capability                 # B06–B09 live (recommended model)
pytest test/rollback -m rollback   # T01–T09 (live, isolated)
make loop E2E=1                 # everything, incl. E01–E05
```

## Exit criteria

1. Every B and T row ✅.
2. Every E row ✅ with the chosen model.
3. Every X row transport-✅ with a documented reliability note.

Remaining 🟡 items are acceptable only when the limiting factor is the local
model's capability ([model-guidance.md](model-guidance.md)) — never a bridge
defect.
