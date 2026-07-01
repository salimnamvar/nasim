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
| CLI Adapter | `nasim/controller/cli.py` | class | CLI Adapter | Terminal REPL: input processing, arg parsing, slash commands, output streaming |
| MCP Adapter | `nasim/controller/mcp.py` | class | MCP Adapter | MCP protocol: tool exposure, stdio/SSE transport, tool discovery |
| Agent Controller | `nasim/controller/agent.py` | class | Agent Controller | Central entry gate. All adapters converge here. Delegates to services. |

### Service Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Session Service | `nasim/service/session.py` | class | Session Service | Session lifecycle: create, load, save, snapshot, revert |

### Provider Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Provider | `nasim/provider/base.py` | Protocol | LLM Repository | Unified LLM interface: chat, chat_stream, model_name via litellm |
| LiteLLMProxy | `nasim/provider/litellm.py` | class | LLM Repository | Universal LLM proxy: 100+ providers via model string prefix |
| ModelRouter | `nasim/provider/router.py` | class | LLM Repository | Model selection, fallback, task classification |
| LLMResponse | `nasim/provider/base.py` | dataclass | — | Parsed LLM response: text, tool_calls, usage |
| ToolCall | `nasim/provider/base.py` | dataclass | — | Parsed tool call: name, arguments, id |
| ProviderCapabilities | `nasim/provider/caps.py` | dataclass | LLM Repository | Provider capability declaration |
| RoutingStrategy | `nasim/provider/strategy.py` | ABC | LLM Repository | Base routing strategy |
| TaskClassifierStrategy | `nasim/provider/strategy.py` | class | LLM Repository | Route by task type |
| CapabilityMatchStrategy | `nasim/provider/strategy.py` | class | LLM Repository | Route by capability match |
| CostOptimizationStrategy | `nasim/provider/strategy.py` | class | LLM Repository | Route by cost |
| RoleStrategy | `nasim/provider/strategy.py` | class | LLM Repository | Route by agent role |
| ModelRoleRegistry | `nasim/provider/registry.py` | class | LLM Repository | Preferred model per role |
| ProviderFactory | `nasim/provider/factory.py` | class | LLM Repository | Creates Provider instances from config |

### Agent Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| AgentOrchestrator | `nasim/agent/orchestrator.py` | class | Task Service | Core agentic orchestrator — drives LLM/tool loop |
| ConversationHistory | `nasim/agent/history.py` | class | Task Service | Message list + token tracking + compaction trigger |
| ContextCompactor | `nasim/agent/compactor.py` | class | Context Service | Context summarization via secondary LLM call |
| PermissionGate | `nasim/agent/safety.py` | class | Safety Service | Permission gating for tool execution |
| PlanSession | `nasim/agent/plan.py` | class | Task Service | Plan mode tool queuing and execution |
| AgentEvent | `nasim/agent/events.py` | ABC | — | Base event type — abstract |
| TextChunk | `nasim/agent/events.py` | class | — | Streaming text token event |
| ToolStart | `nasim/agent/events.py` | class | — | Tool execution start event |
| ToolResultEvent | `nasim/agent/events.py` | class | — | Tool execution result event |
| Error | `nasim/agent/events.py` | class | — | Error event |
| Done | `nasim/agent/events.py` | class | — | Task completion event |

### Tool Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Tool | `nasim/tools/base.py` | ABC | Tool Service | Base tool: name, description, parameters, safe, execute() |
| ToolRegistry | `nasim/tools/base.py` | class | Tool Service | Instance-based tool registry; dynamic registration |
| ToolResult | `nasim/tools/base.py` | dataclass | — | Structured result: success, content, error |
| ReadFileTool | `nasim/tools/file.py` | class | Filesystem Repository | Read file contents with offset/limit |
| WriteFileTool | `nasim/tools/file.py` | class | Filesystem Repository | Create or overwrite files |
| EditFileTool | `nasim/tools/file.py` | class | Filesystem Repository | Replace exact strings in files |
| GrepTool | `nasim/tools/search.py` | class | Filesystem Repository | Search file contents by regex pattern |
| GlobTool | `nasim/tools/search.py` | class | Filesystem Repository | Find files by glob pattern |
| FindFileTool | `nasim/tools/search.py` | class | Filesystem Repository | Find files by name pattern with depth |
| ShellTool | `nasim/tools/shell.py` | class | Sandbox Repository | Shell command execution with timeout |
| DirTool | `nasim/tools/directory.py` | class | Filesystem Repository | List directory contents |
| WebFetchTool | `nasim/tools/web.py` | class | Web Repository | Fetch URL content as markdown |
| WebSearchTool | `nasim/tools/web.py` | class | Web Repository | Search the web for information |
| GitTool | `nasim/tools/git.py` | class | Git Repository | Git status, diff, commit operations |
| LspTool | `nasim/tools/lsp.py` | class | Repo Intelligence Repository | LSP operations: hover, definition, references |
| MCPToolAdapter | `nasim/tools/mcp.py` | class | MCP Repository | Wraps MCP server tools into nasim Tool format |

### Config Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Config | `nasim/config/schema.py` | dataclass | Config Repository | Typed configuration: provider, model, safety, budget, mcp, server |
| ConfigLoader | `nasim/config/loader.py` | class | Config Repository | Loads global YAML + project YAML + env + CLI flags |

### Session Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Session | `nasim/session/model.py` | dataclass | Session Repository | Session data: id, created_at, messages, metadata |
| SessionStore | `nasim/session/store.py` | class | Session Repository | Persists/loads message history to ~/.nasim/sessions/ |
| History Repository | `nasim/session/history.py` | class | History Repository | Snapshots, revert index, search index |

### Server Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| ServerApp | `nasim/server/app.py` | class | HTTP Adapter | ASGI application factory |
| ServerRouter | `nasim/server/routes.py` | class | HTTP Adapter | RESTful route handlers |
| SSEHandler | `nasim/server/sse.py` | class | HTTP Adapter | SSE streaming for agent responses |
| APISchema | `nasim/server/schema.py` | class | HTTP Adapter | OpenAPI schema, request/response models |

### Hook Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| Hook | `nasim/hooks/types.py` | class | Tool Service | Hook definition: name, event, handler |
| HookResult | `nasim/hooks/types.py` | dataclass | Tool Service | Hook execution result: allow, deny, modify |
| HookManager | `nasim/hooks/manager.py` | class | Tool Service | Registers and executes hooks |

### Plugin Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| PluginLoader | `nasim/plugins/loader.py` | class | Tool Service | Discovers and loads plugins |
| PluginManifest | `nasim/plugins/manifest.py` | dataclass | Tool Service | Plugin metadata |
| Plugin | `nasim/plugins/loader.py` | class | Tool Service | Loaded plugin instance |

### Repo Intelligence Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| SymbolGraph | `nasim/repointel/graph.py` | class | Repo Intelligence Repository | In-memory symbol graph with pagerank |
| RankingService | `nasim/repointel/ranking.py` | class | Repo Intelligence Repository | Rank symbols by relevance |
| SemanticSearchService | `nasim/repointel/search.py` | class | Repo Intelligence Repository | Semantic search over embeddings |
| RepoMapBuilder | `nasim/repointel/map.py` | class | Repo Intelligence Repository | Build repo-map from ranked symbols |

### Edit Strategy Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EditStrategyManager | `nasim/editstrategy/manager.py` | ABC | Edit Strategy Repository | Abstract base for edit strategies |
| SearchReplaceCoder | `nasim/editstrategy/search_replace.py` | class | Edit Strategy Repository | Exact string replacement edits |
| WholeFileCoder | `nasim/editstrategy/whole_file.py` | class | Edit Strategy Repository | Full file overwrite edits |
| UnifiedDiffCoder | `nasim/editstrategy/unified_diff.py` | class | Edit Strategy Repository | Unified diff format edits |
| FencedBlockCoder | `nasim/editstrategy/fenced_block.py` | class | Edit Strategy Repository | Fenced code block edits |
| FunctionLevelCoder | `nasim/editstrategy/function_level.py` | class | Edit Strategy Repository | Function-level targeted edits |
| DiffSandboxCoder | `nasim/editstrategy/diff_sandbox.py` | class | Edit Strategy Repository | Sandboxed diff staging and review |
| ArchitectCoder | `nasim/editstrategy/architect.py` | class | Edit Strategy Repository | Architecture-first planning edits |
| InlinePatchCoder | `nasim/editstrategy/inline_patch.py` | class | Edit Strategy Repository | Inline patch format edits |
| StrategySelector | `nasim/editstrategy/selector.py` | class | Edit Strategy Repository | Selects strategy based on model capabilities |

### Evaluation Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EvaluationEngine | `nasim/evaluation/engine.py` | class | Evaluation Service | Orchestrates task quality evaluation |
| SuccessCheckRunner | `nasim/evaluation/success.py` | class | Evaluation Service | Runs success criteria checks |
| LLMReviewer | `nasim/evaluation/review.py` | class | Evaluation Service | Reviews task output via LLM |
| RetryCoordinator | `nasim/evaluation/retry.py` | class | Evaluation Service | Coordinates retry with feedback |
| RepetitionDetector | `nasim/evaluation/repetition.py` | class | Evaluation Service | Detects repeated tool call patterns |
| TurnBudgetInjector | `nasim/evaluation/turn_budget.py` | class | Evaluation Service | Injects turn budget instructions |

### Wire Log Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| WireLog | `nasim/wirelog/log.py` | class | Wire Log Repository | Append-only event store |
| WireAppender | `nasim/wirelog/appender.py` | class | Wire Log Repository | Writes WireEvents to storage |
| WireReader | `nasim/wirelog/reader.py` | class | Wire Log Repository | Iterates and seeks over WireEvents |
| TurnIndex | `nasim/wirelog/index.py` | class | Wire Log Repository | Maps turn number to byte offset |

### Context Graph Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| ContextGraph | `nasim/context/graph.py` | class | Context Service | Directed graph of context nodes |
| ContextNode | `nasim/context/graph.py` | class | Context Service | Node: type, content, token_count |
| ContextEdge | `nasim/context/graph.py` | class | Context Service | Edge: type, source, target |
| PipelineOrchestrator | `nasim/context/pipeline.py` | class | Context Service | Orchestrates the context processing pipeline |
| TruncationProcessor | `nasim/context/truncate.py` | class | Context Service | Truncates low-value context nodes |
| DistillationProcessor | `nasim/context/distill.py` | class | Context Service | Distills context via LLM summarization |
| InjectionProcessor | `nasim/context/inject.py` | class | Context Service | Injects relevant memory as context |
| CompactionProcessor | `nasim/context/compact.py` | class | Context Service | Compacts message history |
| TokenBudgetTracker | `nasim/context/budget.py` | class | Context Service | Tracks and enforces token budgets |

### Memory Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| MemoryRetriever | `nasim/memory/retriever.py` | class | Memory Repository | Queries cross-session knowledge |
| MemoryIndexer | `nasim/memory/indexer.py` | class | Memory Repository | Indexes knowledge entries |
| MemoryStore | `nasim/memory/store.py` | class | MemoryStore | Cross-session knowledge persistence: JSON + embeddings to ~/.nasim/memory/ |

### Data Store Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| WireLogStore | `nasim/wirelog/store.py` | class | WireLogStore | Append-only interaction log: JSONL storage |
| ConfigStore | `nasim/config/store.py` | class | ConfigStore | Configuration persistence: YAML profiles, project overrides, env vars |

### Sandbox Layer

| Class | Module (planned) | Type | C4 Component | Description |
|-------|------------------|------|-------------|-------------|
| EditStagingArea | `nasim/sandbox/staging.py` | class | Sandbox Repository | Staged file content for review |
| DiffComputer | `nasim/sandbox/diff.py` | class | Sandbox Repository | Computes diffs between original and staged |
| DiffPresenter | `nasim/sandbox/diff.py` | class | Sandbox Repository | Renders diff for user presentation |
| StagedApplicator | `nasim/sandbox/apply.py` | class | Sandbox Repository | Applies staged changes after approval |

---

## Relationships

| From | To | Relationship | Notes |
|------|----| ------------ | ----- |
| CLI Adapter | Agent Controller | delegates | Forwards input to central controller |
| MCP Adapter | Agent Controller | delegates | Forwards MCP calls to central controller |
| Agent Controller | Session Service | manages | Coordinates session lifecycle |
| Agent Controller | AgentOrchestrator | delegates | Dispatches tasks to agent core |
| Agent Controller | PermissionGate | enforces | Applies safety checks |
| Session Service | SessionStore | persists | Reads/writes session data |
| Session Service | History Repository | snapshots | Creates and manages snapshots |
| History Repository | SessionStore | reads from | Loads session data for snapshots |
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
