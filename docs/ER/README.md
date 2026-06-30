# nasim — ERD Inventory

Physical store schema diagrams for all persistent stores.

Back to [docs/](../README.md).

## Diagrams

| File | Store Boundary | C4 Store | Type | Description |
| ---- | -------------- | -------- | ---- | ----------- |
| `er_session_store.puml` | Session Store | Session Store | JSON Lines | Session metadata + messages + file metadata |
| `er_memory_store.puml` | Memory Store | Memory Store | JSON Lines | Cross-session knowledge entries with FTS5 index |
| `er_wire_log.puml` | Wire Log | Wire Log Store | JSON Lines | Append-only per-session event store with turn index |
| `er_config_store.puml` | Config Store | Config Store | YAML | Layered configuration schema |
| `er_repo_intelligence.puml` | Repo Intelligence | — (external) | JSON Lines | AST index, symbol graph, embedding store |

**Total: 5 ERD diagrams (4 C4 data stores, 1 informational)**

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
| ConfigStore | `config_layer` → `config_entry` | 1:M | Layered merge: global ← project ← env ← cli |

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
C4 → UC → SM → SQ → CL → ER → CT/DATA → CT/API → RDM
```

ERD documents the physical schema for each C4 data store. All stores are managed by their owning C4 repository component.

## Related Layers

| Layer | Path | Relationship |
| ----- | ---- | ------------ |
| C4 Components (source) | `docs/C4/c4_nasim_component.puml` | Defines data stores and owning components |
| CL Classes | `docs/CL/cl_runtime_model.puml` | Maps runtime classes to data stores |
| CT/DATA Contracts | `docs/CT/DATA/` | Validate ERD field definitions |
