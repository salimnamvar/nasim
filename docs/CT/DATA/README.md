# nasim — CT/DATA Inventory

Data contracts following ODCS v3.1.0 for persistent stores.

Back to [docs/](../README.md).

## Contracts

| File | Store Boundary | Entity Count | Description |
| ---- | -------------- | :----------: | ----------- |
| `nasim_session_store.datacontract.yaml` | Session Store | 3 | Session metadata, messages, file metadata |
| `nasim_memory_store.datacontract.yaml` | Memory Store | 3 | Knowledge entries, index, scope |
| `nasim_todo_store.datacontract.yaml` | Todo Store | 2 | Todo items, session association |
| `ct_data_wire_log.puml` | Wire Log | 3 | WireEvent, TurnIndexEntry, WireMetadata |
| `ct_data_observability.puml` | Observability | 6 | LogRecord, MetricPoint, TraceContext, ObservabilityConfig, RedactionRule, LogLevel |

## Store Summary

| Store | Type | Path Pattern | Description |
| ----- | ---- | ------------ | ----------- |
| Session Store | JSON Lines | `~/.nasim/sessions/{id}/session.jsonl` | Agent conversation history |
| Memory Store | JSON Lines | `~/.nasim/memory/{scope}/{key}.json` | Cross-session knowledge |
| Todo Store | JSON Lines | `~/.nasim/sessions/{id}/todos.jsonl` | Task tracking within sessions |

## Design Chain Position

```
... → SQ → ERD → CL → CT/DATA → CT/API → Code
```

CT/DATA receives input from ERD (logical schema) and SQ (field accesses),
and outputs to CL (entity names, attributes) and CT/API (request/response schemas).

## Related Layers

| Layer | Path |
| ----- | ---- |
| ERD (source) | `docs/er/er_session_store.puml` |
| CL (target) | `docs/cl/cl_runtime_model.puml` |
| CT/API (sibling) | `docs/CT/API/openapi.yaml` |
