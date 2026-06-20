# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conda Environment

```
conda_env: nasim
```

Activate before running any script: `conda activate nasim`

## Commands

```bash
# Launch the interactive REPL (default model: qwen2.5-coder:14b)
python -m nasim.cli

# Override model or server
python -m nasim.cli --model qwen2.5-coder:7b --server http://localhost:11434

# Run a single command and exit (non-interactive)
python -m nasim.cli -c "list files in the current directory"

# Disable streaming (blocking mode)
python -m nasim.cli --no-stream

# Run the Ollama model catalogue scraper (writes data/ollama.csv + logs/)
cd scripts && python scrape.py

# Rank models for this machine (SSH-probes host for VRAM/RAM)
python scripts/analyze.py data/ollama.csv

# Rank for a specific server; override specs manually if SSH not available
python scripts/analyze.py data/ollama.csv myserver --output data/ranked.csv
python scripts/analyze.py data/ollama.csv --vram 11 --ram 32 --output data/ranked.csv --top 50
```

## Architecture

The repo has two independent concerns:

### 1. `nasim/` — Code agent CLI package

A minimal agentic loop running on a local Ollama instance. Entry point: `python -m nasim.cli`.

**Layer stack** (top → bottom):

| Module | Role |
|--------|------|
| `nasim/cli.py` | `argparse` entry, REPL, slash commands (`/help /reset /model /quit`) |
| `nasim/agent.py` | `Agent` class — agentic loop up to `max_iterations=20`; holds conversation history in `self.messages`; dispatches tool calls |
| `nasim/llm.py` | `OllamaClient` — `POST /api/chat` (blocking) and streaming via `chat_stream()` yielding `str | ToolCall` chunks |
| `nasim/tools.py` | `@tool` decorator registers to `TOOL_REGISTRY`; `execute_tool()` dispatches by name |

**Tool set** (registered in `tools.py`): `read_file`, `write_file`, `edit_file`, `list_dir`, `shell_exec`.

**Agentic loop**: `Agent.run()` / `Agent.run_streaming()` loop until the LLM returns no tool calls or `max_iterations` is hit. Tool results are appended as `role: tool` messages. The system prompt is `messages[0]`; `Agent.reset()` truncates back to it.

**Streaming**: `OllamaClient.chat_stream()` buffers `tool_calls` deltas by index into `tool_calls_buf` and yields them after the stream ends, interleaved with text `str` chunks.

### 2. `scripts/` — Standalone Ollama utilities

`scripts/scrape.py` — async + multiprocessing scraper for `ollama.com/library`. Three phases: paginate library → fetch `/tags` pages → fetch version detail pages concurrently. `AdaptiveNetworkFetcher` scales concurrency 15–80 based on 429/5xx rates. Output: `data/ollama.csv`.

`scripts/analyze.py` — SSH-probes a host for GPU VRAM, RAM, CPU; scores and ranks models. Fit tiers: `GPU` (≤ VRAM × 0.85) → `CPU` (≤ RAM × 0.80) → `SKIP`. Score is a weighted sum (quantization × 30, params × 20, context × 10, downloads × 5) plus tier bonus.

### 3. Root scripts

`run.py` — `open-interpreter` session wired to Ollama (`qwen3.5:9b-q8_0` at `192.168.70.125:11434`), `auto_run=True`.

`chats.py` — reads a CSV of chatbot URLs, hits `{url}/api/message`, writes responses to `responses.md`.

## Key Dependencies

| Package | Used by |
|---------|---------|
| `requests` | `nasim/llm.py`, `chats.py` |
| `aiohttp` | `scripts/scrape.py` |
| `beautifulsoup4` + `lxml` | `scripts/scrape.py` |
| `tqdm` | `scripts/scrape.py` |
| `open-interpreter` | `run.py` |
| `pandas` | `chats.py` |
