# nasim — SQ Inventory (API-First)

Sequence diagrams organised by UC group. 149 diagrams across 22 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## C4 Component Name Fidelity

**CRITICAL RULE:** All lifeline names in SQ diagrams MUST be C4-authoritative component names from `docs/C4/c4_nasim_component.puml`.

| Group | C4 Components (Authoritative) |
|-------|-------------------------------|
| API | HTTPAdapter, AgentController, SessionService, ToolService, ConfigRepository |
| Agent | TaskService, ToolService, SafetyService, ContextService, SessionService, EvaluationService, LLMRepository |
| CLI | CLIAdapter, AgentController, TaskService |
| Session | SessionService, SessionRepository, HistoryRepository |
| Tool | ToolService, FilesystemRepository, SandboxRepository, GitRepository, WebRepository, MCPRepository, RepoIntelligenceRepository, MemoryRepository |
| Provider | LLMRepository |
| Config | ConfigRepository |
| Memory | MemoryRepository |
| Git | GitRepository |
| RepoIntelligence | RepoIntelligenceRepository |
| ContextGraph | ContextService |
| EditStrategy | EditStrategyRepository |
| Evaluation | EvaluationService |
| Router | LLMRepository |
| Safety | SafetyService |
| MCP | MCPRepository |
| Sandbox | SandboxRepository |
| Observability | WireLogRepository |
| Hooks | ToolService |
| Plugins | ToolService |
| WireLog | WireLogRepository |

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
ref over mgr : API-02 CREATE Session
```

## Groups

| Group | Canonical (C4) Name | Boundary | Diagrams |
| ----- | :-----------------: | -------- | :------: |
| AC | AgentController | Agent Controller — single convergence point for all interface containers | 4 |
| AGENT | Agent | Agent Core — orchestrator, history, permissions, plans, subagents | 14 |
| CLI | CLI | CLI Interface Container — REPL, parsing, rendering | 8 |
| CONFIG | Config | Configuration — config loading and validation | 3 |
| CONTEXTGRAPH | ContextGraph | Context Management — token counting and compaction | 6 |
| EDITSTRATEGY | EditStrategy | Edit Strategy — polymorphic edit strategies | 10 |
| EVALUATION | Evaluation | Evaluation — task evaluation and quality checks | 9 |
| HOOKS | Hooks | Hooks — pre/post hooks for tool and LLM lifecycle | 6 |
| MCP | MCP | Model Context Protocol — client/server extension tools | 4 |
| MEMORY | Memory | Memory — cross-session knowledge persistence | 4 |

| PLUGINS | Plugins | Plugins — plugin discovery, loading, registration | 6 |
| PROVIDER | Provider | Provider Layer — provider abstraction, chat, streaming | 4 |
| REPOINTELLIGENCE | RepoIntelligence | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 |
| ROUTER | Router | Model Router — model selection, fallback, routing | 4 |
| SAFETY | Safety | Safety — permission checks and user approval | 3 |
| SANDBOX | Sandbox | Sandbox — OS-level process isolation | 4 |
| API | API | API Group (Entry Gate) — REST API, SSE streaming | 11 |
| SESSION | Session | Session — persistence and resumption | 9 |
| TOOL | Tool | Tool Layer — all tool implementations | 22 |
| GIT | Git | Version Control — Git status, diff, commit | 4 |
| WIRELOG | WireLog | Wire Log — append-only event store, fork, checkpoint | 5 |

**Total: 146 SQ diagrams on disk (147 with common/) — OBS group removed**

## Naming Convention

SQ diagrams use canonical C4 group names for directories and file prefixes:

```
docs/SQ/{CanonicalGroup}/sq_{canonical_group}{nn}_{description}.puml
```

Examples:
- `docs/SQ/Agent/sq_agent01_process_user_task.puml`
- `docs/SQ/API/sq_api03_get_session.puml`
- `docs/SQ/Tool/sq_tool10_dispatch_tool_call.puml`

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version (9.1.0), source, review status, CSR Chain, SM States
2. **Lifelines** — Single `User` actor, participants grouped by CSR layer (colored boxes)
3. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks, ref fragments
4. **State writes** — Via `ref` blocks (NOT self-calls), referencing UC ID from SM/README.md

### Common Styles

All diagrams include `common/sq_styles.puml` for consistent CSR layer colours,
skinparam settings, and visual output across all 149 diagrams (152 expected).

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
