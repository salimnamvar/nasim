# nasim — p1.md Corrective Architecture Review

**Date:** 2026-06-20
**Directive:** docs/prompt/p1.md — Master Architecture Correction (10/10 Mode)
**Scope:** Full C4 architecture normalization

---

## Problem Report

### Critical Violations (5 found, 5 fixed)

| ID | Violation | Fix |
|----|-----------|-----|
| C1 | AgentOrchestrator God Object — 15 direct dependencies | Split into SafetyCoordinator, SubagentCoordinator, PersonaManager. Orchestrator delegates to coordinators. |
| C2 | MCP not first-class — hidden inside Tool Layer | Created MCP Group with MCPClientRuntime, MCPServerRuntime, MCPToolAdapter, MCPDiscovery |
| C3 | 9 non-deployable containers (ModelRouter, Config, Session, Hooks, Plugins, Subagent, Observability, Memory, Git) | Reduced to 3 deployable units: CLI, HTTP Server, Core Library. All others are component groups within Core Library. |
| C4 | 3 containers missing component diagrams (Hook System, Plugin System, Subagent) | Created c4_nasim_component_hooks.puml, c4_nasim_component_plugins.puml, c4_nasim_component_subagent.puml |
| C5 | 16 orphan components missing from cross-container overview | All components now present in c4_nasim_component.puml overview |

### Major Violations (10 found, 10 fixed)

| ID | Violation | Fix |
|----|-----------|-----|
| M1 | Components incorrectly modeled as containers | Reclassified as component groups within Core Library |
| M2 | Cross-container overview used Container_Boundary for components | Changed to System_Boundary for component groups |
| M3 | System_Ext used for internal containers in Agentcli/Server diagrams | Replaced with Container_Ext for all internal references |
| M4 | Duplicate memory access from Agent and Tool layers | Memory access consolidated through MemoryTool via ToolRegistry |
| M5 | SafetyPipeline subsumes PermissionGate — both called separately | Merged into SafetyCoordinator (composes PermissionGate internally) |
| M6 | SubagentManager + SubagentTool duplicate spawning | SubagentTool delegates to SubagentCoordinator (single ownership) |
| M7 | ModelRouter dual identity (container? component?) | Resolved: component within Provider Group |
| M8 | Hooks/Plugins containers had no component diagrams | Created dedicated component diagrams |
| M9 | Config naming inconsistency (Config vs Config Layer) | Standardized to "Config Group" everywhere |
| M10 | SAF/CTX UC groups without corresponding containers | Mapped to SafetyCoordinator and ContextCompactor within Agent Group |

### Minor Violations (7 found, 5 fixed)

| ID | Violation | Fix |
|----|-----------|-----|
| m1 | Implementation leakage (Python file paths in diagrams) | Removed file paths from component diagrams |
| m2 | Version inconsistencies (1.0.0 vs 4.0.0) | Standardized all to 5.0.0 |
| m3 | Config diagram different source reference | Updated to comprehensive.reference.audit.md |
| m4 | Overview title "(cross-container)" unclear intent | Renamed to "Component Overview" |
| m5 | ToolResult modeled as component (data type) | Kept — it has behavior (success/content/error) |
| m6 | Session model as component (data type) | Kept — it defines the session contract |
| m7 | Inconsistent annotation style (file paths vs empty) | Removed file paths from all diagrams |

---

## Corrected Target Architecture

### System Context (3 actors, 12 external systems)

```
Developer ──→ nasim ←── HTTP Client
nasim ──→ LLM Backend, Host FS, Host Shell, Web, MCP Server, MCP Client,
          Git Repo, Sandbox, Memory Backend, LSP Server, Plugin Dir
```

### Container Model (3 deployable units)

```
┌─────────────────────────────────────────────────┐
│                    nasim                         │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │    CLI    │  │  HTTP    │  │ Core Library  │ │
│  │  (click)  │  │  Server  │  │  (Python)     │ │
│  │           │  │ (FastAPI) │  │               │ │
│  └─────┬─────┘  └────┬─────┘  └───────┬───────┘ │
│        │              │                │         │
│        └──────────────┼────────────────┘         │
│                       │                          │
│              ┌────────┴────────┐                 │
│              │  Core Library   │                 │
│              │                 │                 │
│  ┌───────────┼─────────────────┼───────────────┐ │
│  │ Agent     │ Provider        │ Tool          │ │
│  │ Group     │ Group           │ Group         │ │
│  ├───────────┼─────────────────┼───────────────┤ │
│  │ MCP       │ Config          │ Session       │ │
│  │ Group     │ Group           │ Group         │ │
│  ├───────────┼─────────────────┼───────────────┤ │
│  │ Hooks     │ Plugins         │ Sandbox       │ │
│  │ Group     │ Group           │ Group         │ │
│  ├───────────┼─────────────────┼───────────────┤ │
│  │Observab.  │ Memory          │ Git           │ │
│  │ Group     │ Group           │ Group         │ │
│  └───────────┴─────────────────┴───────────────┘ │
└─────────────────────────────────────────────────┘
```

### Responsibility Map

| Capability | Owner Group | Internal Components |
|-----------|------------|-------------------|
| LLM orchestration | Agent Group | AgentOrchestrator, ConversationHistory, ContextCompactor, PlanSession, AgentEvent, ErrorBoundary |
| Safety pipeline | Agent Group | SafetyCoordinator (composes PermissionGate, injection scanner, egress inspector) |
| Subagent orchestration | Agent Group | SubagentCoordinator (nesting limit 5, result aggregation) |
| Persona switching | Agent Group | PersonaManager |
| LLM inference | Provider Group | Provider (Protocol), ProviderFactory, OllamaProvider, OpenAIProvider, AnthropicProvider |
| Model routing | Provider Group | ModelRouter, ProviderCapabilities, FallbackChain |
| Tool execution | Tool Group | Tool (ABC), ToolRegistry, FileTools, SearchTools, ShellTool, DirTool, WebTools, GitTool, LspTool, SubagentTool, TodoTool, MemoryTool, PlanTool |
| MCP client | MCP Group | MCPClientRuntime, MCPDiscovery, MCPToolAdapter |
| MCP server | MCP Group | MCPServerRuntime |
| Configuration | Config Group | ConfigLoader, Config |
| Session persistence | Session Group | SessionStore, Session, SessionVersioning, SessionSearch, SessionFork |
| Hook system | Hooks Group | HookManager, Hook, HookResult |
| Plugin system | Plugins Group | PluginLoader, PluginManifest |
| Sandbox isolation | Sandbox Group | SandboxExecutor, SandboxPolicy, SandboxMonitor |
| Observability | Observability Group | StructuredLogger, MetricsCollector, TraceCorrelator |
| Knowledge persistence | Memory Group | MemoryStore, MemoryIndex, MemoryScope |
| Version control | Git Group | GitIntegration, GitStatus, GitCommit |

---

## Architecture Constitution (p1.md §4)

### Container Qualifications

A C4 Container in nasim must be:
1. A separately deployable or runnable unit (process, binary, or independent application)
2. Communicable with via a network protocol (HTTP, stdio, SSE) or direct library call
3. Independently scalable or replaceable

**nasim has exactly 3 containers:** CLI (Python click process), HTTP API Server (FastAPI ASGI process), Core Library (Python package imported by both).

### Component Qualifications

A C4 Component in nasim must:
1. Be a unit of functionality within a container
2. Have a single, well-defined responsibility
3. Be replaceable without affecting other components in the same group
4. Belong to exactly one group (Agent, Provider, Tool, MCP, Config, Session, Hooks, Plugins, Sandbox, Observability, Memory, Git)

### What Must Never Be Mixed

- **Orchestration** (Agent Group) must not contain **inference logic** (Provider Group)
- **Tool execution** (Tool Group) must not contain **safety decisions** (Agent Group → SafetyCoordinator)
- **Protocol handling** (MCP Group) must not contain **tool implementation** (Tool Group)
- **Configuration** (Config Group) must not contain **runtime state** (Session Group)
- **Persistence** (Session/Memory Group) must not contain **business logic** (Agent Group)
- **Cross-cutting concerns** (Hooks, Plugins, Observability) must not contain **domain logic**

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Container | PascalCase noun | `CLI`, `HTTP API Server`, `Core Library` |
| Component Group | PascalCase + "Group" | `Agent Group`, `Provider Group`, `Tool Group` |
| Component | PascalCase noun phrase | `AgentOrchestrator`, `SafetyCoordinator`, `MCPClientRuntime` |
| External System | PascalCase noun | `LLM Backend`, `Host Filesystem`, `MCP Server` |
| Relationship | verb + noun (lowercase) | `chat, stream`, `execute tools`, `persist knowledge` |

### Dependency Direction Rules

- **CLI → Core Library** (never reverse)
- **HTTP Server → Core Library** (never reverse)
- **Agent Group → Provider Group, Tool Group, Session Group, Memory Group** (orchestration delegates down)
- **Tool Group → Sandbox Group** (tool execution delegates to sandbox)
- **MCP Group → Tool Group** (MCP adapts tools into nasim format)
- **Hooks/Plugins Groups → Tool Group, Agent Group** (extension points, not dependencies)
- **No circular dependencies** between any groups
- **No group imports from CLI or HTTP Server** (Core Library is the single dependency)

---

## Files Modified

| File | Change |
|------|--------|
| docs/C4/c4_nasim_context.puml | Version 5.0.0, added 12 external systems |
| docs/C4/c4_nasim_container.puml | Reduced to 3 containers (CLI, Server, Core Library) |
| docs/C4/c4_nasim_component.puml | Cross-container overview with 12 component groups |
| docs/C4/c4_nasim_component_agent.puml | Split God Object: SafetyCoordinator, SubagentCoordinator, PersonaManager |
| docs/C4/c4_nasim_component_cli.puml | Fixed System_Ext abuse → Container_Ext |
| docs/C4/c4_nasim_component_server.puml | Fixed System_Ext abuse → Container_Ext |
| docs/C4/c4_nasim_component_provider.puml | ModelRouter resolved as component within Provider Group |
| docs/C4/c4_nasim_component_tools.puml | Fixed System_Ext abuse → Container_Ext for Sandbox |
| docs/C4/c4_nasim_component_config.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_session.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_sandbox.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_observability.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_memory.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_git.puml | Version standardized to 5.0.0 |
| docs/C4/c4_nasim_component_mcp.puml | NEW — MCP as first-class subsystem |
| docs/C4/c4_nasim_component_hooks.puml | NEW — Hook system components |
| docs/C4/c4_nasim_component_plugins.puml | NEW — Plugin system components |
| docs/C4/c4_nasim_component_subagent.puml | NEW — Subagent orchestration |
| docs/C4/README.md | Updated inventory, architecture principles |
| docs/ENTITIES.md | Renamed layers→groups, added MCP Group, merged duplicates |

---

## Verification

| Check | Status |
|-------|--------|
| All containers have component diagrams | ✓ (CLI, Server, Core Library × 12 groups) |
| No God Objects | ✓ (AgentOrchestrator delegates to coordinators) |
| MCP first-class | ✓ (ClientRuntime, ServerRuntime, ToolAdapter, DiscoveryLayer) |
| No System_Ext abuse | ✓ (Internal refs use Container_Ext) |
| No orphan components | ✓ (All components in overview) |
| No duplicate responsibilities | ✓ (SafetyCoordinator, SubagentCoordinator single ownership) |
| Single Responsibility per group | ✓ (12 groups, each with clear boundary) |
| No cross-layer logic leakage | ✓ (Dependency direction rules enforced) |
| Naming consistency | ✓ (PascalCase throughout, "Group" suffix) |
| Version consistency | ✓ (All diagrams at 5.0.0) |
