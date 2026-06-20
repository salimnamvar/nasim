# nasim

**nasim** — a research code agent.

Built through systematic investigation and original synthesis of usage patterns.

Current status: early functional proof-of-concept with a clean design chain already in place for the target architecture.

## What nasim does (today)

- Interactive REPL + one-shot command mode
- Basic file and shell tools (`read_file`, `write_file`, `edit_file`, `list_dir`, `shell_exec`)
- Ollama-backed LLM with streaming support
- Minimal agent loop with tool calling

## What it is designed to become

Full design chain exists under `docs/`:

- C4 context/container/component diagrams
- 42 Use Cases (UC)
- State Machine (agent lifecycle)
- 1:1 Sequence Diagrams (SQ)
- Entity definitions, runtime Class Diagram (CL)
- Session persistence (JSON), provider abstraction, safety/permission gates, context compaction, layered config, MCP tool extension points

See [docs/README.md](docs/README.md) and the audit notes in `docs/audit/`.

## Quick start

```bash
# From repo root (after cloning)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run
python run.py --model qwen2.5-coder:14b --server http://localhost:11434

# Or one command
python run.py -c "explain the project structure"
```

Requires a running Ollama instance with a capable coding model.

## Development

```bash
# Lint + format + types (uses black, isort, ruff, pyright)
bash scripts/lint.sh

# Clean build / cache artifacts
bash scripts/clean.sh

# Full environment provisioning (recommended on new machine)
bash scripts/setup/setup_env.sh
```

See [scripts/README.md](scripts/README.md) and [scripts/setup/README.md](scripts/setup/README.md).

## Project layout (current)

```
nasim/
├── nasim/
│   ├── agent.py      # core agent loop + tool orchestration
│   ├── cli.py        # REPL + arg parsing + streaming UX
│   ├── llm.py        # Ollama client (streaming + tool calls)
│   └── tools.py      # tool registry + implementations
├── docs/             # full design chain (C4, UC, SM, SQ, CL, entities)
├── scripts/          # lint, clean, setup
├── data/             # research data (reference agent analysis)
├── run.py            # convenience entry
└── pyproject.toml
```

## Configuration (planned)

Layered config (global → project → env → CLI) is designed but not fully implemented in v0.1.

See `docs/uc/uc_config.puml` and `docs/c4/c4_nasim_component_config.puml`.

## License

Licensed under the Apache License, Version 2.0.

See [LICENSE](LICENSE).

Copyright 2026 Salim Namvar.

## Status & philosophy

nasim exists to explore what a high-quality, understandable, and extensible code agent looks like when you start from first principles and real usage patterns.

The heavy design work (C4 → Code) has already been done. Implementation will follow the documented architecture.

Contributions that respect the design chain and the "original synthesis" goal are welcome once the project stabilizes.
