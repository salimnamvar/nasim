# nasim — Canonical Entity Registry

All component names, UC group codes, actors, and external systems registered here
must appear identically across C4 → UC → SM → SQ → ERD → CL → Code layers.

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
| Developer | Terminal user interacting with nasim | Person in C4 Context |
| HTTP Client | External HTTP client (web-app, mobile, desktop) | Person_Ext in C4 Context |
| MCP Client | MCP protocol client connecting to nasim | System_Ext in C4 Context |

---

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Backend | HTTP/JSON | Multi-provider inference (Ollama, OpenAI, Anthropic) |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands (via sandbox) |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| MCP Client | stdio/SSE | External tools connecting to nasim MCP server |
| Global Config | YAML | ~/.nasim/config.yaml |
| Project Config | YAML | .nasim/config.yaml |
| Env Variables | env | NASIM_* environment variables |
| Session Directory | JSON Lines | ~/.nasim/sessions/<id>/ |
| Plugin Directory | filesystem | ~/.nasim/plugins/ — community extensions |
| Git Repository | git CLI | Version control for project files |
| Sandbox Runtime | OS primitives | OS-level process isolation: landlock, seccomp |
| Memory Backend | read/write | Long-term knowledge persistence |
| LSP Server | LSP protocol | Language server for code intelligence |
| Tree-sitter | tree-sitter CLI/lib | AST extraction for code intelligence |
| Embedding Model | HTTP/local | Vector embedding generation for semantic search |
| Vector Store | SQLite + vector | Embedding storage and similarity search |
| OTel Collector | OTLP/gRPC | OpenTelemetry trace and metric export |

---

## C4 Components

### CLI Group

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ArgParser | `nasim/cli/args.py` | CLI argument parsing with layered overrides |
| REPLSession | `nasim/cli/repl.py` | Interactive REPL loop, input handling |
| Renderer | `nasim/cli/renderer.py` | All terminal output: colors, diffs, streaming, tool display |
| SlashCommandHandler | `nasim/cli/commands.py` | Maps `/cmd` strings to actions |

### Agent Group

| Component | Module | Responsibility |
|-----------|--------|---------------|
| AgentOrchestrator | `nasim/agent/orchestrator.py` | Core agentic loop: Provider call, tool dispatch, repeat. Yields AgentEvent objects |
| ConversationHistory | `nasim/agent/history.py` | Owns messages + token count + compaction trigger |
| ContextCompactor | `nasim/agent/compactor.py` | Summarizes old exchanges via secondary LLM call |
| SafetyCoordinator | `nasim/agent/safety.py` | Composes PermissionGate, injection scanner, egress inspector into pipeline |
| PlanSession | `nasim/agent/plan.py` | Holds queued tool calls in plan mode |
| AgentEvent | `nasim/agent/events.py` | Event types: TextChunk, ToolStart, ToolResult, Error, Done |
| SubagentCoordinator | `nasim/agent/subagent.py` | Parent-child orchestration, nesting limit 5, result aggregation |
| ErrorBoundary | `nasim/agent/errors.py` | Structured error handling with recovery actions |
| PersonaManager | `nasim/agent/persona.py` | Runtime persona switching for specialized agent roles |

### Provider Group

| Component | Module | Responsibility |
|-----------|--------|---------------|
| Provider | `nasim/provider/base.py` | Unified Protocol: chat(), chat_stream(), model_name. All providers route through litellm |
| LiteLLMProxy | `nasim/provider/litellm.py` | Universal LLM proxy: 100+ providers via model string prefix |
| ModelRouter | `nasim/provider/router.py` | Model selection: task classification, provider preference, context window matching |
| FallbackChain | `nasim/provider/fallback.py` | Ordered provider failover chain with retry and exponential backoff |
| ProviderCapabilities | `nasim/provider/caps.py` | Capability declaration: streaming, tools, vision, reasoning, context window per model |
| ModelCatalog | `nasim/provider/catalog.py` | Model metadata: context limits, pricing, capabilities from litellm database |

### Tool Group

| Component | Module | Responsibility |
|-----------|--------|---------------|
| Tool | `nasim/tools/base.py` | ABC: name, description, parameters, safe, execute() |
| ToolRegistry | `nasim/tools/base.py` | Instance-based registry; dynamic registration |
| ToolResult | `nasim/tools/base.py` | Structured result: success, content, error |
| ReadFileTool | `nasim/tools/file.py` | Read file contents with offset/limit |
| WriteFileTool | `nasim/tools/file.py` | Create or overwrite files |
| EditFileTool | `nasim/tools/file.py` | Replace exact strings in files |
| GrepTool | `nasim/tools/search.py` | Search file contents by regex pattern |
| GlobTool | `nasim/tools/search.py` | Find files by glob pattern |
| FindFileTool | `nasim/tools/search.py` | Find files by name pattern with depth |
| ShellTool | `nasim/tools/shell.py` | Execute shell commands with timeout |
| DirTool | `nasim/tools/directory.py` | List directory contents |
| WebFetchTool | `nasim/tools/web.py` | Fetch URL content as markdown |
| WebSearchTool | `nasim/tools/web.py` | Search the web for information |
| GitTool | `nasim/tools/git.py` | Git status, diff, commit operations |
| LspTool | `nasim/tools/lsp.py` | LSP operations: hover, definition, references, symbols |
| SubagentTool | `nasim/tools/subagent.py` | Spawns child agents via SubagentCoordinator |
| TodoTool | `nasim/tools/todo.py` | Task tracking within session |
| MemoryTool | `nasim/tools/memory.py` | Persist and retrieve cross-session knowledge |
| PlanTool | `nasim/tools/plan.py` | Plan creation and management |
| RepoMapTool | `nasim/tools/repo_map.py` | Inject token-budgeted repo-map into context |
| SemanticSearchTool | `nasim/tools/semantic_search.py` | Embedding-based semantic code search |
| ReviewTool | `nasim/tools/review.py` | Trigger LLM-as-judge evaluation of completed task |

### MCP Group

| Component | Module | Responsibility |
|-----------|--------|---------------|
| MCPClientRuntime | `nasim/mcp/client.py` | Connects to external MCP servers via stdio/SSE transport |
| MCPServerRuntime | `nasim/mcp/server.py` | Exposes nasim tools to external MCP clients via stdio/SSE |
| MCPToolAdapter | `nasim/mcp/adapter.py` | Wraps MCP server tools into nasim Tool ABC format |
| MCPDiscovery | `nasim/mcp/discovery.py` | Discovers and registers MCP server tools at startup from config |

### Config Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ConfigLoader | `nasim/config/loader.py` | Loads global YAML + project YAML + env + CLI flags |
| Config | `nasim/config/schema.py` | Typed dataclass: provider, model, safety, budget, mcp |

### Session Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| SessionStore | `nasim/session/store.py` | Persists/loads message history to ~/.nasim/sessions/ |
| Session | `nasim/session/model.py` | Session dataclass: id, created_at, messages |
| SessionVersioning | `nasim/session/versioning.py` | Snapshots and undo for session state |
| SessionSearch | `nasim/session/search.py` | Cross-session search via FTS5 index |
| SessionFork | `nasim/session/fork.py` | Branch conversations from any point |

### Server Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ServerApp | `nasim/server/app.py` | ASGI application factory, middleware, routing |
| ServerRouter | `nasim/server/routes.py` | RESTful route handlers: sessions, messages, tools, config |
| SSEHandler | `nasim/server/sse.py` | Server-Sent Events streaming for agent responses |
| APISchema | `nasim/server/schema.py` | OpenAPI 3.1 schema, request/response models |

### Hooks Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| HookManager | `nasim/hooks/manager.py` | Registers, discovers, and executes hooks |
| Hook | `nasim/hooks/types.py` | Hook types: PreToolUse, PostToolUse, PreLLMCall, PostLLMCall |
| HookResult | `nasim/hooks/types.py` | Hook execution result: allow, deny, modify |

### Plugins Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| PluginLoader | `nasim/plugins/loader.py` | Discovers and loads plugins from ~/.nasim/plugins/ |
| PluginManifest | `nasim/plugins/manifest.py` | Plugin metadata: name, version, tools, hooks |

### Sandbox Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| SandboxExecutor | `nasim/sandbox/executor.py` | OS-level process isolation: landlock, seccomp, bubblewrap |
| SandboxPolicy | `nasim/sandbox/policy.py` | Network domain allowlists, filesystem mount rules, exec restrictions |
| SandboxMonitor | `nasim/sandbox/monitor.py` | Process monitoring, timeout enforcement, resource limits |

### Observability Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| StructuredLogger | `nasim/observability/logger.py` | Structured JSON logging to stdout with trace correlation, log levels. Emit-only (tenas pattern). |
| MetricsCollector | `nasim/observability/metrics.py` | Token usage, latency histograms, tool call counters, error rates. Exposes /metrics pull endpoint. |
| TraceCorrelator | `nasim/observability/trace.py` | Generates root trace/span per CLI turn or HTTP request. Binds trace_id, span_id to contextvars. |
| ContextPropagator | `nasim/observability/propagator.py` | Propagates trace context across: Provider calls, tool dispatch, hook execution, subagent spawn, MCP calls. |
| LogRedactor | `nasim/observability/redactor.py` | Regex-based secret stripping before any emission. Always on. Configurable rules (global + per-project). |
| DualOutputAdapter | `nasim/observability/adapter.py` | CLI entry adapter: JSON to stdout (machine) + rich Renderer when isatty (human). HTTP/MCP bypass. |
| OTelExporter | `nasim/observability/otel.py` | Optional (feature flag). Bridges TraceCorrelator spans to OTel SDK. Exports via OTLP/gRPC or stdout. |

### Memory Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| MemoryStore | `nasim/memory/store.py` | Cross-session knowledge persistence and retrieval |
| MemoryIndex | `nasim/memory/index.py` | FTS5 index for semantic search across stored knowledge |
| MemoryScope | `nasim/memory/scope.py` | Scope isolation: global, project, session-level knowledge |
| EpisodicMemoryAdapter | `nasim/memory/episodic.py` | Session summaries + embeddings for episodic retrieval |
| SemanticMemoryAdapter | `nasim/memory/semantic.py` | Facts + embeddings + metadata for semantic retrieval |
| WorkingMemoryAdapter | `nasim/memory/working.py` | In-session scratch pad, no persistence |
| MemoryRetriever | `nasim/memory/retriever.py` | Hybrid retrieval: BM25 + embedding + RRF fusion |
| MemoryIndexer | `nasim/memory/indexer.py` | Indexes new facts after each session |

### Git Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| GitIntegration | `nasim/git/integration.py` | Auto-commit after file edits, branch awareness, diff tracking |
| GitStatus | `nasim/git/status.py` | Read working tree status, staged changes, branch info |
| GitCommit | `nasim/git/commit.py` | Create commits with conventional commit messages |

### Repo Intelligence Group (E-01)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| RepoIntelligenceManager | `nasim/repo_intelligence/manager.py` | Owns all code intelligence: AST, graph, ranking, semantic search, repo-map |
| ASTIndexAdapter | `nasim/repo_intelligence/ast_index.py` | tree-sitter extraction per language, per-file tag store |
| SymbolGraph | `nasim/repo_intelligence/symbol_graph.py` | Directed graph of symbols and references (NetworkX-like) |
| RankingService | `nasim/repo_intelligence/ranking.py` | PageRank with chat-personalization vectors for repo-map |
| EmbeddingAdapter | `nasim/repo_intelligence/embedding.py` | Embedding model adapter (local or API) for code vectors |
| SemanticSearchService | `nasim/repo_intelligence/semantic_search.py` | Cosine similarity search over code embeddings |
| RepoMapBuilder | `nasim/repo_intelligence/repo_map.py` | Token-budgeted repo-map injection into context |

### Edit Strategy Group (E-02)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| EditStrategyManager | `nasim/edit_strategy/manager.py` | Selects best edit strategy per model capability |
| EditStrategy | `nasim/edit_strategy/base.py` | ABC: apply(original, instructions) → result |
| SearchReplaceCoder | `nasim/edit_strategy/search_replace.py` | SEARCH/REPLACE block format |
| WholeFileCoder | `nasim/edit_strategy/whole_file.py` | Rewrite entire file |
| UnifiedDiffCoder | `nasim/edit_strategy/unified_diff.py` | Unified diff format |
| FencedBlockCoder | `nasim/edit_strategy/fenced_block.py` | Fenced code block format |
| FunctionLevelCoder | `nasim/edit_strategy/function_level.py` | AST-targeted function replacement |
| DiffSandboxCoder | `nasim/edit_strategy/diff_sandbox.py` | Stage edits, show diff, apply on approval |
| ArchitectCoder | `nasim/edit_strategy/architect.py` | Plan-then-implement two-phase edit |
| InlinePatchCoder | `nasim/edit_strategy/inline_patch.py` | apply-patch format |
| StrategySelector | `nasim/edit_strategy/selector.py` | Uses ProviderCapabilities to pick optimal strategy |

### Evaluation Group (E-03)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| EvaluationEngine | `nasim/evaluation/engine.py` | Orchestrates post-task quality evaluation |
| TaskEvaluator | `nasim/evaluation/evaluator.py` | Evaluates whether task is complete |
| SuccessCheckRunner | `nasim/evaluation/success_check.py` | Shell exit code checks (sparse reward signal) |
| LLMReviewer | `nasim/evaluation/llm_reviewer.py` | LLM-as-judge scoring (dense process reward) |
| TestRunner | `nasim/evaluation/test_runner.py` | Run test suite, check pass/fail |
| RetryCoordinator | `nasim/evaluation/retry.py` | max_retries, retry_strategy, on_failure rollback |
| QualitySignal | `nasim/evaluation/quality.py` | accept: bool \| float, feedback: str |
| RepetitionDetector | `nasim/evaluation/repetition.py` | Detect tool-call loops, prevent policy divergence |
| TurnBudgetInjector | `nasim/evaluation/turn_budget.py` | Inject turn budget per-turn (exploration constraint) |

### Wire Log Group (E-04)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| WireLog | `nasim/wire_log/log.py` | Append-only per-session event stream (JSONL) |
| WireAppender | `nasim/wire_log/appender.py` | Write-only interface (enforces append-only semantics) |
| WireReader | `nasim/wire_log/reader.py` | Read-only with random seek via TurnIndex |
| TurnIndex | `nasim/wire_log/turn_index.py` | Maps turn_number → byte_offset for O(1) seek |
| SessionForkManager | `nasim/wire_log/fork.py` | `/fork` and `/undo` via turn enumeration from WireReader |

### Context Graph Group (E-06)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ContextGraph | `nasim/context/graph.py` | Typed graph replacing ConversationHistory as runtime model |
| ContextNode | `nasim/context/node.py` | Typed nodes: SystemPrompt, UserMessage, ToolCall, ToolResult, Memory, RepoMap |
| ContextEdge | `nasim/context/edge.py` | Typed edges: follows, calls, returns, summarizes, injects |
| ContextProcessor | `nasim/context/processor.py` | ABC for pipeline processors |
| TruncationProcessor | `nasim/context/truncation.py` | Removes old nodes respecting protection budget |
| DistillationProcessor | `nasim/context/distillation.py` | Secondary LLM call for massive tool outputs |
| InjectionProcessor | `nasim/context/injection.py` | Injects RepoMap, Memory nodes at turn start |
| CompactionProcessor | `nasim/context/compaction.py` | Replaces batch of nodes with summary node |
| PipelineOrchestrator | `nasim/context/pipeline.py` | Runs processors sequentially per turn |
| TokenBudgetTracker | `nasim/context/budget.py` | Counts tokens per node, sums for window budget |

### Diff Sandbox Group (E-09)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| DiffSandboxManager | `nasim/sandbox/diff_sandbox.py` | Manages edit staging and review cycle |
| EditStagingArea | `nasim/sandbox/staging.py` | In-memory file tree copy for staging edits |
| DiffComputer | `nasim/sandbox/diff_computer.py` | Computes diff between original and staged files |
| DiffPresenter | `nasim/sandbox/diff_presenter.py` | Renders diff to Renderer for user review |
| StagedApplicator | `nasim/sandbox/staged_applicator.py` | Applies staged changes to actual files on approval |

---

## Python Modules

| Module | Package | Purpose |
|--------|---------|---------|
| `nasim/__init__.py` | root | Package init |
| `nasim/__main__.py` | root | Entry point |
| `nasim/cli/__init__.py` | cli | CLI package |
| `nasim/cli/args.py` | cli | ArgParser |
| `nasim/cli/repl.py` | cli | REPLSession |
| `nasim/cli/renderer.py` | cli | Renderer |
| `nasim/cli/commands.py` | cli | SlashCommandHandler |
| `nasim/agent/__init__.py` | agent | Agent package |
| `nasim/agent/orchestrator.py` | agent | AgentOrchestrator |
| `nasim/agent/history.py` | agent | ConversationHistory |
| `nasim/agent/compactor.py` | agent | ContextCompactor |
| `nasim/agent/events.py` | agent | AgentEvent hierarchy |
| `nasim/agent/permission.py` | agent | PermissionGate |
| `nasim/agent/plan.py` | agent | PlanSession |
| `nasim/agent/subagent.py` | agent | SubagentCoordinator |
| `nasim/agent/safety.py` | agent | SafetyCoordinator |
| `nasim/agent/errors.py` | agent | ErrorBoundary |
| `nasim/agent/persona.py` | agent | PersonaManager |
| `nasim/provider/__init__.py` | provider | Provider package |
| `nasim/provider/base.py` | provider | Provider Protocol (unified interface) |
| `nasim/provider/litellm.py` | provider | LiteLLMProxy (universal LLM proxy) |
| `nasim/provider/router.py` | provider | ModelRouter |
| `nasim/provider/catalog.py` | provider | ModelCatalog |
| `nasim/provider/fallback.py` | provider | FallbackChain |
| `nasim/provider/caps.py` | provider | ProviderCapabilities |
| `nasim/tools/__init__.py` | tools | Tools package |
| `nasim/tools/base.py` | tools | Tool ABC, ToolRegistry, ToolResult |
| `nasim/tools/file.py` | tools | File tools |
| `nasim/tools/search.py` | tools | Search tools |
| `nasim/tools/shell.py` | tools | ShellTool |
| `nasim/tools/directory.py` | tools | DirTool |
| `nasim/tools/web.py` | tools | Web tools |
| `nasim/tools/git.py` | tools | GitTool |
| `nasim/tools/lsp.py` | tools | LspTool |
| `nasim/tools/subagent.py` | tools | SubagentTool |
| `nasim/tools/todo.py` | tools | TodoTool |
| `nasim/tools/memory.py` | tools | MemoryTool |
| `nasim/tools/plan.py` | tools | PlanTool |
| `nasim/tools/repo_map.py` | tools | RepoMapTool |
| `nasim/tools/semantic_search.py` | tools | SemanticSearchTool |
| `nasim/tools/review.py` | tools | ReviewTool |
| `nasim/mcp/__init__.py` | mcp | MCP package |
| `nasim/mcp/client.py` | mcp | MCPClientRuntime |
| `nasim/mcp/server.py` | mcp | MCPServerRuntime |
| `nasim/mcp/adapter.py` | mcp | MCPToolAdapter |
| `nasim/mcp/discovery.py` | mcp | MCPDiscovery |
| `nasim/config/__init__.py` | config | Config package |
| `nasim/config/loader.py` | config | ConfigLoader |
| `nasim/config/schema.py` | config | Config dataclass |
| `nasim/session/__init__.py` | session | Session package |
| `nasim/session/store.py` | session | SessionStore |
| `nasim/session/model.py` | session | Session model |
| `nasim/session/versioning.py` | session | SessionVersioning |
| `nasim/session/search.py` | session | SessionSearch |
| `nasim/session/fork.py` | session | SessionFork |
| `nasim/server/__init__.py` | server | Server package |
| `nasim/server/app.py` | server | ASGI application factory |
| `nasim/server/routes.py` | server | RESTful route handlers |
| `nasim/server/sse.py` | server | SSE streaming handler |
| `nasim/server/schema.py` | server | OpenAPI schema, request/response models |
| `nasim/hooks/__init__.py` | hooks | Hooks package |
| `nasim/hooks/manager.py` | hooks | HookManager |
| `nasim/hooks/types.py` | hooks | Hook types and results |
| `nasim/plugins/__init__.py` | plugins | Plugins package |
| `nasim/plugins/loader.py` | plugins | PluginLoader |
| `nasim/plugins/manifest.py` | plugins | PluginManifest |
| `nasim/sandbox/__init__.py` | sandbox | Sandbox package |
| `nasim/sandbox/executor.py` | sandbox | SandboxExecutor |
| `nasim/sandbox/policy.py` | sandbox | SandboxPolicy |
| `nasim/sandbox/monitor.py` | sandbox | SandboxMonitor |
| `nasim/sandbox/diff_sandbox.py` | sandbox | DiffSandboxManager |
| `nasim/sandbox/staging.py` | sandbox | EditStagingArea |
| `nasim/sandbox/diff_computer.py` | sandbox | DiffComputer |
| `nasim/sandbox/diff_presenter.py` | sandbox | DiffPresenter |
| `nasim/sandbox/staged_applicator.py` | sandbox | StagedApplicator |
| `nasim/observability/__init__.py` | observability | Observability package |
| `nasim/observability/logger.py` | observability | StructuredLogger |
| `nasim/observability/metrics.py` | observability | MetricsCollector |
| `nasim/observability/trace.py` | observability | TraceCorrelator |
| `nasim/observability/propagator.py` | observability | ContextPropagator |
| `nasim/observability/redactor.py` | observability | LogRedactor |
| `nasim/observability/adapter.py` | observability | DualOutputAdapter |
| `nasim/observability/otel.py` | observability | OTelExporter (optional) |
| `nasim/memory/__init__.py` | memory | Memory package |
| `nasim/memory/store.py` | memory | MemoryStore |
| `nasim/memory/index.py` | memory | MemoryIndex |
| `nasim/memory/scope.py` | memory | MemoryScope |
| `nasim/memory/episodic.py` | memory | EpisodicMemoryAdapter |
| `nasim/memory/semantic.py` | memory | SemanticMemoryAdapter |
| `nasim/memory/working.py` | memory | WorkingMemoryAdapter |
| `nasim/memory/retriever.py` | memory | MemoryRetriever (BM25 + Embedding + RRF) |
| `nasim/memory/indexer.py` | memory | MemoryIndexer |
| `nasim/git/__init__.py` | git | Git package |
| `nasim/git/integration.py` | git | GitIntegration |
| `nasim/git/status.py` | git | GitStatus |
| `nasim/git/commit.py` | git | GitCommit |
| `nasim/repo_intelligence/__init__.py` | repo_intelligence | Repo Intelligence package |
| `nasim/repo_intelligence/manager.py` | repo_intelligence | RepoIntelligenceManager |
| `nasim/repo_intelligence/ast_index.py` | repo_intelligence | ASTIndexAdapter |
| `nasim/repo_intelligence/symbol_graph.py` | repo_intelligence | SymbolGraph |
| `nasim/repo_intelligence/ranking.py` | repo_intelligence | RankingService |
| `nasim/repo_intelligence/embedding.py` | repo_intelligence | EmbeddingAdapter |
| `nasim/repo_intelligence/semantic_search.py` | repo_intelligence | SemanticSearchService |
| `nasim/repo_intelligence/repo_map.py` | repo_intelligence | RepoMapBuilder |
| `nasim/edit_strategy/__init__.py` | edit_strategy | Edit Strategy package |
| `nasim/edit_strategy/manager.py` | edit_strategy | EditStrategyManager |
| `nasim/edit_strategy/base.py` | edit_strategy | EditStrategy ABC |
| `nasim/edit_strategy/search_replace.py` | edit_strategy | SearchReplaceCoder |
| `nasim/edit_strategy/whole_file.py` | edit_strategy | WholeFileCoder |
| `nasim/edit_strategy/unified_diff.py` | edit_strategy | UnifiedDiffCoder |
| `nasim/edit_strategy/fenced_block.py` | edit_strategy | FencedBlockCoder |
| `nasim/edit_strategy/function_level.py` | edit_strategy | FunctionLevelCoder |
| `nasim/edit_strategy/diff_sandbox.py` | edit_strategy | DiffSandboxCoder |
| `nasim/edit_strategy/architect.py` | edit_strategy | ArchitectCoder |
| `nasim/edit_strategy/inline_patch.py` | edit_strategy | InlinePatchCoder |
| `nasim/edit_strategy/selector.py` | edit_strategy | StrategySelector |
| `nasim/evaluation/__init__.py` | evaluation | Evaluation package |
| `nasim/evaluation/engine.py` | evaluation | EvaluationEngine |
| `nasim/evaluation/evaluator.py` | evaluation | TaskEvaluator |
| `nasim/evaluation/success_check.py` | evaluation | SuccessCheckRunner |
| `nasim/evaluation/llm_reviewer.py` | evaluation | LLMReviewer |
| `nasim/evaluation/test_runner.py` | evaluation | TestRunner |
| `nasim/evaluation/retry.py` | evaluation | RetryCoordinator |
| `nasim/evaluation/quality.py` | evaluation | QualitySignal |
| `nasim/evaluation/repetition.py` | evaluation | RepetitionDetector |
| `nasim/evaluation/turn_budget.py` | evaluation | TurnBudgetInjector |
| `nasim/wire_log/__init__.py` | wire_log | Wire Log package |
| `nasim/wire_log/log.py` | wire_log | WireLog |
| `nasim/wire_log/appender.py` | wire_log | WireAppender |
| `nasim/wire_log/reader.py` | wire_log | WireReader |
| `nasim/wire_log/turn_index.py` | wire_log | TurnIndex |
| `nasim/wire_log/fork.py` | wire_log | SessionForkManager |
| `nasim/context/__init__.py` | context | Context Graph package |
| `nasim/context/graph.py` | context | ContextGraph |
| `nasim/context/node.py` | context | ContextNode |
| `nasim/context/edge.py` | context | ContextEdge |
| `nasim/context/processor.py` | context | ContextProcessor ABC |
| `nasim/context/truncation.py` | context | TruncationProcessor |
| `nasim/context/distillation.py` | context | DistillationProcessor |
| `nasim/context/injection.py` | context | InjectionProcessor |
| `nasim/context/compaction.py` | context | CompactionProcessor |
| `nasim/context/pipeline.py` | context | PipelineOrchestrator |
| `nasim/context/budget.py` | context | TokenBudgetTracker |

---

## Verb Extensions (Project-level)

The global verb list in `uc.md` is tuned for OVMS/registry domains. nasim requires
additional verbs for its CLI agent domain:

| Verb | Use | Rationale |
|------|-----|-----------|
| PROCESS | User input handling | No CRUD equivalent exists for REPL input |
| DISPATCH | Tool call routing | Unique routing semantics, not INVOKE |
| COMPACT | Context summarization | Domain-specific operation |
| FETCH | Web content retrieval | Read from external HTTP, not local store |
| SEARCH | Web/code search | Search external or local sources |
| STREAM | Real-time output delivery | Distinct from DISPLAY (push vs pull) |
| SERVE | Start HTTP server | Domain-specific: expose agent as service |
| ROUTE | Model selection | Unique routing semantics for model selection |
| HOOK | Pre/post processing | Extension point for tool and LLM lifecycle |
| DISCOVER | Plugin/tool discovery | Runtime discovery of plugins and MCP tools |
| SPAWN | Subagent creation | Create child agent with restricted tools |
| COLLECT | Subagent result | Gather results from completed child agents |
| DELEGATE | Task delegation | Assign tasks to specialized roles |
| SNAPSHOT | Session snapshot | Create session state snapshot |
| RESTORE | Session restore | Restore session from snapshot |
| BRANCH | Session fork | Branch conversation from any point |
| ISOLATE | Sandbox execution | Execute command in isolated environment |
| PERSIST | Memory write | Store knowledge across sessions |
| RECALL | Memory read | Retrieve knowledge from memory store |
| TRACE | Observability | Correlate events across request scope |
| INDEX | Repo intelligence | Build AST index and symbol graph |
| RANK | Repo intelligence | PageRank ranking of code symbols |
| EMBED | Semantic search | Generate vector embeddings for code |
| INJECT | Context pipeline | Inject repo-map or memory into context |
| DISTILL | Context pipeline | Compress large tool outputs via LLM |
| SELECT | Edit strategy | Choose optimal edit format for model |
| STAGE | Diff sandbox | Stage edits for review before apply |
| EVALUATE | Post-task evaluation | Run success checks and LLM review |
| RETRY | Evaluation retry | Re-attempt failed task with feedback |
| APPEND | Wire log | Append event to append-only log |
| REPLAY | Wire log | Replay session from wire log |
| FORK | Wire log/wire_log | Fork session at any turn |
| CLASSIFY | Model routing | Classify task type for model selection |

These extensions are documented here per `uc.md` — not silently diverging.
