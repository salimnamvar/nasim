# Testing — Taxonomy, Capability Matrix, Exit Criteria

The user's requirement: *all capabilities of Claude Code are tested and working
against the linked Ollama server.* This file makes that bounded and checkable.

## Test taxonomy (`test/`)

| Layer | Dir | Network? | What it proves |
| --- | --- | --- | --- |
| Unit | `test/unit/` | No | Pure translator + runtime logic, exhaustively, with mocks. |
| Integration | `test/integration/` | Live bridge | The bridge endpoints answer correctly over the wire. |
| Capability | `test/capability/` | Live bridge | Every Anthropic-API feature Claude Code depends on. |
| Rollback | `test/rollback/` | Local + SSH | The full `nasim start`/`stop` contract. |
| E2E | `test/e2e/` | Real `claude` | The real binary mutates the filesystem via Ollama. |
| Fixtures | `test/fixtures/` | — | Captured real Claude Code request bodies for replay. |

`make test` runs unit only (fast, no network). `make loop` runs everything in
order, deploying the bridge first.

## Capability matrix

Status values: ✅ green · 🟡 model-bound (transport green, reliability depends on
model) · ⬜ not yet. Maintained current in `rules/sprint.md`.

### Bridge-guaranteed — must all be ✅ (these are fully in our control)

| ID | Capability |
| --- | --- |
| B01 | `/health` reports ok + model inventory |
| B02 | `/v1/models` returns the picker list |
| B03 | `/v1/messages/count_tokens` estimates input tokens |
| B04 | Non-streaming text round-trip |
| B05 | Streaming text round-trip (correct SSE order) |
| B06 | Single `tool_use` — non-streaming |
| B07 | Single `tool_use` — streaming (valid `input_json_delta`) |
| B08 | Multiple `tool_use` blocks in one turn |
| B09 | Multi-turn tool chain (`tool_use`→`tool_result`→continue) |
| B10 | `tool_result` with `is_error` handled |
| B11 | System prompt as string AND as block list |
| B12 | `stop_reason` mapping: `end_turn` / `tool_use` / `max_tokens` |
| B13 | Error mapping: 400 (bad JSON) / 502 (ollama error) / 503 (unreachable) |
| B14 | `model_map`: `opus`→default, `haiku`→fast, `:tag` passthrough |
| B15 | `schema_coerce`: type coercion, drop-unknown, fill-required |
| B16 | `tool_salvage`: `<tool_call>` tag form AND bare-JSON form |
| B17 | Image block → `[image omitted]` (no crash) |
| B18 | Sampling params + `stop_sequences` passthrough |

### Client toggle / rollback — must all be ✅

| ID | Capability |
| --- | --- |
| T01 | `start` opens tunnel, sets env, writes state, backs up model |
| T02 | `start` injects marked Ollama models into the picker |
| T03 | `start` selects the recommended/default model |
| T04 | `status` reflects running state |
| T05 | `stop` unsets env, kills tunnel, ejects all marked models |
| T06 | `stop` restores the exact pre-start model (heals an Ollama `/model` pick) |
| T07 | Double `start` idempotent (no orphan tunnel, no duplicate/lost tracking) |
| T08 | Double `stop` safe |
| T09 | Baseline `/model` selection intact after a full cycle |

### E2E (real `claude` binary, recommended model) — must demonstrate ✅

| ID | Capability |
| --- | --- |
| E01 | Write a new file → file exists on disk with correct content |
| E02 | Edit an existing file → change applied on disk |
| E03 | Read + grep → correct content reported |
| E04 | Bash command executed, output observed |
| E05 | Multi-step task mutates ≥2 files → all changes on disk |

### Exhaustive surface — characterized (transport ✅, reliability 🟡)

These are **client-side** features. The bridge's only job is to relay the tool
definitions and the model's `tool_use` faithfully; whether the model correctly
*drives* the feature is model-capability bound. Each test asserts transport
correctness and records observed reliability per model.

| ID | Capability | What we guarantee |
| --- | --- | --- |
| X01 | MCP tool invocation | Bridge relays MCP tool schemas + calls verbatim |
| X02 | Sub-agents (`Task`) | Bridge relays the Task tool + nested session calls |
| X03 | Plan mode | Bridge relays plan tools; exit-plan round-trips |
| X04 | Hooks | Hooks are client-side; unaffected by the bridge |
| X05 | Skills / slash commands | Bridge relays skill tool calls |
| X06 | `WebFetch` / `WebSearch` | Bridge relays the tools; execution is client-side |

## Exit criteria (the loop stops when)

1. Every **B\*** and **T\*** row is ✅.
2. Every **E\*** row is ✅ with `models.recommended` active.
3. Every **X\*** row has transport ✅ and a documented reliability note.

Remaining 🟡 items are acceptable **only** when the limiting factor is the local
model's capability, documented in `docs/model-guidance.md` — never a bridge
defect.
