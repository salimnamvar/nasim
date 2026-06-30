# NASIM Application — C4 Diagram Inventory

## How to Read These Diagrams

The C4 model provides a hierarchical way to understand software architecture at different zoom levels. NASIM Application's diagram set follows this hierarchy:

```
Level 1: Context    →  c4_nasim_context.puml
Level 2: Container  →  c4_nasim_container.puml
Level 3: Component  →  c4_nasim_component_overview_core.puml (core groups)
                     →  c4_nasim_component_overview_infra.puml (infra groups)
                     →  c4_nasim_component_*.puml (per-group details)
```

### Reading Path

1. **Start with Context** (`c4_nasim_context.puml`): Understand what NASIM Application is and what external systems it interacts with.
2. **Move to Container** (`c4_nasim_container.puml`): See the 3 runtime entry points: CLI Process, HTTP API Server, and Core Engine. Note: NASIM Application runs as a single Python process — CLI and HTTP are modeled as separate Containers because they represent distinct runtime entry points and responsibilities.
3. **Explore Overview** (`c4_nasim_component_overview_core.puml` + `_infra.puml`): See all 21 component groups inside the Core Engine, color-coded by CSR layer.
4. **Dive into Details** (`c4_nasim_component_*.puml`): Each per-group diagram shows internal components, relationships, and external dependencies.

## C4 Diagram Set

### Level 1: System Context

| Diagram | Level | Version | Description |
|---------|-------|---------|-------------|
| `c4_nasim_context.puml` | Context | v9.1.5 | NASIM Application as a single system with User actor and 9 external systems |

### Level 2: Containers

| Diagram | Level | Version | Description |
|---------|-------|---------|-------------|
| `c4_nasim_container.puml` | Container | v10.0.1 | 4 internal containers (CLI Process, HTTP API Server, AgentController, Core Engine) + 4 external interface clients (WebApp, DesktopApp, MobileApp, MCP Client) + 13 external systems. All interfaces converge through AgentController before reaching Core Engine — no bypass paths. |

### Level 3: Components

| Diagram | Level | Description |
|---------|-------|-------------|
| `c4_nasim_component_overview_core.puml` | Component (Overview) | High-level view of core groups with CSR layer coloring and key cross-group relationships. **SIM-01 exception:** 40 elements — intentionally exceeds 12-element limit as a full-system overview map. |
| `c4_nasim_component_overview_infra.puml` | Component (Overview) | High-level view of infrastructure groups. Paired with `_core` for full-system visibility. |

## Per-Group Component Diagrams (21 diagrams)

Each per-group diagram shows internal components within `Container_Boundary(nasim_application, "NASIM Application")` and `Boundary(group_name)`. Cross-group references use `System_Ext(alias, "ComponentName", "Group Name")`.

### Controller Layer (Blue)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_cli.puml` | CLI Group | ArgParser, REPLSession, Renderer, SlashCommandHandler |

### Service Layer (Orange)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_agent.puml` | Agent Group | AgentOrchestrator, ConversationHistory, ContextCompactor, PlanSession, SubagentCoordinator, ErrorBoundary, PersonaManager |
| `c4_nasim_component_context_graph.puml` | Context Graph Group | ContextGraph, PipelineOrchestrator, ContextPrioritizer, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor |
| `c4_nasim_component_edit_strategy.puml` | Edit Strategy Group | EditStrategyManager, EditStrategy (ABC), SearchReplaceCoder, WholeFileCoder, UnifiedDiffCoder, FencedBlockCoder, FunctionLevelCoder, DiffSandboxCoder, ArchitectCoder, InlinePatchCoder, StrategySelector |

### Repository Layer (Green)

| Diagram | Group | Key Components |
|---------|-------|----------------|
| `c4_nasim_component_session.puml` | Session Group | SessionStore, SessionVersioning, SessionSearch, SessionFork |
| `c4_nasim_component_tools.puml` | Tool Group | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool, RepoMapTool, SemanticSearchTool, ReviewTool |
| `c4_nasim_component_config.puml` | Config Group | ConfigLoader, Config (dataclass) |

### Infrastructure Layer (Purple)

**Total: 10 C4 diagrams (1 context + 1 container + 1 overview + 7 group components)**

## CSR Layering & Visual Coding

Each component group is color-coded by its CSR layer:

| Color | Layer | Groups |
|-------|-------|--------|
| Blue | **Controller** | CLI Group (CLIAdapter), API Group (HTTPAdapter, MCPAdapter — in main component diagram) |
| Orange | **Service** | Agent Group, Safety Group, Context Graph Group, Edit Strategy Group |
| Green | **Repository** | Session Group, Tool Group, Config Group, WireLog Group |
| Purple | **Infrastructure** | (none — cross-cutting concerns implemented in code) |

### CSR Pattern Flow

```
User → Controller (CLI/API) → Service (Agent/Router/Safety/...) → Repository (Session/Tool/Memory/...)
```

**Key delegation paths:**
- `AgentOrchestrator` → `SafetyCoordinator` (safety validation before every tool dispatch)
- `AgentOrchestrator` → `ErrorBoundary` (structured error handling with recovery)
- `AgentOrchestrator` → `ContextGraph` (context pipeline orchestration)
- `ServerRouter` → `AgentOrchestrator` (sole entry gate for all interface containers)

## C4 Hierarchy

```
Context:   Person(User) → System(NASIM Application) → System_Ext(...)
Container: System_Boundary(nasim_application, "NASIM Application") {
               Container(cli_process, "CLI Process")
               Container(api_server, "HTTP API Server")
               Container(agent_controller, "AgentController")
               Container(core_engine, "Core Engine")
           }
           Container_Ext(WebApp, DesktopApp, MobileApp) → Container(api_server)
           Container_Ext(MCP Client) → Container(agent_controller)
           Container(cli_process, api_server, mcp_client) → Container(agent_controller) → Container(core_engine)
           System_Ext(LLM Backend, Host FS, Sandbox, Web, MCP Server,
                      Git Repo, Tree-sitter, LSP, Embedding, Vector Store,
                      Log Agent, Prometheus, Grafana) → Container(core_engine)
Component: Container_Boundary(nasim_application, "NASIM Application") {
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

### Context-level grouping for SIM-01 compliance

The System Context diagram (`c4_nasim_context.puml`) groups several external systems under composite names to stay within the 12-element limit (SIM-01):

| Context Name | Grouped Systems | Rationale |
|--------------|-----------------|-----------|
| Host Filesystem | Host FS + Plugin Directory | Plugins are accessed via filesystem reads at startup |
| Sandbox Runtime | Sandbox + Host Shell | Sandbox mediates all shell execution; shell is not a direct dependency |
| Repo Intelligence Backend | Tree-sitter + LSP Server + Embedding Model + Vector Store | All consumed by the Repo Intelligence subsystem (RIM) for code understanding |
| Observability Platform | Log agent + Prometheus + Grafana + OTel Collector | OTel is part of the platform's collection pipeline |

These groupings are **Context-level simplifications only**. The distinct responsibilities of each external system are visible in the corresponding Component diagrams (e.g., `RepoIntelligenceRepository` in the main component diagram shows Tree-sitter, Embedding Model, and Vector Store as separate `System_Ext` elements).

## Interface Containers (external, separate deployable units)

| Container | Type | Connection to NASIM Application |
|-----------|------|---------------------------------|
| WebApp | JavaScript SPA | HTTP/JSON + SSE to ServerRouter → AgentController |
| DesktopApp | Electron / Tauri | HTTP/JSON + SSE to ServerRouter → AgentController |
| MobileApp | React Native / Flutter | HTTPS + SSE to ServerRouter → AgentController |
| MCP Client | External tools / IDEs | stdio / SSE to AgentController |

WebApp, DesktopApp, and MobileApp are separate deployable units that connect to NASIM Application's HTTP API Server. They are modeled as `Container_Ext` (outside the system boundary) because they are clients, not part of NASIM Application itself.

MCP Client is a separate deployable unit that connects to AgentController via MCP protocol (stdio/SSE). All interfaces converge through AgentController before reaching Core Engine.

## External Systems

### Context Level (grouped)

| System | Purpose |
|--------|---------|
| LLM Backend | Multi-provider inference (Ollama, OpenAI, Anthropic, etc.) via litellm |
| Host Filesystem | Project source code, configuration, documentation, and community plugin files |
| Sandbox Runtime | OS-level process isolation and shell execution: landlock, seccomp, bubblewrap |
| Web | Documentation, search engines for live context retrieval |
| MCP Server | Extension tools provided to NASIM Application via Model Context Protocol |
| MCP Client | External tools and IDEs that consume NASIM Application's exposed capabilities via MCP |
| Git Repository | Version-controlled project files: branch state, history, and commits |
| Repo Intelligence Backend | Tree-sitter (AST parsing), LSP Server (code intelligence), Embedding Model (vector generation), Vector Store (similarity search) |
| Observability Platform | Log agent, Prometheus, Grafana, OTel Collector: NASIM Application emits; platform owns collection, storage, visualization |

### Container Level (ungrouped for precision)

| System | Purpose |
|--------|---------|
| LLM Backend | Multi-provider inference via litellm |
| Host Filesystem | Project source code, config, docs, plugin files |
| Sandbox Runtime | OS-level process isolation: landlock, seccomp, bubblewrap |
| Web | Documentation, package APIs, search engines |
| MCP Server | Extension tools provided via MCP protocol |
| Git Repository | Version-controlled project files |
| Tree-sitter | AST parsing for code understanding |
| LSP Server | Code intelligence: completions, diagnostics, references |
| Embedding Model | Vector generation for semantic search |
| Vector Store | Similarity search over code embeddings |
| Log Agent | Fluent Bit / Vector: tails stdout, parses, enriches, pushes to Loki |
| Prometheus | Pull-scrapes /metrics endpoint for time-series metrics |
| Grafana | Read-only visualization and alerting dashboard |

## Actor / Entry-Chain Approach

NASIM Application uses a **single-User API-First** model across all C4 and SQ diagrams.

### C4 Levels (Context + Container)

Both Context and Container diagrams use `Person(user, "User")` as the single human
actor. This is SE-05 (information hiding) — Level 1–2 show *what* the system interacts
with, not *how* the user connects.

### SQ Level (Sequence Diagrams)

All 148 SQ diagrams use `actor "User"` as the single entry. The API-First delegation
chain is:

```
User → [Interface Container] → HTTPAdapter/CLIAdapter/MCPAdapter → AgentController → Services
```

- **CLI flows:** `User → CLIAdapter → AgentController`. REPLSession and
  ArgParser are internal CLI Group components (visible in `c4_nasim_component_cli.puml`)
  but are not modeled as SQ lifelines because the CLI entry point is CLIAdapter.
  The CLI-to-API boundary is enforced by the CSR box structure in SQ diagrams, not
  by separate actor lifelines.
- **HTTP flows:** `User → HTTPAdapter → AgentController`. WebApp, DesktopApp,
  MobileApp are `Container_Ext` in C4 (separate deployable units) and route through
  ServerRouter.
- **MCP flows:** `User → MCPClientRuntime → CoreEngine`. MCPClientRuntime is the
  MCP entry point; it delegates to ServerRouter for business operations.

### Rationale

The single-User model was adopted (CAR-SQ-08, 2026-06-23) because:
1. All interfaces converge on `ServerRouter` — the API layer is the sole entry gate.
2. Interface-specific actors (`Developer`, `HTTPClient`) added visual noise without
   architectural value at SQ level.
3. The CSR box structure in SQ diagrams already distinguishes interface containers.

**Deviation from multi-interface pattern:** The `sq.md` multi-interface decomposition
originally specified interface-specific actors. This project deviates by collapsing to
a single `User` actor. The deviation is documented here and in `docs/SQ/README.md`
(API-First Convention section). REPLSession, ArgParser, and other CLI-specific
components are intentionally absent from SQ lifelines — they appear in C4 component
diagrams only.

## Architecture Principles

- **Single process:** NASIM Application runs as one Python process. CLI and HTTP API Server share the same process boundary but are modeled as separate Containers because they are distinct runtime entry points with different responsibilities (terminal REPL vs HTTP+SSE). This is a C4 modeling choice, not a deployment choice.
- **Container = runtime entry point OR separate deployment:** In C4, a Container does not always mean a separate process. It can also mean a distinct runtime responsibility within a shared process. CLI Process and HTTP API Server use this interpretation.
- **Container_Ext = separate deployable unit outside the system boundary:** WebApp, DesktopApp, MobileApp, and MCP Client are truly separate applications with their own processes. They are clients of NASIM Application, not part of it.
- **Single convergence point (AgentController):** All interface containers (CLI Process, HTTP API Server, MCP Client) delegate to AgentController, which routes requests to Core Engine. This makes the convergence visually explicit and enforceable for Sequence Diagrams.
- **CSR Pattern:** Controller (CLIAdapter, HTTPAdapter, MCPAdapter → AgentController) → Service (TaskService, ToolService, SessionService, etc.) → Repository (SessionRepository, MemoryRepository, WireLogRepository, etc.). Strict delegation.
- **One group, one Boundary:** Each component group is a `Boundary` inside `Container_Boundary(nasim_application, "NASIM Application")`. Groups are logical, not deployable.
- **System_Ext for cross-group references:** Cross-group references inside NASIM Application use `System_Ext(alias, "ComponentName", "Group Name")` as opaque references, never `Container_Ext`.
- **System_Ext for real externals only:** Filesystems, web, git repos, LLM backends, MCP servers, LSP servers — genuinely external infrastructure.
- **Version consistency:** Context diagram at v9.1.5, Container diagram at v10.0.1, Component diagrams at v18.0.0.
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

18 of 25 per-group component diagrams comply with SIM-01 (≤12 elements). Seven diagrams are documented exceptions:

| Diagram | Elements | Exception Rationale |
|---------|----------|---------------------|
| `c4_nasim_component_overview_core.puml` | 40 | Intentional full-system overview map (core groups). Splitting defeats its purpose as a navigation aid. |
| `c4_nasim_component_overview_infra.puml` | 25 | Infrastructure groups overview. Paired with `_core` for full-system visibility. |
| `c4_nasim_container.puml` | 22 | Container-level view showing all external system integrations and single convergence point (AgentController). Splitting would break the "system boundary" model. |
| `c4_nasim_component_tools.puml` | 24 | 16 tool implementations + 8 externals. All tools share the same ABC interface and registry — splitting obscures the polymorphic pattern. |
| `c4_nasim_component_agent.puml` | 13 | 7 components + 6 externals. Core agent loop components are inseparable — orchestrator, history, compactor form a single processing pipeline. |
| `c4_nasim_component_edit_strategy.puml` | 13 | 11 strategy implementations + 2 externals. Polymorphic strategy pattern requires all implementations visible together. |
| `c4_nasim_context.puml` | 11 | All architecturally significant external systems visible. Grouped: Plugin Dir → Host FS, Host Shell → Sandbox Runtime, Tree-sitter/LSP/Embedding/Vector → Repo Intelligence Backend, OTel → Observability Platform. |

## SIM-03 Compliance (meaningful intent labels)

All `Rel()` lines use meaningful intent labels (what the relationship accomplishes), not protocol or technology names. Protocol information is placed in the optional technology slot.
