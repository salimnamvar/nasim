# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conda Environment

```
conda_env: nasim
```

Activate before running any script: `conda activate nasim`

## Commands

```bash
# Run the Ollama scraper (writes ollama_master_db.csv + logs/; Size stored as "X.XX GB")
cd scripts && python scrape.py

# Rank models for black (default — no server argument needed)
python scripts/analyze.py data/ollama.csv

# Rank models for a different server
python scripts/analyze.py data/ollama.csv myserver --output data/ranked.csv

# Override specs manually (no SSH)
python scripts/analyze.py data/ollama.csv --vram 11 --ram 32 --output data/ranked.csv

# Limit to top 50 GPU models
python scripts/analyze.py data/ollama.csv --top 50

# Run the open-interpreter chat session against a local Ollama instance
python run.py

# Run the chatbot API probe script
python chats.py
```

## Architecture

This repo contains three independent scripts — no shared package, no framework.

### `scripts/scrape.py` — Ollama model catalogue scraper

Async + multiprocessing pipeline that scrapes `ollama.com/library` and writes a CSV
of every model version with all metadata fields discovered dynamically (no hardcoded
column list). Three pipeline phases:

1. **Phase 1** — paginate `/library` to collect base model hrefs.
2. **Phase 2** — fetch `/tags` pages; `parse_tags_page()` extracts version hrefs and blob
   metadata (Size, Context, Input, Updated) using `_classify_blob_segment()` purely by
   value pattern — no CSS class dependency.
3. **Phase 3** — fetch every version detail page concurrently; `extract_detail_metadata()`
   uses three discovery strategies (two-span Tailwind containers, indigo badge spans,
   page-text regex) to capture arbitrary new metadata fields automatically.

`AdaptiveNetworkFetcher` adjusts concurrency between 15 and 80 based on 429/5xx
responses. HTML parsing (CPU-bound) runs in a `ProcessPoolExecutor`. Output is
`ollama_master_db.csv` with priority columns first, then sorted dynamic columns.
Per-run logs go to `logs/ollama_scraper_<timestamp>.log`.

### `scripts/analyze.py` — Model ranker for a target machine

Reads the scraper CSV, SSH-probes the target host for GPU VRAM, RAM, and CPU count,
then scores every model version and writes a ranked CSV.

**Fit tiers** (written to `Fit` column, appear as first sort key):
- `GPU` — model size ≤ VRAM × 0.85 (reserves KV-cache headroom)
- `CPU` — exceeds GPU limit but ≤ RAM × 0.80
- `SKIP` — exceeds RAM; excluded by default

**Score** (higher = better within tier) is a weighted sum:
- Quantization quality × 30 (F16=9.5, Q8=8.0, Q4_K_M=5.5, Q2_K=3.0, …)
- Parameter count × 20 (log₁₀ scale)
- Context window × 10 (log₁₀ scale)
- Popularity (downloads) × 5 (log₁₀ scale)
- Tier bonus: GPU +1000, CPU +100

Output CSV adds columns: `Fit`, `Score`, `Score_Detail`, `Size_GB`, `GPU_Limit_GB`, `RAM_Limit_GB`.

### `run.py` — open-interpreter chat runner

Connects `open-interpreter` to a local Ollama instance
(`ollama/qwen3.5:9b-q8_0` at `http://192.168.70.125:11434`) with `auto_run=True`
and starts an interactive CLI session.

### `chats.py` — chatbot API probe

Reads a CSV of chatbot URLs, hits `{url}/api/message`, and saves all responses to
`responses.md`. Standalone script; CSV path is hardcoded.

## Key Dependencies

| Package | Purpose |
| --- | --- |
| `aiohttp` | Async HTTP fetching in scraper |
| `beautifulsoup4` + `lxml` | HTML parsing |
| `tqdm` | Progress bars (`tqdm_asyncio`) |
| `open-interpreter` | LLM chat runtime (`run.py`) |
| `uvloop` | Optional faster event loop for scraper |
| `pandas` + `requests` | Used in `chats.py` |
