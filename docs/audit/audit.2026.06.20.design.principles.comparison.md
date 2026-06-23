# nasim — Design Principles Comparison & Improvement Roadmap

**Date:** 2026-06-20
**Scope:** nasim design chain (docs/) vs reference agent best practices
**Purpose:** How nasim's documented design compares and how to improve it

---

## 1. nasim Design Chain Assessment

nasim has a complete design chain: `C4 → UC → SM → SQ → ERD → CL → Code`
with 42 UCs, 9 UC groups, 42 SQ diagrams, 9-state SM, and a full CL diagram.

### Strengths of nasim's Design

| Strength | Evidence |
|----------|----------|
| **Complete chain** | All layers authored and frozen. Most reference agents have NO design chain. |
| **Canonical entity registry** | `entities.md` with 30+ classes, 9 UC groups, verb extensions. |
| **Target architecture documented** | 6-package structure fully specified before coding. |
| **Event-driven planned** | `AgentEvent` hierarchy designed before implementation. |
| **Provider abstraction planned** | Protocol-based design in CL before any code. |
| **Safety-first planned** | `PermissionGate` with modes designed at UC level. |
| **Implementation roadmap** | 10 milestone docs with quality gates and CI/CD. |

### Weaknesses of nasim's Design (vs Reference Best Practices)

| Weakness | nasim Design | Best Reference | Gap |
|----------|-------------|---------------|-----|
| **No ROD/API layer** | "No HTTP APIs needed" | opencode: full HTTP API | nasim can't serve web/mobile/desktop |
| **No OpenAPI spec** | Not designed | opencode: Hono with typed routes | No machine-readable API contract |
| **No hook system** | Not designed | gemini-CLI: 9 hook events | No extensibility without code changes |
| **No plugin architecture** | Not designed | claude-code: marketplace | No community extensions |
| **No subagent model** | Not designed | claude-code: 5-level nesting | No parallel task execution |
| **No LSP integration** | Not designed | opencode: hover/def/refs/symbols | No semantic code understanding |
| **No model routing** | Single model per session | gemini-CLI: composite strategy | Can't auto-select best model |
| **SM is process FSM only** | Documented deviation | codex: full state machine | Less rigorous state management |

---

## 2. Reference Agent Design Patterns nasim Should Adopt

### Pattern 1: Provider Trait + Factory (codex)
```
codex: ModelProvider trait → ConfiguredModelProvider, AmazonBedrockModelProvider
nasim target: Provider Protocol → OllamaProvider, OpenAIProvider, AnthropicProvider
```
**Why:** Clean polymorphism. Adding a provider = implement Protocol + register.
**How:** Already designed in CL. Implement in Phase 1.

### Pattern 2: Tool ABC + Dynamic Registry (opencode)
```
opencode: Tool.make() + ToolRegistry → permission-filtered materialized definitions
nasim target: Tool ABC + ToolRegistry → register/execute/get_definitions
```
**Why:** Encapsulated, testable, extensible (MCP).
**How:** Already designed in CL. Implement in Phase 1.

### Pattern 3: 4-Layer Config (aider)
```
aider: CLI > .env > .aider.conf.yml (CWD/git-root/home) > defaults
nasim target: CLI > env (NASIM_*) > .nasim/config.yaml (project) > ~/.nasim/config.yaml (global)
```
**Why:** Persistent + project-specific + overridable.
**How:** Already designed in Config layer. Implement in Phase 1.

### Pattern 4: Event-Driven Agent Loop (gemini-CLI + opencode)
```
gemini-CLI: 9 hook events (BeforeModel, AfterModel, BeforeToolSelection, etc.)
opencode: AgentEvent hierarchy (TextChunk, ToolStart, ToolResult, Error, Done)
nasim target: AgentEvent hierarchy + Iterator[AgentEvent] from orchestrator
```
**Why:** Decouples agent from UI. Enables CLI + web + mobile.
**How:** Already designed in CL. Implement in Phase 1.

### Pattern 5: Background Context Compaction (aider)
```
aider: ChatSummary in background thread when done_messages > budget
nasim target: ContextCompactor triggered by ConversationHistory.check_budget()
```
**Why:** Prevents long-session degradation.
**How:** Already designed in AGT-06/CTX-02 UCs. Implement in Phase 2.

### Pattern 6: OS-Level Sandboxing (codex)
```
codex: landlock/seccomp (Linux), seatbelt (macOS), bubblewrap
nasim target: PermissionGate with ask/auto/off modes (simpler but effective)
```
**Why:** Defense in depth. nasim's approach is simpler but covers 90% of use cases.
**How:** Already designed in SAF group UCs. Implement in Phase 1.

### Pattern 7: Plan-Then-Build (opencode + gemini-CLI)
```
opencode: Dedicated plan agent that denies edits except .opencode/plans/
gemini-CLI: EnterPlanMode/ExitPlanMode tools, restricted to plans directory
nasim target: PlanSession with queue_tool_call/approve_plan
```
**Why:** Reduces wasted compute on wrong approaches.
**How:** Already designed in AGT-07/AGT-08 UCs. Implement in Phase 2.

### Pattern 8: MCP as Extension Standard (goose + 12 others)
```
goose: Extensions ARE MCP servers
nasim target: MCPClient + MCPToolAdapter wrapping discovered tools
```
**Why:** 100+ community MCP servers available.
**How:** Already designed in TL-12 UC. Implement in Phase 2.

---

## 3. Design Improvements nasim Needs (Beyond Current Design)

### IMP-01: HTTP API Server Mode (ROD + OpenAPI)

**Current design:** "No HTTP APIs needed" (docs/README.md)
**Problem:** User wants web-app, mobile-app, desktop-app served by nasim.
**Improvement:** Add a `serve` command that exposes nasim as an HTTP + SSE service.

Design:
- Resources: `sessions`, `messages`, `tools`, `config`
- RESTful CRUD on each resource
- SSE streaming for agent responses
- OpenAPI 3.1 spec auto-generated
- Same `AgentOrchestrator` consumed by HTTP handler

New artifacts needed:
- `docs/ct/api/` — API contract (OpenAPI spec)
- `docs/c4/c4_nasim_component_server.puml` — server component diagram
- UC group `SRV` — server-specific use cases

### IMP-02: Hook System

**Current design:** No hooks designed
**Problem:** No way to extend behavior without code changes.
**Improvement:** Pre/post hooks for tool use and LLM calls.

Design:
- Hook events: `pre_tool_use`, `post_tool_use`, `pre_llm_call`, `post_llm_call`
- Hook types: command (bash), prompt (LLM-driven)
- Hooks run in parallel, can approve/deny/modify

New artifacts:
- UC group `HK` — hook lifecycle
- SQ diagrams for hook execution flow

### IMP-03: Plugin Architecture

**Current design:** No plugins
**Problem:** Can't add capabilities without code changes.
**Improvement:** Plugin manifest + discovery + registration.

Design:
- Plugin manifest: `nasim-plugin.json`
- Plugin directory: `~/.nasim/plugins/`
- Plugin hooks + tool registration
- Plugin marketplace (Phase 4)

### IMP-04: Model Routing

**Current design:** Single model per session
**Problem:** Can't auto-select best model for task type.
**Improvement:** Composite strategy routing.

Design:
- Model router: classifier → selection → fallback → approval
- Per-task model profiles (code = strong, chat = cheap, reasoning = reasoning)
- Mid-session model switching

### IMP-05: Subagent Spawning

**Current design:** Single agent only
**Problem:** Can't parallelize or specialize.
**Improvement:** Parent agent spawns child agents.

Design:
- `SubagentTool(Tool)`: spawn child with restricted tools
- Child inherits provider, config; can have different model
- Parent receives final output
- Nesting limit (5 levels)
- Foreground/background modes

### IMP-06: LSP Integration

**Current design:** No LSP
**Problem:** Can't do semantic code navigation (go-to-definition, find references).
**Improvement:** LSP client as a tool.

Design:
- Auto-discover LSP servers by file extension
- Operations: hover, definition, references, symbols
- Exposed as `LspTool(Tool)` with permission gating
- Configurable per-server

---

## 4. Updated Design Chain Requirements

### New/Modified Artifacts Needed

| Artifact | Change | Priority |
|----------|--------|----------|
| `entities.md` | Add SRV, HK groups + new components | P0 |
| `c4_nasim_container.puml` | Add HTTP Server container | P1 |
| `c4_nasim_component_server.puml` | New: server components | P1 |
| `uc_server.puml` | New: server UC group | P1 |
| `uc_hooks.puml` | New: hook lifecycle UCs | P2 |
| `uc_plugins.puml` | New: plugin UCs | P3 |
| `sq/SRV/*.puml` | New: server SQ diagrams | P1 |
| `sq/HK/*.puml` | New: hook SQ diagrams | P2 |
| `cl_runtime_model.puml` | Add Server, Hook, Plugin classes | P1 |
| OpenAPI spec | New: `docs/api/openapi.yaml` | P1 |

### Updated Package Structure

```
nasim/
    __init__.py
    __main__.py
    CLI/              ← CLI interface
        __init__.py
        args.py
        repl.py
        renderer.py
        commands.py
    agent/            ← Agent core (UI-agnostic)
        __init__.py
        orchestrator.py
        history.py
        compactor.py
        events.py
        permission.py
        plan.py
    provider/         ← LLM abstraction
        __init__.py
        base.py
        ollama.py
        openai.py
        anthropic.py
        router.py     ← NEW: model routing
    tools/            ← Tool abstraction
        __init__.py
        base.py
        file.py
        search.py
        shell.py
        directory.py
        web.py
        git.py
        mcp.py
        lsp.py        ← NEW: LSP integration
    config/           ← Configuration
        __init__.py
        loader.py
        schema.py
    session/          ← Session persistence
        __init__.py
        store.py
        model.py
    server/           ← NEW: HTTP API server
        __init__.py
        app.py
        routes.py
        sse.py
    hooks/            ← NEW: Hook system
        __init__.py
        manager.py
        types.py
    plugins/          ← NEW: Plugin system
        __init__.py
        loader.py
        manifest.py
```

---

## 5. How nasim Can Be Better Than All References

### Design Excellence
- **Complete design chain** (no reference agent has this)
- **Canonical entity registry** (no reference agent has this)
- **Implementation roadmap with quality gates** (no reference agent has this)

### Architecture Excellence
- **Clean layered architecture** with 6 packages and 30+ modules
- **Protocol-based abstractions** (Provider, Tool, Hook)
- **Event-driven agent** with UI-agnostic event stream
- **Multi-interface support** (CLI + HTTP API + MCP server)

### Functionality Excellence
- **Multi-provider LLM** (like opencode, but simpler Python implementation)
- **Rich tool set** (12+ tools including search, web, git, MCP, LSP)
- **Context compaction** (like aider, but with token-budgeted triggering)
- **Session persistence** (JSON Lines, like aider but structured)
- **Plan mode** (like opencode, but simpler queue-based)
- **Safety first** (like codex, but without OS-level complexity)

### Developer Experience
- **Python** (most accessible language for contributions)
- **Clean code** (mypy --strict, ruff, black from day one)
- **Comprehensive docs** (design chain + audit + roadmap)
- **Easy setup** (`pip install nasim` + Ollama)

### Unique Differentiator: Service Architecture
**No reference agent cleanly serves CLI + HTTP API + MCP server from the same core.**
nasim's design makes this possible:
- Agent core emits events
- CLI renders events to terminal
- HTTP server sends events as SSE
- MCP server sends events as JSON-RPC

This is the key architectural advantage: **one agent core, three interfaces**.

---

## 6. Summary

nasim's current design chain is **more complete than any reference agent's**.
The gap is in **implementation** (v0.1 is a 450-LOC proof of concept) and
**missing features** (no provider abstraction, no search, no config, etc.).

The CAR improvement plan addresses every gap systematically:
- Phase 1 (Foundation): Refactor to 6 packages with proper abstractions
- Phase 2 (Core): Add search, context mgmt, sessions, safety, rich UI
- Phase 3 (Service): HTTP API, subagents, plugins, LSP

After Phase 3, nasim would be:
- **Better designed** than all references (complete design chain)
- **Better architected** than most references (clean layers, event-driven)
- **More scalable** than all references (CLI + HTTP + MCP from one core)
- **More accessible** than most references (Python, pip install)
- **More extensible** than most references (MCP + hooks + plugins)

The one trade-off: nasim won't have the raw performance of Rust agents (codex, goose, warp)
or the deep IDE integration of TypeScript agents (cline, kilocode, Roo-Code).
But it will have the **cleanest architecture** and the **most complete design documentation**
of any code agent in existence.
