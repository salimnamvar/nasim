nasim — a CLI code agent + HTTP API server + MCP server, designed from first
principles with a full C4 → code design chain.

## What nasim does

- **Code assistance** — read, write, edit files; search code and web; run shell
  commands; manage git operations
- **Multi-interface** — CLI (REPL), HTTP API (FastAPI + SSE), and MCP server
  from a single agent core
- **Multi-provider** — Ollama, OpenAI, Anthropic, and 100+ LLM backends via
  litellm
- **Safety-first** — permission gates, sandboxed execution, injection scanning
- **Extensible** — plugin system, hook system, MCP tool integration

## Status

Design-chain phase (C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code)
is in draft under `docs/`. Implementation has not yet begun. CI-CD is in plan
step across the whole project.

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
bash scripts/lint.sh
```

See `docs/RDM/` for the implementation roadmap.

## Docs navigation

| Directory | Contents |
| --------- | -------- |
| [docs/C4/](docs/C4/README.md) | 24 C4 architecture diagrams |
| [docs/UC/](docs/UC/README.md) | 148 use cases across 21 groups |
| [docs/SM/](docs/SM/README.md) | 4 state machine diagrams |
| [docs/SQ/](docs/SQ/README.md) | 148 sequence diagrams |
| [docs/ER/](docs/ER/README.md) | 5 entity-relationship diagrams |
| [docs/CL/](docs/CL/README.md) | Runtime class model |
| [docs/CT/](docs/CT/DATA/README.md) | Data contracts (ODCS v3.1.0) + HTTP API (OAS 3.1.0) |
| [docs/RDM/](docs/RDM/README.md) | Implementation roadmap |
| [docs/MM/](docs/MM/README.md) | Design chain maps |

## License

Apache 2.0 — see [LICENSE](LICENSE).
