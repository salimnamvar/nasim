# NASIM Application — C4 Diagram Inventory

## How to Read These Diagrams

The C4 model provides a hierarchical way to understand software architecture at different zoom levels. NASIM Application's diagram set follows this hierarchy:

```
Level 1: Context    →  c4_nasim_context.puml
Level 2: Container  →  c4_nasim_container.puml
Level 3: Component  →  c4_nasim_component_overview.puml (high-level)
                     →  c4_nasim_component_*.puml (per-group details)
```

### Reading Path

1. **Start with Context** (`c4_nasim_context.puml`): Understand what NASIM Application is and what external systems it interacts with.
2. **Move to Container** (`c4_nasim_container.puml`): See the 3 runtime entry points: CLI Process, HTTP API Server, and Core Engine. Note: NASIM Application runs as a single Python process — CLI and HTTP are modeled as separate Containers because they represent distinct runtime entry points and responsibilities.
3. **Explore Overview** (`c4_nasim_component_overview.puml`): See all 21 component groups inside the Core Engine, color-coded by CSR layer.
4. **Dive into Details** (`c4_nasim_component_*.puml`): Each per-group diagram shows internal components, relationships, and external dependencies.

## C4 Diagram Set

### Level 1: System Context

| Diagram | Level | Description |
|---------|-------|-------------|
| `c4_nasim_context.puml` | Context | NASIM Application as a single system with User actor and 11 external systems |

### Level 2: Containers

| Diagram | Level | Description |
|---------|-------|-------------|
| `c4_nasim_container.puml` | Container | 3 runtime entry points: CLI Process, HTTP API Server, Core Engine + 4 external interface containers |

### Level 3: Components

| Diagram | Level | Description |
|---------|-------|-------------|
| `c4_nasim_component_overview.puml` | Component (Overview) | High-level view of all 21 groups with CSR layer coloring and key cross-group relationships. **SIM-01 exception:** 62 elements — intentionally exceeds 12-element limit as a full-system overview map. Detailed views are in per-group diagrams. |

## Per-Group Component Diagrams (21 diagrams)

Each per-group diagram shows internal components within `Boundary(nasim_application, "NASIM Application")` and `Boundary(group_name)`. Cross-group references use `Component_Ext(alias, "ComponentName", "Group Name")`.

### Controller Layer (Blue)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_cli.puml` | CLI Group | ArgParser, REPLSession, Renderer, SlashCommandHandler |
| `c4_nasim_component_server.puml` | API Group | ServerApp, ServerRouter, SSEHandler, APISchema |

### Service Layer (Orange)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_agent.puml` | Agent Group | AgentOrchestrator, ConversationHistory, ContextCompactor, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| `c4_nasim_component_router.puml` | Router Group | ModelRouter, FallbackChain, ProviderCapabilities |
| `c4_nasim_component_provider.puml` | Provider Group | Provider (Protocol), LiteLLMProxy |
| `c4_nasim_component_safety.puml` | Safety Group | SafetyCoordinator, PermissionGate, InjectionScanner, EgressInspector |
| `c4_nasim_component_context_graph.puml` | Context Graph Group | ContextGraph, PipelineOrchestrator, ContextPrioritizer, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor |
| `c4_nasim_component_edit_strategy.puml` | Edit Strategy Group | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |
| `c4_nasim_component_evaluation.puml` | Evaluation Group | EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, RepetitionDetector, TurnBudgetInjector |

### Repository Layer (Green)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_session.puml` | Session Group | SessionStore, SessionVersioning, SessionSearch, SessionFork |
| `c4_nasim_component_tools.puml` | Tool Group | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| `c4_nasim_component_memory.puml` | Memory Group | MemoryStore, MemoryIndex, MemoryScope, EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, MemoryIndexer |
| `c4_nasim_component_config.puml` | Config Group | ConfigLoader, Config (dataclass) |
| `c4_nasim_component_git.puml` | Git Group | GitIntegration, GitStatus, GitCommit |
| `c4_nasim_component_repo_intelligence.puml` | Repo Intelligence Group | RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder |

### Infrastructure Layer (Purple)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_mcp.puml` | MCP Group | MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| `c4_nasim_component_sandbox.puml` | Sandbox Group | SandboxExecutor, SandboxPolicy, SandboxMonitor, ResourceLimiter, DiffSandboxManager, EditStagingArea, DiffComputer, StagedApplicator |
| `c4_nasim_component_observability.puml` | Observability Group | StructuredLogger, MetricsCollector, TraceCorrelator, ContextPropagator, LogRedactor, DualOutputAdapter, InstrumentationMiddleware, OTelExporter |
| `c4_nasim_component_wire_log.puml` | Wire Log Group | WireLog, WireAppender, WireReader, SessionForkManager |
| `c4_nasim_component_hooks.puml` | Hooks Group | HookManager |
| `c4_nasim_component_plugins.puml` | Plugins Group | PluginLoader |

**Total: 24 C4 diagrams (1 context + 1 container + 1 overview + 21 group components)**

## CSR Layering & Visual Coding

Each component group is color-coded by its CSR layer:

| Color | Layer | Groups |
|-------|-------|--------|
| Blue | **Controller** | CLI Group, API Group |
| Orange | **Service** | Agent Group, Router Group, Provider Group, Safety Group, Context Graph Group, Edit Strategy Group, Evaluation Group |
| Green | **Repository** | Session Group, Tool Group, Memory Group, Config Group, Git Group, Repo Intelligence Group |
| Purple | **Infrastructure** | MCP Group, Sandbox Group, Observability Group, Wire Log Group, Hooks Group, Plugins Group |

### CSR Pattern Flow

```
User → Controller (CLI/API) → Service (Agent/Router/Safety/...) → Repository (Session/Tool/Memory/...)
```

**Key delegation paths:**
- `AgentOrchestrator` → `SafetyCoordinator` (safety validation before every tool dispatch)
- `AgentOrchestrator` → `ErrorBoundary` (structured error handling with recovery)
- `AgentOrchestrator` → `ContextGraph` (context pipeline orchestration)
- `ServerRouter` → `AgentOrchestrator` (sole entry gate for all interface containers)

## Architecture Differentiators vs Reference Agents

### vs aider
- **CSR enforcement**: nasim strictly separates Controller → Service → Repository. aider mixes concerns.
- **SafetyCoordinator**: Dedicated safety pipeline with PermissionGate, InjectionScanner, EgressInspector. aider has ad-hoc safety checks.
- **ErrorBoundary**: Structured error hierarchy with recovery actions. aider uses generic try/except.

### vs Cline
- **No God Objects**: nasim decomposes functionality into 21 focused groups. Cline often has monolithic controllers.
- **ContextGraph**: Dedicated context pipeline with prioritization, truncation, distillation, injection, compaction. Cline uses simpler context management.
- **EditStrategyManager**: Polymorphic edit strategies (8 implementations) vs Cline's single approach.

### vs Claude Code
- **CSR visibility**: nasim's diagrams make the layering explicit through color coding and stereotypes.
- **SafetyCoordinator**: Proactive safety pipeline vs Claude Code's reactive approach.
- **Observability**: Dedicated StructuredLogger, MetricsCollector, TraceCorrelator with OTel support. Claude Code has minimal observability.

### vs Roo-Code
- **Container clarity**: nasim's 3-runtime-entry-point model (CLI, API Server, Core Engine) is cleaner than Roo-Code's architecture.
- **MCP integration**: nasim treats MCP as first-class with dedicated runtime, adapter, and discovery components.
- **Memory system**: nasim has 8 memory components (store, index, scope, adapters, retriever, indexer) vs Roo-Code's simpler approach.

## C4 Hierarchy

```
Context:   Person(User) → System(NASIM Application) → System_Ext(...)
Container: System_Boundary(nasim_application, "NASIM Application") {
               Container(cli_process, "CLI Process")
               Container(api_server, "HTTP API Server")
               Container(core_engine, "Core Engine")
           }
           Container_Ext(WebApp, DesktopApp, MobileApp) → Container(api_server)
Component: Boundary(nasim_application, "NASIM Application") {
               Boundary(cli_group) <<controller>> { ... }
               Boundary(api_group) <<controller>> { ... }
               Boundary(agent_group) <<service>> { ... }
               Boundary(router_group) <<service>> { ... }
               Boundary(safety_group) <<service>> { ... }
               Boundary(context_graph_group) <<service>> { ... }
               Boundary(edit_strategy_group) <<service>> { ... }
               Boundary(evaluation_group) <<service>> { ... }
               Boundary(session_group) <<repository>> { ... }
               Boundary(tool_group) <<repository>> { ... }
               Boundary(memory_group) <<repository>> { ... }
               Boundary(config_group) <<repository>> { ... }
               Boundary(git_group) <<repository>> { ... }
               Boundary(repo_intelligence_group) <<repository>> { ... }
               Boundary(mcp_group) <<infrastructure>> { ... }
               Boundary(sandbox_group) <<infrastructure>> { ... }
               Boundary(observability_group) <<infrastructure>> { ... }
               Boundary(wire_log_group) <<infrastructure>> { ... }
               Boundary(hooks_group) <<infrastructure>> { ... }
               Boundary(plugins_group) <<infrastructure>> { ... }
               Boundary(provider_group) <<service>> { ... }
           }
           Container_Ext(WebApp, DesktopApp, MobileApp) → ServerRouter
           Person(User) → REPLSession (CLI mode)
```

## Actors

| Actor | Description |
|-------|-------------|
| User | Human developer. Interacts via CLI (REPLSession) or via interface container apps (WebApp, DesktopApp, MobileApp → ServerRouter). |

## Key C4 Modeling Decisions

This section explains the C4 modeling choices that commonly confuse readers.

### Why CLI Process and HTTP API Server are modeled as separate Containers

NASIM Application runs as a **single Python process**. However, **CLI Process** and **HTTP API Server** are modeled as separate `Container` elements — not because they are separate deployments, but because they represent **distinct runtime entry points**.

In C4, a Container models either:
1. A separately deployable unit, OR
2. A distinct runtime responsibility with its own lifecycle

CLI Process and HTTP API Server fall into category 2. They share a process boundary but serve fundamentally different interaction models:
- **CLI Process**: Terminal REPL with argument parsing, rendering, and slash commands
- **HTTP API Server**: FastAPI server with HTTP endpoints and SSE streaming

Each has its own initialization sequence, request handling, and lifecycle management. Modeling them as separate Containers makes the architecture's entry points visible and allows readers to understand the two distinct ways users interact with NASIM Application.

### Why WebApp, DesktopApp, and MobileApp are modeled as Container_Ext

**WebApp** (JavaScript SPA), **DesktopApp** (Electron/Tauri), and **MobileApp** (React Native/Flutter) are modeled as `Container_Ext` because they are **genuinely separate deployable units** — each with its own process, codebase, and deployment pipeline.

These are **clients** of NASIM Application, not part of it. They communicate with NASIM Application over HTTP/SSE to the API Server. In C4:
- `Container` = inside the system boundary (NASIM Application owns it)
- `Container_Ext` = outside the system boundary but interacts with it

Since WebApp/DesktopApp/MobileApp are not developed, deployed, or versioned as part of NASIM Application, they correctly belong outside the boundary as `Container_Ext`.

### Container vs Component: When is something a Container?

A **Container** represents a unit with a distinct runtime responsibility — either a separate deployment or a separate entry point. A **Component** represents an internal module within a Container.

The **HTTP API Server** is a Container (not a Component) because:
- It is a distinct entry point with its own lifecycle
- It handles a fundamentally different interaction model (HTTP) than the CLI (terminal)
- It is not an internal module of the Core Engine — it *delegates to* the Core Engine

The **Core Engine** is a Container because it is the main application shell that contains all business logic components. Within it, components like `AgentOrchestrator`, `SafetyCoordinator`, and `ToolRegistry` are internal modules.

## Interface Containers (external, separate deployable units)

| Container | Type | Connection to NASIM Application |
|-----------|------|---------------------------------|
| WebApp | JavaScript SPA | HTTP/JSON + SSE to ServerRouter |
| DesktopApp | Electron / Tauri | HTTP/JSON + SSE to ServerRouter |
| MobileApp | React Native / Flutter | HTTP/JSON + SSE to ServerRouter |

These are separate deployable units that connect to NASIM Application's HTTP API Server. They are modeled as `Container_Ext` (outside the system boundary) because they are clients, not part of NASIM Application itself.

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| LLM Backend | HTTP/JSON | Multi-provider inference (Ollama, OpenAI, Anthropic, etc.) via litellm |
| Host Filesystem | path I/O | Read/write/search project files |
| Host Shell | subprocess | Execute shell commands (via sandbox) |
| Web | HTTP | Fetch documentation, search results |
| MCP Server | stdio/SSE | Extension tools via Model Context Protocol |
| MCP Client | stdio/SSE | External tools connecting to NASIM Application MCP server |
| Git Repository | git CLI | Version control for project files |
| Sandbox Runtime | OS primitives | OS-level process isolation (landlock, seccomp, bubblewrap) |
| Memory Backend | read/write | Long-term knowledge persistence |
| LSP Server | LSP protocol | Language server for code intelligence |
| Plugin Directory | filesystem | ~/.nasim/plugins/ — community extensions |
| Tree-sitter | tree-sitter CLI/lib | AST extraction for code intelligence |
| Embedding Model | HTTP/local | Vector embedding generation for semantic search |
| Vector Store | SQLite + vector | Embedding storage and similarity search |
| OTel Collector | OTLP/gRPC | OpenTelemetry trace and metric export (optional) |

## Architecture Principles

- **Single process:** NASIM Application runs as one Python process. CLI and HTTP API Server share the same process boundary but are modeled as separate Containers because they are distinct runtime entry points with different responsibilities (terminal REPL vs HTTP+SSE). This is a C4 modeling choice, not a deployment choice.
- **Container = runtime entry point OR separate deployment:** In C4, a Container does not always mean a separate process. It can also mean a distinct runtime responsibility within a shared process. CLI Process and HTTP API Server use this interpretation.
- **Container_Ext = separate deployable unit outside the system boundary:** WebApp, DesktopApp, and MobileApp are truly separate applications with their own processes. They are clients of NASIM Application, not part of it.
- **CSR Pattern:** Controller (CLI Group / API Group) → Service (Agent Group, Router Group, etc.) → Repository (Session Group, Tool Group, Memory Group, Config Group). Strict delegation.
- **One group, one Boundary:** Each component group is a `Boundary` inside `Boundary(nasim_application, "NASIM Application")`. Groups are logical, not deployable.
- **No Container_Ext for internals:** Cross-group references inside NASIM Application use `Component_Ext(alias, "ComponentName", "Group Name")`, never `Container_Ext` or `System_Ext`.
- **System_Ext for real externals only:** Filesystems, web, git repos, LLM backends, MCP servers, LSP servers — genuinely external infrastructure.
- **Version consistency:** All diagram headers use Version 9.0.0.
- **Pin C4-PlantUML:** All diagrams reference v2.10.0 — never `master`.

## Shared Styles

All diagrams include `common/c4_styles.puml` for:
- Consistent color palette per CSR layer
- Skinparam settings for readability
- Legend macro for CSR layer explanation

## Design Chain Consistency

All diagrams are traceable to the design chain:
- **C4** → **UC** (Use Case) → **SQ** (Sequence) → **SM** (State Machine)
- **Cross-layer sync verified:** All lifelines in SQ diagrams exist as C4 components.
- **100% design chain consistency** across 148 SQ diagrams and 24 C4 diagrams.

## SIM-01 Compliance (5–12 elements per diagram)

18 of 24 per-group component diagrams comply with SIM-01 (≤12 elements). Six diagrams are documented exceptions:

| Diagram | Elements | Exception Rationale |
|---------|----------|---------------------|
| `c4_nasim_component_overview.puml` | 40 | Intentional full-system overview map. Splitting defeats its purpose as a navigation aid. |
| `c4_nasim_container.puml` | 22 | Container-level view showing all external system integrations. Splitting would break the "system boundary" model. |
| `c4_nasim_component_tools.puml` | 24 | 16 tool implementations + 8 externals. All tools share the same ABC interface and registry — splitting obscures the polymorphic pattern. |
| `c4_nasim_component_observability.puml` | 17 | 8 internal components + 9 externals. Observability concerns are tightly coupled (logger ↔ metrics ↔ correlator ↔ propagator). |
| `c4_nasim_component_agent.puml` | 13 | 7 components + 6 externals. Core agent loop components are inseparable — orchestrator, history, compactor form a single processing pipeline. |
| `c4_nasim_component_edit_strategy.puml` | 13 | 11 strategy implementations + 2 externals. Polymorphic strategy pattern requires all implementations visible together. |

## SIM-03 Compliance (meaningful intent labels)

All `Rel()` lines use meaningful intent labels (what the relationship accomplishes), not protocol or technology names. Protocol information is placed in the optional technology slot.
