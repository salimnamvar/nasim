# nasim — CT/API Inventory

HTTP API surface following OAS 3.1.0 + ROD (Resource-Oriented Design).

Back to [docs/](../README.md).

## Artifacts

| File | Scope | Description |
| ---- | ----- | ----------- |
| `openapi.yaml` | HTTP API | OpenAPI 3.1.0 spec — 7 endpoints across 4 resources |
| `rod_decisions.md` | ROD | Resource model, methods, field behavior, pagination, errors |

## Resource Model

| Resource | Collection | Methods | UC Range |
| -------- | ---------- | ------- | -------- |
| Session | `/v1/sessions` | List, Get, Create | SSN-03, SRV-02 |
| Message | `/v1/sessions/{id}/messages` | List, Create (SSE) | SRV-05, SRV-03 |
| Tool | `/v1/tools` | List | SRV-06 |
| Config | `/v1/config` | Get | SRV-07 |

## Endpoint Index

| Method | Path | operationId | UC ID | Description |
| ------ | ---- | ----------- | ------- | ----------- |
| GET | `/v1/sessions` | ssn03ListSessions | SSN-03 | List sessions (paginated) |
| POST | `/v1/sessions` | srv02CreateSession | SRV-02 | Create new session |
| GET | `/v1/sessions/{session_id}` | srv08GetSession | — | Get session metadata |
| GET | `/v1/sessions/{session_id}/messages` | srv05GetMessageHistory | SRV-05 | Get message history (paginated) |
| POST | `/v1/sessions/{session_id}/messages` | srv03SendMessage | SRV-03 | Send message (SSE stream) |
| GET | `/v1/tools` | srv06ListTools | SRV-06 | List registered tools |
| GET | `/v1/config` | srv07GetConfig | SRV-07 | Get agent configuration |

## Design Chain Position

```
... → CL → CT/DATA → CT/API → Code
```

CT/API receives input from CT/DATA (field names, types), ROD (resource model),
and UC (operation definitions), and outputs to Code (route handlers, schemas).

## Related Layers

| Layer | Path |
| ----- | ---- |
| UC (source) | `docs/uc/uc_server.puml` |
| SQ (source) | `docs/sq/SRV/` |
| CL (source) | `docs/cl/cl_runtime_model.puml` |
| CT/DATA (sibling) | `docs/CT/DATA/nasim_session_store.datacontract.yaml` |
