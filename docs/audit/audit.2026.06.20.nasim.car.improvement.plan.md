# nasim — CAR Improvement Plan

**Date:** 2026-06-20
**Scope:** All gaps identified in reference-agent audit + gap analysis
**Framework:** Challenge → Action → Result (CAR)
**Goal:** Make nasim better than all reference agents in design, functionality, architecture

---

## Overview

Each improvement is structured as:
- **Challenge:** What problem exists or capability is missing
- **Action:** What to implement (design + code changes)
- **Result:** What the system looks like after, and how it compares to references

---

## CAR-01: Provider Abstraction Layer

### Challenge
nasim is hardcoded to Ollama (`OllamaClient`). 26/27 reference agents support multiple
providers. This blocks every other capability — context management, streaming, web access
all depend on the provider interface being right.

### Action
1. Define `Provider` Protocol in `nasim/provider/base.py`:
   ```python
   class Provider(Protocol):
       model_name: str
       def chat(self, messages, tools) -> LLMResponse: ...
       def chat_stream(self, messages, tools) -> Iterator[str | ToolCall]: ...
   ```
2. Move `OllamaClient` → `OllamaProvider(Provider)` in `nasim/provider/ollama.py`
3. Add `ProviderFactory` that reads config and instantiates correct provider
4. Add `OpenAIProvider` and `AnthropicProvider` (Phase 2)
5. `Agent.__init__` takes `Provider` (Protocol), not `OllamaClient` (concrete)

### Result
- nasim supports 3+ providers from day one
- Adding a new provider = implement Protocol + register in factory
- **Better than:** aider (litellm wrapper), codex (trait-object), opencode (Route abstraction)
- **Best-in-class pattern:** opencode's `Route` (Protocol + Endpoint + Auth + Transport)
  combined with codex's trait-object simplicity

---

## CAR-02: Tool System Redesign

### Challenge
Tools are module-level free functions registered via decorator into a global mutable dict.
No ABC, no instance state, no `ToolResult`, no `safe` flag. Can't add MCP tools dynamically.
5 tools total (read, write, edit, list_dir, shell). No search/grep/glob.

### Action
1. Define `Tool` ABC in `nasim/tools/base.py`:
   ```python
   class Tool(ABC):
       name: str
       description: str
       parameters: dict
       safe: bool
       @abstractmethod
       def execute(self, **args) -> ToolResult: ...
   ```
2. `ToolResult(success: bool, content: str, error: str | None)` dataclass
3. `ToolRegistry` instance class with `register()`, `execute()`, `get_definitions()`
4. Migrate existing tools to class-based: `ReadFileTool(Tool)`, `WriteFileTool(Tool)`, etc.
5. Add new tools: `GrepTool`, `GlobTool`, `FindFileTool`, `WebFetchTool`, `WebSearchTool`, `GitTool`
6. `MCPToolAdapter(Tool)` wraps MCP server tools into nasim format (Phase 2)

### Result
- 12+ tools from day one (5 existing + 7 new)
- Dynamic tool registration for MCP at runtime
- Structured error handling (no more string errors)
- Safety annotation per tool (`safe: bool`)
- **Better than:** aider (no tool system), SWE-agent (bash-only), gemini-cli (no ABC)
- **Best-in-class pattern:** opencode's `Tool.make()` with Effect Schema + `ToolRegistry`

---

## CAR-03: Configuration System

### Challenge
All settings are CLI arguments with hardcoded defaults. No persistence. Every session
must re-specify `--server`, `--model`. 25/27 reference agents have config files.

### Action
1. `Config` dataclass in `nasim/config/schema.py` with typed fields
2. `ConfigLoader` in `nasim/config/loader.py` with 4-layer merge:
   - Global: `~/.nasim/config.yaml`
   - Project: `.nasim/config.yaml`
   - Environment: `NASIM_*` prefix
   - CLI flags (highest priority)
3. Validation at load time (fail fast)
4. `pydantic-settings` for schema validation

### Result
- Persistent configuration across sessions
- Project-level overrides for different repos
- Environment variable support for CI/CD
- **Better than:** aider (configargparse, no validation), SWE-agent (YAML only)
- **Best-in-class pattern:** aider's 4-layer + opencode's JSONC with Effect Schema

---

## CAR-04: Event-Driven Agent Architecture

### Challenge
`Agent` calls `print()` 8 times. Agent mixes orchestration, state, and rendering.
Can't swap UI (CLI → web → voice). Can't test agent without stdout capture.
Every reference agent uses events or callbacks.

### Action
1. Define `AgentEvent` hierarchy in `nasim/agent/events.py`:
   ```python
   class AgentEvent: ...
   class TextChunk(AgentEvent): text: str
   class ToolStart(AgentEvent): name: str; args: dict
   class ToolResultEvent(AgentEvent): name: str; success: bool; content: str
   class Error(AgentEvent): message: str
   class Done(AgentEvent): final_text: str
   ```
2. `AgentOrchestrator.run()` → `Iterator[AgentEvent]` (generator)
3. Remove ALL `print()` from `agent.py`
4. CLI `Renderer` subscribes to events and renders to terminal
5. HTTP handler subscribes and sends SSE events (Phase 4)

### Result
- Agent core is UI-agnostic (testable, serverable)
- CLI, web, mobile, desktop all consume the same event stream
- **Better than:** aider (print), SWE-agent (print), cline (no events)
- **Best-in-class pattern:** gemini-cli (9 hook events) + opencode (Effect-TS events)

---

## CAR-05: Context Window Management

### Challenge
Messages grow without bound. No token counting. Long sessions crash or degrade.
`self.messages` appends every message and tool result forever.

### Action
1. `ConversationHistory` class in `nasim/agent/history.py`:
   - `messages: list[dict]`, `token_count: int`, `context_budget: int`
   - `add_message()`, `get_messages()`, `check_budget() → bool`
2. Token counter (tiktoken or provider-reported)
3. `ContextCompactor` in `nasim/agent/compactor.py`:
   - Triggers when `token_count > budget_threshold`
   - Summarizes oldest tool-result exchanges via secondary LLM call
   - Replaces summarized range with single summary message
4. Budget configurable per model

### Result
- Unlimited session length without degradation
- Graceful compaction preserves recent context
- **Better than:** aider (simple summary), SWE-agent (truncation only), plandex (none)
- **Best-in-class pattern:** aider's background `ChatSummary` + codex's `compact.rs`

---

## CAR-06: Session Persistence

### Challenge
Quit = lose everything. No way to resume. 18/27 reference agents persist sessions.

### Action
1. `SessionStore` in `nasim/session/store.py`:
   - JSON Lines files in `~/.nasim/sessions/<session-id>/`
   - Atomic writes (write to tmp, rename)
   - `save()`, `load()`, `load_latest()`, `list_sessions()`
2. `Session` dataclass: `id`, `created_at`, `messages`
3. CLI flags: `--continue` (resume last), `--session <id>`, `--list-sessions`

### Result
- Sessions survive process restarts
- Resume exactly where you left off
- Multiple named sessions per project
- **Better than:** aider (markdown-only), SWE-agent (ephemeral), cline (local storage only)
- **Best-in-class pattern:** opencode (SQLite event-sourced) or codex (SQLite ThreadStore)

---

## CAR-07: Safety & Permission System

### Challenge
`shell_exec` runs any command. `write_file` overwrites without asking. No safeguards.
A confused LLM can delete files, run `rm -rf`, or run harmful commands.

### Action
1. `PermissionGate` in `nasim/agent/permission.py`:
   - `mode: str` (`ask | auto | off`)
   - `check(tool_name) → bool`
   - In `ask` mode: shell + write/edit prompt `[y/N]` before execution
2. Tool-level `safe: bool` annotation in registry
3. CLI flags: `--yes` / `--no-confirm` for scripted use
4. Iteration budget surfaced in config (currently hardcoded 20)

### Result
- No dangerous operation executes without user consent in `ask` mode
- Safe tools (read_file, list_dir) skip confirmation
- Scriptable with `--yes` flag
- **Better than:** aider (confirmation only), SWE-agent (blocklist only), cline (VS Code sandbox)
- **Best-in-class pattern:** codex (OS sandbox) for production, gemini-cli (4 approval modes) for flexibility

---

## CAR-08: Rich Output Rendering

### Challenge
Plain ASCII output. No colors, no diffs, no structured tool display.
Every reference agent has rich output.

### Action
1. `Renderer` class in `nasim/cli/renderer.py`:
   - Colored prompts (`you>` blue, `nasim>` green)
   - Tool call display: indented name + args + truncated result
   - Diff display for file edits (unified diff format)
   - Error highlight in red
   - Token/cost display per turn (optional)
2. Use `rich` library (already in Python ecosystem)
3. Agent emits events; Renderer subscribes

### Result
- Professional terminal experience
- Visual diff on file edits
- Error highlighting
- **Better than:** aider (Rich but ad-hoc), SWE-agent (plain), most TUI agents
- **Best-in-class pattern:** aider's Rich streaming + gemini-cli's structured output

---

## CAR-09: Plan Mode

### Challenge
Agent always executes immediately. No intermediate review. 3/27 agents have plan mode.
Users want to approve plans before execution.

### Action
1. `PlanSession` in `nasim/agent/plan.py`:
   - `pending_calls: list[tuple]`
   - `queue_tool_call()`, `approve_plan()`, `display_plan()`, `is_active()`
2. `/plan` slash command toggles plan mode
3. In plan mode: tool calls queued, not executed
4. `approve_plan()` executes queued calls

### Result
- Users review before execution
- Reduces wasted compute on wrong approaches
- **Better than:** most agents (don't have it)
- **Best-in-class pattern:** opencode's dedicated plan agent + gemini-cli's PLAN mode

---

## CAR-10: MCP Client Support

### Challenge
No extension mechanism. 12/27 reference agents support MCP. Can't consume any
MCP server tools.

### Action
1. `MCPClient` class wrapping MCP `stdio` and `sse` transports
2. `MCPToolAdapter(Tool)` wraps discovered MCP tools into nasim `Tool` format
3. Config block: `mcp_servers: [{name, command, args}]`
4. Dynamic tool registration at startup from configured MCP servers

### Result
- Access to 100+ community MCP servers
- Extensible without code changes
- **Better than:** aider (no MCP), SWE-agent (no MCP), kimi-cli (fastmcp only)
- **Best-in-class pattern:** goose (extensions ARE MCP servers)

---

## CAR-11: HTTP API Server Mode

### Challenge
CLI-only interface. User wants web-app, mobile-app, desktop-app all served by nasim.
The service architecture should support multiple interfaces.

### Action
1. `serve` command in CLI: `nasim serve --port 8080`
2. HTTP + SSE server using `httpx` + `starlette`/`fastapi`
3. RESTful endpoints following ROD (Resource-Oriented Design):
   - `POST /v1/sessions` — create session
   - `POST /v1/sessions/{id}/messages` — send user message, receive SSE stream
   - `GET /v1/sessions/{id}/messages` — get message history
   - `GET /v1/tools` — list available tools
   - `GET /v1/config` — get current config
4. OpenAPI 3.1 spec auto-generated
5. Same `AgentOrchestrator` + `AgentEvent` stream consumed by HTTP handler

### Result
- nasim serves CLI + web + mobile + desktop simultaneously
- Same agent core, different interface layers
- API-first design enables any client
- **Better than:** ALL reference agents (none have clean HTTP API + CLI + web)
- **Best-in-class pattern:** opencode (TUI + web + desktop + server) as the model

```
                    ┌─────────────────────────────────────┐
                    │         nasim Service Core           │
                    │  ┌──────────┐  ┌──────────────────┐ │
                    │  │ Provider │  │ AgentOrchestrator│ │
                    │  │ Layer    │←→│ + Events         │ │
                    │  └──────────┘  └──────────────────┘ │
                    │  ┌──────────┐  ┌──────────────────┐ │
                    │  │ Tool     │  │ Config + Session │ │
                    │  │ Registry │  │ Store            │ │
                    │  └──────────┘  └──────────────────┘ │
                    └──────────┬──────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
        ┌─────┴─────┐  ┌──────┴──────┐  ┌──────┴──────┐
        │    CLI    │  │  HTTP API   │  │  MCP Server │
        │  (REPL)   │  │  (REST+SSE) │  │  (stdio)    │
        └───────────┘  └─────────────┘  └─────────────┘
              │                │                │
        ┌─────┴─────┐  ┌──────┴──────┐  ┌──────┴──────┐
        │ Terminal  │  │ Web App     │  │ MCP Clients │
        │           │  │ Mobile App  │  │             │
        │           │  │ Desktop App │  │             │
        └───────────┘  └─────────────┘  └─────────────┘
```

---

## CAR-12: Async Architecture

### Challenge
Synchronous `requests` library. Each LLM call blocks. Can't run web server alongside
agent loop. Can't execute concurrent tool calls.

### Action
1. Replace `requests` with `httpx.AsyncClient` for provider calls
2. `asyncio` event loop at top level
3. Tools that are I/O-bound run concurrently via `asyncio.gather`
4. Main CLI uses `asyncio.run()` at top level
5. HTTP server runs as async ASGI app

### Result
- Concurrent tool execution
- Non-blocking LLM calls
- HTTP server alongside agent loop
- **Better than:** aider (sync), SWE-agent (sync), most Python agents
- **Best-in-class pattern:** opencode (Effect-TS), gemini-cli (async Node.js)

---

## CAR-13: Logging & Observability

### Challenge
No `logging` import anywhere. Debug requires attaching a debugger. Can't trace
LLM requests, tool calls, or latency.

### Action
1. Structured logging via stdlib `logging`
2. Logger hierarchy: `nasim.cli`, `nasim.agent`, `nasim.provider.*`, `nasim.tools.*`
3. LLM request/response at `DEBUG`, tool calls at `INFO`, errors at `ERROR`
4. Config: `--log-level`, `LOG_LEVEL` env var
5. Optional: OpenTelemetry traces (Phase 3)

### Result
- Full traceability of every LLM call and tool execution
- Debug mode for development
- Production monitoring capability
- **Better than:** SWE-agent (no logging), most Python agents
- **Best-in-class pattern:** goose (OpenTelemetry), aider (structured logging)

---

## CAR-14: Search/Grep/Glob Tools

### Challenge
`list_dir` lists one directory shallowly. Can't search across codebase.
This is the #1 functional gap for a *code* agent. 20/27 agents have search.

### Action
1. `GrepTool`: search file contents by regex (ripgrep-backed for performance)
2. `GlobTool`: find files by glob pattern
3. `FindFileTool`: find files by name pattern with depth limit
4. All return `ToolResult` with structured output

### Result
- Agent can navigate any codebase without user providing exact paths
- **Better than:** aider (repo-map only), SWE-agent (none), plandex (tree-sitter only)
- **Best-in-class pattern:** gemini-cli (ripgrep + glob + find + ls)

---

## CAR-15: Structured Error Handling

### Challenge
All errors are `f"Error: ..."` strings. Agent can't distinguish error from valid output.
LLM sees error as tool output and may proceed with wrong data.

### Action
1. `ToolResult(success: bool, content: str, error: str | None)`
2. Tool handlers raise `ToolError(message)` on failure
3. `execute_tool()` catches `ToolError`, wraps in `ToolResult(success=False)`
4. Agent checks `result.success` and handles structurally

### Result
- Errors are first-class objects, not strings
- Agent can retry, report, or stop on error
- **Better than:** aider (string errors), SWE-agent (string errors)
- **Best-in-class pattern:** codex (`SafetyCheck` enum + `ToolResult`)

---

## CAR-16: Git Integration Tools

### Challenge
No git awareness. Agent can't check status, view diffs, or create commits.
10/27 agents have git integration.

### Action
1. `GitTool(Tool)`: `git status`, `git diff`, `git commit`, `git log`
2. Auto-commit after file edits (configurable, like aider)
3. Branch awareness for context

### Result
- Agent understands version control state
- Can create commits automatically
- **Better than:** SWE-agent (ephemeral), kimi-cli (none)
- **Best-in-class pattern:** aider (auto-commit + git-aware edits)

---

## CAR-17: Multi-Agent / Subagent Spawning

### Challenge
Single-agent only. Can't delegate subtasks. 10/27 agents support subagents.

### Action (Phase 3)
1. `SubagentTool(Tool)`: spawn a child agent with restricted tools
2. Child inherits parent's provider and config
3. Parent receives child's final output
4. Nesting limit (5 levels, like claude-code)

### Result
- Parallel task execution
- Specialized sub-agents (explore, implement, review)
- **Better than:** aider (arch mode only), SWE-agent (retry only)
- **Best-in-class pattern:** claude-code (5-level nesting, foreground/background)

---

## CAR-18: Plugin / Extension System

### Challenge
No extension mechanism beyond MCP. Can't add capabilities without code changes.
12/27 agents have plugin systems.

### Action (Phase 3)
1. Plugin manifest: `nasim-plugin.json` with name, version, tools, hooks
2. Plugin directory: `~/.nasim/plugins/`
3. Plugin hooks: `pre_tool_use`, `post_tool_use`, `pre_llm_call`, `post_llm_call`
4. Plugins can register tools via `ToolRegistry.register()`

### Result
- Community extensions without core changes
- Hook-based customization
- **Better than:** aider (no plugins), SWE-agent (no plugins)
- **Best-in-class pattern:** claude-code (marketplace + hooks)

---

## Implementation Phasing

### Phase 1 — Foundation (CAR-01 to CAR-08)
Must complete before any feature work. Refactors nasim from 4 flat modules to
6 packages with proper abstractions.

| CAR | Item | Effort | Unblocks |
|-----|------|--------|----------|
| CAR-01 | Provider Protocol + factory | Medium | All provider work |
| CAR-02 | Tool ABC + registry + ToolResult | Medium | All tool work |
| CAR-03 | Config system | Low | All config-dependent work |
| CAR-04 | Event-driven agent | Medium | All UI work |
| CAR-05 | ConversationHistory + token counting | Medium | Context mgmt |
| CAR-06 | SessionStore + persistence | Medium | Resume capability |
| CAR-07 | PermissionGate | Low | Safety |
| CAR-08 | Rich Renderer | Low | UX |
| CAR-13 | Logging | Low | Debugging |
| CAR-15 | Structured errors | Low | Error handling |

### Phase 2 — Core Capabilities (CAR-09 to CAR-16)
Feature work that makes nasim competitive.

| CAR | Item | Effort | Delivers |
|-----|------|--------|----------|
| CAR-09 | Plan mode | Medium | User approval workflow |
| CAR-10 | MCP client | Medium | Extension ecosystem |
| CAR-14 | Search/grep/glob tools | Low | Codebase navigation |
| CAR-16 | Git tools | Low | Version control awareness |
| CAR-12 | Async architecture | Medium | Performance + web server |

### Phase 3 — Service Architecture (CAR-11, CAR-17, CAR-18)
Makes nasim a multi-interface service.

| CAR | Item | Effort | Delivers |
|-----|------|--------|----------|
| CAR-11 | HTTP API server | High | Web/mobile/desktop interfaces |
| CAR-17 | Subagent spawning | High | Parallel task execution |
| CAR-18 | Plugin system | Medium | Community extensions |

---

## Comparison: nasim After CAR vs Reference Agents

| Feature | nasim after CAR | Best reference agent |
|---------|----------------|---------------------|
| Multi-provider | ✓ (Protocol + 3 providers) | opencode (13 providers) |
| Search/grep/glob | ✓ (ripgrep-backed) | gemini-cli (ripgrep + glob) |
| Web access | ✓ (fetch + search) | opencode (web_fetch + web_search) |
| Config system | ✓ (4-layer YAML) | aider (4-layer configargparse) |
| Context compaction | ✓ (background summarization) | aider (ChatSummary) |
| Session persistence | ✓ (JSON Lines + resume) | codex (SQLite ThreadStore) |
| Safety/permissions | ✓ (ask/auto/off modes) | codex (OS sandbox) |
| Rich UI | ✓ (Rich library) | aider (Rich) |
| Plan mode | ✓ (queue + approve) | opencode (dedicated agent) |
| MCP client | ✓ (stdio + sse) | goose (extensions ARE MCP) |
| HTTP API | ✓ (REST + SSE, ROD) | opencode (Hono server) |
| Event system | ✓ (AgentEvent hierarchy) | gemini-cli (9 hook events) |
| Async | ✓ (httpx + asyncio) | opencode (Effect-TS) |
| Logging | ✓ (structured) | goose (OpenTelemetry) |
| Error handling | ✓ (ToolResult) | codex (SafetyCheck) |
| Git integration | ✓ (status/diff/commit) | aider (auto-commit) |
| OOP/SOLID | ✓ (Protocol, ABC, SRP) | codex (124 crates, strict boundaries) |
| DRY | ✓ (unified run loop) | opencode (single agent runner) |
| SoC | ✓ (6 packages, clear boundaries) | opencode (25 packages) |
| Modularity | ✓ (30+ modules) | gemini-cli (33+ subdirs) |
| Scalability | ✓ (async, multi-provider, API) | opencode (TUI + web + desktop + server) |

**nasim after CAR would be comparable to opencode and gemini-cli in architecture,
while maintaining the simplicity of a Python codebase (vs Rust/TypeScript complexity).**
