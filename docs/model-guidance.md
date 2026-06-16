# Model Guidance — the local-model ceiling and how to tune it

The bridge is provably correct: it relays tool definitions and recovers tool
calls faithfully (see [capability-matrix.md](capability-matrix.md)). What it
**cannot** do is exceed the capability of the local model you point it at. This
document records what was measured, why a prompt can "run but change nothing,"
and how to get reliable results.

## TL;DR

- Use a capable **coder** model that **fits entirely in GPU memory**.
- Keep the injected context lean — a giant global `CLAUDE.md` can overflow the
  context window and derail a small model.
- The bridge pins **temperature 0** for tool requests by default; leave it there.
- On an 11 GB GPU, `qwen2.5-coder:7b` (fits fully) completes real file-writing
  tasks reliably; `qwen2.5-coder:14b` is stronger but spills to CPU and slows to
  minutes per turn.

## The symptom

"Claude is busy for a while, then finishes, but nothing changed on disk." This is
almost always one of:

1. The model emitted no usable tool call (it answered in prose, or produced an
   empty/placeholder call).
2. The model called the **wrong** tool for the request.
3. The model was too slow and the turn timed out.

None of these is a bridge fault — each was reproduced and traced to the model or
the host below.

## What was measured

Real Claude Code request bodies were captured at the bridge (a gated diagnostic,
`BRIDGE_DEBUG_DUMP`) and replayed directly to Ollama.

### Finding 1 — the model emits tool calls as text, not natively

Ollama returned `tool_calls: null` and put the call in `message.content` as a
markdown ```json block. This is why the bridge has a **salvage** layer: it
recovers `<tool_call>…</tool_call>` and bare/fenced JSON whose `name` matches an
offered tool. Well-formed text calls are recovered into valid `tool_use` blocks.

### Finding 2 — temperature was the difference between clean and garbage calls

Captured requests carried **no temperature**, so the model ran at its default
(~0.7) and frequently produced degenerate calls:

```json
{"name": "", "arguments": {}}            // empty — unsalvageable (correctly)
{"name": <function-name>, "arguments": <args-json-object>}   // template echo
```

Replaying the same body at **temperature 0** produced clean, complete calls:

```json
{"name": "Write", "arguments": {"file_path": "hello.txt", "content": "Hello from Nasim"}}
```

The bridge now pins a low temperature for tool-bearing requests when the client
sets none (`bridge.tool_temperature`, default `0.0`). A client-supplied
temperature is always respected.

### Finding 3 — the pipeline executes tools end-to-end

A `stream-json` run of the real binary showed Claude Code receiving a `tool_use`,
**executing it**, and returning a `tool_result`. The pipeline is whole. When the
model produced a sensible `Write` call, the file appeared on disk.

### Finding 4 — context size and GPU fit decide success

- A developer's global `CLAUDE.md` can inject **200 KB+** of unrelated rules.
  That overflows a 32k context window and pushes a small model toward whatever
  the context emphasises (e.g. task/doc tooling) instead of the obvious action.
- `qwen2.5-coder:14b` (~9 GB weights + KV cache for a 20k+ prompt) does not fit a
  **11 GB** GPU; it runs split CPU/GPU (~2–5 min/turn, non-deterministic).
- `qwen2.5-coder:7b` fits fully → fast → completes the same tasks reliably.

With a lean context and a GPU-resident model, the end-to-end suite (E01–E05:
write, edit, read, bash, multi-file) all land changes on disk.

## How to get reliable results

| Lever | Action |
| --- | --- |
| Model choice | A coder model that fits GPU memory fully. On 11 GB: `qwen2.5-coder:7b`. |
| Context size | Keep the active `CLAUDE.md` small; avoid injecting large rule trees into every session. |
| Temperature | Leave `bridge.tool_temperature = 0.0`. |
| Context window | Set `bridge.num_ctx` large enough for the real prompt but small enough to stay on GPU. |
| Bigger model | Only worth it if it still fits the GPU; otherwise the CPU spill negates the quality gain. |

## Configuration knobs

All in `cfg/nasim.toml` (or the matching environment override):

```toml
[bridge]
num_ctx          = 32768   # raise only if it still fits in GPU memory
tool_temperature = 0.0     # low = best tool-call format adherence

[models]
default     = "qwen2.5-coder:14b"
fast        = "qwen2.5-coder:7b"
recommended = "qwen2.5-coder:14b"
```

`nasim start` selects `recommended` and warns if it is not present on the server.
For e2e validation on a memory-constrained host, `NASIM_E2E_MODEL` overrides the
model the end-to-end tests drive (defaults to `models.fast`).

## The bottom line

The bridge maximises robustness — native and text-form tool-call recovery,
schema coercion, low-temperature tool requests — but the result quality is bounded
by the local model and the GPU. Choose a model that fits, keep the context lean,
and the "nothing changed" symptom goes away.
