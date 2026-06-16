# Ollama Model Compatibility — Nasim

Models from https://ollama.com/library evaluated for use with Nasim on a
machine with an **11 GB GPU** (e.g. NVIDIA GTX 1080 Ti).

The only hard requirement for Claude Code compatibility is the **`tools` tag** —
the model must support the Ollama native tool-call protocol or produce
recoverable text-form calls. Without it, the bridge has nothing to salvage.

GPU fit is the second hard requirement: a model that spills to CPU RAM on an
11 GB card degrades to 2–5 minutes per turn (see `docs/model-guidance.md`,
AP-12 in `.claude/rules/anti-patterns.md`).

## VRAM size estimate

Ollama defaults to Q4_K_M quantization: ≈ 0.56 GB per billion parameters.

| Param count | Estimated VRAM | Fits 11 GB GPU? |
| --- | --- | --- |
| 1–3 B | 0.6–1.7 GB | ✅ |
| 7–8 B | 3.9–4.5 GB | ✅ |
| 12–14 B | 6.7–7.9 GB | ✅ |
| 16 B | ~9 GB | ✅ (tight) |
| 22–24 B | 12–13.5 GB | ❌ |
| 30 B+ | 17 GB+ | ❌ |

---

## Recommended — GPU-resident + tools tag (≤ 14 B)

Models proven or expected to run fully on GPU and emit tool calls compatible
with the bridge. Sorted by coding suitability.

| Model | Size | VRAM est. | Strength | Nasim config key |
| --- | --- | --- | --- | --- |
| `qwen2.5-coder:14b` | 14 B | 9.0 GB | Best agentic coding on this GPU; proven e2e | `models.default` / `models.recommended` |
| `qwen2.5-coder:7b` | 7 B | 4.7 GB | Reliable, GPU-resident; used for e2e tests | `models.fast` |
| `qwen2.5-coder:7b-instruct` | 7 B | 4.7 GB | Same weights, instruct-tuned variant | — |
| `llama3.1:8b` | 8 B | 4.9 GB | ⚠️ Bridge protocol ✅ but e2e ❌ — emits bash-style pseudo-calls under Claude Code system prompt | — |
| `qwen3:8b` | 8 B | 5.2 GB | Qwen3 with thinking mode; good tool-use | — |
| `deepseek-r1:14b` | 14 B | 9.0 GB | Reasoning model; slower per turn, correct | — |
| `deepseek-r1:8b` | 8 B | 5.2 GB | Lighter reasoning; fits GPU | — |
| `gemma4:latest` (12B) | 12 B | 9.6 GB | Google; vision + tools; tight fit | — |
| `mistral-nemo:12b` | 12 B | 6.7 GB | 128k context; solid tool-use | — |
| `granite4.1:8b` | 8 B | ~4.5 GB | IBM coding model; `tools` tag | — |
| `granite3.3:8b` | 8 B | ~4.5 GB | IBM; 128k context; `tools` | — |
| `cogito:8b` | 8 B | ~4.5 GB | Hybrid reasoning; `tools` | — |
| `hermes3:8b` | 8 B | ~4.5 GB | Nous-Hermes; strong function calling | — |
| `mistral:7b` | 7 B | 4.1 GB | Mistral v0.3; `tools` tag | — |
| `llama3.2:3b` | 3 B | ~1.7 GB | Fast; light tool-use | — |
| `phi4-mini:3.8b` | 3.8 B | ~2.2 GB | Microsoft; strong reasoning at size | — |
| `granite4.1:3b` | 3 B | ~1.7 GB | IBM; smallest `tools` model | — |
| `command-r7b` | 7 B | ~4.0 GB | Cohere; built for RAG + tools | — |
| `lfm2.5:8b` | 8 B | ~4.5 GB | Fast reliable tool calling; `tools` | — |
| `smollm2:1.7b` | 1.7 B | ~1.0 GB | Tiny; `tools`; light tasks only | — |
| `devstral-small-2` | 24 B | ~13.5 GB | ⚠️ borderline — see note below | — |

> **devstral-small-2 note:** Mistral's "best open-source coding agent" model.
> At 24B it almost certainly exceeds 11 GB; test with `ollama ps` before use.
> The 24B non-small `devstral` is also listed but clearly too large.

---

## Tested results (2026-06-15)

| Model | Bridge protocol | e2e (Claude Code) | Notes |
| --- | --- | --- | --- |
| `qwen2.5-coder:7b` | ✅ | ✅ | All E01–E05 pass; writes/edits/reads on disk |
| `qwen2.5-coder:14b` | ✅ | ✅ | Proven; spills CPU on 11 GB, slower but works |
| `llama3.1:8b` | ✅ | ❌ | Bridge returns `stop_reason: tool_use` correctly; under Claude Code's full system prompt the model emits bash-style `/tool cat …` text instead of JSON tool_use — E01, E02, E03, E05 fail |

`llama3.1:8b` failure mode: the model describes tool usage as prose/bash instead of calling
the tool. `tool_salvage` cannot recover `/tool cat` format calls. Not suitable for agentic
Claude Code use despite passing the minimal direct bridge test.

---

## Installed on `black` (as of 2026-06-15)

| Model | Size | GPU fit | Notes |
| --- | --- | --- | --- |
| `qwen2.5-coder:14b` | 9.0 GB | ✅ | Default; proven e2e |
| `qwen2.5-coder:7b` | 4.7 GB | ✅ | Fast; used for e2e tests |
| `qwen2.5-coder:7b-instruct` | 4.7 GB | ✅ | Same weights, instruct alias |
| `llama3.1:8b` | 4.9 GB | ✅ | Installed 2026-06-15; tested |
| `qwen3:8b` | 5.2 GB | ✅ | Qwen3 with thinking |
| `deepseek-r1:8b` | 5.2 GB | ✅ | Reasoning; slower |
| `deepseek-r1:14b` | 9.0 GB | ✅ | Reasoning; tight |
| `gemma4:latest` | 9.6 GB | ✅ | Vision + tools; tight |
| `deepseek-r1:32b` | 19 GB | ❌ | CPU spill — avoid for agentic |
| `gemma4:31b` | 19 GB | ❌ | CPU spill — avoid for agentic |
| `qwen3.6:latest` | 23 GB | ❌ | CPU spill — avoid for agentic |
| `minimax-m3:cloud` | — | 🌐 | Cloud-routed by Ollama |
| `kimi-k2.7-code:cloud` | — | 🌐 | Cloud-routed by Ollama |

---

## Too large — CPU/GPU split on 11 GB (avoid for agentic tasks)

These have the `tools` tag but exceed 11 GB; they produce 2–5 min/turn on
this hardware. Use a smaller variant or upgrade the GPU.

| Model | Param count | Min VRAM est. | Alternative |
| --- | --- | --- | --- |
| `devstral:24b` | 24 B | ~13.5 GB | `devstral-small-2` if it fits |
| `mistral-small3.2:24b` | 24 B | ~13.5 GB | `mistral-nemo:12b` |
| `mistral-small:22b` | 22 B | ~12.4 GB | `mistral-nemo:12b` |
| `qwen3.6:latest` | 27–35 B | ~17–20 GB | `qwen3:8b` |
| `deepseek-r1:32b` | 32 B | ~19 GB | `deepseek-r1:14b` |
| `gemma4:31b` | 31 B | ~17 GB | `gemma4:latest` (12B) |
| `qwq:32b` | 32 B | ~19 GB | `qwen3:8b` with thinking |
| `qwen3-coder:30b` | 30 B | ~17 GB | `qwen2.5-coder:14b` |

---

## Cloud-only models (0 VRAM — Ollama routes to vendor API)

These show 0 bytes in `ollama list`. They require network access and a vendor
account. Tool-use quality depends on the cloud backend.

| Model | Vendor | Tool-use | Notes |
| --- | --- | --- | --- |
| `minimax-m3:cloud` | MiniMax | ✅ | Installed on black |
| `kimi-k2.7-code:cloud` | Moonshot AI | ✅ | Installed on black; code-focused |
| `kimi-k2:cloud` | Moonshot AI | ✅ | Agentic MoE |
| `qwen3-coder:cloud` | Alibaba | ✅ | Long-context coding |
| `glm-5.1:cloud` | Zhipu AI | ✅ | Agentic engineering |

---

## Not compatible — no `tools` tag

These may run fine as chat models but the bridge cannot reliably coerce tool
calls from them. `tool_salvage` may recover some text-form calls from models
that happen to mimic the format, but it is not guaranteed.

Notable examples: `phi4:14b`, `gemma2`, `codellama`, `deepseek-coder`,
`starcoder2`, `codegemma`, `deepcoder:14b`, `opencoder`.

---

## Switching models in a running session

```bash
nasim start                  # selects models.recommended
/model qwen3:8b              # hot-swap inside claude (colon-tag passes through bridge)
/model llama3.1:8b           # hot-swap to the newly installed model
```

Or set a different default before starting:

```bash
DEFAULT_MODEL=llama3.1:8b nasim start
```

---

## How to add a new model

```bash
# On the server
ssh black "ollama pull <model:tag>"

# Verify it appears and check actual size
ssh black "ollama list"

# If size > ~10 GB, check GPU fit before using for agentic work
ssh black "ollama ps"        # shows VRAM vs CPU split after first inference
```

See `docs/model-guidance.md` for tuning knobs (num_ctx, tool_temperature).
