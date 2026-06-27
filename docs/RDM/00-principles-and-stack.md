# 00 — Principles & Tech Stack

Back to [docs/rdm/](./README.md).

**Status:** Active · **Scope:** Implementation rules that apply to every milestone.

---

## Non-Negotiables

1. **Design-chain traceability.** Every class, method, and test traces to a C4 component +
   UC ID + SQ diagram. No orphan logic. SQ diagrams are the spec for call order, guards,
   alt paths, and rollback.
2. **Layered architecture.** CLI → Agent → Provider/Tools/Config/Session. Each layer
   owns its concern. No circular dependencies. Agent core never imports CLI or rendering.
3. **Event-driven agent.** AgentOrchestrator yields `AgentEvent` objects. CLI/renderer
   subscribes. No `print()` in agent core. No direct user I/O from agent layer.
4. **C4 fidelity.** Implement exactly the components in `docs/c4/c4_nasim_component*.puml`.
   Public class names follow C4 (`AgentOrchestrator`, `ConversationHistory`, ...).
5. **Safety-first permission model.** `PermissionGate` with `ask | auto | off` modes.
   Unsafe tools always prompt in `ask` mode. No bypass without explicit user approval.

## Implementation Standards (Apply Immediately — No Postponement)

All code written in any milestone **must** follow these without deferral:

- **Type hints**: Full type annotations on all public methods. `mypy --strict` clean.
- **Dataclasses / Protocol**: Use `dataclasses` for data carriers, `Protocol` for interfaces.
  ABC only when inheritance is needed (Tool base class).
- **Structured errors**: Domain exceptions raised in agent/tools, translated in CLI layer.
  No bare `Exception` catches. No `sys.exit()` in library code.
- **Event system**: `AgentEvent` hierarchy (TextChunk, ToolStart, ToolResult, Error, Done).
  CLI subscribes via generator protocol.
- **Config layering**: Global YAML → project YAML → env vars → CLI flags. Typed `Config`
  dataclass with validation. `NASIM_*` env prefix.
- **Session persistence**: JSON Lines in `~/.nasim/sessions/<id>/`. Atomic writes.
  `--continue` and `--session` flags.
- **Static analysis & quality**: `mypy --strict`, `ruff`, `black` (120) clean on every change.
  Code is written to the highest standard from the first line.

---

## Tech Stack (Locked)

| Concern | Choice | Notes |
| --- | --- | --- |
| Language | Python 3.11+ | Modern typing, `match` statement, `asyncio` |
| CLI framework | `click` + `rich` | Structured CLI, rich terminal output |
| LLM providers | `httpx` (sync) | Async-ready for web server mode |
| Config | `pydantic` + `pydantic-settings` | Typed config with validation |
| Session storage | JSON Lines (`pathlib` + `json`) | No database required |
| Testing | `pytest` + `pytest-asyncio` + `httpx` TestClient | Layered: agent/toolcli |
| Lint/Format | `ruff` · `black`(120) · `mypy --strict` | Configured in `pyproject.toml` |
| MCP | `mcp` SDK | Extension tools via Model Context Protocol |
| Context compaction | Secondary LLM call | Summarize old exchanges when budget exceeded |

---

## References

- Design chain: `docs/c4/`, `docs/uc/`, `docs/sm/`, `docs/sq/`, `docs/er/`, `docs/cl/`
- Project rules: `.claude/rules/`, `.grok/rules/`
- Global rules: `~/.claude/rules/software-design/`
