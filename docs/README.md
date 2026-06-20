# docs — Design Artifacts

Design chain artifacts for the nasim CLI code agent. All layers are frozen through SQ.
Implementation roadmap (RDM) is active.

Back to [project root](../README.md).

## Design chain

```
C4 → UC → SM → SQ → ERD → CL → Code
```

nasim uses JSON file sessions (no relational database). No CT/DATA or CT/API layers
are needed — nasim exposes no HTTP APIs. LLM providers are external dependencies.

Each layer must be authored in order. No layer may be authored before the one above it.

## Layer index

| Directory | Layer | Status | Contents |
| --------- | ----- | ------ | -------- |
| [C4/](c4/README.md) | C4 Architecture | Frozen | Context, container, 8 component diagrams (6 containers) |
| [UC/](uc/README.md) | Use Cases | Frozen | 42 UCs — 9 groups (CLI/AGT/PRV/CFG/SSN/SAF/CTX/LLM/TL) |
| [SM/](sm/README.md) | State Machine | Frozen | Agent lifecycle — 9 states (process FSM, not entity lifecycle) |
| [SQ/](sq/README.md) | Sequence Diagrams | Frozen | 42 diagrams — one per UC, by group |
| [ER/](er/README.md) | ERD | Frozen | Session JSON Lines schema — logical store |
| [CL/](cl/README.md) | Class Diagram | Frozen | Runtime class model — providers, tools, orchestrator, config, session |
| [RDM/](rdm/README.md) | Implementation Roadmap | Active | Milestone docs for coding |
| [MM/](mm/README.md) | Design Chain Maps | Frozen | Summary and detail chain overview diagrams |

## Quick Navigation

### C4 Architecture
- [Context](c4/c4_nasim_context.puml) — System boundary and external dependencies
- [Container](c4/c4_nasim_container.puml) — Deployable units and technology choices
- [Component Overview](c4/c4_nasim_component.puml) — Cross-container overview
- [Component: CLI](c4/c4_nasim_component_cli.puml) — CLI layer components
- [Component: Agent](c4/c4_nasim_component_agent.puml) — Agent layer components
- [Component: Provider](c4/c4_nasim_component_provider.puml) — Provider layer components
- [Component: Tools](c4/c4_nasim_component_tools.puml) — Tool layer components
- [Component: Config](c4/c4_nasim_component_config.puml) — Config layer components
- [Component: Session](c4/c4_nasim_component_session.puml) — Session layer components
- [Component Inventory](c4/README.md)

### Use Cases
- [CLI Interaction](uc/uc_cli.puml) — User I/O, slash commands, plan toggle
- [Agent Core](uc/uc_agent.puml) — Agentic loop, permissions, context, plans
- [Provider Layer](uc/uc_provider.puml) — Provider abstraction and LLM interaction
- [Configuration](uc/uc_config.puml) — Config loading and validation
- [Session Persistence](uc/uc_session.puml) — Save, load, list sessions
- [Safety](uc/uc_safety.puml) — Permission checks and user approval
- [Context Management](uc/uc_context.puml) — Token counting and compaction
- [Tool Layer](uc/uc_tools.puml) — All tool implementations
- [UC Inventory](uc/README.md) — 42 UCs total

### State Machine
- [Agent Lifecycle](sm/sm_agent_lifecycle.puml) — 9 agent states including COMPACTING, AWAITING_APPROVAL, PLANNING
- [SM Inventory](sm/README.md)

### Sequence Diagrams
- [SQ Inventory](sq/README.md) — 42 SQ diagrams (1:1 with UCs)

### Class Diagram
- [Runtime Model](cl/cl_runtime_model.puml) — All runtime classes and relationships
- [CL Inventory](cl/README.md)

### Entity Registry
- [entities.md](entities.md) — Canonical names for all components, UCs, actors

### Implementation Roadmap
- [RDM Overview](rdm/README.md) — Principles, stack, milestones, CI gates

### Design Chain Maps
- [MM Overview](mm/README.md) — Meta-level navigation diagrams

## Architecture Decisions

1. **Provider abstraction** — Protocol-based provider layer supporting Ollama, OpenAI, Anthropic. Factory pattern for instantiation.
2. **Tool ABC** — Instance-based tool registry with `safe` flag, structured `ToolResult`, dynamic registration for MCP.
3. **Event-driven agent** — AgentOrchestrator yields `AgentEvent` objects; CLI/renderer subscribes. No print() in agent core.
4. **Layered config** — Global YAML → project YAML → env vars → CLI flags. Typed `Config` dataclass.
5. **Session persistence** — JSON Lines files in `~/.nasim/sessions/<id>/`. `--continue` and `--session` flags.
6. **Safety first** — `PermissionGate` with `ask | auto | off` modes. Unsafe tools prompt user before execution.
7. **Context compaction** — `ContextCompactor` summarizes old exchanges via secondary LLM call when token budget exceeded.
8. **Process FSM, not entity lifecycle** — SM states are transient agent states, not persisted entity lifecycle. SMT ownership rules from `sm.md` do not apply (documented deviation).
9. **CL covers runtime structure** — nasim has no business domain entities; CL diagrams document the runtime class model (documented deviation).
10. **Async-ready** — httpx for provider calls; asyncio-compatible architecture for future web server mode.
