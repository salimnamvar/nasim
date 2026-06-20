# nasim — ERD Inventory

| Diagram | Store | Description |
|---------|-------|-------------|
| er_session_store | Session Store | Session JSON Lines schema: session metadata + messages |

## Notes

nasim uses JSON Lines files for session persistence, not a relational database.
This ERD documents the logical schema for reference. Physical storage:

```
~/.nasim/sessions/<session-id>/session.jsonl
```

Each line is a JSON object containing either session metadata or a message entry.
No SQL database, no SQLite, no migrations needed.
