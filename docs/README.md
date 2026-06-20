# docs — Design Artifacts

Design chain artifacts for the nasim CLI code agent + HTTP API server.
All layers are frozen through SQ. Implementation roadmap (RDM) is active.

Back to [project root](../README.md).

## Design chain

```
C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code
```

nasim uses JSON file sessions (no relational database). CT/DATA covers the session
store data contract. CT/API covers the HTTP API server surface (OAS 3.1.0).
LLM providers are external dependencies.

Each layer must be authored in order. No layer may be authored before the one above it.

## Layer index

| Directory | Layer | Status | Contents |
| --------- | ----- | ------ | -------- |
| [C4/](c4/README.md) | C4 Architecture | Frozen | Context, container, 10 component diagrams (8 containers) |
| [UC/](uc/README.md) | Use Cases | Frozen | 66 UCs — 13 groups (CLI/AGT/PRV/CFG/SSN/SAF/CTX/LLM/TL/SRV/HK/PLG/RTG) |
| [SM/](sm/README.md) | State Machine | Frozen | Agent lifecycle — 12 states (process FSM, not entity lifecycle) |
| [SQ/](sq/README.md) | Sequence Diagrams | Frozen | 55 diagrams — one per UC, by group |
| [ER/](er/README.md) | ERD | Frozen | Session JSON Lines schema — logical store |
| [CL/](cl/README.md) | Class Diagram | Frozen | Runtime class model — providers, tools, orchestrator, config, session, server, hooks, plugins |
| [CT/DATA/](CT/DATA/README.md) | Data Contracts | Frozen | ODCS v3.1.0 — session store data contract |
| [CT/API/](CT/API/README.md) | HTTP API Surface | Frozen | OAS 3.1.0 + ROD — 7 endpoints, 4 resources |
| [RDM/](rdm/README.md) | Implementation Roadmap | Active | Milestone docs for coding |
| [MM/](mm/README.md) | Design Chain Maps | Frozen | Summary and detail chain overview diagrams |
| [audit/](audit/README.md) | Audit Reports | Active | Reference agent audits, gap analysis, CAR improvement plan |

## Quick Navigation

### C4 Architecture
- [Context](c4/c4_nasim_context.puml) — System boundary and external dependencies
- [Container](c4/c4_nasim_container.puml) — Deployable units and technology choices
- [Component Overview](c4/c4_nasim_component.puml) — Cross-container overview
- [Component: CLI](c4/c4_nasim_component_cli.puml) — CLI layer components
- [Component: Agent](c4/c4_nasim_component_agent.puml) — Agent layer components
- [Component: Provider](c4/c4_nim_component_provider.puml) — Provider layer components
- [Component: Tools](c4/c4_nasim_component_tools.puml) — Tool layer components
- [Component: Config](c4/c4_nasim_component_config.puml) — Config layer components
- [Component: Session](c4/c4_nasim_component_session.puml) — Session layer components
- [Component: Server](c4/c4_nasim_component_server.puml) — Server layer components (ROD-compliant)
- [Component Inventory](c4/README.md)

### Use Cases
- [CLI Interaction](uc/uc_cli.puml) — User I/O, slash commands, plan toggle, model switch
- [Agent Core](uc/uc_agent.puml) — Agentic loop, permissions, context, plans, hooks
- [Provider Layer](uc/uc_provider.puml) — Provider abstraction and LLM interaction
- [Configuration](uc/uc_config.puml) — Config loading and validation
- [Session Persistence](uc/uc_session.puml) — Save, load, list sessions
- [Safety](uc/uc_safety.puml) — Permission checks and user approval
- [Context Management](uc/uc_context.puml) — Token counting and compaction
- [Tool Layer](uc/uc_tools.puml) — All tool implementations
- [HTTP Server](uc/uc_server.puml) — REST API and SSE streaming
- [Hook System](uc/uc_hooks.puml) — Pre/post hooks for tool and LLM lifecycle
- [Plugin System](uc/uc_plugins.puml) — Plugin discovery and registration
- [Model Router](uc/uc_router.puml) — Model selection and fallback
- [UC Inventory](uc/README.md) — 55 UCs total

### State Machine
- [Agent Lifecycle](sm/sm_agent_lifecycle.puml) — 12 agent states including HOOK_RUNNING, ROUTING, SERVING
- [SM Inventory](sm/README.md)

### Sequence Diagrams
- [SQ Inventory](sq/README.md) — 55 SQ diagrams (1:1 with UCs)

### Class Diagram
- [Runtime Model](cl/cl_runtime_model.puml) — All runtime classes and relationships
- [CL Inventory](cl/README.md)

### Data Contracts (CT/DATA)
- [Session Store Contract](CT/DATA/nasim_session_store.datacontract.yaml) — ODCS v3.1.0 data contract
- [CT/DATA Inventory](CT/DATA/README.md)

### HTTP API Surface (CT/API)
- [OpenAPI Spec](CT/API/openapi.yaml) — OAS 3.1.0 — 7 endpoints, 4 resources
- [ROD Decisions](CT/API/rod_decisions.md) — Resource model, methods, field behavior, errors
- [CT/API Inventory](CT/API/README.md)

### Entity Registry
- [entities.md](entities.md) — Canonical names for all components, UCs, actors

### Implementation Roadmap
- [RDM Overview](rdm/README.md) — Principles, stack, milestones, CI gates

### Design Chain Maps
- [MM Overview](mm/README.md) — Meta-level navigation diagrams

### Audit Reports
- [Audit Overview](audit/README.md) — Reference agent audits, gap analysis, CAR plan
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
7. **Safety first** — `PermissionGate` with `ask | auto | off` modes. Unsafe tools prompt user before execution.
8. **Context compaction** — `ContextCompactor` summarizes old exchanges via secondary LLM call when token budget exceeded.
9. **Process FSM, not entity lifecycle** — SM states are transient agent states, not persisted entity lifecycle. SMT ownership rules from `sm.md` do not apply (documented deviation).
10. **CL covers runtime structure** — nasim has no business domain entities; CL diagrams document the runtime class model (documented deviation).
11. **HTTP API server** — Starlette ASGI app with RESTful routes + SSE streaming. Same agent core consumed by CLI and HTTP.
12. **Hook system** — Pre/post hooks for tool use and LLM calls. Command (bash) and prompt (LLM-driven) hook types.
13. **Plugin system** — Plugin manifests, dynamic tool/hook registration. Extension without core changes.
14. **Multi-interface** — One agent core serves CLI, HTTP API, and MCP server simultaneously.
15. **CSR compliance** — Controller (CLI/HTTP) → Service (Agent/Provider) → Repository (Tools/Config/Session) layered architecture.
16. **ROD compliance** — HTTP API follows Resource-Oriented Design: resources (Session, Message, Tool, Config), standard methods, custom methods (:send), AIP-193 errors.
