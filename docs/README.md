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
| [C4/](C4/README.md) | C4 Architecture | Frozen | Context, container, 21 component diagrams (24 total) |
| [UC/](UC/README.md) | Use Cases | Frozen | 148 UCs — 21 groups |
| [SM/](SM/README.md) | State Machine | Frozen | 4 diagrams — agent lifecycle (process FSM), session, plan, plugin lifecycles |
| [SQ/](SQ/README.md) | Sequence Diagrams | Frozen | 148 diagrams across 21 groups (1:1 with UCs) |
| [ER/](ER/README.md) | ERD | Frozen | 5 store schemas |
| [CL/](CL/README.md) | Class Diagram | Frozen | Runtime class model — 90+ classes across 12 groups |
| [CT/DATA/](CT/DATA/README.md) | Data Contracts | Frozen | ODCS v3.1.0 — 5 contract diagrams + 2 YAML schemas |
| [CT/API/](CT/API/README.md) | HTTP API Surface | Frozen | OAS 3.1.0 + ROD — 23 endpoints, 8 resources |
| [RDM/](RDM/README.md) | Implementation Roadmap | Active | 10 milestone docs for coding |
| [MM/](MM/README.md) | Design Chain Maps | Frozen | Summary and detail chain overview diagrams |
