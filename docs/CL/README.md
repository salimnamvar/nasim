# nasim — Class Diagram Inventory

Runtime class model for the nasim CLI code agent + HTTP API server + MCP server.

> **Design Note:** nasim has no business domain entities. CL diagrams document the
> runtime structure of the agent system — providers, tools, orchestration, and
> infrastructure. This is a deliberate deviation from OVMS-style domain-only CL.

Back to [docs/](../README.md).

---

## Design Chain Position

```
... → SQ → ERD → CL → CT/DATA → CT/API → Code
```

---

## Diagrams

| File | Scope | Version | Description |
|------|-------|---------|-------------|
| `cl_runtime_model.puml` | Runtime | 6.0.0 | Core runtime classes: Controller, Service, Provider, Tool, AgentOrchestrator, Config, Session, AgentEvent, Server, Hooks, Plugins, Data Stores |

---

## Class Inventory

### Controller Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| CLIAdapter | `nasim/controller/cli.py` | class | CLIAdapter | Terminal REPL: input processing, arg parsing, slash commands, output streaming |
| MCPAdapter | `nasim/controller/mcp.py` | class | MCPAdapter | MCP protocol: tool exposure, stdio/SSE transport, tool discovery |
| AgentController | `nasim/controller/agent.py` | class | AgentController | Central entry gate. All adapters converge here. Delegates to services. |

### Service Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| SessionService | `nasim/service/session.py` | class | SessionService | Session lifecycle: create, load, save, snapshot, revert |

### Provider Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Provider | `nasim/provider/base.py` | Protocol | LLMRepository | Unified LLM interface: chat, chat_stream, model_name via litellm |
| LiteLLMProxy | `nasim/provider/litellm.py` | class | LLMRepository | Universal LLM proxy: 100+ providers via model string prefix |
| ModelRouter | `nasim/provider/router.py` | class | LLMRepository | Model selection, fallback, task classification |
| LLMResponse | `nasim/provider/base.py` | dataclass | — | Parsed LLM response: text, tool_calls, usage |
| ToolCall | `nasim/provider/base.py` | dataclass | — | Parsed tool call: name, arguments, id |
| ProviderCapabilities | `nasim/provider/caps.py` | dataclass | LLMRepository | Provider capability declaration |
| RoutingStrategy | `nasim/provider/strategy.py` | ABC | LLMRepository | Base routing strategy |
| TaskClassifierStrategy | `nasim/provider/strategy.py` | class | LLMRepository | Route by task type |
| CapabilityMatchStrategy | `nasim/provider/strategy.py` | class | LLMRepository | Route by capability match |
| CostOptimizationStrategy | `nasim/provider/strategy.py` | class | LLMRepository | Route by cost |
| RoleStrategy | `nasim/provider/strategy.py` | class | LLMRepository | Route by agent role |
| ModelRoleRegistry | `nasim/provider/registry.py` | class | LLMRepository | Preferred model per role |
| ProviderFactory | `nasim/provider/factory.py` | class | LLMRepository | Creates Provider instances from config |

### Agent Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| AgentOrchestrator | `nasim/agent/orchestrator.py` | class | TaskService | Core agentic orchestrator — drives LLM/tool loop |
| ConversationHistory | `nasim/agent/history.py` | class | TaskService | Message list + token tracking + compaction trigger |
| ContextCompactor | `nasim/agent/compactor.py` | class | ContextService | Context summarization via secondary LLM call |
| PermissionGate | `nasim/agent/safety.py` | class | SafetyService | Permission gating for tool execution |
| PlanSession | `nasim/agent/plan.py` | class | TaskService | Plan mode tool queuing and execution |
| AgentEvent | `nasim/agent/events.py` | ABC | — | Base event type — abstract |
| TextChunk | `nasim/agent/events.py` | class | — | Streaming text token event |
| ToolStart | `nasim/agent/events.py` | class | — | Tool execution start event |
| ToolResultEvent | `nasim/agent/events.py` | class | — | Tool execution result event |
| Error | `nasim/agent/events.py` | class | — | Error event |
| Done | `nasim/agent/events.py` | class | — | Task completion event |

### Tool Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Tool | `nasim/tools/base.py` | ABC | ToolService | Base tool: name, description, parameters, safe, execute() |
| ToolRegistry | `nasim/tools/base.py` | class | ToolService | Instance-based tool registry; dynamic registration |
| ToolResult | `nasim/tools/base.py` | dataclass | — | Structured result: success, content, error |
| ReadFileTool | `nasim/tools/file.py` | class | FilesystemRepository | Read file contents with offset/limit |
| WriteFileTool | `nasim/tools/file.py` | class | FilesystemRepository | Create or overwrite files |
| EditFileTool | `nasim/tools/file.py` | class | FilesystemRepository | Replace exact strings in files |
| GrepTool | `nasim/tools/search.py` | class | FilesystemRepository | Search file contents by regex pattern |
| GlobTool | `nasim/tools/search.py` | class | FilesystemRepository | Find files by glob pattern |
| FindFileTool | `nasim/tools/search.py` | class | FilesystemRepository | Find files by name pattern with depth |
| ShellTool | `nasim/tools/shell.py` | class | SandboxRepository | Shell command execution with timeout |
| DirTool | `nasim/tools/directory.py` | class | FilesystemRepository | List directory contents |
| WebFetchTool | `nasim/tools/web.py` | class | WebRepository | Fetch URL content as markdown |
| WebSearchTool | `nasim/tools/web.py` | class | WebRepository | Search the web for information |
| GitTool | `nasim/tools/git.py` | class | GitRepository | Git status, diff, commit operations |
| LspTool | `nasim/tools/lsp.py` | class | RepoIntelligenceRepository | LSP operations: hover, definition, references |
| MCPToolAdapter | `nasim/tools/mcp.py` | class | MCPRepository | Wraps MCP server tools into nasim Tool format |

### Config Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Config | `nasim/config/schema.py` | dataclass | ConfigRepository | Typed configuration: provider, model, safety, budget, mcp, server |
| ConfigLoader | `nasim/config/loader.py` | class | ConfigRepository | Loads global YAML + project YAML + env + CLI flags |

### Session Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Session | `nasim/session/model.py` | dataclass | SessionRepository | Session data: id, created_at, messages, metadata |
| SessionStore | `nasim/session/store.py` | class | SessionRepository | Persists/loads message history to ~/.nasim/sessions/ |
| HistoryRepository | `nasim/session/history.py` | class | HistoryRepository | Snapshots, revert index, search index |

### Server Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| ServerApp | `nasim/server/app.py` | class | HTTPAdapter | ASGI application factory |
| ServerRouter | `nasim/server/routes.py` | class | HTTPAdapter | RESTful route handlers |
| SSEHandler | `nasim/server/sse.py` | class | HTTPAdapter | SSE streaming for agent responses |
| APISchema | `nasim/server/schema.py` | class | HTTPAdapter | OpenAPI schema, request/response models |

### Hook Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Hook | `nasim/hooks/types.py` | class | ToolService | Hook definition: name, event, handler |
| HookResult | `nasim/hooks/types.py` | dataclass | ToolService | Hook execution result: allow, deny, modify |
| HookManager | `nasim/hooks/manager.py` | class | ToolService | Registers and executes hooks |

### Plugin Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| PluginLoader | `nasim/plugins/loader.py` | class | ToolService | Discovers and loads plugins |
| PluginManifest | `nasim/plugins/manifest.py` | dataclass | ToolService | Plugin metadata |
| Plugin | `nasim/plugins/loader.py` | class | ToolService | Loaded plugin instance |

### Repo Intelligence Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| SymbolGraph | `nasim/repointel/graph.py` | class | RepoIntelligenceRepository | In-memory symbol graph with pagerank |
| RankingService | `nasim/repointel/ranking.py` | class | RepoIntelligenceRepository | Rank symbols by relevance |
| SemanticSearchService | `nasim/repointel/search.py` | class | RepoIntelligenceRepository | Semantic search over embeddings |
| RepoMapBuilder | `nasim/repointel/map.py` | class | RepoIntelligenceRepository | Build repo-map from ranked symbols |

### Edit Strategy Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EditStrategyManager | `nasim/editstrategy/manager.py` | ABC | EditStrategyRepository | Abstract base for edit strategies |
| SearchReplaceCoder | `nasim/editstrategy/search_replace.py` | class | EditStrategyRepository | Exact string replacement edits |
| WholeFileCoder | `nasim/editstrategy/whole_file.py` | class | EditStrategyRepository | Full file overwrite edits |
| UnifiedDiffCoder | `nasim/editstrategy/unified_diff.py` | class | EditStrategyRepository | Unified diff format edits |
| FencedBlockCoder | `nasim/editstrategy/fenced_block.py` | class | EditStrategyRepository | Fenced code block edits |
| FunctionLevelCoder | `nasim/editstrategy/function_level.py` | class | EditStrategyRepository | Function-level targeted edits |
| DiffSandboxCoder | `nasim/editstrategy/diff_sandbox.py` | class | EditStrategyRepository | Sandboxed diff staging and review |
| ArchitectCoder | `nasim/editstrategy/architect.py` | class | EditStrategyRepository | Architecture-first planning edits |
| InlinePatchCoder | `nasim/editstrategy/inline_patch.py` | class | EditStrategyRepository | Inline patch format edits |
| StrategySelector | `nasim/editstrategy/selector.py` | class | EditStrategyRepository | Selects strategy based on model capabilities |

### Evaluation Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EvaluationEngine | `nasim/evaluation/engine.py` | class | EvaluationService | Orchestrates task quality evaluation |
| SuccessCheckRunner | `nasim/evaluation/success.py` | class | EvaluationService | Runs success criteria checks |
| LLMReviewer | `nasim/evaluation/review.py` | class | EvaluationService | Reviews task output via LLM |
| RetryCoordinator | `nasim/evaluation/retry.py` | class | EvaluationService | Coordinates retry with feedback |
| RepetitionDetector | `nasim/evaluation/repetition.py` | class | EvaluationService | Detects repeated tool call patterns |
| TurnBudgetInjector | `nasim/evaluation/turn_budget.py` | class | EvaluationService | Injects turn budget instructions |

### Wire Log Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| WireLog | `nasim/wirelog/log.py` | class | WireLogRepository | Append-only event store |
| WireAppender | `nasim/wirelog/appender.py` | class | WireLogRepository | Writes WireEvents to storage |
| WireReader | `nasim/wirelog/reader.py` | class | WireLogRepository | Iterates and seeks over WireEvents |
| TurnIndex | `nasim/wirelog/index.py` | class | WireLogRepository | Maps turn number to byte offset |

### Context Graph Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| ContextGraph | `nasim/context/graph.py` | class | ContextService | Directed graph of context nodes |
| ContextNode | `nasim/context/graph.py` | class | ContextService | Node: type, content, token_count |
| ContextEdge | `nasim/context/graph.py` | class | ContextService | Edge: type, source, target |
| PipelineOrchestrator | `nasim/context/pipeline.py` | class | ContextService | Orchestrates the context processing pipeline |
| TruncationProcessor | `nasim/context/truncate.py` | class | ContextService | Truncates low-value context nodes |
| DistillationProcessor | `nasim/context/distill.py` | class | ContextService | Distills context via LLM summarization |
| InjectionProcessor | `nasim/context/inject.py` | class | ContextService | Injects relevant memory as context |
| CompactionProcessor | `nasim/context/compact.py` | class | ContextService | Compacts message history |
| TokenBudgetTracker | `nasim/context/budget.py` | class | ContextService | Tracks and enforces token budgets |

### Memory Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| MemoryRetriever | `nasim/memory/retriever.py` | class | MemoryRepository | Queries cross-session knowledge |
| MemoryIndexer | `nasim/memory/indexer.py` | class | MemoryRepository | Indexes knowledge entries |
| MemoryStore | `nasim/memory/store.py` | class | MemoryStore | Cross-session knowledge persistence: JSON + embeddings to ~/.nasim/memory/ |

### Data Store Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| WireLogStore | `nasim/wirelog/store.py` | class | WireLogStore | Append-only interaction log: JSONL storage |
| ConfigStore | `nasim/config/store.py` | class | ConfigStore | Configuration persistence: YAML profiles, project overrides, env vars |

### Sandbox Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EditStagingArea | `nasim/sandbox/staging.py` | class | SandboxRepository | Staged file content for review |
| DiffComputer | `nasim/sandbox/diff.py` | class | SandboxRepository | Computes diffs between original and staged |
| DiffPresenter | `nasim/sandbox/diff.py` | class | SandboxRepository | Renders diff for user presentation |
| StagedApplicator | `nasim/sandbox/apply.py` | class | SandboxRepository | Applies staged changes after approval |

---

## Relationships

| From | To | Relationship | Notes |
|------|----| ------------ | ----- |
| CLIAdapter | AgentController | delegates | Forwards input to central controller |
| MCPAdapter | AgentController | delegates | Forwards MCP calls to central controller |
| AgentController | SessionService | manages | Coordinates session lifecycle |
| AgentController | AgentOrchestrator | delegates | Dispatches tasks to agent core |
| AgentController | PermissionGate | enforces | Applies safety checks |
| SessionService | SessionStore | persists | Reads/writes session data |
| SessionService | HistoryRepository | snapshots | Creates and manages snapshots |
| HistoryRepository | SessionStore | reads from | Loads session data for snapshots |
| MemoryStore | MemoryRetriever | backs | Provides storage for memory queries |
| WireLogStore | WireAppender | writes via | Backs wire log writes |
| WireLogStore | WireReader | reads via | Backs wire log reads |
| ConfigStore | ConfigLoader | sources from | Provides config data |
| AgentOrchestrator | Provider | uses | Calls chat()/chat_stream() |
| AgentOrchestrator | ToolRegistry | uses | Dispatches tool calls |
| AgentOrchestrator | ConversationHistory | owns | Manages message list |
| AgentOrchestrator | PermissionGate | uses | Checks before tool exec |
| AgentOrchestrator | PlanSession | uses | Queues in plan mode |
| AgentOrchestrator | HookManager | uses | Triggers pre/post hooks |
| AgentOrchestrator | ModelRouter | uses | Routes model selection |
| ConversationHistory | ContextCompactor | delegates | Triggers compaction |
| ProviderFactory | Provider | creates | Instantiates from config |
| ModelRouter | Provider | selects | Chooses provider backend |
| ConfigLoader | Config | produces | Returns typed config |
| SessionStore | Session | persists | JSON Lines files |
| ServerApp | ServerRouter | uses | Routes HTTP requests |
| ServerRouter | AgentOrchestrator | delegates | Processes requests |
| ServerRouter | SSEHandler | streams | SSE event streaming |
| HookManager | Hook | manages | Registers and executes |
| PluginLoader | Plugin | creates | Discovers and loads |
| Plugin | Tool | provides | Registers plugin tools |
| Plugin | Hook | provides | Registers plugin hooks |

---

## Implementation Status

| Status | Count | Notes |
|--------|-------|-------|
| Planned | 98+ | All module paths are planned. No Python source code exists yet. |

---

## Design Decisions

- **Runtime, not domain:** CL diagrams cover runtime structure (providers, tools, orchestration) rather than business domain entities. This is deliberate for an agent system.
- **ABC contracts:** Tool, AgentEvent, and RoutingStrategy use ABC to define extension points.
- **Protocol for Provider:** Provider is a Protocol (structural subtyping) to allow any LLM backend.
- **Event hierarchy:** AgentEvent uses ABC base with concrete subtypes (TextChunk, ToolStart, ToolResultEvent, Error, Done).
- **Server layer:** ServerApp, ServerRouter, SSEHandler enable multi-interface (CLI + HTTP + MCP).
- **Hook/Plugin extensibility:** Both systems enable extension without core code changes.

---

## Related Layers

| Layer | Path | Relationship |
|-------|------|--------------|
| C4 Components (source) | `docs/C4/c4_nasim_component.puml` | Maps classes to C4 components |
| UC Inventory | `docs/UC/` | Use cases that drive class behavior |
| SQ Diagrams | `docs/SQ/` | Sequence diagrams showing class collaboration |
| ERD | `docs/ER/` | Data store schemas: Session, Memory, Wire Log, Config |
| CT/DATA | `docs/CT/DATA/` | Data contracts mapped from ERDs |
