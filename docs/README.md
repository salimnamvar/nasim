# nasim — Design Documentation

## Design Chain

```
C4  →  UC  →  SM  →  SQ  →  ERD  →  CL  →  Code
```

nasim is a CLI tool with no persistent storage, so the chain terminates at CL
(no ERD/CT/DATA needed — no databases or structured stores).

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
- [AGT-01: Execute User Task](SQ/AGENT/sq_agt01_execute_user_task.puml) — Core loop
- [LLM-01: Call Ollama Chat](SQ/LLM/sq_llm01_call_ollama_chat.puml) — Sync LLM call
- [TL-01: Read File](SQ/TOOL/sq_tl01_read_file.puml) — File read tool

### Class Diagram
- [Domain Model](CL/cl_domain_model.puml) — Core classes and relationships

## Architecture Decisions

1. **No framework** — pure Python + requests. Minimal dependencies.
2. **Tool calling via Ollama native format** — uses `/api/chat` with `tools` parameter.
3. **Streaming support** — tokens displayed as they arrive for better UX.
4. **Max iteration guard** — agent stops after 20 tool-call rounds to prevent infinite loops.
5. **String-based tool results** — tools return strings, not structured objects. LLM parses results.
