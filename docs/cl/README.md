# nasim — CL Inventory

Class diagram covering the runtime class model for the nasim CLI code agent + HTTP API server.
No business domain entities — CL diagrams document the runtime structure.

Back to [docs/](../README.md).

## Diagrams

| File | Scope | Description |
| ---- | ----- | ----------- |
| `cl_runtime_model.puml` | Runtime | Core runtime classes: Provider, Tool, AgentOrchestrator, Config, Session, AgentEvent, Server, Hooks, Plugins |

## Class List

| Class | Module | Type | C4 Component | Description |
|-------|--------|------|-------------|-------------|
| Provider | `nasim/provider/base.py` | Protocol | Provider | LLM provider interface: chat(), chat_stream(), model_name |
| OllamaProvider | `nasim/provider/ollama.py` | class | Provider | Ollama /api/chat implementation |
| OpenAIProvider | `nasim/provider/openai.py` | class | Provider | OpenAI API implementation |
| AnthropicProvider | `nasim/provider/anthropic.py` | class | Provider | Anthropic API implementation |
| ProviderFactory | `nasim/provider/base.py` | class | Provider | Provider instantiation from config |
| ModelRouter | `nasim/provider/router.py` | class | Provider | Model selection, fallback, routing strategies |
| LLMResponse | `nasim/provider/base.py` | dataclass | — | Parsed LLM response: text, tool_calls, usage |
| ToolCall | `nasim/provider/base.py` | dataclass | — | Parsed tool call: name, arguments, id |
| AgentOrchestrator | `nasim/agent/orchestrator.py` | class | AgentOrchestrator | Core agentic orchestrator — drives LLM/tool loop |
| ConversationHistory | `nasim/agent/history.py` | class | ConversationHistory | Message list + token tracking + compaction trigger |
| ContextCompactor | `nasim/agent/compactor.py` | class | ContextCompactor | Context summarization via secondary LLM call |
| PermissionGate | `nasim/agent/permission.py` | class | PermissionGate | Tool permission checks: ask/auto/off modes |
| PlanSession | `nasim/agent/plan.py` | class | PlanSession | Plan mode tool queuing and execution |
| AgentEvent | `nasim/agent/events.py` | ABC | AgentEvent | Base event type — abstract |
| TextChunk | `nasim/agent/events.py` | class | AgentEvent | Streaming text token event |
| ToolStart | `nasim/agent/events.py` | class | AgentEvent | Tool execution start event |
| ToolResultEvent | `nasim/agent/events.py` | class | AgentEvent | Tool execution result event |
| Error | `nasim/agent/events.py` | class | AgentEvent | Error event |
| Done | `nasim/agent/events.py` | class | AgentEvent | Task completion event |
| Tool | `nasim/tools/base.py` | ABC | Tool | Base tool: name, description, parameters, safe, execute() |
| ToolRegistry | `nasim/tools/base.py` | class | ToolRegistry | Instance-based tool registry; dynamic registration |
| ToolResult | `nasim/tools/base.py` | dataclass | ToolResult | Structured result: success, content, error |
| ReadFileTool | `nasim/tools/file.py` | class | Tool | Read file contents with offset/limit |
| WriteFileTool | `nasim/tools/file.py` | class | Tool | Create or overwrite files |
| EditFileTool | `nasim/tools/file.py` | class | Tool | Replace exact strings in files |
| GrepTool | `nasim/tools/search.py` | class | Tool | Search file contents by regex pattern |
| GlobTool | `nasim/tools/search.py` | class | Tool | Find files by glob pattern |
| FindFileTool | `nasim/tools/search.py` | class | Tool | Find files by name pattern with depth |
| ShellTool | `nasim/tools/shell.py` | class | Tool | Shell command execution with timeout |
| DirTool | `nasim/tools/directory.py` | class | Tool | List directory contents |
| WebFetchTool | `nasim/tools/web.py` | class | Tool | Fetch URL content as markdown |
| WebSearchTool | `nasim/tools/web.py` | class | Tool | Search the web for information |
| GitTool | `nasim/tools/git.py` | class | Tool | Git status, diff, commit operations |
| LspTool | `nasim/tools/lsp.py` | class | Tool | LSP operations: hover, definition, references |
| MCPToolAdapter | `nasim/tools/mcp.py` | class | Tool | Wraps MCP server tools into nasim Tool format |
| Config | `nasim/config/schema.py` | dataclass | Config | Typed configuration: provider, model, safety, budget, mcp, server |
| ConfigLoader | `nasim/config/loader.py` | class | ConfigLoader | Loads global YAML + project YAML + env + CLI flags |
| Session | `nasim/session/model.py` | dataclass | Session | Session data: id, created_at, messages |
| SessionStore | `nasim/session/store.py` | class | SessionStore | Persists/loads message history to ~/.nasim/sessions/ |
| ServerApp | `nasim/server/app.py` | class | Server | ASGI application factory |
| ServerRouter | `nasim/server/routes.py` | class | Server | RESTful route handlers |
| SSEHandler | `nasim/server/sse.py` | class | Server | SSE streaming for agent responses |
| APISchema | `nasim/server/schema.py` | class | Server | OpenAPI schema, request/response models |
| HookManager | `nasim/hooks/manager.py` | class | Hook | Registers and executes hooks |
| Hook | `nasim/hooks/types.py` | class | Hook | Hook definition: name, event, handler |
| HookResult | `nasim/hooks/types.py` | dataclass | Hook | Hook execution result: allow, deny, modify |
| PluginLoader | `nasim/plugins/loader.py` | class | Plugin | Discovers and loads plugins |
| PluginManifest | `nasim/plugins/manifest.py` | dataclass | Plugin | Plugin metadata |
| Plugin | `nasim/plugins/loader.py` | class | Plugin | Loaded plugin instance |

## Relationships

| From | To | Relationship | Notes |
| ---- | --- | ------------ | ----- |
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

## Notes

- nasim is a CLI agent tool with HTTP API server mode. The CL diagram covers runtime structure
  rather than a pure domain model (no business entities). This is a deliberate
  deviation from the OVMS-style domain CL — documented in entities.md.
- AgentEvent hierarchy uses ABC base with concrete subtypes (TextChunk, ToolStart, ToolResultEvent, Error, Done).
- Tool ABC defines the contract; ToolRegistry manages instances.
- Provider Protocol defines the interface; concrete implementations per backend.
- Server layer (ServerApp, ServerRouter, SSEHandler) enables multi-interface: CLI + HTTP + MCP.
- Hook system enables extension without code changes.
- Plugin system enables community extensions.

## Design Chain Position

```
... → SQ → ERD → CL → Code
```

## Related Layers

| Layer | Path |
| ----- | ---- |
| C4 components (source) | `docs/c4/` |
| UC inventory | `docs/uc/` |
| SQ diagrams | `docs/sq/` |
| ERD — session store | `docs/er/er_session_store.puml` |
| Entity registry | `docs/entities.md` |
