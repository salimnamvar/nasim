# nasim — CL Inventory

| Diagram | Scope | Description |
|---------|-------|-------------|
| cl_runtime_model | Runtime | Core runtime classes: Provider, Tool, AgentOrchestrator, Config, Session, AgentEvent hierarchy |

## Class List

| Class | Module | Type | Description |
|-------|--------|------|-------------|
| Provider | `nasim/provider/base.py` | Protocol | LLM provider interface: chat(), chat_stream() |
| OllamaProvider | `nasim/provider/ollama.py` | class | Ollama /api/chat implementation |
| OpenAIProvider | `nasim/provider/openai.py` | class | OpenAI API implementation (Phase 2) |
| AnthropicProvider | `nasim/provider/anthropic.py` | class | Anthropic API implementation (Phase 2) |
| ProviderFactory | `nasim/provider/base.py` | class | Provider instantiation from config |
| LLMResponse | `nasim/provider/base.py` | dataclass | Parsed LLM response |
| ToolCall | `nasim/provider/base.py` | dataclass | Parsed tool call |
| AgentOrchestrator | `nasim/agent/orchestrator.py` | class | Core agentic orchestrator |
| ConversationHistory | `nasim/agent/history.py` | class | Message list + token tracking |
| ContextCompactor | `nasim/agent/compactor.py` | class | Context summarization |
| PermissionGate | `nasim/agent/permission.py` | class | Tool permission checks |
| PlanSession | `nasim/agent/plan.py` | class | Plan mode tool queuing |
| AgentEvent | `nasim/agent/events.py` | ABC | Base event type |
| TextChunk | `nasim/agent/events.py` | class | Streaming text token |
| ToolStart | `nasim/agent/events.py` | class | Tool execution start |
| ToolResult | `nasim/agent/events.py` | class | Tool execution result |
| Error | `nasim/agent/events.py` | class | Error event |
| Done | `nasim/agent/events.py` | class | Task completion event |
| Tool | `nasim/tools/base.py` | ABC | Base tool with execute() |
| ToolRegistry | `nasim/tools/base.py` | class | Instance-based tool registry |
| ReadFileTool | `nasim/tools/file.py` | class | Read file contents |
| WriteFileTool | `nasim/tools/file.py` | class | Write/overwrite files |
| EditFileTool | `nasim/tools/file.py` | class | Find-and-replace in files |
| GrepTool | `nasim/tools/search.py` | class | Regex search in files |
| GlobTool | `nasim/tools/search.py` | class | Glob pattern file search |
| FindFileTool | `nasim/tools/search.py` | class | Name pattern file search |
| ShellTool | `nasim/tools/shell.py` | class | Shell command execution |
| DirTool | `nasim/tools/directory.py` | class | Directory listing |
| WebFetchTool | `nasim/tools/web.py` | class | URL content fetch |
| WebSearchTool | `nasim/tools/web.py` | class | Web search |
| GitTool | `nasim/tools/git.py` | class | Git operations |
| MCPToolAdapter | `nasim/tools/mcp.py` | class | MCP server tool wrapper |
| Config | `nasim/config/schema.py` | dataclass | Typed configuration |
| ConfigLoader | `nasim/config/loader.py` | class | Layered config loading |
| Session | `nasim/session/model.py` | dataclass | Session data |
| SessionStore | `nasim/session/store.py` | class | Session persistence |

Note: nasim is a CLI agent tool. The CL diagram covers runtime structure
rather than a pure domain model (no business entities). This is a deliberate
deviation from the OVMS-style domain CL — documented in entities.md.
