# nasim — SQ Inventory (API-First)

Sequence diagrams organised by UC group. 148 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## API-First Convention

All SQ diagrams follow the API-First delegation chain:

```
User → [Interface Container] → API (ServerRouter) → Core Component → Repository
```

- **Single actor:** `User` routes through `ServerRouter` (API Group)
- **No bypass:** No interface may call core services directly
- **CSR pattern:** Controller → Service → Repository
- **ROD AIP-193:** All failure paths use `{error: {code, message, status}}`

## C4 Component Name Fidelity

**CRITICAL RULE:** All lifeline names in SQ diagrams MUST be C4-authoritative component names from `ENTITIES.md`. No invented managers, orchestrators, stores, or directories.

| Group | C4 Components (Authoritative) |
|-------|-------------------------------|
| API | ServerApp, ServerRouter, SSEHandler, APISchema |
| Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, SafetyCoordinator, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| CLI | ArgParser, REPLSession, Renderer, SlashCommandHandler |
| Session | SessionStore, SessionVersioning, SessionSearch, SessionFork |
| Tool | Tool (ABC), ToolRegistry, ReadFileTool, WriteFileTool, EditFileTool, GrepTool, GlobTool, FindFileTool, ShellTool, DirTool, WebFetchTool, WebSearchTool, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| Provider | Provider, LiteLLMProxy, ModelRouter, FallbackChain, ModelCatalog |
| Config | ConfigLoader, Config |
| Memory | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| Git | GitIntegration, GitStatus, GitCommit |
| RepoIntelligence | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |
| ContextGraph | ContextGraph, ContextNode, ContextEdge, ContextProcessor, ContextPrioritizer, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, PipelineOrchestrator, TokenBudgetTracker |
| EditStrategy | EditStrategyManager, EditStrategy, SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |
| Evaluation | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, QualitySignal, RepetitionDetector, TurnBudgetInjector |
| Router | ModelRouter, FallbackChain |
| Safety | SafetyCoordinator |
| MCP | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| Sandbox | SandboxExecutor, SandboxPolicy, SandboxMonitor |
| Observability | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, OTelExporter |
| Hooks | HookManager, Hook, HookResult |
| Plugins | PluginLoader, PluginManifest |
| WireLog | WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager |

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
| AGT | Agent | Agent Core — orchestrator, history, permissions, plans, subagents | 14 |
| CLI | CLI | CLI Interface Container — REPL, parsing, rendering | 8 |
| CFG | Config | Configuration — config loading and validation | 3 |
| CTX | ContextGraph | Context Management — token counting and compaction | 6 |
| EDT | EditStrategy | Edit Strategy — polymorphic edit strategies | 10 |
| EVL | Evaluation | Evaluation — task evaluation and quality checks | 9 |
| HK | Hooks | Hooks — pre/post hooks for tool and LLM lifecycle | 6 |
| MCP | MCP | Model Context Protocol — client/server extension tools | 4 |
| MEM | Memory | Memory — cross-session knowledge persistence | 4 |
| OBS | Observability | Observability — structured logging, metrics, trace correlation | 6 |
| PLG | Plugins | Plugins — plugin discovery, loading, registration | 6 |
| PRV | Provider | Provider Layer — provider abstraction, chat, streaming | 4 |
| RIM | RepoIntelligence | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 |
| RTG | Router | Model Router — model selection, fallback, routing | 4 |
| SAF | Safety | Safety — permission checks and user approval | 3 |
| SBX | Sandbox | Sandbox — OS-level process isolation | 4 |
| SRV | API | API Group (Entry Gate) — REST API, SSE streaming | 11 |
| SSN | Session | Session — persistence and resumption | 9 |
| TL | Tool | Tool Layer — all tool implementations | 22 |
| VCS | Git | Version Control — Git status, diff, commit | 4 |
| WRL | WireLog | Wire Log — append-only event store, fork, checkpoint | 5 |

**Total: 148 SQ diagrams across 21 groups**

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
skinparam settings, and visual output across all 148 diagrams.

### Enforcement

Run `python docs/SQ/common/sq_enforce.py` to check all 148 diagrams against:
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
