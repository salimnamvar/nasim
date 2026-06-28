# MM — Design Chain Maps

Meta-level diagrams showing the full design chain for the nasim CLI code agent.
These are navigation aids, not design artifacts — they summarise layer completion
and link to the actual artifacts in other `docs/` directories.

Back to [docs/](../README.md).

## Diagrams

No PlantUML diagrams exist in this directory yet. The README serves as the chain overview.

## Design Chain

```
C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code
```

| Layer | Location |
| ----- | -------- |
| C4 Architecture | `docs/C4/` |
| Use Cases | `docs/UC/` |
| State Machine | `docs/SM/` |
| Sequence Diagrams | `docs/SQ/` |
| ERD (logical schema) | `docs/ER/` |
| Class Diagram | `docs/CL/` |
| Data Contracts | `docs/CT/DATA/` |
| API Surface | `docs/CT/API/` |
| Implementation Roadmap | `docs/RDM/` |

## Layer Status

| Layer | Status | Artifacts | Notes |
| ----- | ------ | --------- | ----- |
| C4 | In progress | 24 diagrams | Context + container + 21 component groups |
| UC | In progress | 25 UC files + inventory | 148 UCs across 21 groups |
| SM | In progress | 15 diagrams + inventory | Agent, session, plan, plugin, and more |
| SQ | In progress | 149 diagrams | 1:1 with UCs, across 21 groups |
| ERD | In progress | 5 diagrams + inventory | Session, memory, observability, repo intelligence, wire log |
| CL | In progress | 1 diagram + inventory | Runtime class model (90+ classes) |
| CT/DATA | In progress | 5 contract diagrams + 2 YAML | ODCS v3.1.0 data contracts |
| CT/API | In progress | 6 API diagrams + OpenAPI + ROD | OAS 3.1.0 HTTP API surface |
| RDM | Active | 10 milestone docs | Implementation roadmap |
