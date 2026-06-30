# docs — Design Artifacts

Design chain artifacts for the nasim CLI code agent + HTTP API server + MCP
server.

Back to [project root](../README.md).

## Design chain

```
C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code
```

Nasim uses JSON file sessions (no relational database). CT/DATA covers session,
memory, and todo store data contracts. CT/API covers the HTTP API server surface
(OAS 3.1.0).

## Layer index

| Directory | Layer | Status | Contents |
| --------- | ----- | ------ | -------- |
| [C4/](C4/README.md) | C4 Architecture | Revised | Context, container, consolidated component diagram (3 + styles) |
| [UC/](UC/README.md) | Use Cases | In progress | 146 UCs — 21 groups |
| [SM/](SM/README.md) | State Machine | In progress | 15 diagrams — 195 transitions, all SQ-covered |
| [SQ/](SQ/README.md) | Sequence Diagrams | In progress | 146 diagrams across 22 groups |
| [ER/](ER/README.md) | ERD | In progress | 5 store schemas (4 C4 data stores + 1 informational) |
| [CL/](CL/README.md) | Class Diagram | In progress | Runtime class model — 102 classes across 17 layers |
| [CT/DATA/](CT/DATA/README.md) | Data Contracts | In progress | ODCS v3.1.0 — 5 contract diagrams + 3 schemas |
| [CT/API/](CT/API/README.md) | HTTP API Surface | In progress | OAS 3.1.0 + ROD — 23 endpoints, 8 resources |
| [RDM/](RDM/README.md) | Implementation Roadmap | Active | 12 milestone docs for coding |
| [MM/](MM/README.md) | Design Chain Maps | In progress | Summary and detail chain overview diagrams |
