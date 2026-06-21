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
| C4 | Frozen | 24 diagrams | Context + container + 21 component groups |
| UC | Frozen | 22 UC files + inventory | 148 UCs across 21 groups |
| SM | Frozen | 4 diagrams + inventory | Agent, session, plan, plugin lifecycles |
| SQ | Frozen | 148 diagrams | 1:1 with UCs, across 21 groups |
| ERD | Frozen | 5 diagrams + inventory | Session, memory, observability, repo intelligence, wire log |
| CL | Frozen | 1 diagram + inventory | Runtime class model (90+ classes) |
| CT/DATA | Frozen | 5 contract diagrams + 2 YAML | ODCS v3.1.0 data contracts |
| CT/API | Frozen | 6 API diagrams + OpenAPI + ROD | OAS 3.1.0 HTTP API surface |
| RDM | Active | 10 milestone docs | Implementation roadmap |
