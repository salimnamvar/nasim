# nasim — Gap Analysis vs Reference Agents & Design Principles

**Date:** 2026-06-20
**Scope:** nasim v0.1 source vs all 27 reference agents; design principles compliance
**Purpose:** Identify every gap and violation to produce the CAR improvement plan

---

## 1. Design Principles Compliance

### 1.1 OOP / Object-Oriented Design

| Principle | nasim v0.1 Status | Reference Agent Best Practice |
|-----------|------------------|------------------------------|
| **Abstraction** | No interfaces/protocols. `Agent` takes concrete `OllamaClient`. | codex: `ModelProvider` trait, `ThreadStore` trait, `ToolExecutor` trait. All behind `Arc<dyn T>`. |
| **Encapsulation** | Global mutable `TOOL_REGISTRY` dict. Agent holds messages + renders. | opencode: `Tool.make()` encapsulates I/O schema. `ToolRegistry` is instance-owned. |
| **Inheritance/Composition** | No ABC, no Protocol, no composition. | aider: 14 `Coder` subclasses via Strategy pattern. opencode: `Tool.make()` with Effect Schema. |
| **Polymorphism** | None. Single provider, single tool set. | codex: trait-object polymorphism. opencode: Effect-TS algebraic effects. |
| **SRP violation** | `Agent` owns: conversation + orchestration + rendering. 3 responsibilities. | opencode: Separate `AgentOrchestrator`, `SessionProjector`, `Renderer`. |

**Verdict:** nasim has zero OOP structure. Every class violates at least one SOLID principle.

### 1.2 DRY (Don't Repeat Yourself)

| Violation | Location | Reference Fix |
|-----------|----------|---------------|
| `run()` and `run_streaming()` duplicate ~80 LOC of loop logic | `agent.py:31-58` vs `agent.py:60-105` | opencode: single `_run_turn()` with renderer callback |
| `tool_calls_buf` accumulation duplicated | `llm.py:68-103` + `agent.py:67-74` | opencode: LLM yields complete `ToolCall` objects, agent consumes directly |
| Error strings `f"Error: ..."` repeated across all tools | `tools.py:44-50`, each tool handler | codex: `ToolResult(success, content, error)` structured result |

**Verdict:** 3 DRY violations in 450 LOC. Ratio: 1 violation per 150 lines.

### 1.3 Separation of Concerns (SoC)

| Concern | nasim Implementation | Correct Pattern | Best Reference |
|---------|---------------------|-----------------|----------------|
| **Rendering** | `agent.py` calls `print()` 8 times | Agent yields events; CLI renders | opencode: Agent emits `AgentEvent`, TUI subscribes |
| **Conversation state** | `self.messages` in `Agent` class | Separate `ConversationHistory` class | aider: `ChatHistory` with cur/done split |
| **Tool dispatch** | `execute_tool()` free function | `ToolRegistry` instance method | opencode: `ToolRegistry.execute()` |
| **Configuration** | CLI args + hardcoded defaults | Layered config: global → project → env → CLI | aider: 4-layer configargparse |
| **Safety** | None. `shell_exec` runs anything. | `PermissionGate` per tool | codex: exec policy + sandbox |

**Verdict:** 5 SoC violations. Agent mixes orchestration, state, and rendering.

### 1.4 Composition

| Violation | Correct Pattern |
|-----------|-----------------|
| `Agent.__init__` takes `OllamaClient` (concrete) | `Agent.__init__` takes `Provider` (Protocol) + `ToolRegistry` (instance) |
| No `Tool` ABC. Tools are free functions with decorator registration. | `Tool` ABC with `execute(**args) → ToolResult`. Instance-based registration. |
| No `Config` dataclass. | `Config` as typed dataclass from `pydantic-settings`. |

### 1.5 Separation of Concerns (Detailed)

```
CURRENT nasim:                    CORRECT nasim:
┌─────────────────────┐          ┌──────────────┐
│ Agent                │          │ CLI Layer     │
│  ├─ messages (state) │          │  ├─ ArgParser │
│  ├─ LLM loop (orch)  │          │  ├─ Renderer  │
│  ├─ tool dispatch    │          │  ├─ Commands  │
│  └─ print() (render) │          │  └─ REPL      │
├─────────────────────┤          ├──────────────┤
│ OllamaClient (LLM)  │          │ Agent Layer   │
│  └─ chat, stream     │          │  ├─ Orchestrator│
├─────────────────────┤          │  ├─ History    │
│ tools (5 functions)  │          │  ├─ Compactor  │
│  └─ global registry  │          │  ├─ Permission │
└─────────────────────┘          │  └─ PlanSession│
                                 ├──────────────┤
                                 │ Provider Layer│
                                 │  ├─ Protocol   │
                                 │  ├─ Ollama     │
                                 │  └─ OpenAI     │
                                 ├──────────────┤
                                 │ Tool Layer    │
                                 │  ├─ ABC        │
                                 │  ├─ Registry   │
                                 │  ├─ FileTools  │
                                 │  ├─ SearchTools│
                                 │  ├─ WebTools   │
                                 │  └─ MCPAdapter │
                                 ├──────────────┤
                                 │ Config Layer  │
                                 │  ├─ Loader     │
                                 │  └─ Schema     │
                                 ├──────────────┤
                                 │ Session Layer │
                                 │  ├─ Store      │
                                 │  └─ Model      │
                                 └──────────────┘
```

### 1.6 Scalability

| Dimension | nasim v0.1 | Target | Reference |
|-----------|-----------|--------|-----------|
| **Providers** | 1 (Ollama) | N providers via Protocol | opencode: 13 providers |
| **Tools** | 5 (hardcoded) | Dynamic registry + MCP | gemini-CLI: 20+ built-in + MCP |
| **Interfaces** | CLI only | CLI + HTTP API + MCP server | opencode: TUI + web + desktop + server |
| **Config** | None | Layered YAML + env + CLI | aider: 4-layer config |
| **Sessions** | In-memory | Persistent JSON + resume | codex: SQLite-backed threads |
| **Context** | Unbounded | Token-budgeted + compaction | aider: background summarization |
| **Concurrency** | Synchronous | Async (httpx + asyncio) | opencode: Effect-TS |
| **Testing** | None | pytest + mypy + ruff | aider: pytest + coverage |

### 1.7 Modular Design

```
CURRENT: 4 modules (agent.py, CLI.py, llm.py, tools.py)
TARGET:  6 packages, 30+ modules (see entities.md Python Modules table)
```

The target package structure from `entities.md` is the correct modular decomposition.
No module in nasim currently implements its designed responsibility.

### 1.8 Controller-Service-Repository (CSR)

nasim's design chain `docs/software-design/csr.md` defines the CSR pattern.
Current nasim has:
- **Controller:** `CLI.py` (REPL + args + output) — mixed responsibilities
- **Service:** `agent.py` (orchestration + state + rendering) — SRP violation
- **Repository:** None (no persistence layer)

Target CSR mapping (from CL diagram):
- **Controller:** `CLI/` package (ArgParser, REPLSession, Renderer, SlashCommandHandler)
- **Service:** `agent/` package (AgentOrchestrator, ConversationHistory, ContextCompactor, PermissionGate)
- **Repository:** `session/` package (SessionStore, Session model)

### 1.9 Resource-Oriented Design (ROD)

nasim's `docs/software-design/rod.md` defines ROD for API design.
Current nasim exposes no API. The HTTP server mode (Phase 4) should follow ROD:
- Resources: `sessions`, `messages`, `tools`, `config`
- CRUD operations on each resource
- HTTP verbs mapped to operations
- Content negotiation via Accept headers

### 1.10 Open Data Specification / OpenAPI

nasim's `docs/software-design/odcs.md` and `openapi.md` define standards.
For the HTTP API mode:
- OpenAPI 3.1 spec describing all endpoints
- JSON Schema for request/response bodies
- Consistent error response format
- Versioned API (`/v1/`)

---

## 2. Capability Gaps vs Reference Agents

### Critical Gaps (must fix to be production-grade)

| Gap | nasim v0.1 | Best Reference | Impact |
|-----|-----------|---------------|--------|
| No provider abstraction | `OllamaClient` hardcoded | opencode: 13 providers | Locked to one backend |
| No search/grep/glob | `list_dir` only | gemini-CLI: ripgrep + glob + find | Can't navigate codebases |
| No web access | None | opencode: web_fetch + web_search | Can't look up docs/APIs |
| No config system | CLI args only | aider: 4-layer configargparse | Unusable in production |
| No context management | Unbounded messages | aider: ChatSummary background thread | Long sessions crash |
| No session persistence | In-memory RAM | codex: SQLite ThreadStore | Can't resume work |
| No safety/permissions | `shell_exec` runs anything | codex: OS sandbox + exec policy | Dangerous for real use |
| No event system | `print()` in agent | opencode: AgentEvent hierarchy | Can't swap UI |
| No logging | None | aider: structured logging | Can't debug |
| No async | Synchronous `requests` | opencode: Effect-TS async | Can't run web server |

### Major Gaps (important for parity)

| Gap | nasim v0.1 | Best Reference |
|-----|-----------|---------------|
| No rich output | Plain ASCII | aider: Rich library |
| No plan mode | None | opencode: dedicated plan agent |
| No MCP client | None | goose: extensions ARE MCP |
| No multi-provider models | Single model | aider: litellm (100+) |
| No git integration | None | aider: auto-commit + git aware |
| No structured errors | String errors | codex: `ToolResult(success, content, error)` |
| No context compaction | None | aider: `ChatSummary` |
| No background tasks | None | goose: scheduler |
| No plugin system | None | claude-code: marketplace |

### Design Principle Violations

| Principle | Violation | Severity |
|-----------|-----------|----------|
| OOP — Abstraction | No interfaces, concrete types everywhere | Critical |
| OOP — Encapsulation | Global mutable `TOOL_REGISTRY` | Critical |
| OOP — SRP | Agent mixes 3 responsibilities | Critical |
| DRY | 3 duplication violations in 450 LOC | High |
| SoC | Agent renders, manages state, orchestrates | Critical |
| Composition | No ABC, no Protocol, no dependency injection | Critical |
| Modular | 4 flat modules instead of 6 packages | High |
| Scalable | Synchronous, single-provider, no config | Critical |
| CSR | No separation of Controller/Service/Repository | High |
| ROD | No API (not yet designed) | Medium |

---

## 3. What nasim Does Well (Keep)

| Strength | Evidence |
|----------|----------|
| Clean tool registry pattern | `@tool` decorator is a good start (just needs ABC + instance) |
| Streaming support | `chat_stream()` works with tool call accumulation |
| Readable code | 450 LOC is well-organized for its size |
| Good `pyproject.toml` | Tooling config is correct (ruff, black, pyright, pytest) |
| Design chain exists | C4 → UC → SM → SQ → CL → Code chain is fully authored |
| Target architecture documented | `entities.md` has 30+ classes, full module map |
| Roadmap exists | 10 milestone docs with quality gates |
| Conventional commits | Git workflow is established |

---

## 4. Priority Matrix

| Priority | Items | Rationale |
|----------|-------|-----------|
| **P0 — Foundation** | Provider Protocol, Tool ABC, Config, Events, Logging | Every feature depends on these |
| **P1 — Core** | Search tools, Context mgmt, Session persistence, Safety, Rich UI | Minimum viable agent |
| **P2 — Advanced** | Plan mode, MCP, OpenAI/Anthropic providers, Git tools | Feature parity with top agents |
| **P3 — Differentiators** | HTTP API, Subagents, LSP, RAG, Multi-role | Competitive advantage |
