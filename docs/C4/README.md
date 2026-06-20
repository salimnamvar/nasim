# nasim — Component Inventory

## C4 Diagram Set

| Diagram | Level | Boundary | Description |
|---------|-------|----------|-------------|
| c4_nasim_context.puml | Context | System | nasim with all external actors and systems (12 external) |
| c4_nasim_container.puml | Container | System | Deployable units: CLI, HTTP Server, Core Library (3 containers) |
| c4_nasim_component.puml | Component | Cross-container | Core Library component overview: all 18 groups and interactions |

## Per-Group Component Diagrams

| Diagram | Group | Components |
|---------|-------|------------|
| c4_nasim_component_agent.puml | Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, SafetyCoordinator, PlanSession, AgentEvent, SubagentCoordinator, ErrorBoundary, PersonaManager, CompactionPolicy |
| c4_nasim_component_provider.puml | Provider | Provider (Protocol), LiteLLMProxy, ModelRouter, FallbackChain, ProviderCapabilities |
| c4_nasim_component_tools.puml | Tools | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| c4_nasim_component_mcp.puml | MCP | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| c4_nasim_component_config.puml | Config | ConfigLoader, Config |
| c4_nasim_component_session.puml | Session | SessionStore, Session, SessionVersioning, SessionSearch, SessionFork |
| c4_nasim_component_server.puml | Server | ServerApp, ServerRouter, SSEHandler, APISchema |
| c4_nasim_component_hooks.puml | Hooks | HookManager, Hook, HookResult |
| c4_nasim_component_plugins.puml | Plugins | PluginLoader, PluginManifest |
| c4_nasim_component_sandbox.puml | Sandbox | SandboxExecutor, SandboxPolicy, SandboxMonitor, ResourceLimiter, DiffSandboxManager, EditStagingArea, DiffComputer, DiffPresenter, StagedApplicator |
| c4_nasim_component_observability.puml | Observability | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, InstrumentationMiddleware, OTelExporter |
| c4_nasim_component_memory.puml | Memory | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| c4_nasim_component_git.puml | Git | GitIntegration, GitStatus, GitCommit |
| c4_nasim_component_repo_intelligence.puml | Repo Intelligence | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |
| c4_nasim_component_edit_strategy.puml | Edit Strategy | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector, StrategyHeuristics |
| c4_nasim_component_evaluation.puml | Evaluation | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, QualitySignal, RepetitionDetector, TurnBudgetInjector |
| c4_nasim_component_wire_log.puml | Wire Log | WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager |
| c4_nasim_component_context_graph.puml | Context Graph | ContextGraph, ContextNode, ContextEdge, PipelineOrchestrator, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, TokenBudgetTracker |
| c4_nasim_component_subagent.puml | Subagent | SubagentCoordinator, AgentOrchestrator (child) |

## Actors

| Actor | Description |
|-------|-------------|
| Developer | Terminal user interacting with nasim |
| HTTP Client | External HTTP client (web-app, mobile, desktop) |

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

## Architecture Principles (p1.md Compliance)

- **3 deployable units only:** CLI process, HTTP Server process, Core Library
- **Single Responsibility per group:** Agent=orchestration, Provider=inference, Tool=execution, MCP=protocol, Config=configuration, Session=persistence, Server=HTTP API, Hooks=extensibility, Plugins=discovery, Sandbox=isolation, Observability=logging, Memory=knowledge, Git=version control, RepoIntelligence=codebase indexing, EditStrategy=edit polymorphism, Evaluation=quality, WireLog=event log, ContextGraph=pipeline
- **No God Objects:** AgentOrchestrator delegates to SafetyCoordinator, SubagentCoordinator, PersonaManager, ErrorBoundary
- **MCP first-class:** ClientRuntime, ServerRuntime, ToolAdapter, Discovery as separate components
- **No System_Ext abuse:** Internal containers referenced via Container_Ext only
- **No orphan components:** Every component in detail diagrams appears in the cross-container overview
- **Include pinned:** All diagrams pin C4-PlantUML to v2.10.0
- **Version consistency:** All diagram headers use Version 6.0.0
