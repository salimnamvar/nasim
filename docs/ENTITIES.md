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
| CTX | Context Management | Token counting, context compaction |
| SRV | HTTP Server | REST API, SSE streaming, session management via API |
| HK | Hooks | Pre/post hooks for tool use and LLM calls |
| PLG | Plugins | Plugin discovery, loading, registration |
| RTG | Model Router | Model selection, fallback, routing strategies |
| OBS | Observability | Structured logging, metrics, trace correlation |
| MEM | Memory | Cross-session knowledge persistence and retrieval |
| VCS | Git Integration | Auto-commit, branch awareness, diff tracking |
| SBX | Sandbox | OS-level process isolation for shell execution |

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
| StructuredLogger | `nasim/observability/logger.py` | Structured logging with trace correlation and log levels |
| MetricsCollector | `nasim/observability/metrics.py` | Token usage, latency, tool call counts, error rates |
| TraceCorrelator | `nasim/observability/trace.py` | Request-scoped trace IDs linking LLM calls, tool calls, events |

### Memory Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| MemoryStore | `nasim/memory/store.py` | Cross-session knowledge persistence and retrieval |
| MemoryIndex | `nasim/memory/index.py` | FTS5 index for semantic search across stored knowledge |
| MemoryScope | `nasim/memory/scope.py` | Scope isolation: global, project, session-level knowledge |

### Git Group (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| GitIntegration | `nasim/git/integration.py` | Auto-commit after file edits, branch awareness, diff tracking |
| GitStatus | `nasim/git/status.py` | Read working tree status, staged changes, branch info |
| GitCommit | `nasim/git/commit.py` | Create commits with conventional commit messages |

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
| `nasim/observability/__init__.py` | observability | Observability package |
| `nasim/observability/logger.py` | observability | StructuredLogger |
| `nasim/observability/metrics.py` | observability | MetricsCollector |
| `nasim/observability/trace.py` | observability | TraceCorrelator |
| `nasim/memory/__init__.py` | memory | Memory package |
| `nasim/memory/store.py` | memory | MemoryStore |
| `nasim/memory/index.py` | memory | MemoryIndex |
| `nasim/memory/scope.py` | memory | MemoryScope |
| `nasim/git/__init__.py` | git | Git package |
| `nasim/git/integration.py` | git | GitIntegration |
| `nasim/git/status.py` | git | GitStatus |
| `nasim/git/commit.py` | git | GitCommit |

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

These extensions are documented here per `uc.md` — not silently diverging.
