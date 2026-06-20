# nasim — Design Documentation

## Design Chain

```
C4  →  UC  →  SM  →  SQ  →  CL  →  Code
```

nasim is a CLI tool with no persistent storage. The chain terminates at CL —
no ERD, CT/DATA, or CT/API layers are needed (no databases, no HTTP APIs
exposed by nasim itself). The Ollama server is an external dependency, not
a nasim API.

## Quick Navigation

### C4 Architecture
- [Context](C4/c4_nasim_context.puml) — System boundary and external dependencies
- [Container](C4/c4_nasim_container.puml) — Deployable units and technology choices
- [Component](C4/c4_nasim_component.puml) — Internal component structure
- [Component Inventory](C4/README.md)

### Use Cases
- [CLI Interaction](UC/uc_cli.puml) — User I/O and slash commands
- [Agent Core](UC/uc_agent.puml) — Agentic loop and tool invocation
- [UC Inventory](UC/README.md)

### State Machine
- [Agent Lifecycle](SM/sm_agent_lifecycle.puml) — Agent states during task execution
- [SM Inventory](SM/README.md)

### Sequence Diagrams
- [SQ Inventory](SQ/README.md) — All 15 SQ diagrams (1:1 with UCs)

### Class Diagram
- [Runtime Model](CL/cl_domain_model.puml) — Core classes and relationships
- [CL Inventory](CL/README.md)

## Architecture Decisions

1. **No framework** — pure Python + requests. Minimal dependencies.
2. **Tool calling via Ollama native format** — uses `/api/chat` with `tools` parameter.
3. **Streaming support** — tokens displayed as they arrive for better UX.
4. **Max iteration guard** — agent stops after 20 tool-call rounds to prevent infinite loops.
5. **String-based tool results** — tools return strings, not structured objects. LLM parses results.
6. **Process FSM, not entity lifecycle** — SM states are transient agent states, not persisted entity lifecycle. SMT ownership rules from `sm.md` do not apply (documented deviation).
7. **CL covers runtime structure** — nasim has no business domain entities; CL diagrams document the runtime class model (documented deviation).
