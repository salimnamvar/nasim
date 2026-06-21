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
| [C4/](C4/README.md) | C4 Architecture | Frozen | Context, container, 21 component diagrams (24 total) |
| [UC/](UC/README.md) | Use Cases | Frozen | 148 UCs — 21 groups (CLI/AGT/PRV/CFG/SSN/SAF/CTX/MCP/TL/SRV/HK/PLG/RTG/OBS/MEM/VCS/SBX/RIM/EDT/EVL/WRL) |
| [SM/](SM/README.md) | State Machine | Frozen | 4 diagrams — agent lifecycle (process FSM), session, plan, plugin lifecycles |
| [SQ/](SQ/README.md) | Sequence Diagrams | Frozen | 149 diagrams across 21 groups (Meta-Software Designer audit 2026-06-21) |
| [ER/](ER/README.md) | ERD | Frozen | 5 store schemas (session, memory, todo, wire log, observability, repo intelligence) |
| [CL/](CL/README.md) | Class Diagram | Frozen | Runtime class model — 90+ classes across 12 groups |
| [CT/DATA/](CT/DATA/README.md) | Data Contracts | Frozen | ODCS v3.1.0 — 5 contract diagrams + 2 YAML schemas |
| [CT/API/](CT/API/README.md) | HTTP API Surface | Frozen | OAS 3.1.0 + ROD — 23 endpoints, 8 resources |
| [RDM/](RDM/README.md) | Implementation Roadmap | Active | 10 milestone docs for coding |
| [MM/](MM/README.md) | Design Chain Maps | Frozen | Summary and detail chain overview diagrams |
| [audit/](audit/README.md) | Audit Reports | Active | 17 audit reports — reference agent audits, gap analysis, CAR improvement plan |
| [prompt/](prompt/) | Prompt Engineering | Reference | p1–p9.md design directives |
| [REF/](REF/) | Reference Data | Reference | agents.md reference agent list |

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
