# nasim — Component Inventory

## Per-Container Component Diagrams

| Diagram | Container | Components |
|---------|-----------|------------|
| c4_nasim_component_cli.puml | CLI | ArgParser, REPLSession, Renderer, SlashCommandHandler |
| c4_nasim_component_agent.puml | Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, PermissionGate, PlanSession, AgentEvent, SubagentManager, TaskDispatcher, ErrorBoundary, SafetyPipeline, PersonaLoader |
| c4_nasim_component_provider.puml | Provider | Provider (Protocol), ProviderFactory, ModelRouter, ProviderCapabilities, FallbackChain, OllamaProvider, OpenAIProvider, AnthropicProvider |
| c4_nasim_component_tools.puml | Tools | Tool (ABC), ToolRegistry, ToolResult, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, MCPToolAdapter, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool |
| c4_nasim_component_config.puml | Config | ConfigLoader, Config |
| c4_nasim_component_session.puml | Session | SessionStore, Session, SessionVersioning, SessionSearch, SessionFork |
| c4_nasim_component_server.puml | Server | ServerApp, ServerRouter, SSEHandler, APISchema |
| c4_nasim_component_sandbox.puml | Sandbox | SandboxExecutor, SandboxPolicy, SandboxMonitor |
| c4_nasim_component_observability.puml | Observability | StructuredLogger, MetricsCollector, TraceCorrelator |
| c4_nasim_component_memory.puml | Memory | MemoryStore, MemoryIndex, MemoryScope |
| c4_nasim_component_git.puml | Git | GitIntegration, GitStatus, GitCommit |

## Actors

| Actor | Description |
|-------|-------------|
| Developer | Terminal user interacting with nasim |
| HTTP Client | External HTTP client (web-app, mobile, desktop) |

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Backend | HTTP/JSON | Multi-provider inference (Ollama, OpenAI, Anthropic) |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands (via sandbox) |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| MCP Client | stdio/SSE | External tools connecting to nasim MCP server |
| Git Repository | git CLI | Version control for project files |
| Plugin Directory | filesystem | ~/.nasim/plugins/ — community extensions |
| Sandbox Runtime | OS primitives | OS-level process isolation |
| Memory Backend | read/write | Long-term knowledge persistence |
| LSP Server | LSP protocol | Language server for code intelligence |
