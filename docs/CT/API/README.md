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
| Session | `/v1/sessions` | List, Get, Create, Update, Delete | SSN-01..04, SRV-01..05 |
| Message | `/v1/sessions/{id}/messages` | List, Create (SSE) | SRV-06..07 |
| Tool | `/v1/tools` | List, Get | SRV-08..09 |
| Config | `/v1/config` | Get, Update | SRV-10..11 |
| Subagent | `/v1/sessions/{id}/subagents` | List, Create, Get | AGT-09..10 |
| Memory | `/v1/memory` | List, Create, Search | MEM-01..03 |
| Snapshot | `/v1/sessions/{id}/snapshots` | List, Create, Restore | SSN-05..06 |
| Todo | `/v1/sessions/{id}/todos` | List, Create, Update | TL-16..18 |

## Endpoint Index

| Method | Path | operationId | UC ID | Description |
| ------ | ---- | ----------- | ------- | ----------- |
| GET | `/v1/sessions` | ssn03ListSessions | SSN-03 | List sessions (paginated) |
| POST | `/v1/sessions` | srv02CreateSession | SRV-02 | Create new session |
| GET | `/v1/sessions/{session_id}` | srv08GetSession | — | Get session metadata |
| PATCH | `/v1/sessions/{session_id}` | srv04UpdateSession | SRV-04 | Update session metadata |
| DELETE | `/v1/sessions/{session_id}` | srv05DeleteSession | SRV-05 | Delete session |
| GET | `/v1/sessions/{session_id}/messages` | srv05GetMessageHistory | SRV-05 | Get message history (paginated) |
| POST | `/v1/sessions/{session_id}/messages` | srv03SendMessage | SRV-03 | Send message (SSE stream) |
| GET | `/v1/tools` | srv06ListTools | SRV-06 | List registered tools |
| GET | `/v1/tools/{tool_id}` | srv09GetTool | SRV-09 | Get tool details |
| GET | `/v1/config` | srv07GetConfig | SRV-07 | Get agent configuration |
| PATCH | `/v1/config` | srv11UpdateConfig | SRV-11 | Update agent configuration |
| GET | `/v1/sessions/{session_id}/subagents` | agt09ListSubagents | AGT-09 | List child agents |
| POST | `/v1/sessions/{session_id}/subagents` | agt09SpawnSubagent | AGT-09 | Spawn child agent |
| GET | `/v1/sessions/{session_id}/subagents/{subagent_id}` | agt10GetSubagent | AGT-10 | Get subagent result |
| POST | `/v1/memory` | mem01PersistKnowledge | MEM-01 | Store knowledge entry |
| GET | `/v1/memory` | mem02RecallKnowledge | MEM-02 | Retrieve knowledge |
| GET | `/v1/memory/search` | mem03SearchKnowledge | MEM-03 | Search knowledge (FTS) |
| GET | `/v1/sessions/{session_id}/snapshots` | ssn05ListSnapshots | SSN-05 | List session snapshots |
| POST | `/v1/sessions/{session_id}/snapshots` | ssn05CreateSnapshot | SSN-05 | Create session snapshot |
| POST | `/v1/sessions/{session_id}/snapshots/{snapshot_id}:restore` | ssn06RestoreSnapshot | SSN-06 | Restore from snapshot |
| GET | `/v1/sessions/{session_id}/todos` | tl18ListTodos | TL-18 | List session todos |
| POST | `/v1/sessions/{session_id}/todos` | tl16CreateTodo | TL-16 | Create todo item |
| PATCH | `/v1/sessions/{session_id}/todos/{todo_id}` | tl17UpdateTodo | TL-17 | Update todo item |

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
