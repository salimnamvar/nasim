# nasim

**nasim** — a research code agent.

Built through systematic investigation and original synthesis of usage patterns.

Current status: comprehensive design chain with 148 sequence diagrams, 148 use cases, full C4 architecture, and detailed implementation roadmap. Implementation has not yet begun.

## What nasim is

A CLI code agent + HTTP API server + MCP server, designed from first principles with a complete C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code design chain.

## What exists today

- Complete design chain under `docs/` (frozen)
- Implementation roadmap under `docs/RDM/` (10 milestone docs)
- Reference agent audits against 28 agents under `docs/audit/`
- Research data on Ollama models under `data/`
- Development scripts: lint, clean, environment setup
- Utility scripts: Ollama model scraping/analysis, doc merging

## Design artifacts

| Layer | Artifacts | Status |
|-------|-----------|--------|
| C4 Architecture | 24 diagrams (context, container, 21 component groups) | Frozen |
| Use Cases | 22 UC files — 148 UCs across 21 groups | Frozen |
| State Machine | 4 diagrams (agent, session, plan, plugin lifecycles) | Frozen |
| Sequence Diagrams | 148 diagrams across 21 groups | Frozen |
| ERD | 5 store schemas | Frozen |
| Class Diagram | 1 runtime model | Frozen |
| Data Contracts | 5 ODCS v3.1.0 contracts + 2 YAML schemas | Frozen |
| HTTP API Surface | 6 API puml + OpenAPI 3.1.0 + ROD decisions | Frozen |
| Implementation Roadmap | 10 milestone docs | Active |
| Audit Reports | 18 audit documents (28 reference agents) | Active |

## Quick start

```bash
# From repo root (after cloning)
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Environment setup (recommended on new machine)

```bash
bash scripts/setup/setup_env.sh
```

Requires Python 3.10+. Reads `pyproject.toml` automatically.

## Development

```bash
# Lint + format + types (uses black, isort, ruff, pyright)
bash scripts/lint.sh

# Clean build / cache artifacts
bash scripts/clean.sh

# Full environment provisioning
bash scripts/setup/setup_env.sh
```

See [scripts/README.md](scripts/README.md) and [scripts/setup/README.md](scripts/setup/README.md).

## Project layout

```
nasim/
├── docs/              # full design chain (C4, UC, SM, SQ, ERD, CL, CT, audit, RDM)
│   ├── C4/            # 24 C4 architecture diagrams
│   ├── UC/            # 22 use case diagrams (148 UCs)
│   ├── SM/            # 4 state machine diagrams
│   ├── SQ/            # 148 sequence diagrams across 21 groups
│   ├── ER/            # 5 entity-relationship diagrams
│   ├── CL/            # class diagram (runtime model)
│   ├── CT/DATA/       # data contracts (ODCS v3.1.0)
│   ├── CT/API/        # HTTP API surface (OAS 3.1.0)
│   ├── RDM/           # implementation roadmap (10 milestones)
│   ├── MM/            # design chain maps
│   ├── audit/         # reference agent audits (18 docs)
│   ├── prompt/        # prompt engineering docs (p1–p9)
│   └── REF/           # reference agent list
├── scripts/           # lint, clean, setup, ollama tools, doc merge
├── data/              # research data (Ollama model analysis)
├── C4.md              # C4 consolidated view
├── UC.md              # UC consolidated view
├── SM.md              # SM consolidated view
├── pyproject.toml
└── README.md
```

## Configuration (planned)

Layered config (global → project → env → CLI) is designed but not implemented.

See `docs/UC/uc_config.puml` and `docs/C4/c4_nasim_component_config.puml`.

## License

Licensed under the Apache License, Version 2.0.

See [LICENSE](LICENSE).

Copyright 2026 Salim Namvar.

## Status & philosophy

nasim exists to explore what a high-quality, understandable, and extensible code agent looks like when you start from first principles and real usage patterns.

The heavy design work (C4 → Code) is complete. Implementation will follow the documented roadmap in `docs/RDM/`.

Contributions that respect the design chain and the "original synthesis" goal are welcome once the project stabilizes.
