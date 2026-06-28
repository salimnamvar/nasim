# nasim

**Author:** Salim Namvar &nbsp;|&nbsp; **License:** Apache 2.0

![Design Chain](https://img.shields.io/badge/Design%20Chain-%E2%9C%85%20FROZEN-blue?style=flat-square)

## What nasim does

A CLI code agent + HTTP API server + MCP server, designed from first
principles with a full C4 → code design chain.

- **Code assistance** — read, write, edit files; search code and web; run shell
  commands; manage git operations
- **Multi-interface** — CLI (REPL), HTTP API (FastAPI + SSE), and MCP server
  from a single agent core
- **Multi-provider** — Ollama, OpenAI, Anthropic, and 100+ LLM backends via
  litellm
- **Safety-first** — permission gates, sandboxed execution, injection scanning
- **Extensible** — plugin system, hook system, MCP tool integration

## Architecture Overview

nasim's design follows a **7-layer design chain**: C4 → UC → SM → SQ → ERD/CL → CT/DATA → CT/API.

The architecture uses the **Controller-Service-Repository (CSR)** pattern with strict delegation:

```
User → Controller (CLI/API) → Service (Agent/Router/Safety/...) → Repository (Session/Tool/Memory/...)
```

21 component groups are organized across 4 CSR layers:

| CSR Layer | Groups |
|-----------|--------|
| Blue — Controller | CLI Group, API Group |
| Orange — Service | Agent, Router, Provider, Safety, Context Graph, Edit Strategy, Evaluation |
| Green — Repository | Session, Tool, Memory, Config, Git, Repo Intelligence |
| Purple — Infrastructure | MCP, Sandbox, Observability, Wire Log, Hooks, Plugins |

See [docs/MM/README.md](docs/MM/README.md) for the design chain meta-map and [docs/C4/README.md](docs/C4/README.md) for full C4 inventory (24 diagrams: 1 context + 1 container + 2 overviews + 21 component groups).

## Design Layer Status

| Layer | Directory | Artifacts | Count | Status |
|-------|-----------|-----------|-------|--------|
| C4 | [docs/C4/](docs/C4/README.md) | 24 `.puml` — context, container, overviews, 21 component groups | 24 | ✅ FROZEN & LINTED |
| UC | [docs/UC/](docs/UC/README.md) | 25 `.puml` — 148 use cases across 21 groups | 25 | ✅ FROZEN & LINTED |
| SM | [docs/SM/](docs/SM/README.md) | 15 `.puml` — lifecycle transitions (agent, session, plan, plugin, etc.) | 15 | ✅ FROZEN & LINTED |
| SQ | [docs/SQ/](docs/SQ/README.md) | 149 `.puml` — 148 behavioral + 1 template, across 21 groups | 149 | ✅ FROZEN & LINTED |
| ERD | [docs/ER/](docs/ER/README.md) | 5 `.puml` — session store, memory, observability, repo intel, wire log | 5 | ✅ FROZEN & LINTED |
| CL | [docs/CL/](docs/CL/README.md) | 1 `.puml` — runtime class model (90+ classes) | 1 | ✅ FROZEN & LINTED |
| CT/DATA | [docs/CT/DATA/](docs/CT/DATA/README.md) | 5 `.puml` + 2 `.yaml` — data contracts (ODCS v3.1.0) | 7 | ✅ FROZEN & LINTED |
| CT/API | [docs/CT/API/](docs/CT/API/README.md) | 6 `.puml` + `openapi.yaml` + `rod_decisions.md` — OAS 3.1.0 API (23 endpoints) | 8 | ✅ FROZEN & LINTED |
| RDM | [docs/RDM/](docs/RDM/README.md) | 10 `.md` — implementation roadmap milestones | 10 | ✅ FROZEN & LINTED |

## Audit & Quality

33 audit documents processed across 3 auditor groups:

| Auditor | Documents | Solved | Partial |
|---------|-----------|--------|---------|
| Agents | 11 | 9 ✅ | 2 ⚠️ |
| big-pickle | 11 | 8 ✅ | 3 ⚠️ |
| mimo | 11 | 11 ✅ | 0 ⚠️ |
| **Total** | **33** | **28 ✅** | **5 ⚠️** |

### Linter Results (all at 0 violations)

| Linter | Scope | Result |
|--------|-------|--------|
| C4 linter | 236 files | 0 violations |
| SM linter | 16 files | 0 violations |
| SQ linter | 151 files | 0 violations |
| UC linter | UC files | no violations found |
| ERD linter | 5 files | 0 violations |
| ROD/CSR/SQ | 26 files | 0 violations |
| Cross-layer naming | — | 0 violations |

### Completed Tasks (Sprint 4)

- S4-AGENTS-ALL: 11 agent audit docs processed — 52 findings
- S4-BIGPICKLE-ALL: 11 big-pickle audit docs processed — 60 findings
- S4-MIMO-ALL: 11 mimo audit docs processed — 430 findings (all resolved)
- S4-FIX-UC-STEREO: 11 UC misclassifications fixed
- S4-FIX-CSR-WRL05: CSR layering in sq_wirelog05 fixed
- S4-FIX-API-ROD: 6 API diagrams — HTTP→ROD + structured errors
- S4-FIX-EVL09-ROD: sq_evaluation09 HTTP→ROD format
- S4-FIX-SQ-FILENAMES: ~100 SQ filename refs corrected in UC README
- S4-FIX-UC-HEADERS: 20 `.puml` header comments aligned
- S4-ADD-ANTIPATTERNS: anti-patterns.md, sm.md, rod.md updated
- S4-LINTER-SWEEP: 0 violations across all layers

## Project Status

- **Design chain:** ✅ FROZEN — all 8 layers complete, audited, and verified
- **Implementation:** ⏳ Not yet begun — see [docs/RDM/](docs/RDM/README.md) for roadmap
- **CI/CD:** Workflows defined in `.github/workflows/` (`python-ci.yml`, `c4-lint.yml`)
- **Pre-commit hooks:** Configured in `.githooks/` (pre-commit, post-commit, pre-push)

## Docs Navigation

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

## Open Items (Deferred Architectural Decisions)

11 items deferred from audit, awaiting resolution:

- F-1: HTTP `/v1/` prefix consistency for non-API groups (CT/API owner)
- F-2: Structured error schema `{error:{code,message,status}}` standardization (CT/API owner)
- F-3: AGT-01 state misassignment RUNNING vs lifecycle states (Agent owner)
- F-5: EDT-01 StrategySelector vs EditStrategyManager decomposition (Edit Strategy owner)
- F-6: C4 Tools vs SQ Tools naming granularity (Tool/C4 owner)
- A-04: Black Box Service threshold for simple service components (Tech Lead)
- ContextGraph Repository layer: stateless exception needs formal sign-off (Tech Lead)
- ContextGraph CTX-06: PipelineOrchestrator vs TokenBudgetTracker ownership (UC owner)
- CI linting automation integration (DevOps)
- `sq_enforce.py` / template compliance tooling (Tech Lead)
- UC-ID gap documentation — AGT-05 vacant rationale (UC owner)

## Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
bash scripts/lint.sh
```

See [docs/RDM/](docs/RDM/README.md) for the implementation roadmap.

## License

Apache 2.0 — see [LICENSE](LICENSE).
