# nasim — Design Chain (Project-Specific)

Extends `~/.claude/rules/software-design/design-chain.md` for nasim.

---

## nasim Design Chain

```
C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code
```

nasim is a code agent with CLI + HTTP + MCP interfaces. The design chain follows
the standard flow with these project-specific adaptations:

### Agent System Pattern

- Agent core yields typed event objects (TextChunk, ToolStart, ToolResult, Error, Done)
- No `print()` or direct I/O in the agent core
- CLI/renderer subscribes to events; HTTP server sends events as SSE
- The agent core is **UI-agnostic** — same core serves CLI, HTTP, and MCP

### Provider Abstraction

- `Provider` Protocol with `chat()`, `chat_stream()`, `model_name`
- **Universal proxy via litellm** — one library handles 100+ providers
- Model string prefix routes to provider: `anthropic/claude-sonnet-4-6`, `openai/gpt-4o`

### Tool System

- `Tool` ABC with `name`, `description`, `parameters`, `safe`, `execute()`
- `ToolRegistry` instance-based with dynamic registration (MCP)
- `ToolResult(success, content, error)` structured result
- Tools annotated with `safe: bool` for permission gating

### Multi-Interface Architecture

- C4 Container diagram shows CLI, HTTP Server, Core Library as separate Containers
- UC groups per interface: CLI, SRV, MCP
- Agent core UCs (AGT) are shared across interfaces
- Each interface has its own SQ diagrams; shared flows referenced via `ref`

### Safety-First Permission Model

- `PermissionGate` with `ask | auto | off` modes
- Unsafe tools prompt user before execution in `ask` mode
- Tool-level `safe: bool` annotation in registry

---

## Layer Ownership (nasim-specific)

| What changes | Layer that owns it |
|:---|:---|
| Component names, boundary definitions | C4 |
| Operation names, group membership, verb | UC |
| Lifecycle states, valid transitions | SM |
| Collaboration order, guards, failure paths | SQ |
| Physical schema (file-based, minimal) | ERD |
| Domain class names, attributes, relationships | CL |
| Field names, types, store-level constraints | CT/DATA |
| HTTP paths, methods, request/response schemas | CT/API |
| Implementation classes, adapters, services | Code |

---

## nasim-Specific Anti-Patterns

1. Do not hard-code Ollama URLs or model names in core logic
2. Do not put print()/input() inside the agent loop — use events + CLI renderer
3. Do not skip reading a file before edit_file
4. Do not implement new capabilities in PoC files without updating design docs first
5. Avoid god objects — keep Tool, Provider, PermissionGate, Config, SessionStore distinct
6. Do not call AgentOrchestrator → PermissionGate directly — use SafetyCoordinator
7. Do not inline shared flow detail in interface SQ diagrams — use `ref` frames
8. Do not write lifecycle_state outside the lifecycle-write UC group

---

## Source References

- C4 Model: https://c4model.com/
- PlantUML: https://plantuml.com/
- Google AIP (ROD): https://google.aip.dev/
- litellm: https://github.com/BerriAI/litellm
- Agent design patterns: aider, codex, opencode, gemini-cli, goose
