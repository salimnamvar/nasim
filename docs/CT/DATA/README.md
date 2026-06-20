# nasim — CT/DATA Inventory

Data contracts following ODCS v3.1.0 for persistent stores.

Back to [docs/](../README.md).

## Contracts

| File | Store Boundary | Entity Count | Description |
| ---- | -------------- | :----------: | ----------- |
| `nasim_session_store.datacontract.yaml` | Session Store | 3 | Session metadata, messages, file metadata |

## Store Summary

| Store | Type | Path Pattern | Description |
| ----- | ---- | ------------ | ----------- |
| Session Store | JSON Lines | `~/.nasim/sessions/{id}/session.jsonl` | Agent conversation history |

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
