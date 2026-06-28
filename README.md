nasim — a CLI code agent, HTTP API server, and MCP server designed from first
principles with a full C4-to-code design chain.

## What nasim does

- **Code assistance** — read, write, edit files; search code and web; run shell
  commands; manage git operations
- **Multi-interface** — CLI (REPL), HTTP API (FastAPI + SSE), and MCP server
  from a single agent core
- **Multi-provider** — Ollama, OpenAI, Anthropic, and 100+ LLM backends via
  litellm
- **Safety-first** — permission gates, sandboxed execution, injection scanning
- **Extensible** — plugin system, hook system, MCP tool integration

## Design chain

nasim's architecture follows a layered design chain that traces from system
overview through to API contracts. Each layer has a dedicated directory under
`docs/` with its own README inventory.

| Layer | Directory | Artifacts | Status |
|-------|-----------|-----------|--------|
| C4 Architecture | [docs/C4/](docs/C4/README.md) | 24 PlantUML diagrams | In progress |
| Use Cases | [docs/UC/](docs/UC/README.md) | 25 PlantUML, 148 use cases | In progress |
| State Machines | [docs/SM/](docs/SM/README.md) | 15 PlantUML diagrams | In progress |
| Sequence Diagrams | [docs/SQ/](docs/SQ/README.md) | 149 PlantUML diagrams | In progress |
| ER Diagrams | [docs/ER/](docs/ER/README.md) | 5 PlantUML diagrams | In progress |
| Class Diagram | [docs/CL/](docs/CL/README.md) | 1 PlantUML (90+ classes) | In progress |
| Data Contracts | [docs/CT/DATA/](docs/CT/DATA/README.md) | ODCS v3.1.0 contracts | In progress |
| API Surface | [docs/CT/API/](docs/CT/API/README.md) | OAS 3.1.0 (23 endpoints) | In progress |
| Roadmap | [docs/RDM/](docs/RDM/README.md) | 10 milestone documents | Active |
| Chain Maps | [docs/MM/](docs/MM/README.md) | Design chain meta-overview | Active |

See [docs/MM/README.md](docs/MM/README.md) for the full design chain
meta-map.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
bash scripts/lint.sh
```

See [docs/RDM/](docs/RDM/README.md) for the implementation roadmap.

## Docs navigation

| Directory | Contents |
| --------- | -------- |
| [docs/C4/](docs/C4/README.md) | 24 C4 architecture diagrams |
| [docs/UC/](docs/UC/README.md) | 148 use cases across 21 groups |
| [docs/SM/](docs/SM/README.md) | 15 state machine diagrams |
| [docs/SQ/](docs/SQ/README.md) | 149 sequence diagrams |
| [docs/ER/](docs/ER/README.md) | 5 entity-relationship diagrams |
| [docs/CL/](docs/CL/README.md) | Runtime class model |
| [docs/CT/](docs/CT/DATA/README.md) | Data contracts (ODCS v3.1.0) + HTTP API (OAS 3.1.0) |
| [docs/RDM/](docs/RDM/README.md) | Implementation roadmap |
| [docs/MM/](docs/MM/README.md) | Design chain maps |

## License

Apache 2.0 — see [LICENSE](LICENSE).
