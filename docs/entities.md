# nasim — Canonical Entity Registry

All component names, UC group codes, actors, and external systems registered here
must appear identically across C4 → UC → SM → SQ → CL → Code layers.

---

## UC Group Codes

| Code | Group | Scope |
|------|-------|-------|
| CLI | CLI Layer | REPL, argument parsing, slash commands, rendering |
| AGT | Agent Core | Orchestrator, conversation, context, permissions |
| LLM | Provider Layer | LLM provider abstraction, chat, streaming |
| TL | Tool Layer | All tool implementations |
| PRV | Provider Init | Provider lifecycle (init, chat, stream) |
| CFG | Configuration | Config loading and validation |
| SSN | Session | Session persistence and resumption |
| SAF | Safety | Permission checks and user approval |
| CTX | Context Management | Token counting and context compaction |

---

## Actors

| Actor | Description | C4 Reference |
|-------|-------------|-------------|
| Developer | Terminal user interacting with nasim | Person in C4 Context |

---

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Provider | HTTP/JSON | Inference backend (Ollama, OpenAI, Anthropic, etc.) |
| Host Filesystem | path I/O | Read/write project files |
| Host Shell | subprocess | Execute shell commands |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |

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
| ContextCompactor | `nasim/agent/compactor.py` | Summarizes old exchanges when budget exceeded |
| PermissionGate | `nasim/agent/permission.py` | Per-tool safety check; blocks or prompts in ask mode |
| PlanSession | `nasim/agent/plan.py` | Holds queued tool calls in plan mode |
| AgentEvent | `nasim/agent/events.py` | Event types: TextChunk, ToolStart, ToolResult, Error, Done |

### Provider Layer

| Component | Module | Responsibility |
|-----------|--------|---------------|
| Provider | `nasim/provider/base.py` | Protocol/interface: chat(), chat_stream(), model_name |
| ProviderFactory | `nasim/provider/base.py` | Reads config, instantiates correct provider |
| OllamaProvider | `nasim/provider/ollama.py` | Ollama /api/chat implementation |
| OpenAIProvider | `nasim/provider/openai.py` | OpenAI API implementation (Phase 2) |
| AnthropicProvider | `nasim/provider/anthropic.py` | Anthropic API implementation (Phase 2) |

### Tool Layer

| Component | Module | Responsibility |
|-----------|--------|---------------|
| Tool | `nasim/tools/base.py` | ABC: name, description, parameters, safe, execute() |
| ToolRegistry | `nasim/tools/base.py` | Instance-based registry; supports dynamic registration |
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
| `nasim/config/__init__.py` | config | Config package |
| `nasim/config/loader.py` | config | ConfigLoader |
| `nasim/config/schema.py` | config | Config dataclass |
| `nasim/session/__init__.py` | session | Session package |
| `nasim/session/store.py` | session | SessionStore |
| `nasim/session/model.py` | session | Session model |

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

These extensions are documented here per `uc.md` — not silently diverging.
