# nasim — Component Inventory

## C4 Diagram Set

| Diagram | Level | Boundary | Description |
|---------|-------|----------|-------------|
| c4_nasim_context.puml | Context | System | nasim with all external actors and systems (12 external) |
| c4_nasim_container.puml | Container | System | Deployable units: CLI, HTTP Server, Core Library (3 containers) |
| c4_nasim_component.puml | Component | Cross-container | Overview of all component groups and interactions |

## Per-Group Component Diagrams

| Diagram | Group | Components |
|---------|-------|------------|
| c4_nasim_component_agent.puml | Agent | AgentOrchestrator, ConversationHistory, ContextCompactor, SafetyCoordinator, PlanSession, AgentEvent, SubagentCoordinator, ErrorBoundary, PersonaManager |
| c4_nasim_component_provider.puml | Provider | Provider (Protocol), ProviderFactory, ModelRouter, ProviderCapabilities, FallbackChain, OllamaProvider, OpenAIProvider, AnthropicProvider |
| c4_nasim_component_tools.puml | Tools | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool |
| c4_nasim_component_mcp.puml | MCP | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| c4_nasim_component_config.puml | Config | ConfigLoader, Config |
| c4_nasim_component_session.puml | Session | SessionStore, Session, SessionVersioning, SessionSearch, SessionFork |
| c4_nasim_component_hooks.puml | Hooks | HookManager, Hook, HookResult |
| c4_nasim_component_plugins.puml | Plugins | PluginLoader, PluginManifest |
| c4_nasim_component_sandbox.puml | Sandbox | SandboxExecutor, SandboxPolicy, SandboxMonitor |
| c4_nasim_component_observability.puml | Observability | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, OTelExporter |
| c4_nasim_component_memory.puml | Memory | MemoryStore, MemoryIndex, MemoryScope |
| c4_nasim_component_git.puml | Git | GitIntegration, GitStatus, GitCommit |
| c4_nasim_component_subagent.puml | Subagent | SubagentCoordinator, AgentOrchestrator (child) |

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
| Sandbox Runtime | OS primitives | OS-level process isolation |
| Memory Backend | read/write | Long-term knowledge persistence |
| LSP Server | LSP protocol | Language server for code intelligence |
| Plugin Directory | filesystem | ~/.nasim/plugins/ — community extensions |

## Architecture Principles (p1.md Compliance)

- **3 deployable units only:** CLI process, HTTP Server process, Core Library
- **Single Responsibility per group:** Agent=orchestration, Provider=inference, Tool=execution, MCP=protocol, Config=configuration, Session=persistence, Hooks=extensibility, Plugins=discovery, Sandbox=isolation, Observability=logging, Memory=knowledge, Git=version control
- **No God Objects:** AgentOrchestrator delegates to SafetyCoordinator, SubagentCoordinator, PersonaManager
- **MCP first-class:** ClientRuntime, ServerRuntime, ToolAdapter, DiscoveryLayer as separate components
- **No System_Ext abuse:** Internal containers referenced via Container_Ext only
- **No orphan components:** Every component in detail diagrams appears in the cross-container overview
