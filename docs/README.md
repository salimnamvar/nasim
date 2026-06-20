# docs — Design Artifacts

Design chain artifacts for the nasim CLI code agent + HTTP API server + MCP server.

Back to [project root](../README.md).

## Design chain

```
C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code
```

nasim uses JSON file sessions (no relational database). CT/DATA covers session,
memory, and todo store data contracts. CT/API covers the HTTP API server surface
(OAS 3.1.0). LLM providers are external dependencies.

Each layer must be authored in order. No layer may be authored before the one above it.

## Layer index

| Directory | Layer | Status | Contents |
| --------- | ----- | ------ | -------- |
| [C4/](c4/README.md) | C4 Architecture | Frozen | Context, container, 15 component diagrams (15 containers) |
| [UC/](uc/README.md) | Use Cases | Frozen | 109 UCs — 17 groups (CLI/AGT/PRV/CFG/SSN/SAF/CTX/LLM/TL/SRV/HK/PLG/RTG/OBS/MEM/VCS/SBX) |
| [SM/](sm/README.md) | State Machine | Frozen | Agent lifecycle — 20 states (process FSM, not entity lifecycle) |
| [SQ/](sq/README.md) | Sequence Diagrams | Frozen | 55 diagrams — one per UC, by group |
| [ER/](er/README.md) | ERD | Frozen | Session, memory, todo JSON Lines schemas — logical stores |
| [CL/](cl/README.md) | Class Diagram | Frozen | Runtime class model — 90+ classes, providers, tools, orchestrator, config, session, server, hooks, plugins, sandbox, observability, memory, git |
| [CT/DATA/](CT/DATA/README.md) | Data Contracts | Frozen | ODCS v3.1.0 — session, memory, todo store data contracts |
| [CT/API/](CT/API/README.md) | HTTP API Surface | Frozen | OAS 3.1.0 + ROD — 23 endpoints, 8 resources |
| [RDM/](rdm/README.md) | Implementation Roadmap | Active | Milestone docs for coding |
| [MM/](mm/README.md) | Design Chain Maps | Frozen | Summary and detail chain overview diagrams |
| [audit/](audit/README.md) | Audit Reports | Active | Reference agent audits, gap analysis, CAR improvement plan |

## Quick Navigation

### C4 Architecture
- [Context](c4/c4_nasim_context.puml) — System boundary and external dependencies (11 external systems)
- [Container](c4/c4_nasim_container.puml) — Deployable units and technology choices (15 containers)
- [Component Overview](c4/c4_nasim_component.puml) — Cross-container overview
- [Component: CLI](c4/c4_nasim_component_cli.puml) — CLI layer components
- [Component: Agent](c4/c4_nasim_component_agent.puml) — Agent layer components (11 components)
- [Component: Provider](c4/c4_nasim_component_provider.puml) — Provider layer components (8 components)
- [Component: Tools](c4/c4_nasim_component_tools.puml) — Tool layer components (19 components)
- [Component: Config](c4/c4_nasim_component_config.puml) — Config layer components
- [Component: Session](c4/c4_nasim_component_session.puml) — Session layer components (5 components)
- [Component: Server](c4/c4_nasim_component_server.puml) — Server layer components (ROD-compliant)
- [Component: Sandbox](c4/c4_nasim_component_sandbox.puml) — Sandbox layer components
- [Component: Observability](c4/c4_nasim_component_observability.puml) — Observability layer components
- [Component: Memory](c4/c4_nasim_component_memory.puml) — Memory layer components
- [Component: Git](c4/c4_nasim_component_git.puml) — Git integration layer components
- [Component Inventory](c4/README.md)

### Use Cases
- [CLI Interaction](uc/uc_cli.puml) — User I/O, slash commands, plan toggle, model switch
- [Agent Core](uc/uc_agent.puml) — Agentic loop, permissions, context, plans, hooks, subagents
- [Provider Layer](uc/uc_provider.puml) — Provider abstraction and LLM interaction
- [Configuration](uc/uc_config.puml) — Config loading and validation
- [Session Persistence](uc/uc_session.puml) — Save, load, list, snapshot, search, fork sessions
- [Safety](uc/uc_safety.puml) — Permission checks, user approval, sandbox
- [Context Management](uc/uc_context.puml) — Token counting and compaction
- [Tool Layer](uc/uc_tools.puml) — All tool implementations (19 tools)
- [HTTP Server](uc/uc_server.puml) — REST API and SSE streaming
- [Hook System](uc/uc_hooks.puml) — Pre/post hooks for tool and LLM lifecycle
- [Plugin System](uc/uc_plugins.puml) — Plugin discovery and registration
- [Model Router](uc/uc_router.puml) — Model selection and fallback
- [Observability](uc/uc_observability.puml) — Logging, metrics, traces
- [Memory](uc/uc_memory.puml) — Cross-session knowledge
- [Git Integration](uc/uc_git.puml) — Version control awareness
- [Sandbox](uc/uc_sandbox.puml) — OS-level process isolation
- [UC Inventory](uc/README.md) — 109 UCs total

### State Machine
- [Agent Lifecycle](sm/sm_agent_lifecycle.puml) — 20 agent states including subagent, sandbox, memory, git states
- [SM Inventory](sm/README.md)

### Sequence Diagrams
- [SQ Inventory](sq/README.md) — 55 SQ diagrams (1:1 with UCs)

### Class Diagram
- [Runtime Model](cl/cl_runtime_model.puml) — All runtime classes and relationships (90+ classes)
- [CL Inventory](cl/README.md)

### Data Contracts (CT/DATA)
- [Session Store Contract](CT/DATA/nasim_session_store.datacontract.yaml) — ODCS v3.1.0
- [Memory Store Contract](CT/DATA/nasim_memory_store.datacontract.yaml) — ODCS v3.1.0
- [Todo Store Contract](CT/DATA/nasim_todo_store.datacontract.yaml) — ODCS v3.1.0
- [CT/DATA Inventory](CT/DATA/README.md)

### HTTP API Surface (CT/API)
- [OpenAPI Spec](CT/API/openapi.yaml) — OAS 3.1.0 — 23 endpoints, 8 resources
- [ROD Decisions](CT/API/rod_decisions.md) — Resource model, methods, field behavior, errors
- [CT/API Inventory](CT/API/README.md)

### Entity Registry
- [entities.md](entities.md) — Canonical names for all components, UCs, actors (17 UC groups)

### Implementation Roadmap
- [RDM Overview](rdm/README.md) — Principles, stack, milestones, CI gates

### Design Chain Maps
- [MM Overview](mm/README.md) — Meta-level navigation diagrams

### Audit Reports
- [Audit Overview](audit/README.md) — Reference agent audits, gap analysis, CAR plan
- [Comprehensive Reference Audit](audit/audit.2026.06.20.comprehensive.reference.audit.md) — MASTER: 28 agents, C4 gap analysis, enhancement roadmap
- [Reference Agents Deep Dive](audit/reference-agents-deep-dive.md) — All 27 agents analyzed
- [Gap Analysis](audit/nasim-gap-analysis.md) — Design principles compliance + gaps
- [CAR Improvement Plan](audit/nasim-car-improvement-plan.md) — 18 improvement items
- [Design Principles Comparison](audit/design-principles-comparison.md) — Design comparison
- [CSR + ROD Audit](audit/audit.2026.06.20.car-framework-csr-rod.md) — Controller-Service-Repository + Resource-Oriented Design audit

## Architecture Decisions

1. **Provider abstraction** — Protocol-based provider layer supporting Ollama, OpenAI, Anthropic. Factory pattern for instantiation.
2. **Model routing** — Composite strategy for model selection: classify task → select model → fallback chain.
3. **Tool ABC** — Instance-based tool registry with `safe` flag, structured `ToolResult`, dynamic registration for MCP.
4. **Event-driven agent** — AgentOrchestrator yields `AgentEvent` objects; CLI/renderer subscribes. No print() in agent core.
5. **Layered config** — Global YAML → project YAML → env vars → CLI flags. Typed `Config` dataclass.
6. **Session persistence** — JSON Lines files in `~/.nasim/sessions/<id>/`. `--continue` and `--session` flags.
7. **Safety first** — `PermissionGate` with `ask | auto | off` modes. `SafetyPipeline` with multi-stage checks. `SandboxExecutor` for OS-level isolation.
8. **Context compaction** — `ContextCompactor` summarizes old exchanges via secondary LLM call when token budget exceeded.
9. **Process FSM, not entity lifecycle** — SM states are transient agent states, not persisted entity lifecycle.
10. **CL covers runtime structure** — nasim has no business domain entities; CL diagrams document the runtime class model.
11. **HTTP API server** — FastAPI ASGI app with RESTful routes + SSE streaming. Same agent core consumed by CLI and HTTP.
12. **Hook system** — Pre/post hooks for tool use and LLM calls. Command (bash) and prompt (LLM-driven) hook types.
13. **Plugin system** — Plugin manifests, dynamic tool/hook registration. Extension without core changes.
14. **Multi-interface** — One agent core serves CLI, HTTP API, and MCP server simultaneously.
15. **CSR compliance** — Controller (CLI/HTTP) → Service (Agent/Provider) → Repository (Tools/Config/Session) layered architecture.
16. **ROD compliance** — HTTP API follows Resource-Oriented Design: 8 resources, standard methods, custom methods, AIP-193 errors.
17. **Subagent orchestration** — `SubagentManager` with nesting limit of 5. `TaskDispatcher` for role-based delegation.
18. **Sandbox security** — `SandboxExecutor` with OS-level isolation (landlock, seccomp, bubblewrap). `SandboxPolicy` for rules.
19. **Observability** — `StructuredLogger` with trace correlation. `MetricsCollector` for token/latency metrics.
20. **Memory persistence** — `MemoryStore` with FTS5 search. Scope isolation: global, project, session.
21. **Git integration** — `GitIntegration` with auto-commit, branch awareness, diff tracking.
