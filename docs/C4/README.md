# NASIM C4 Architecture Diagrams

C4 architecture model for NASIM Service: a single deployable Python application
that translates natural language into file changes via agentic tool orchestration.

## Diagram set

| File | C4 Level | Version | Description |
| ---- | -------- | ------- | ----------- |
| [c4_nasim_context.puml](c4_nasim_context.puml) | Context | v13.0.0 | NASIM Service as a single system with Developer actor and 8 external systems |
| [c4_nasim_container.puml](c4_nasim_container.puml) | Container | v13.0.0 | Single NASIM Application container + 5 external clients + 8 external systems |
| [c4_nasim_component.puml](c4_nasim_component.puml) | Component | v13.0.0 | Full CSR 3-layer view: Controller, Service, Repository, Data Store |
| [common/c4_styles.puml](common/c4_styles.puml) | — | v10.0.0 | Shared CSR AddElementTag palette and skinparam stereotypes |

## How to read

1. **Context** — what NASIM Service is and what it talks to.
2. **Container** — the single deployable application, its external clients,
   and system dependencies.
3. **Component** — internal architecture: adapters → Agent Controller →
   services → repositories → data stores → external systems.

## Architecture summary

NASIM Service runs as a single Python process. All interfaces (CLI, WebApp,
DesktopApp, MobileApp, MCP Client) are external clients that connect to the
same NASIM Application container via HTTP/JSON + SSE or stdio.

### CSR pattern

```
User → Controller (CLI Adapter, HTTP Adapter, MCP Adapter → Agent Controller)
     → Service (Task Service, Tool Service, Session Service, Config Service,
                Safety Service, Context Service, Evaluation Service)
     → Repository (Session Repository, LLM Repository, Filesystem Repository,
                    Sandbox Repository, Edit Strategy Repository, Git Repository,
                    MCP Repository, Repo Intelligence Repository, Web Repository,
                    Wire Log Repository, Memory Repository, Config Repository,
                    History Repository)
     → Data Stores (Session, Memory, WireLog, Config)
```

### External systems

| System | Purpose |
| ------ | ------- |
| LLM Backend | Multi-provider inference via litellm |
| Host Filesystem | Project source code and configuration |
| Sandbox Runtime | OS-level process isolation |
| Web | Documentation and search engines |
| MCP Server | Extension tools via MCP protocol |
| Git Repository | Version-controlled project files |
| Repo Intelligence Backend | Tree-sitter, LSP, embeddings, vector store |

### External clients

| Client | Transport |
| ------ | --------- |
| CLI | HTTP/JSON + SSE |
| WebApp | HTTP/JSON + SSE |
| DesktopApp | HTTP/JSON + SSE |
| MobileApp | HTTPS + SSE |
| MCP Client | stdio / SSE |

## Rendering

All diagrams use [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
v2.10.0. Render with any PlantUML tool:

```bash
plantuml c4_nasim_context.puml
plantuml c4_nasim_container.puml
plantuml c4_nasim_component.puml
```

## Versioning

Context, Container, and Component diagrams share version **v13.0.0**.
Source traceability: `README.md` → Context → Container → Component.

## Design chain

C4 feeds into UC → SM → SQ → ERD → CL → CT. All lifelines in SQ diagrams
trace back to components defined here.

## See also

- [Design chain index](../README.md)
- [UC diagrams](../UC/README.md)
- [Sequence diagrams](../SQ/README.md)