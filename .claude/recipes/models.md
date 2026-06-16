# Model Selection & GPU Fit for Agentic Coding (2026)

## Core Rule
For Claude Code / OpenCode / heavy agent loops: **the model must run fully on GPU** (or unified memory on Apple). CPU offload makes each turn 10-100× slower; the agent never reaches synthesis/write phases ("nothing happens" symptom).

On black (example 11 GB GPU from prior notes):
- 7B–14B dense or well-quantized larger models are safe.
- 30B+ dense usually spills unless heavily quantized or you have more VRAM.
- MoE models (some Qwen/DeepSeek/Gemma) can be efficient because only active params count for VRAM.

Check on black while idle + during load:
```bash
curl -s http://localhost:11434/api/ps | jq
# or ollama ps
# Look for high GPU utilization, low/zero CPU layers for the model.
```

## Current Strong Recs for Agentic Work (Ollama tags, check exact availability)
- **Qwen3-Coder series** (various sizes / "Next" MoE variants): Repeatedly top for tool use, SWE-Bench style agent tasks, long-horizon. Primary recommendation.
- **GLM-5.1 / GLM-5 cloud via Ollama**: Excellent long-horizon judgment and sustained iteration.
- **DeepSeek V4 / Coder V2 (MoE)**: Great perf/price, strong on coding benchmarks.
- **Gemma 4** (12B, 26B MoE etc.): Strong agentic in its size class, fast.
- Others worth testing: Kimi variants (cloud or local), recent MiniMax/Nemotron open weights.

Also watch "ollama.com/library" and "ollama launch claude" recommended lists (they surface current cloud + local standouts like kimi-k2.5:cloud, glm-5:cloud when you want reference quality without local VRAM cost).

## Context
Claude Code and serious agents want 32k–128k+ tokens. Set high `num_ctx` (Ollama default or per-model). Larger context + strong reasoning usually beats a bigger model that is slow or spilling.

## Testing an Agentic Model
1. Point Claude Code / OpenCode / Aider at it (via remote tunnel).
2. Give it a real multi-step task in a real repo: explore → plan → edit ≥2 files → run tests/bash → iterate on failures.
3. Observe: does it emit clean tool_use (or native calls), execute, recover, finish with correct disk changes?
4. Time per turn and "stuck" behavior.

If weak tool calling or loops: try a different (usually larger or more "coder" tuned) model or lower temperature if the agent exposes it. Pin low temp (0.0) for tool-bearing turns when the client doesn't send one (common pattern in proxies/bridges historically).

## Cloud Reference When Needed
- Ollama cloud models (glm, kimi, minimax...) via the same `claude --model xxx:cloud` flow.
- OpenRouter for many of the above open weights + frontier closed.
- Direct xAI for grok-code-fast-1 when you want that specific speed/reasoning profile (via agents that support it: Cline, Cursor, opencode, grok-cli wrappers, etc.).

Update this file after any major new model release + verification on black.
