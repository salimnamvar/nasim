# C4 Architecture

C4 model for NASIM Service: a single Python application that translates
natural language into file changes via agentic tool orchestration.

## Diagram set

| File | C4 Level | Version | Description |
| ---- | -------- | ------- | ----------- |
| [c4_nasim_context.puml](c4_nasim_context.puml) | Context | v13.0.0 | NASIM as a system with Developer and 8 external systems |
| [c4_nasim_container.puml](c4_nasim_container.puml) | Container | v13.0.0 | Single NASIM Application + 5 clients + 8 systems |
| [c4_nasim_component.puml](c4_nasim_component.puml) | Component | v13.0.0 | CSR 3-layer: Controller, Service, Repository, Data Store |
| [common/c4_styles.puml](common/c4_styles.puml) | — | v10.0.0 | Shared CSR palette and skinparam stereotypes |

## How to read

1. **Context** — what NASIM is and what it talks to.
2. **Container** — the deployable unit, its clients, and dependencies.
3. **Component** — internal architecture: adapters to Agent Controller to
   services to repositories to data stores to external systems.

## Architecture

NASIM runs as a single Python process. All clients (CLI, WebApp, DesktopApp,
MobileApp, MCP Client) connect via HTTP/JSON+SSE or stdio. Internally the
application follows a strict CSR pattern: Controller → Service → Repository →
Data Store. See the [component diagram](c4_nasim_component.puml) for the
full layer breakdown.

## Rendering

Requires [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
v2.10.0:

```bash
plantuml c4_nasim_context.puml
plantuml c4_nasim_container.puml
plantuml c4_nasim_component.puml
```

## Design chain

C4 feeds into UC → SM → SQ → ERD → CL → CT. All lifelines in SQ diagrams
trace back to components defined here.

## See also

- [Design chain index](../README.md)
- [UC diagrams](../UC/README.md)
- [Sequence diagrams](../SQ/README.md)
