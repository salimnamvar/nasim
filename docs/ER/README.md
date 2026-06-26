# nasim — ERD Inventory

Physical store schema diagrams for all persistent stores.

Back to [docs/](../README.md).

## Diagrams

| File | Store Boundary | Type | Description |
| ---- | -------------- | ---- | ----------- |
| `er_session_store.puml` | Session Store | JSON Lines | Session metadata + messages + file metadata |
| `er_memory_store.puml` | Memory Store | JSON Lines | Cross-session knowledge entries with FTS5 index |
| `er_observability.puml` | Observability | In-memory / stdout | Structured logs, metrics, trace context, redaction rules |
| `er_repo_intelligence.puml` | Repo Intelligence | JSON Lines | AST index, symbol graph, embedding store |
| `er_wire_log.puml` | Wire Log | JSON Lines | Append-only per-session event store with turn index |

**Total: 5 ERD diagrams**

## Notation

PlantUML IE (Information Engineering) — crow's foot notation.
See the [PlantUML IE reference](https://plantuml.com/ie-diagram) for syntax.

| Convention | Meaning |
| ---------- | ------- |
| `*` prefix | Mandatory (NOT NULL / must exist) |
| `<<PK>>` | Primary key |
| `<<FK>>` | Foreign key |
| `<<PK, FK>>` | Composite key that is also a FK |
| Solid line `--` | Identifying relationship (1:M within the same store) |
| Dashed arrow `..>` | Non-identifying / derived / cross-store reference |
| `TEXT (JSON)` | JSON blob stored as TEXT |
| `TEXT (ISO 8601)` | Timestamp as ISO 8601 text |
| `{A\|B\|C}` | Enum constraint in type annotation |

## Relationship Decisions

| Store | Relationship | Cardinality | Notes |
| ----- | ------------ | ----------- | ----- |
| SessionStore | `session` → `message` | 1:M | Messages ordered by sequence number |
| SessionStore | `session` → `session_file` | 1:1 | One JSONL file per session |

## Notes

nasim uses JSON Lines files for session persistence, not a relational database.
This ERD documents the logical schema for reference. Physical storage:

```
~/.nasim/sessions/<session-id>/session.jsonl
```

Each line is a JSON object containing either session metadata or a message entry.
No SQL database, no SQLite, no migrations needed.

## Design Chain Position

```
... → SM → SQ → ERD → CL → Code
```

ERD bridges the logical session model and the physical JSON Lines implementation.

## Related Layers

| Layer | Path |
| ----- | ---- |
| Class diagram (source) | `docs/CL/cl_runtime_model.puml` |
| Lifecycle states | `docs/SM/sm_agent_lifecycle.puml` |
| Session UCs | `docs/UC/uc_session.puml` |
