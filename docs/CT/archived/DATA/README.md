# nasim — CT/DATA Inventory

Data contracts following ODCS v3.1.0 for persistent stores.

Back to [docs/](../README.md).

## Contracts

### Data Contracts (ODCS YAML)

| File | Store Boundary | Entity Count | Description |
| ---- | -------------- | :----------: | ----------- |
| `nasim_session_store.datacontract.yaml` | Session Store | 3 | Session metadata, messages, file metadata |
| `data_contract_session_store.yaml` | Session Store | — | Legacy/alternate session store contract |

### Data Contract Diagrams (PlantUML)

| File | Store Boundary | C4 Component | Entity Count | Description |
| ---- | -------------- | ------------ | :----------: | ----------- |
| `ct_data_wire_log.puml` | Wire Log | Wire Log Repository | 3 | WireEvent, TurnIndexEntry, WireMetadata |
| `ct_data_repo_intelligence.puml` | Repo Intelligence | Repo Intelligence Repository | 8 | ASTTag, SymbolNode, SymbolEdge, RankedSymbol, SearchResult, RepoMap, SymbolType, EdgeType |
| `ct_data_evaluation.puml` | Evaluation | Evaluation Service | 6 | SuccessCheck, QualitySignal, ReviewResult, RetryConfig, TurnBudget, FailureStrategy |
| `ct_data_context_graph.puml` | Context Graph | Context Service | 5 | ContextNode, ContextEdge, PipelineResult, NodeType, EdgeType |

### Missing Contracts (Gap Analysis)

| C4 Data Store | ERD | CT/DATA Contract | Status |
| ------------- | --- | ---------------- | ------ |
| Session Store | `er_session_store.puml` | `nasim_session_store.datacontract.yaml` | ✅ Complete |
| Wire Log Store | `er_wire_log.puml` | `ct_data_wire_log.puml` | ✅ Complete |
| Memory Store | `er_memory_store.puml` | — (in-memory + filesystem) | ⚠️ No formal contract needed — JSON files |
| Config Store | `er_config_store.puml` | — (YAML files) | ⚠️ No formal contract needed — layered YAML |

## Design Chain Position

```
C4 → UC → SM → SQ → CL → ER → CT/DATA → CT/API → RDM
```

CT/DATA receives input from ERD (logical schema) and outputs to CL (entity names, attributes).

## Related Layers

| Layer | Path | Relationship |
| ----- | ---- | ------------ |
| ERD (source) | `docs/ER/` | Defines physical store schema for each data store |
| CL (target) | `docs/CL/cl_runtime_model.puml` | Maps data structures to runtime classes |
| CT/API (sibling) | `docs/CT/API/openapi.yaml` | Shares schema definitions for HTTP access |
