# nasim — C4 Diagram Inventory

## C4 Diagram Set

| Diagram | Level | Boundary | Description |
|---------|-------|----------|-------------|
| c4_nasim_context.puml | Context | System | nasim as a single system: User actor + external systems |
| c4_nasim_container.puml | Container | System | nasim is one Container inside `System_Boundary(nasim_sys)`; external interface apps are `Container_Ext` |
| c4_nasim_component.puml | Component | nasim (container) | Overview: all groups inside `Container_Boundary(nasim)` |

## Per-Group Component Diagrams (21 diagrams)

Each per-group diagram wraps its components with `Container_Boundary(nasim, "nasim") { Boundary(xxx_group, "XXX Group") { ... } }`.
Cross-group references use `Component_Ext(alias, "ComponentName", "Group Name")`.
Genuinely external resources use `System_Ext(...)`.
External interface apps (separate deployable units) use `Container_Ext(...)`.

| Diagram | Group | Key Components |
|---------|-------|----------------|
| c4_nasim_component_agent.puml | Agent Group | AgentOrchestrator, ConversationHistory, ContextCompactor, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| c4_nasim_component_provider.puml | Provider Group | Provider (Protocol), LiteLLMProxy |
| c4_nasim_component_tools.puml | Tool Group | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| c4_nasim_component_mcp.puml | MCP Group | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| c4_nasim_component_config.puml | Config Group | ConfigLoader, Config (dataclass) |
| c4_nasim_component_session.puml | Session Group | SessionStore, SessionVersioning, SessionSearch, SessionFork |
| c4_nasim_component_server.puml | API Group | ServerApp, ServerRouter, SSEHandler, APISchema |
| c4_nasim_component_hooks.puml | Hooks Group | HookManager |
| c4_nasim_component_plugins.puml | Plugins Group | PluginLoader |
| c4_nasim_component_safety.puml | Safety Group | SafetyCoordinator, PermissionGate, InjectionScanner, EgressInspector |
| c4_nasim_component_router.puml | Router Group | ModelRouter, FallbackChain, ProviderCapabilities |
| c4_nasim_component_sandbox.puml | Sandbox Group | SandboxExecutor, SandboxPolicy, SandboxMonitor, ResourceLimiter, DiffSandboxManager, EditStagingArea, DiffComputer, DiffPresenter, StagedApplicator |
| c4_nasim_component_observability.puml | Observability Group | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, InstrumentationMiddleware, OTelExporter |
| c4_nasim_component_memory.puml | Memory Group | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| c4_nasim_component_git.puml | Git Group | GitIntegration, GitStatus, GitCommit |
| c4_nasim_component_repo_intelligence.puml | Repo Intelligence Group | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |
| c4_nasim_component_edit_strategy.puml | Edit Strategy Group | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |
| c4_nasim_component_evaluation.puml | Evaluation Group | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, RepetitionDetector, TurnBudgetInjector, QualitySignal |
| c4_nasim_component_wire_log.puml | Wire Log Group | WireLog, WireAppender, WireReader, SessionForkManager |
| c4_nasim_component_context_graph.puml | Context Graph Group | ContextGraph, PipelineOrchestrator, ContextPrioritizer, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, TokenBudgetTracker |
| c4_nasim_component_cli.puml | CLI Group | ArgParser, REPLSession, Renderer, SlashCommandHandler |

**Total: 24 C4 diagrams (1 context + 1 container + 1 overview + 21 group components)**

## C4 Hierarchy

```
Context:   Person(User) → System(nasim) → System_Ext(...)
Container: System_Boundary(nasim_sys) { Container(nasim) }
           Container_Ext(WebApp, DesktopApp, MobileApp) → Container(nasim)
Component: Container_Boundary(nasim) {
               Boundary(api_group) { Component(ServerRouter) ... }
               Boundary(agent_group) { Component(AgentOrchestrator) ... }
               Boundary(cli_group) { Component(REPLSession) ... }
               ...
           }
           Container_Ext(WebApp, DesktopApp, MobileApp) → ServerRouter
           Person(User) → REPLSession (CLI mode)
```

**Key distinction:** nasim is a **single Python process**. CLI Group (ArgParser, REPLSession, Renderer) and API Group (ServerRouter) are `Boundary` groups inside the same `Container_Boundary(nasim)`. CLI and API are not separate containers — they are logical boundaries within one deployable unit.

## Actors

| Actor | Description |
|-------|-------------|
| User | Human developer. Interacts via CLI (REPLSession) or via interface container apps (WebApp, DesktopApp, MobileApp → ServerRouter). |

## Interface Containers (external, separate deployable units)

| Container | Type | Connection to nasim |
|-----------|------|---------------------|
| WebApp | JavaScript SPA | HTTP/JSON + SSE to ServerRouter |
| DesktopApp | Electron / Tauri | HTTP/JSON + SSE to ServerRouter |
| MobileApp | React Native / Flutter | HTTP/JSON + SSE to ServerRouter |

CLI mode is NOT a separate container — it is the CLI Group boundary inside nasim.

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Backend | HTTP/JSON | Multi-provider inference (Ollama, OpenAI, Anthropic, etc.) via litellm |
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

## Architecture Principles

- **Single process:** nasim is one Python process; CLI and HTTP server modes share the same Container_Boundary.
- **CSR Pattern:** Controller (CLI Group / API Group) → Service (Agent Group, Router Group, etc.) → Repository (Session Group, Tool Group, Memory Group, Config Group). Strict delegation.
- **One group, one Boundary:** Each component group is a `Boundary` inside `Container_Boundary(nasim)`. Groups are logical, not deployable.
- **No Container_Ext for internals:** Cross-group references inside nasim use `Component_Ext(alias, "ComponentName", "Group Name")`, never `Container_Ext` or `System_Ext`.
- **System_Ext for real externals only:** Filesystems, web, git repos, LLM backends, MCP servers, LSP servers — genuinely external infrastructure.
- **Container_Ext for real external containers:** WebApp, DesktopApp, MobileApp — separate deployable units with their own processes.
- **Version consistency:** All diagram headers use Version 9.0.0.
- **Pin C4-PlantUML:** All diagrams reference v2.10.0 — never `master`.
