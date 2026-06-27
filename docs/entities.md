# nasim — Canonical Entity Registry

Single source of truth for component names, UC group codes, actors, and
external systems across the design chain:
`C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code`.

Names here must appear identically in every layer. No deviation without an AD.

---

## UC Group Codes

| Code | Group | Scope |
|------|-------|-------|
| CLI | CLI Layer | REPL, argument parsing, slash commands, rendering |
| AGT | Agent Core | Orchestrator, conversation, context, permissions, plans, subagents, dispatch |
| LLM | Provider Backend | LLM provider-specific chat and streaming |
| TL | Tool Layer | All tool implementations |
| PRV | Provider Abstraction | Provider lifecycle, factory, backend selection, routing |
| CFG | Configuration | Config loading, validation, layered merge |
| SSN | Session | Session persistence, resumption, listing, versioning, search, fork |
| SAF | Safety | Permission checks, user approval, safety modes, sandbox |
| CTX | Context Management | Token counting, context compaction, graph pipeline |
| SRV | HTTP Server | REST API, SSE streaming, session management via API |
| HK | Hooks | Pre/post hooks for tool use and LLM calls |
| PLG | Plugins | Plugin discovery, loading, registration |
| RTG | Model Router | Model selection, fallback, routing strategies |
| OBS | Observability | Structured logging, metrics, trace correlation |
| MEM | Memory | Cross-session knowledge persistence and retrieval, RAG |
| VCS | Git Integration | Auto-commit, branch awareness, diff tracking |
| SBX | Sandbox | OS-level process isolation for shell execution |
| RIM | Repo Intelligence | AST indexing, symbol graph, PageRank, semantic search, repo-map |
| EDT | Edit Strategy | Strategy polymorphism, diff sandbox, staged edits, revert |
| EVL | Evaluation | Success checks, LLM reviewer, retry coordination, turn budget |
| WRL | Wire Log | Append-only event log, replay, session fork from wire |

---

## Actors

| Actor | Description | C4 Reference |
|-------|-------------|-------------|
| User | Developer using NASIM Application (generic C1/C2 label) | Person in C4 Context and Container |
| Developer | Terminal user interacting with nasim via CLI | Actor alias in SQ diagrams (CLI flows) |
| HTTP Client | External HTTP client (web-app, mobile, desktop) | Person_Ext in C4 Context |
| MCP Client | MCP protocol client connecting to nasim | System_Ext in C4 Context |

**Actor abstraction note:** C4 Context (Level 1) and Container (Level 2) diagrams use
`User` as the single human actor per SE-05 (information hiding — Level 1 shows no
implementation detail). SQ diagrams at Level 3 use `Developer` (CLI flows) or
`HTTP Client` / `MCP Client` as appropriate to the interface. This is a deliberate
layered abstraction, not an inconsistency. See `docs/C4/README.md` — Actor/Entry-Chain
Approach section.

---

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Backend | HTTP/JSON | Multi-provider inference (Ollama, OpenAI, Anthropic) via litellm |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands (via sandbox) |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| MCP Client | stdio/SSE | External tools connecting to nasim MCP server |
| Git Repository | git CLI | Version control for project files |
| Sandbox Runtime | OS primitives | OS-level process isolation: landlock, seccomp |
| Repo Intelligence Backend | various | tree-sitter, LSP, Embedding Model, Vector Store |
| Observability Platform | OTLP, push | Log agent, Prometheus, Grafana, OTel Collector |

---

## C4 Containers

| Container | Technology | Responsibility |
|-----------|-----------|---------------|
| CLI Process | Python 3.10+ | Terminal interface: REPL, arg parsing, rendering. Delegates to Core Engine. |
| HTTP API Server | FastAPI + SSE | REST API with SSE streaming. Entry gate for interface containers. |
| Core Engine | Python 3.10+ | Unified agent engine: agentic loop, tools, safety, context, business logic |

---

## C4 Component Groups (Core Engine)

| Group | UC Code | CSR Layer | Key Components |
|-------|---------|-----------|----------------|
| CLI Group | CLI | Controller | ArgParser, REPLSession, Renderer, SlashCommandHandler |
| Agent Group | AGT | Service | AgentOrchestrator, ConversationHistory, ContextCompactor, SafetyCoordinator, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| Provider Group | PRV + LLM | Service | Provider (Protocol), LiteLLMProxy, ProviderCapabilities, ModelRouter, FallbackChain, ModelCatalog |
| Tool Group | TL | Repository | Tool (ABC), ToolRegistry, ToolResult, ReadFileTool, WriteFileTool, EditFileTool, GrepTool, ShellTool, and others |
| MCP Group | — | Infrastructure | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| Config Group | CFG | cross-cutting | ConfigLoader, Config |
| Session Group | SSN | Repository | SessionStore, Session, SessionVersioning, SessionSearch, SessionFork |
| Server Group | SRV | Controller | ServerApp, ServerRouter, SSEHandler, APISchema |
| Hooks Group | HK | Infrastructure | HookManager, Hook, HookResult |
| Plugins Group | PLG | Infrastructure | PluginLoader, PluginManifest |
| Sandbox Group | SBX | Infrastructure | SandboxExecutor, SandboxPolicy, SandboxMonitor |
| Observability Group | OBS | Infrastructure | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, OTelExporter |
| Memory Group | MEM | Repository | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| Git Group | VCS | Repository | GitIntegration, GitStatus, GitCommit |
| Repo Intelligence Group | RIM | Repository | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |
| Edit Strategy Group | EDT | Service | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |
| Evaluation Group | EVL | Service | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, QualitySignal, RepetitionDetector, TurnBudgetInjector |
| Wire Log Group | WRL | Infrastructure | WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager |
| Context Graph Group | CTX | Service | ContextGraph, ContextNode, ContextEdge, ContextProcessor, ContextPrioritizer, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, PipelineOrchestrator, TokenBudgetTracker |
| Router Group | RTG | Service | (see Provider Group — ModelRouter) |

---

## Verb Extensions

Domain verbs registered per `uc.md` M-4 rule. All UC titles must use only core verbs
(INSERT, READ, UPDATE, DELETE, LIST, SEARCH, VALIDATE, DISPATCH) or these registered
domain verbs. Banned: CREATE, GET, EXECUTE, RUN, INVOKE, PERFORM, TRIGGER, MANAGE.

| Verb | Use | UC Examples |
|------|-----|-------------|
| PROCESS | Orchestrate a multi-step workflow | AGT-01 PROCESS User Task |
| SPAWN | Create a child agent or process | AGT-09 SPAWN Subagent |
| COLLECT | Gather results from a child process | AGT-10 COLLECT Subagent Result |
| COMPACT | Summarize or compress context | AGT-06 COMPACT Context |
| COORDINATE | Manage retry, escalation, or scheduling | EVL-06 COORDINATE Retry |
| INJECT | Insert data into a pipeline or context | RIM-04 INJECT Repo Map |
| SCORE | Rank or prioritize by criteria | EVL-03 SCORE Task |
| DISTILL | Summarize or compress | CTX-04 DISTILL Context |
| REDACT | Strip sensitive data | OBS-05 REDACT Logs |
| EMIT | Write to a log or metric stream | OBS-01 EMIT Trace, OBS-02 EMIT Metric |
| EXPOSE | Make capabilities available externally | PLG-06 EXPOSE Plugin |
| DISCOVER | Find or enumerate available resources | MCP-01 DISCOVER MCP Server, PLG-01 DISCOVER Plugins |
| ADAPT | Transform between formats | EDT-10 ADAPT Strategy |
| QUEUE | Hold items for batch processing | AGT-07 QUEUE Plan |
| APPROVE | Authorize a queued or pending action | AGT-08 APPROVE Plan, SAF-02 REQUEST Approval |
| DELEGATE | Hand off to a specialized handler | AGT-11 DELEGATE Subagent |
| LOAD | Retrieve and initialize a resource | AGT-12 LOAD Persona, CFG-01 LOAD Config, PLG-02 LOAD Plugin |
| HANDLE | Process an exceptional condition | AGT-14 HANDLE Error |
| REGISTER | Attach a provider, hook, or plugin | PRV-01 REGISTER Provider, HK-01 REGISTER Hook, PLG-03 REGISTER Plugin, PLG-04 UNREGISTER Plugin |
| SELECT | Choose among alternatives | PRV-04 SELECT Provider, RTG-01 SELECT Model, EDT-01 SELECT Strategy |
| APPLY | Execute a chosen strategy or configuration | EDT-02..09 APPLY Strategy, CFG-03 APPLY Config, SAF-03 APPLY Safety, RTG-02 APPLY Routing, SBX-02 APPLY Sandbox |
| PERSIST | Store a snapshot or checkpoint | SSN-01 PERSIST Session, MEM-01 PERSIST Memory, TL-19 PERSIST Todo |
| FORK | Create a divergent copy | WRL-04 FORK Session |
| CHECKPOINT | Save intermediate state | WRL-05 CHECKPOINT Session |
| EVALUATE | Assess task quality or success | EVL-01 EVALUATE Task |
| DETECT | Identify patterns or anomalies | EVL-08 DETECT Repetition |
| CORRELATE | Link traces, logs, or events | OBS-03 CORRELATE Traces |
| EXPORT | Send data to external systems | OBS-06 EXPORT Telemetry |
| STREAM | Continuous data flow | CLI-03 STREAM Output, PRV-03 STREAM Chat, OBS-01 STREAM Events |
| ENABLE | Activate a feature or plugin | CLI-05 ENABLE Feature, PLG-05 ENABLE Plugin |
| REQUEST | Ask for external action or approval | CLI-06 REQUEST Approval, PRV-02 REQUEST Chat, SAF-02 REQUEST Approval |
| SWITCH | Change active state or provider | CLI-07 SWITCH Persona, AGT-13 SWITCH Persona, RTG-04 SWITCH Model |

---

## Provider Resolution (AD from DGA-02)

**Decision:** `LiteLLMProxy` is the sole `Provider` implementation. No per-provider classes.
Model routing is via litellm model string prefix only (e.g., `anthropic/claude-sonnet-4-6`,
`openai/gpt-4o`, `ollama/qwen2.5-coder:7b`).

---

## Source

Authoritative rule-layer version: `.nasim/rules/ENTITIES.md`
This file is the design-chain-facing public view for all `docs/` artifacts.
