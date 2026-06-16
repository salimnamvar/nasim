# Bridge Protocol — Anthropic Messages API ⇄ Ollama chat API

The bridge is an Anthropic Messages API server on one side and an Ollama
`/api/chat` client on the other. This file is the translation contract. Changes
to translation logic must keep every rule here true and be covered by a unit
test.

- Anthropic Messages API: https://docs.anthropic.com/en/api/messages
- Ollama chat API: https://github.com/ollama/ollama/blob/main/docs/api.md

## Endpoints the CLI uses

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Liveness + Ollama connectivity + model inventory (nasim-specific). |
| GET | `/v1/models` | Model picker list. |
| POST | `/v1/messages` | Chat — streaming and non-streaming. The hot path. |
| POST | `/v1/messages/count_tokens` | Input token estimate. |

The CLI may append `?beta=true`; ignore the query string.

## Request translation (`anthropic→ollama`)

| Anthropic | Ollama | Rule |
| --- | --- | --- |
| `system` (str or block list) | leading `{"role":"system"}` message | Flatten text blocks; join with newlines. |
| `messages[].content` str | `content` str | Pass through. |
| assistant `text` blocks | assistant `content` | Join with newlines. |
| assistant `tool_use` block | assistant `tool_calls[]` | `{function:{name,arguments}}`. Record `id→name`. |
| user `tool_result` block | `{"role":"tool", ...}` message | Flatten content to text; label `tool_name` via the recorded `id→name`; prefix `ERROR:` if `is_error`. |
| interleaved user text + tool_result | separate messages, **in order** | Order matters; do not merge across a tool_result. |
| `image` block | `[image omitted]` text | Coder models are not vision models. |
| `thinking` block | dropped | Not represented in Ollama chat. |
| `max_tokens` | `options.num_predict` | — |
| `temperature`/`top_p`/`top_k` | `options.*` | Pass through when present. |
| `stop_sequences` | `options.stop` | — |
| `tools[]` with `input_schema` | `tools[]` `{type:function, function:{name,description,parameters}}` | Only tools that have an `input_schema`. |
| (always) | `options.num_ctx`, `keep_alive` | From config. |

## Response translation (`ollama→anthropic`, non-streaming)

1. Take `message.content` as text and `message.tool_calls` as native calls.
2. If there are **no** native calls but tools were offered, run
   `tool_salvage` over the text to recover text-encoded calls.
3. Each tool call → an Anthropic `tool_use` block, after `schema_coerce`
   against that tool's `input_schema`.
4. Emit text block first (if any non-empty residual), then tool_use blocks.
5. `stop_reason`: `tool_use` if any calls, else `max_tokens` if Ollama
   `done_reason == "length"`, else `end_turn`.
6. `usage.input_tokens = prompt_eval_count`, `output_tokens = eval_count`.

## Streaming translation (SSE event contract)

The CLI's SDK requires exactly this event order:

```
message_start
( content_block_start → content_block_delta(+) → content_block_stop )*
message_delta            # carries stop_reason + final usage
message_stop
```

- Text block delta type: `text_delta`.
- Tool-use block: `content_block_start` carries `{type:tool_use,id,name,input:{}}`;
  argument JSON is sent as one or more `input_json_delta.partial_json` strings
  whose concatenation parses to the full input object; then `content_block_stop`.
- **When tools are offered, buffer text** instead of streaming it live, so a
  text-encoded tool call can be salvaged at end-of-stream. With no tools, stream
  text live for responsiveness.
- `message_delta` carries the final `stop_reason` and `usage`.

## Tool-call robustness (the reliability core)

Small/general models degrade under the full Claude Code load. Two layers defend
correctness:

1. **`tool_salvage`** — recover calls a model wrote as text instead of using the
   protocol. Handles `<tool_call>{...}</tool_call>` tags and bare top-level JSON
   objects whose `name` matches an offered tool. Brace-balanced scan; never
   matches JSON that is not a known tool name.
2. **`schema_coerce`** — make a recovered/native call pass the CLI's strict
   client-side schema validation (the cause of "Invalid tool parameters"):
   - parse `arguments` if it arrived as a JSON string;
   - coerce each present field to its schema type (`"5"`→`5`, `"true"`→`true`);
   - drop properties absent from the schema when `additionalProperties:false`;
   - fill **missing required fields** with type-zero defaults so validation
     passes. Models omit trivial annotation fields (e.g. a `description`), not
     the semantically critical ones, so this is safe in practice. Never invent
     values for fields the model did provide.

## Model mapping (`model_map`)

| Requested name | Resolves to |
| --- | --- |
| contains `:` (already an Ollama tag) | itself (enables `/model qwen2.5-coder:7b` hot-swap) |
| contains `haiku` | `fast` model (config) |
| anything else (`opus`/`sonnet`/`fable`/unknown) | `default` model (config) |

Consequence: even a stale `model: "opus"` still routes to a real Ollama model;
requests never fail for lack of an exact name.

## Errors (Anthropic-shaped)

| Condition | HTTP | Body |
| --- | --- | --- |
| Body not JSON | 400 | `{type:error, error:{type:invalid_request_error, message}}` |
| Ollama returned non-200 | 502 | `error.type=api_error` |
| Ollama unreachable | 503 | `error.type=overloaded_error` |

In streaming, a mid-stream failure emits an `error` SSE event with the same body
shape.
