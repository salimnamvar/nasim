# 02 — Milestone 0: Bootstrap

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [01-project-skeleton.md](01-project-skeleton.md)

Set up project structure, config loading, and session persistence. Foundation for all subsequent milestones.

---

## Scope

- Project skeleton (pyproject.toml, src layout, tests/)
- Config schema and layered loading (global YAML → project YAML → env → CLI)
- Session model and JSON Lines persistence
- Domain exceptions base class
- First test suite (config + session)

## Deliverables

| # | Deliverable | UC Trace | SQ Trace |
| - | --- | --- | --- |
| 1 | `pyproject.toml` with all deps + tool config | — | — |
| 2 | `Config` dataclass + `ConfigRepository` | CONFIGREPOSITORY-01, CONFIGREPOSITORY-02, CONFIGREPOSITORY-03 | sq_cfg01, sq_cfg02, sq_cfg03 |
| 3 | `Session` dataclass + `SessionRepository` | SESSIONSERVICE-01, SESSIONSERVICE-02, SESSIONSERVICE-03, SESSIONSERVICE-04 | sq_ssn01, sq_ssn02, sq_ssn03, sq_ssn04 |
| 4 | `DomainException` base + specific exceptions | — | — |
| 5 | Test suite: config loading, session CRUD | CONFIGREPOSITORY-01..03, SESSIONSERVICE-01..04 | sq_cfg01..03, sq_ssn01..04 |

## Acceptance Criteria

- `mypy --strict` passes
- `ruff check` passes
- `black --check` passes
- All config tests pass (layered loading, env override, validation)
- All session tests pass (save, load, list, resume, atomic writes)
- No agentcli imports in config or session code
