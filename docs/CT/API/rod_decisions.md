# nasim — Resource-Oriented Design (ROD) Decisions

**Date:** 2026-06-20
**Scope:** HTTP API server mode — resource model, methods, names, errors
**Upstream:** CT/DATA (session store data contract)
**Downstream:** CT/API (OpenAPI 3.1.0 spec)

---

## Resource Model

### Resources

| Resource | Collection | Parent | Description |
| -------- | ---------- | ------ | ----------- |
| Session | sessions | — | Agent conversation session |
| Message | messages | Session | Individual message within a session |
| Tool | tools | — | Registered tool definitions (read-only) |
| Config | config | — | Agent configuration (read-only singleton) |

### Resource Hierarchy

```
/sessions
/sessions/{session_id}
/sessions/{session_id}/messages
/tools
/config
```

### Resource Names (AIP-122)

- Session name: `sessions/{session_id}` — session_id is a UUID v4
- Message name: `sessions/{session_id}/messages/{sequence}` — sequence is an integer
- Tool name: `tools/{tool_name}` — tool_name is the registered tool identifier
- Config name: `config` — singleton, no ID

---

## Standard Methods

| Resource | Method | HTTP | Path | UC ID | Notes |
| -------- | ------ | ---- | ---- | ------- | ----- |
| Session | List | GET | `/v1/sessions` | SESSIONSERVICE-03 | Paginated (AIP-158) |
| Session | Get | GET | `/v1/sessions/{session_id}` | SESSIONSERVICE-02 | Single session by ID |
| Session | Create | POST | `/v1/sessions` | SRV-02 | Returns 201 with session |
| Message | List | GET | `/v1/sessions/{session_id}/messages` | SRV-05 | Ordered by sequence |
| Message | Create | POST | `/v1/sessions/{session_id}/messages` | SRV-03 | Returns SSE stream |
| Tool | List | GET | `/v1/tools` | SRV-06 | Read-only collection |
| Config | Get | GET | `/v1/config` | SRV-07 | Read-only singleton |

### Method Mapping Rationale

- **Session Create (POST → 201):** Standard AIP-133. Server assigns UUID.
- **Session List (GET):** Standard AIP-131. Supports `page_size` + `page_token`.
- **Session Get (GET):** Standard AIP-132. Returns full session metadata.
- **Message Create (POST → SSE):** Non-standard response type. The request body is the user message; the response is an SSE stream of AgentEvents. This is the only non-JSON response in the API.
- **Message List (GET):** Standard AIP-131. Returns all messages in sequence order.
- **Tool List (GET):** Read-only collection. No create/update/delete — tools are registered at startup.
- **Config Get (GET):** Read-only singleton. No update — config is loaded at startup.

### Custom Methods

None required. All operations fit standard methods. The SSE streaming on Message Create is a response format choice, not a distinct resource operation.

---

## Field Behavior (AIP-203)

### Session

| Field | Behavior | Notes |
| ----- | -------- | ----- |
| `session_id` | OUTPUT_ONLY | Server-assigned UUID v4 |
| `created_at` | OUTPUT_ONLY, IMMUTABLE | Set on create, never changed |
| `model` | OUTPUT_ONLY, IMMUTABLE | Snapshot from Config at creation |
| `provider` | OUTPUT_ONLY, IMMUTABLE | Snapshot from Config at creation |
| `message_count` | OUTPUT_ONLY | Running count, updated after each message |
| `total_tokens` | OUTPUT_ONLY | Cumulative tokens, updated after each LLM round-trip |

### Message (Request)

| Field | Behavior | Notes |
| ----- | -------- | ----- |
| `role` | REQUIRED | Must be "user" on Create — system/assistant/tool are server-generated |
| `content` | REQUIRED | Text content of the user message |

### Message (Response)

| Field | Behavior | Notes |
| ----- | -------- | ----- |
| `session_id` | OUTPUT_ONLY | Parent session reference |
| `sequence` | OUTPUT_ONLY | Server-assigned sequence number |
| `role` | OUTPUT_ONLY | Message role (system/user/assistant/tool) |
| `content` | OUTPUT_ONLY | Text content |
| `tool_calls` | OUTPUT_ONLY | Present on assistant messages with tool use |
| `tool_call_id` | OUTPUT_ONLY | Links tool results to calls |
| `tokens` | OUTPUT_ONLY | Token count for this message |
| `timestamp` | OUTPUT_ONLY | ISO 8601 creation timestamp |

### Tool

| Field | Behavior | Notes |
| ----- | -------- | ----- |
| `name` | OUTPUT_ONLY | Tool identifier |
| `description` | OUTPUT_ONLY | Human-readable description |
| `parameters` | OUTPUT_ONLY | JSON Schema for tool parameters |
| `safe` | OUTPUT_ONLY | Whether tool requires permission gating |

### Config

| Field | Behavior | Notes |
| ----- | -------- | ----- |
| `provider` | OUTPUT_ONLY | Default provider backend |
| `model` | OUTPUT_ONLY | Default model identifier |
| `safety_mode` | OUTPUT_ONLY | ask / auto / off |
| `context_budget` | OUTPUT_ONLY | Max token budget |
| `timeout` | OUTPUT_ONLY | Request timeout in seconds |
| `max_iterations` | OUTPUT_ONLY | Max agentic loop iterations |

---

## Pagination (AIP-158)

Session List supports pagination:

| Parameter | In | Type | Description |
| --------- | -- | ---- | ----------- |
| `page_size` | query | integer | Max sessions to return (default 20, max 100) |
| `page_token` | query | string | Opaque cursor from previous response |
| `next_page_token` | response | string | Empty string when no more pages |

Message List supports pagination:

| Parameter | In | Type | Description |
| --------- | -- | ---- | ----------- |
| `page_size` | query | integer | Max messages to return (default 100, max 1000) |
| `page_token` | query | string | Opaque cursor (sequence number) |
| `next_page_token` | response | string | Empty string when no more pages |

---

## Errors (AIP-193)

All error responses use the canonical error model:

```json
{
  "error": {
    "code": 404,
    "message": "Session not found: abc-123",
    "status": "NOT_FOUND",
    "details": []
  }
}
```

### Error Mapping

| HTTP | `status` | Condition |
| ---- | -------- | --------- |
| 400 | `INVALID_ARGUMENT` | Malformed request body, missing required fields |
| 404 | `NOT_FOUND` | Session or tool not found |
| 422 | `FAILED_PRECONDITION` | Session in wrong state for operation |
| 500 | `INTERNAL` | Unexpected server failure |
| 503 | `UNAVAILABLE` | Agent core or LLM provider unreachable |

---

## SSE Streaming Format

Message Create returns a Server-Sent Events stream. Event types:

| Event | Data Schema | Description |
| ----- | ----------- | ----------- |
| `text_chunk` | `{text: string}` | Streaming text token from LLM |
| `tool_start` | `{name: string, args: object}` | Tool execution started |
| `tool_result` | `{name: string, success: boolean, content: string, error: string \| null}` | Tool execution completed |
| `error` | `{message: string}` | Error occurred during processing |
| `done` | `{final_text: string}` | Agent turn complete |

---

## Versioning

All paths start with `/v1/` (AIP-185). The API version is independent of the server version. Breaking changes bump the major version.

**Status:** RESOLVED (DGA-01 fix, 2026-06-22). All 8 path entries in `openapi.yaml` updated with `/v1/` prefix.

---

## Design Chain Traceability

| ROD Element | Traces To |
| ----------- | --------- |
| Session resource | ERD `session` entity, CL `Session` class, UC group SSN |
| Message resource | ERD `message` entity, CL `Message` (embedded in Session), UC group SRV |
| Tool resource | CL `Tool` ABC + `ToolRegistry`, UC group TL |
| Config resource | CL `Config` dataclass, UC group CFG |
| SSE streaming | SQ `sq_srv03_send_message`, SQ `sq_srv04_stream_response` |
| Pagination | AIP-158, UC SESSIONSERVICE-03 (List Sessions) |
| Errors | AIP-193, SM error states |
