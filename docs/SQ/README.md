# nasim — SQ Inventory (API-First)

> **SQ Architect pass:** 2026-07-01 — Critical task_svc flows rewritten to v10.0.0 with strict CSR layering, SM state guards, RoD method names, and DRY `ref` fragments in `common/sq_ref_*.puml`. Traceability: `docs/UC/README.md` § Sequence Diagram Layer.
>
> **Update 2026-07-01:** Added 19 missing SQ diagrams for ConfigService, MCPAdapter, SessionRepository, HistoryRepository, FilesystemRepository, WebRepository groups. Total now 171 diagrams (165 group + 6 common) across 25 groups.

Sequence diagrams organised by UC group. 165 diagrams across 25 groups (171 total with common/).
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## C4 Component Name Fidelity

**CRITICAL RULE:** All lifeline names in SQ diagrams MUST be C4-authoritative component names from `docs/C4/c4_nasim_component.puml`.

| Group | C4 Components (Authoritative) |
|-------|-------------------------------|
| API | HTTP Adapter, Agent Controller, Session Service, Tool Service, Config Repository |
| Agent | Task Service, Tool Service, Safety Service, Context Service, Session Service, Evaluation Service, LLM Repository |
| CLI | CLI Adapter, Agent Controller, Task Service |
| Session | Session Service, Session Repository, History Repository |
| Tool | Tool Service, Filesystem Repository, Sandbox Repository, Git Repository, Web Repository, MCP Repository, Repo Intelligence Repository, Memory Repository |
| Provider | LLM Repository |
| Config | Config Repository |
| Memory | Memory Repository |
| Git | Git Repository |
| RepoIntelligence | Repo Intelligence Repository |
| ContextGraph | Context Service |
| EditStrategy | Edit Strategy Repository |
| Evaluation | Evaluation Service |
| Router | LLM Repository |
| Safety | Safety Service |
| MCP | MCP Repository |
| Sandbox | Sandbox Repository |
| Observability | Wire Log Repository |
| Hooks | Tool Service |
| Plugins | Tool Service |
| WireLog | Wire Log Repository |

## State Write Convention

Every lifecycle state write MUST use a `ref` block:

```plantuml
ref over alias : UC_ID VERB Resource
  ' State: <back:#HEX>FROM_STATE</back> → <back:#HEX2>TO_STATE</back>
  ' Owned by: UC_ID (SM/README.md)
```

**NEVER** use self-calls for state writes:
```plantuml
' WRONG:
mgr -> mgr : TRANSITION State(<back:#43A047>ACTIVE</back>)
' CORRECT:
ref over mgr : HTTPADAPTER-02 CREATE Session
```

## Groups

| Group | Canonical (C4) Name | Boundary | Diagrams |
| ----- | :-----------------: | -------- | :------: |
| AC | Agent Controller | Agent Controller — single convergence point for all interface containers | 4 |
| AGENT | Agent | Agent Core — orchestrator, history, permissions, plans, subagents | 14 |
| CLI | CLI | CLI Interface Container — REPL, parsing, rendering | 8 |
| CONFIG | Config | Configuration — config loading and validation | 3 |
| CONFIGSERVICE | ConfigService | Config Service — config loading, validation, layered overrides | 3 |
| CONTEXTGRAPH | ContextGraph | Context Management — token counting and compaction | 6 |
| EDITSTRATEGY | EditStrategy | Edit Strategy — polymorphic edit strategies | 10 |
| EVALUATION | Evaluation | Evaluation — task evaluation and quality checks | 9 |
| FILESYSTEMREPO | FilesystemRepository | Filesystem Repository — file I/O, glob, grep | 4 |
| HOOKS | Hooks | Hooks — pre/post hooks for tool and LLM lifecycle | 6 |
| HISTORYREPO | HistoryRepository | History Repository — snapshots, revert, FTS5 search | 3 |
| MCP | MCP | Model Context Protocol — client/server extension tools | 4 |
| MCPADAPTER | MCPAdapter | MCP Adapter — MCP protocol adaptation for external clients | 4 |
| MEMORY | Memory | Memory — cross-session knowledge persistence | 4 |
| PLUGINS | Plugins | Plugins — plugin discovery, loading, registration | 6 |
| PROVIDER | Provider | Provider Layer — provider abstraction, chat, streaming | 4 |
| REPOINTELLIGENCE | RepoIntelligence | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 |
| ROUTER | Router | Model Router — model selection, fallback, routing | 4 |
| SAFETY | Safety | Safety — permission checks and user approval | 3 |
| SANDBOX | Sandbox | Sandbox — OS-level process isolation | 4 |
| API | API | API Group (Entry Gate) — REST API, SSE streaming | 11 |
| SESSION | Session | Session — persistence and resumption | 9 |
| SESSIONREPO | SessionRepository | Session Repository — JSONL message persistence, turn management | 3 |
| TOOL | Tool | Tool Layer — all tool implementations | 22 |
| WEBREPO | WebRepository | Web Repository — web fetch, search | 2 |
| GIT | Git | Version Control — Git status, diff, commit | 4 |
| WIRELOG | WireLog | Wire Log — append-only event store, fork, checkpoint | 5 |

**Total: 165 SQ diagrams on disk (171 with common/) — OBS group removed**

## Naming Convention

SQ diagrams use canonical C4 group names for directories and file prefixes:

```
docs/SQ/{CanonicalGroup}/sq_{canonical_group}{nn}_{description}.puml
```

Examples:
- `docs/SQ/AgentController/sq_agentcontroller01_process_request.puml`
- `docs/SQ/HTTPAdapter/sq_httpadapter06_dispatch_message.puml`
- `docs/SQ/TaskService/sq_taskservice01_process_user_task.puml`
- `docs/SQ/ConfigService/sq_configservice01_load_config.puml`
- `docs/SQ/MCPAdapter/sq_mcpadapter01_process_mcp_request.puml`
- `docs/SQ/SessionRepository/sq_sessionrepository01_append_message.puml`

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version (10.0.0), source, review status, CSR Chain, SM States
2. **Lifelines** — Single `User` actor, participants grouped by CSR layer (colored boxes)
3. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks, ref fragments
4. **State writes** — Via `ref` blocks (NOT self-calls), referencing UC ID from SM/README.md

### Reusable Ref Fragments (DRY)

| File | Purpose | Consumers |
|------|---------|-----------|
| `common/sq_ref_assemble_context.puml` | CONTEXTSVC-01..06 + compaction guard | TASKSVC-01 |
| `common/sq_ref_dispatch_safety_pipeline.puml` | TASKSVC-15 + SAFETYSVC approval alt | TASKSVC-02 |
| `common/sq_ref_persist_conversation.puml` | TASKSVC-03 + repo persistence | TASKSVC-01, TASKSVC-02 |
| `common/sq_ref_handle_error.puml` | TASKSVC-14 ERROR → IDLE | TASKSVC-01 |

### Common Styles

All diagrams include `common/sq_styles.puml` for consistent CSR layer colours,
skinparam settings, and visual output across all 171 diagrams.

### Enforcement

Run `python docs/SQ/common/sq_enforce.py` to check all diagrams against:
- E-SQ-01: C4 Name Fidelity (CRITICAL)
- E-SQ-02: Ref Blocks for State Writes (HIGH)
- E-SQ-03: Activation Pairs (MEDIUM)
- E-SQ-04: CSR Box Colors (HIGH)
- E-SQ-05: Entry Chain (HIGH)
- E-SQ-06: Header Fields (MEDIUM)
- E-SQ-07: No Notes (CRITICAL)
- E-SQ-08: ROD Format (HIGH)

### Template

New SQ diagrams MUST be created from `common/sq_template.puml`.
