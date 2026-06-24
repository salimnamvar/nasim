# nasim — ROD Pattern (Project-Specific)

Extends `~/.claude/rules/software-design/rod.md` for nasim's HTTP Server Layer.

## Applicability

ROD applies to the future HTTP Server Layer (Phase 3). The CLI interface does not use ROD.

## Resource Model (Phase 3)

### Resources

| Resource | Collection | Description |
|----------|------------|-------------|
| Session | `/sessions` | Agent conversation session |
| Message | `/sessions/{session}/messages` | Message within a session |
| Tool | `/tools` | Registered tool |
| Config | `/config` | Agent configuration (singleton) |

### Standard Methods

| Resource | List | Get | Create | Update | Delete |
|----------|------|-----|--------|--------|--------|
| Session | GET /sessions | GET /sessions/{session} | POST /sessions | PATCH /sessions/{session} | DELETE /sessions/{session} |
| Message | GET /sessions/{session}/messages | — | POST /sessions/{session}/messages | — | — |
| Tool | GET /tools | GET /tools/{tool} | — | — | — |
| Config | — | GET /config | — | PATCH /config | — |

### Custom Methods

| Method | Path | Description |
|--------|------|-------------|
| send | POST /sessions/{session}:send | Submit user message and get agent response |

### Pagination

Every List endpoint supports:
- `page_size` (query) — max items to return
- `page_token` (query) — opaque cursor from previous response
- Response includes `next_page_token`

### Field Masks

PATCH operations use `update_mask` to specify which fields to update.

### Error Format (AIP-193)

```json
{
  "error": {
    "code": 404,
    "message": "Session not found",
    "status": "NOT_FOUND",
    "details": []
  }
}
```

### Field Behavior

| Resource | Field | Behavior |
|----------|-------|----------|
| Session | id | OUTPUT_ONLY |
| Session | created_at | OUTPUT_ONLY |
| Session | model | REQUIRED |
| Session | state | OUTPUT_ONLY |
| Message | role | REQUIRED |
| Message | content | REQUIRED |
| Message | tool_calls | OUTPUT_ONLY |
| Tool | name | OUTPUT_ONLY |
| Tool | description | OUTPUT_ONLY |
| Tool | parameters | OUTPUT_ONLY |
| Config | provider | REQUIRED |
| Config | model | REQUIRED |
| Config | safety_mode | OPTIONAL |
