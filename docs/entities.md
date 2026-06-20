# nasim — Canonical Entity Registry

All component names, UC group codes, actors, and external systems registered here
must appear identically across C4 → UC → SM → SQ → ERD → CL → Code layers.

---

## UC Group Codes

| Code | Group | Scope |
|------|-------|-------|
| CLI | CLI Layer | REPL, argument parsing, slash commands, rendering |
| AGT | Agent Core | Orchestrator, conversation, context, permissions, plans |
| LLM | Provider Backend | LLM provider-specific chat and streaming |
| TL | Tool Layer | All tool implementations |
| PRV | Provider Abstraction | Provider lifecycle, factory, backend selection |
| CFG | Configuration | Config loading, validation, layered merge |
| SSN | Session | Session persistence, resumption, listing |
| SAF | Safety | Permission checks, user approval, safety modes |
| CTX | Context Management | Token counting, context compaction |
| SRV | HTTP Server | REST API, SSE streaming, session management via API |
| HK | Hooks | Pre/post hooks for tool use and LLM calls |
| PLG | Plugins | Plugin discovery, loading, registration |
| RTG | Model Router | Model selection, fallback, routing strategies |

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
| LLM Provider | HTTP/JSON | Inference backend (Ollama, OpenAI, Anthropic, etc.) |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| Global Config | YAML | ~/.nasim/config.yaml |
| Project Config | YAML | .nasim/config.yaml |
| Env Variables | env | NASIM_* environment variables |
| Session Directory | JSON Lines | ~/.nasim/sessions/<id>/ |
| Plugin Directory | JSON manifest | ~/.nasim/plugins/ |

---

## C4 Components

### CLI Layer

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ArgParser | `nasim/cli/args.py` | CLI argument parsing with layered overrides |
| REPLSession | `nasim/cli/repl.py` | Interactive REPL loop, input handling |
| Renderer | `nasim/cli/renderer.py` | All terminal output: colors, diffs, streaming, tool display |
| SlashCommandHandler | `nasim/cli/commands.py` | Maps `/cmd` strings to actions |

### Agent Layer

| Component | Module | Responsibility |
|-----------|--------|---------------|
| AgentOrchestrator | `nasim/agent/orchestrator.py` | Drives LLM/tool loop; emits events; stateless |
| ConversationHistory | `nasim/agent/history.py` | Owns messages + token count + compaction trigger |
| ContextCompactor | `nasim/agent/compactor.py` | Summarizes old exchanges via secondary LLM call |
| PermissionGate | `nasim/agent/permission.py` | Per-tool safety check; ask/auto/off modes |
| PlanSession | `nasim/agent/plan.py` | Holds queued tool calls in plan mode |
| AgentEvent | `nasim/agent/events.py` | Event types: TextChunk, ToolStart, ToolResult, Error, Done |

### Provider Layer

| Component | Module | Responsibility |
|-----------|--------|---------------|
| Provider | `nasim/provider/base.py` | Protocol: chat(), chat_stream(), model_name |
| ProviderFactory | `nasim/provider/base.py` | Reads config, instantiates correct provider |
| ModelRouter | `nasim/provider/router.py` | Model selection, fallback, routing strategies |
| OllamaProvider | `nasim/provider/ollama.py` | Ollama /api/chat implementation |
| OpenAIProvider | `nasim/provider/openai.py` | OpenAI Chat Completions API |
| AnthropicProvider | `nasim/provider/anthropic.py` | Anthropic Messages API |

### Tool Layer

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
| MCPToolAdapter | `nasim/tools/mcp.py` | Wraps MCP server tools into nasim Tool format |
| LspTool | `nasim/tools/lsp.py` | LSP operations: hover, definition, references, symbols |

### Config Layer (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ConfigLoader | `nasim/config/loader.py` | Loads global YAML + project YAML + env + CLI flags |
| Config | `nasim/config/schema.py` | Typed dataclass: provider, model, safety, budget, mcp |

### Session Layer (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| SessionStore | `nasim/session/store.py` | Persists/loads message history to ~/.nasim/sessions/ |
| Session | `nasim/session/model.py` | Session dataclass: id, created_at, messages |

### Server Layer (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| ServerApp | `nasim/server/app.py` | ASGI application factory, middleware, routing |
| ServerRouter | `nasim/server/routes.py` | RESTful route handlers: sessions, messages, tools, config |
| SSEHandler | `nasim/server/sse.py` | Server-Sent Events streaming for agent responses |
| APISchema | `nasim/server/schema.py` | OpenAPI 3.1 schema, request/response models |

### Hook Layer (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| HookManager | `nasim/hooks/manager.py` | Registers, discovers, and executes hooks |
| Hook | `nasim/hooks/types.py` | Hook types: PreToolUse, PostToolUse, PreLLMCall, PostLLMCall |
| HookResult | `nasim/hooks/types.py` | Hook execution result: allow, deny, modify |

### Plugin Layer (cross-cutting)

| Component | Module | Responsibility |
|-----------|--------|---------------|
| PluginLoader | `nasim/plugins/loader.py` | Discovers and loads plugins from ~/.nasim/plugins/ |
| PluginManifest | `nasim/plugins/manifest.py` | Plugin metadata: name, version, tools, hooks |

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
| `nasim/provider/__init__.py` | provider | Provider package |
| `nasim/provider/base.py` | provider | Provider Protocol + factory |
| `nasim/provider/router.py` | provider | ModelRouter |
| `nasim/provider/ollama.py` | provider | OllamaProvider |
| `nasim/provider/openai.py` | provider | OpenAIProvider |
| `nasim/provider/anthropic.py` | provider | AnthropicProvider |
| `nasim/tools/__init__.py` | tools | Tools package |
| `nasim/tools/base.py` | tools | Tool ABC, ToolRegistry, ToolResult |
| `nasim/tools/file.py` | tools | File tools |
| `nasim/tools/search.py` | tools | Search tools |
| `nasim/tools/shell.py` | tools | ShellTool |
| `nasim/tools/directory.py` | tools | DirTool |
| `nasim/tools/web.py` | tools | Web tools |
| `nasim/tools/git.py` | tools | GitTool |
| `nasim/tools/mcp.py` | tools | MCPToolAdapter |
| `nasim/tools/lsp.py` | tools | LspTool |
| `nasim/config/__init__.py` | config | Config package |
| `nasim/config/loader.py` | config | ConfigLoader |
| `nasim/config/schema.py` | config | Config dataclass |
| `nasim/session/__init__.py` | session | Session package |
| `nasim/session/store.py` | session | SessionStore |
| `nasim/session/model.py` | session | Session model |
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

These extensions are documented here per `uc.md` — not silently diverging.
