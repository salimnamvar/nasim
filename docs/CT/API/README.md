# nasim — CT/API Inventory

HTTP API surface following OAS 3.1.0 + ROD (Resource-Oriented Design).

Back to [docs/](../README.md).

## Artifacts

### OpenAPI + ROD

| File | Scope | Description |
| ---- | ----- | ----------- |
| `openapi.yaml` | HTTP API | OpenAPI 3.1.0 spec — 23 endpoints across 8 resources |
| `rod_decisions.md` | ROD | Resource model, methods, field behavior, pagination, errors |

### API Diagrams (PlantUML)

| File | Scope | Description |
| ---- | ----- | ----------- |
| `ct_api_wire_log.puml` | Wire Log | Wire log API surface |
| `ct_api_repo_intelligence.puml` | Repo Intelligence | Repo intelligence API surface |
| `ct_api_edit_strategy.puml` | Edit Strategy | Edit strategy API surface |
| `ct_api_evaluation.puml` | Evaluation | Evaluation API surface |
| `ct_api_context_graph.puml` | Context Graph | Context graph API surface |

## Resource Model

| Resource | Collection | Methods | UC Range |
| -------- | ---------- | ------- | -------- |
| Session | `/v1/sessions` | List, Get, Create, Update, Delete | SESSION-01..04, SRV-01..05 |
| Message | `/v1/sessions/{id}/messages` | List, Create (SSE) | SRV-06..07 |
| Tool | `/v1/tools` | List, Get | SRV-08..09 |
| Config | `/v1/config` | Get, Update | SRV-10..11 |
| Subagent | `/v1/sessions/{id}/subagents` | List, Create, Get | AGENT-09..10 |
| Memory | `/v1/memory` | List, Create, Search | MEMORY-01..03 |
| Snapshot | `/v1/sessions/{id}/snapshots` | List, Create, Restore | SESSION-05..06 |
| Todo | `/v1/sessions/{id}/todos` | List, Create, Update | TOOL-16..18 |

## Endpoint Index

| Method | Path | operationId | UC ID | Description |
| ------ | ---- | ----------- | ------- | ----------- |
| GET | `/v1/sessions` | listSessions | SESSION-03 | List sessions (paginated) |
| POST | `/v1/sessions` | createSession | SESSION-01 | Create new session |
| GET | `/v1/sessions/{session}` | getSession | SESSION-02 | Get session metadata |
| PATCH | `/v1/sessions/{session}` | updateSession | SESSION-04 | Update session metadata |
| DELETE | `/v1/sessions/{session}` | deleteSession | SESSION-09 | Delete session |
| POST | `/v1/sessions/{session}:dispatch` | sendMessage | API-06 | Send message (SSE stream) |
| GET | `/v1/sessions/{session}/messages` | listMessages | API-07 | Get message history (paginated) |
| GET | `/v1/tools` | listTools | TOOL-14 | List registered tools |
| GET | `/v1/tools/{tool}` | getTool | TOOL-14 | Get tool details |
| GET | `/v1/config` | getConfig | CONFIG-01 | Get agent configuration |
| PATCH | `/v1/config` | updateConfig | CONFIG-02 | Update agent configuration |
| GET | `/v1/sessions/{session}/subagents` | listSubagents | AGENT-09 | List child agents |
| POST | `/v1/sessions/{session}/subagents` | spawnSubagent | AGENT-09 | Spawn child agent |
| GET | `/v1/sessions/{session}/subagents/{subagent}` | getSubagent | AGENT-10 | Get subagent result |
| POST | `/v1/memory` | persistKnowledge | MEMORY-01 | Store knowledge entry |
| GET | `/v1/memory` | recallKnowledge | MEMORY-02 | Retrieve knowledge |
| GET | `/v1/memory/search` | searchKnowledge | MEMORY-03 | Search knowledge (FTS) |
| GET | `/v1/sessions/{session}/snapshots` | listSnapshots | SESSION-05 | List session snapshots |
| POST | `/v1/sessions/{session}/snapshots` | createSnapshot | SESSION-05 | Create session snapshot |
| POST | `/v1/sessions/{session}/snapshots/{snapshot}:restore` | restoreSnapshot | SESSION-06 | Restore from snapshot |
| GET | `/v1/sessions/{session}/todos` | listTodos | TOOL-18 | List session todos |
| POST | `/v1/sessions/{session}/todos` | createTodo | TOOL-16 | Create todo item |
| PATCH | `/v1/sessions/{session}/todos/{todo}` | updateTodo | TOOL-17 | Update todo item |

**Total: 23 endpoints across 8 resources**

## Resources

| Resource | Collection Path | Methods | Owner (C4) |
| -------- | --------------- | ------- | ---------- |
| Session | `/v1/sessions` | List, Get, Create, Update, Delete | HTTPAdapter → SessionService |
| Message | `/v1/sessions/{session}/messages` | List, Create (SSE via `:dispatch`) | HTTPAdapter → AgentController |
| Tool | `/v1/tools` | List, Get | HTTPAdapter → ToolService |
| Config | `/v1/config` | Get, Update | HTTPAdapter → ConfigRepository |
| Subagent | `/v1/sessions/{session}/subagents` | List, Create, Get | HTTPAdapter → TaskService |
| Memory | `/v1/memory` | List, Create, Search | HTTPAdapter → MemoryRepository |
| Snapshot | `/v1/sessions/{session}/snapshots` | List, Create, Restore | HTTPAdapter → SessionService |
| Todo | `/v1/sessions/{session}/todos` | List, Create, Update | HTTPAdapter → TaskService |

## Design Chain Position

```
C4 → UC → SM → SQ → CL → ER → CT/DATA → CT/API → RDM
```

CT/API receives input from UC (operation definitions), CT/DATA (field names, types),
and SQ (message flow), and outputs to Code (route handlers, schemas).

## Related Layers

| Layer | Path | Relationship |
| ----- | ---- | ------------ |
| UC (source) | `docs/UC/` | Defines operations that map to HTTP endpoints |
| SQ (source) | `docs/SQ/` | Validates message flow through HTTPAdapter |
| CT/DATA (sibling) | `docs/CT/DATA/` | Shares schema definitions for request/response bodies |
