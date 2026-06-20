# MM — Design Chain Maps

Meta-level diagrams showing the full design chain for the nasim CLI code agent.
These are navigation aids, not design artifacts — they summarise layer completion
and link to the actual artifacts in other `docs/` directories.

Back to [docs/](../README.md).

## Diagrams

| File | Purpose |
| ---- | ------- |
| `mm_design_chain_summary.puml` | Single-page summary of all design layers and their status |
| `mm_design_chain_detail.puml` | Expanded view with component counts, UC groups, and layer notes |

## Design Chain

```
C4 → UC → SM → SQ → ERD → CL → Code
```

| Layer | Location |
| ----- | -------- |
| C4 Architecture | `docs/c4/` |
| Use Cases | `docs/uc/` |
| State Machine | `docs/sm/` |
| Sequence Diagrams | `docs/sq/` |
| ERD (logical schema) | `docs/er/` |
| Class Diagram | `docs/cl/` |
| Implementation Roadmap | `docs/rdm/` |

## Layer Status

| Layer | Status | Artifacts | Notes |
| ----- | ------ | --------- | ----- |
| C4 | Frozen | 10 diagrams | Context + container + 8 component diagrams |
| UC | Frozen | 8 UC files + inventory | 42 UCs across 9 groups |
| SM | Frozen | 1 diagram + inventory | Agent lifecycle process FSM |
| SQ | Frozen | 42 diagrams | 1:1 with UCs, by group |
| ERD | Frozen | 1 diagram + inventory | Session JSON Lines schema |
| CL | Frozen | 1 diagram + inventory | Runtime class model |
| RDM | Active | 10 milestone docs | Implementation roadmap |
