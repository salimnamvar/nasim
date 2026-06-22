# nasim — Component Inventory (API-First)

## C4 Diagram Set

| Diagram | Level | Boundary | Description |
|---------|-------|----------|-------------|
| c4_nasim_context.puml | Context | System | nasim as API-First platform: single User actor, 15 external systems |
| c4_nasim_container.puml | Container | System | nasim is one container; CLI, WebApp, DesktopApp, MobileApp are interface containers |
| c4_nasim_component.puml | Component | nasim (container) | Internal structure: API Group (entry gate) + 19 component groups |

## Per-Group Component Diagrams (21 diagrams)

| Diagram | Group | Components |
|---------|-------|------------|
| c4_nasim_component_agent.puml | Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| c4_nasim_component_provider.puml | Provider | Provider (Protocol), LiteLLMProxy |
| c4_nasim_component_tools.puml | Tools | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| c4_nasim_component_mcp.puml | MCP | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| c4_nasim_component_config.puml | Config | ConfigLoader, Config (dataclass) |
| c4_nasim_component_session.puml | Session | SessionStore, SessionVersioning, SessionSearch, SessionFork |
| c4_nasim_component_server.puml | API | ServerApp, ServerRouter, SSEHandler, APISchema — **Entry Gate Component** |
| c4_nasim_component_hooks.puml | Hooks | HookManager |
| c4_nasim_component_plugins.puml | Plugins | PluginLoader |
| c4_nasim_component_safety.puml | Safety | SafetyCoordinator, PermissionGate, InjectionScanner, EgressInspector |
| c4_nasim_component_router.puml | Router | ModelRouter, FallbackChain, ProviderCapabilities |
| c4_nasim_component_sandbox.puml | Sandbox | SandboxExecutor, SandboxPolicy, SandboxMonitor, ResourceLimiter, DiffSandboxManager, EditStagingArea, DiffComputer, DiffPresenter, StagedApplicator |
| c4_nasim_component_observability.puml | Observability | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, InstrumentationMiddleware, OTelExporter |
| c4_nasim_component_memory.puml | Memory | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| c4_nasim_component_git.puml | Git | GitIntegration, GitStatus, GitCommit |
| c4_nasim_component_repo_intelligence.puml | Repo Intelligence | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |
| c4_nasim_component_edit_strategy.puml | Edit Strategy | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |
| c4_nasim_component_evaluation.puml | Evaluation | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, RepetitionDetector, TurnBudgetInjector, QualitySignal |
| c4_nasim_component_wire_log.puml | Wire Log | WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager |
| c4_nasim_component_context_graph.puml | Context Graph | ContextGraph, ContextNode, ContextEdge, ContextProcessor (ABC), PipelineOrchestrator, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, TokenBudgetTracker |

**Total: 24 C4 diagrams (1 context + 1 container + 1 overview + 21 group components)**

## C4 Hierarchy

```
Context:  Person(User) → System(nasim) → System_Ext(...)
Container: Person(User) → Container(CLI, WebApp, DesktopApp, MobileApp) → Container(nasim) → System_Ext(...)
Component: Container_Ext(CLI, WebApp, ...) → Boundary(nasim) → Boundary(API Group) → Component(ServerRouter) → Component(AgentOrchestrator)
```

> **Key distinction:** API (ServerRouter) is a **component** inside the nasim container, not a separate container. Interface containers are separate deployable units that connect to nasim.

## Actors

| Actor | Description |
|-------|-------------|
| User | Single actor. Interacts with nasim via CLI, WebApp, DesktopApp, or MobileApp. All paths route through the API component inside nasim. |

## Interface Containers

| Container | Technology | Connection to nasim |
|-----------|------------|---------------------|
| CLI | Python click + rich | In-process / HTTP to ServerRouter component |
| WebApp | JavaScript SPA | HTTP/JSON + SSE to ServerRouter component |
| DesktopApp | Electron / Tauri | HTTP/JSON + SSE to ServerRouter component |
| MobileApp | React Native / Flutter | HTTP/JSON + SSE to ServerRouter component |

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
| Sandbox Runtime | OS primitives | OS-level process isolation (landlock, seccomp, bubblewrap) |
| Memory Backend | read/write | Long-term knowledge persistence |
| LSP Server | LSP protocol | Language server for code intelligence |
| Plugin Directory | filesystem | ~/.nasim/plugins/ — community extensions |
| Tree-sitter | tree-sitter CLI/lib | AST extraction for code intelligence |
| Embedding Model | HTTP/local | Vector embedding generation for semantic search |
| Vector Store | SQLite + vector | Embedding storage and similarity search |
| OTel Collector | OTLP/gRPC | OpenTelemetry trace and metric export (optional) |

## Architecture Principles (API-First Compliance)

- **API as Component:** The API (ServerRouter) is a component inside the nasim container, not a separate container. Interface containers are separate deployable units that connect to nasim through the API component.
- **CSR Pattern:** Controller (API/ServerRouter) → Service (AgentOrchestrator) → Repository (SessionStore, ToolRegistry, MemoryStore). Strict delegation chain.
- **Single Responsibility per group:** Agent=orchestration, Provider=inference, Router=model selection, Tool=execution, MCP=protocol, Config=configuration, Session=persistence, API=entry gate, Hooks=extensibility, Plugins=discovery, Sandbox=isolation, Safety=permission scanning, Observability=logging, Memory=knowledge, Git=version control, RepoIntelligence=codebase indexing, EditStrategy=edit polymorphism, Evaluation=quality, WireLog=event log, ContextGraph=pipeline
- **No God Objects:** AgentOrchestrator delegates to SafetyCoordinator (Safety group), SubagentCoordinator, PersonaManager, ErrorBoundary
- **MCP first-class:** ClientRuntime, ServerRuntime, ToolAdapter, Discovery as separate components
- **No System_Ext abuse:** Internal containers referenced via Container_Ext only
- **No orphan components:** Every component in detail diagrams appears in the cross-container overview
- **Include pinned:** All diagrams pin C4-PlantUML to v2.10.0
- **Version consistency:** All diagram headers use Version 8.0.0
- **Passive Policies:** CompactionPolicy, StrategyHeuristics are configuration/rule objects. They appear in UC as passive policies but are NOT C4 components (no runtime behavior).
- **Boundary syntax:** Internal logical groupings in component diagrams use `Boundary` (PlantUML generic) rather than `Container_Boundary` to avoid implying deployable container semantics for logical groups.
