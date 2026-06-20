# nasim — Component Inventory

## Per-Container Component Diagrams

| Diagram | Container | Components |
|---------|-----------|------------|
| c4_nasim_component_cli.puml | CLI | ArgParser, REPLSession, Renderer, SlashCommandHandler |
| c4_nasim_component_agent.puml | Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, PermissionGate, PlanSession, AgentEvent |
| c4_nasim_component_provider.puml | Provider | Provider (Protocol), ProviderFactory, OllamaProvider, OpenAIProvider, AnthropicProvider |
| c4_nasim_component_tools.puml | Tools | Tool (ABC), ToolRegistry, ToolResult, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, MCPToolAdapter |
| c4_nasim_component_config.puml | Config | ConfigLoader, Config |
| c4_nasim_component_session.puml | Session | SessionStore, Session |
| c4_nasim_component_server.puml | Server | ServerApp, ServerRouter, SSEHandler, APISchema |

## Actors

| Actor | Description |
|-------|-------------|
| Developer | Terminal user interacting with nasim |

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Provider | HTTP/JSON | Inference backend (Ollama, OpenAI, Anthropic) |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| Global Config | YAML | ~/.nasim/config.yaml |
| Project Config | YAML | .nasim/config.yaml |
| Env Variables | env | NASIM_* environment variables |
| Session Directory | JSON Lines | ~/.nasim/sessions/<id>/ |
