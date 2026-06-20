# nasim — Capability and Architecture Audit

**Date:** 2026-06-20
**Scope:** Full capability gap analysis against 25 reference code agents; architecture
quality audit of `nasim/` source; design chain readiness for the target architecture.
**Method:** Deep code inspection of all reference repos under `/home/salim/prj/salim/nasim/code/`;
traceability check against current `nasim/` source; application of all global
software-design rules.
**Companion audit:** `audit_2026-06-20_design-chain.md` (design chain consistency only).

---

## Executive Summary

nasim v0.1 is a functional proof-of-concept: 4 modules (~450 LOC), 5 tools,
Ollama-only, no configuration, no safety, no persistence. The reference corpus
spans 25 agents (aider, codex, gemini-cli, goose, cline, opencode, SWE-agent,
hermes-agent, kimi-cli, and 16 others). Against that corpus, nasim is missing
**every capability** that defines a production-grade code agent beyond the raw
agentic loop. The source code has 11 architectural violations that compound as
each new capability is added. The design chain (C4 → Code) must be fully rebuilt
to reflect the target architecture before implementation begins.

This audit is the input to the design sprint. Nothing in `nasim/` is correct to
extend as-is. The architecture must be redesigned first.

| Tier | Finding count | Blocks |
|------|--------------|--------|
| Critical capability gaps | 7 | production readiness |
| Architecture violations | 11 | extensibility / SoC / DRY |
| Design chain blockers | 6 | chain correctness (from design audit) |
| Design chain gaps | 8 | new capabilities not yet designed |

---

## Part 1 — Capability Gap Analysis

Capabilities are categorized by frequency across reference agents. Tier-1 features
appear in ≥ 80% of agents. Tier-2 in 40–79%. Tier-3 are standout differentiators
found in 1–3 agents.

---

### Tier-1 Gaps (in every serious agent; critical)

#### CAP-01 — Multi-provider LLM abstraction

**What reference agents do:** Every agent except the single-vendor binaries (amazon-q,
copilot-cli, gemini-cli, warp) uses a provider abstraction layer.
- aider / SWE-agent / plandex → litellm (100+ providers in one call).
- goose → 15 native provider crates + ACP backends.
- kimi-cli / hermes-agent → adapter classes per provider.
- cline / opencode / kilocode → catalog of provider configs, runtime-selectable.

**What nasim does:** `OllamaClient` is hardcoded. One URL, one model, no abstraction.
No way to add a second provider without rewriting the agent loop.

**Impact:** Locked to Ollama. Cannot use OpenAI, Anthropic, Gemini, LM Studio,
OpenRouter, or any other backend. Cannot test different models without a code change.

**Required architecture:** A `Provider` protocol/interface (`chat()`, `chat_stream()`,
`model_name`) with one concrete implementation per backend. A provider factory
that reads config and instantiates the correct class. `OllamaProvider`,
`OpenAIProvider`, `AnthropicProvider` as initial implementations.

---

#### CAP-02 — Search / grep / glob tools

**What reference agents do:** All agents have find-in-codebase tools.
- codex, amazon-q, gemini-cli, opencode, kilocode → `grep` (ripgrep-backed),
  `glob` (pattern matching), `find`.
- aider → repo-map (tree-sitter ctags, symbol-level outline).
- opencode / crush → LSP integration for semantic symbol search.
- SWE-agent → `search` bundle (YAML-configured grep + tree traversal).

**What nasim does:** `list_dir` lists one directory shallowly. `read_file` reads one
file. No way to search across a codebase for a symbol, string, or file pattern.

**Impact:** The agent cannot locate code without the user providing exact paths.
Useless for any codebase of non-trivial size. This is the single biggest functional
gap for a *code* agent.

**Required tools:** `grep_search(pattern, path, case_sensitive, include_glob)`,
`glob_files(pattern, base_path)`, `find_files(name_pattern, path, max_depth)`.
Optional: `ripgrep` wrapper for performance; tree-sitter repo-map for large repos.

---

#### CAP-03 — Web fetch / web search

**What reference agents do:** gemini-cli, opencode, cline, kilocode, mistral-vibe,
codex, kimi-cli, hermes-agent, and others all include `web_fetch(url)` and
`web_search(query)` tools. Google Search grounding is built into gemini-cli.

**What nasim does:** No web access at all.

**Impact:** Agent cannot look up documentation, error messages, package APIs,
or any external information during a task.

**Required tools:** `web_fetch(url, timeout)` → returns page text (markdown or
stripped HTML). `web_search(query, num_results)` → returns ranked results with
snippets. Provider: requests + html2text for fetch; a configurable search backend
(SerpAPI, DuckDuckGo, Brave) for search.

---

#### CAP-04 — Configuration system

**What reference agents do:** All agents persist configuration.
- aider → `~/.aider.conf.yml` + project `.aider.conf.yml` + CLI overrides.
- claude-code → `~/.claude/settings.json` + project `.claude/settings.json`.
- goose → `~/.config/goose/` YAML + env vars + profiles.
- opencode → `opencode.json` in project root.
- SWE-agent → YAML config files defining the entire agent harness.

**What nasim does:** All settings are CLI arguments with hardcoded defaults.
No persistence. Every session must re-specify `--server`, `--model`.

**Impact:** Unusable in production. No project-level config. No profiles. No
persistent memory of the user's environment.

**Required:** A layered config system:
1. Global: `~/.nasim/config.yaml` — default provider, model, safety settings.
2. Project: `.nasim/config.yaml` — project-specific overrides, system prompt additions.
3. CLI: flags override everything.
Config dataclass with typed fields; loaded once at startup; validated at load.

---

#### CAP-05 — Context window management

**What reference agents do:**
- aider → chat history summarization via secondary LLM call when budget exceeded.
  Also a repo-map that compresses the whole codebase into a symbol outline.
- codex → `compact.rs`, `token_budget.rs`; structured compaction with budget tracking.
- gemini-cli → truncation utilities + omission placeholder detection.
- hermes-agent → `context_compressor.py`, `context_engine.py`,
  `conversation_compression.py`; prompt caching as a sacred constraint.
- plandex → server-side context management across plan steps.

**What nasim does:** Appends every message and tool result to `self.messages` without
bound. No token counting. No truncation. No summarization.

**Impact:** Long sessions crash or produce incoherent responses when the context
window is exceeded. The agent silently degrades.

**Required:**
- Token counter (model-specific; tiktoken or provider-reported counts).
- `ContextManager` class owning `messages: list[Message]`, tracking `token_count`.
- Compaction trigger when `token_count > budget_threshold`.
- Compaction strategy: summarize oldest tool-result exchanges via a secondary LLM call;
  replace summarized range with a single summary message.
- Budget configurable per model (different models have different context windows).

---

#### CAP-06 — Session persistence

**What reference agents do:**
- aider → `--chat-history-file`; auto-commits after each change.
- codex → persistent sessions in state DB; `--continue` flag.
- plandex → server-side named plans with history and branching.
- opencode → SQLite sessions, snapshots, `opencode run --continue`.
- kimi-cli → `~/.kimi/sessions/`, subagent instances by ID.
- claude-code → `--continue` flag, session history.

**What nasim does:** `self.messages` lives in RAM. Quitting the process loses all
history. No way to resume.

**Required:**
- Session directory: `~/.nasim/sessions/<session-id>/`.
- Session file: JSON Lines of messages, persisted after each LLM round-trip.
- CLI: `--continue` loads the last session; `--session <id>` loads a named one;
  `--list-sessions` shows available sessions.

---

#### CAP-07 — Safety / permission system

**What reference agents do:**
- codex → most thorough: Linux landlock + macOS seatbelt + Windows sandbox,
  exec policy, network policy, guardian process.
- amazon-q → `tool_permission_checker.rs` per-tool checks.
- cline / kilocode → `tool-policies.ts`: `enabled` + `autoApprove` per tool.
- copilot-cli → "preview every action before execution".
- aider → `y/n` confirmation on shell commands unless `--yes`.
- SWE-agent → Docker sandboxing for benchmark runs.
- hermes-agent → `file_safety.py`, `tool_guardrails.py`, iteration budget.
- kimi-cli → `ApprovalRuntime`: approval queue projected to UI.

**What nasim does:** `shell_exec` runs any command immediately with no confirmation.
`write_file` overwrites without asking. No safeguards at all.

**Impact:** A confused LLM can delete files, run `rm -rf`, or run harmful commands
with no human gate. Unacceptable for any non-toy use.

**Required minimum (Phase 1):**
- `safety_mode: ask | auto | off` config option.
- In `ask` mode: shell commands and write/edit operations print the command and prompt
  `[y/N]` before execution.
- Tool-level `safe: bool` annotation in the registry.
- Iteration budget cap (already at `max_iterations=20`, but not surfaced in config).
- `--yes` / `--no-confirm` flag to suppress prompts for scripted use.

---

### Tier-2 Gaps (majority of serious agents)

#### CAP-08 — Rich output rendering

**What reference agents do:** All terminal-based agents use color and structured
display. aider uses Rich for streaming tokens + cost tracking per message. codex uses
a TUI (Rust Ratatui). cline / opencode have VS Code extension UIs. goose / crush use
Charm's Bubbletea (Rust/Go TUIs). At minimum: colored prompt, dimmed tool calls,
highlighted errors, diff display for file edits.

**What nasim does:** Plain ASCII. Tool calls printed as `  > tool_name({args})`.
Streamed tokens printed raw with `print(chunk, end="", flush=True)`.

**Required minimum:** A `Renderer` abstraction in the CLI layer.
- Colored prompts (`you>` in blue, `nasim>` in green).
- Tool call display: box or indent with tool name + args + truncated result.
- Diff display for file edits (unified diff format).
- Error highlight in red.
- Token/cost display per turn (optional but visible in aider).
Use `rich` library (already likely in the Python ecosystem).

---

#### CAP-09 — Plan mode

**What reference agents do:** gemini-cli, opencode, kilocode, mistral-vibe, kimi-cli
all implement a `plan_mode` — a first-class conversation state where the agent reasons
about what to do without executing any tools. The user approves the plan before
execution begins.

**What nasim does:** The agent always executes immediately. No intermediate review.

**Required (Phase 2):**
- `plan_mode: bool` state in the agent.
- In plan mode: tool calls are not executed; they are queued and displayed as a plan.
- `/plan` slash command toggles plan mode.
- `approve_plan()` executes the queued tool calls.
- A `plan` tool lets the LLM explicitly signal plan completion.

---

#### CAP-10 — MCP client support

**What reference agents do:** amazon-q, claude-code, codex, gemini-cli, goose,
opencode, cline, kilocode, hermes-agent, kimi-cli, mistral-vibe, crush, claw-code,
warp — virtually all modern agents support MCP. Goose uses MCP as its primary
extension mechanism (70+ MCP extensions). Gemini-cli has `list-mcp-resources`
and `read-mcp-resource` as built-in tools.

**What nasim does:** No MCP. Cannot consume any MCP server.

**Required (Phase 2):**
- `MCPClient` class wrapping the MCP `stdio` and `sse` transports.
- `MCPToolAdapter` that wraps discovered MCP tools into nasim's `ToolDef` format.
- Config block: `mcp_servers: [{name, command, args}]`.
- Dynamic tool registration at startup from configured MCP servers.

---

#### CAP-11 — Multiple run modes

**What reference agents do:** All agents support more than one invocation mode.
- `agent -c "..."` / `--print` — single-shot, non-interactive, stdout output.
- `--headless` — no REPL; stdin/stdout pipe.
- `serve` — HTTP+SSE server (opencode, kimi-cli ACP mode).
- Batch/benchmark mode (SWE-agent, aider).

**What nasim does:** REPL or single-shot via `-c`. No headless/pipe mode. No
server mode. Single-shot doesn't handle stdin piping properly.

**Required minimum:**
- Headless mode: read from stdin when no TTY detected (pipe mode).
- Single-shot already works (`-c`); ensure exit code propagation.
- Proper `--output` flag for single-shot JSON output (structured for tooling).

---

### Tier-3 Capabilities (standout; Phase 3+)

| ID | Capability | Reference agents | Priority |
|----|-----------|-----------------|----------|
| CAP-12 | Repo-map (codebase symbol outline) | aider | High value for large codebases |
| CAP-13 | Multi-agent / subagent spawning | claude-code, cline, codex, kimi-cli | Phase 3 |
| CAP-14 | LSP integration for semantic context | opencode, crush | High quality |
| CAP-15 | Session rewind / undo | plandex, mistral-vibe | Ergonomics |
| CAP-16 | YAML agent harness / profiles | SWE-agent, kimi-cli | Configurability |
| CAP-17 | Scheduler / background tasks | goose | Automation |
| CAP-18 | Voice I/O (TTS + transcription) | hermes-agent, mistral-vibe | Accessibility |
| CAP-19 | Browser / computer use | openinterpreter | Phase 4 |
| CAP-20 | RAG / semantic codebase search | claw-code | Phase 3 |
| CAP-21 | Git-aware tools (status, diff, commit) | aider, claude-code, plandex | Near-term |

---

## Part 2 — Architecture Quality Audit

The current `nasim/` source has 11 violations of OOP, DRY, and SoC principles.
These compound with every new capability added. They must be resolved in the
redesign, not patched incrementally.

---

### ARCH-01 — No provider interface (SoC / OCP violation)

`agent.py` takes an `OllamaClient` concrete type. `Agent.__init__` is typed to
`OllamaClient`. Adding any other provider requires changing the agent.

**Correct design:** A `Provider` abstract class or Protocol:
```python
class Provider(Protocol):
    model_name: str
    def chat(self, messages, tools) -> LLMResponse: ...
    def chat_stream(self, messages, tools) -> Iterator[str | ToolCall]: ...
```
`OllamaProvider`, `OpenAIProvider`, `AnthropicProvider` implement it.
`Agent` holds `self._provider: Provider`.

---

### ARCH-02 — Tool registry is a module-level dict (no class, no interface)

`TOOL_REGISTRY: dict[str, dict]` is a global mutable dict populated via decorator
side-effects at import time. This makes:
- Tool isolation impossible (no instance state per tool).
- Testing painful (must monkey-patch module globals).
- Dynamic registration impossible at runtime (e.g. MCP tools added after startup).
- No tool metadata beyond name + description + parameters + handler.

**Correct design:** A `ToolRegistry` class (one instance per agent), a `Tool` abstract
base class or dataclass with `name`, `description`, `parameters`, `safe: bool`,
`execute(args) → str`. Tools registered by instance: `registry.register(FileTool())`.

---

### ARCH-03 — Duplicated streaming state management (DRY violation)

`tool_calls_buf` accumulation logic is copy-pasted between `llm.py:chat_stream()`
and `agent.py:run_streaming()`. Both maintain independent `dict[int, ToolCall]`
buffers. The LLM layer already yields complete `ToolCall` objects from
`chat_stream()`; the agent re-buffers them.

**Correct design:** The LLM layer yields only `str | ToolCall` with complete objects.
The agent consumes the stream without rebuffering. The `tool_calls_buf` in
`agent.py:run_streaming()` becomes a simple list accumulation.

---

### ARCH-04 — `run()` and `run_streaming()` are near-duplicates (DRY violation)

Both methods:
1. Append user message.
2. Loop up to `max_iterations`.
3. Get LLM response.
4. If tool calls → execute → append → continue.
5. If text → append → return.

The only difference is streaming vs blocking, and print-to-terminal vs return-string.
~80 LOC duplicated with minor variations. A bug in tool-call handling must be fixed
in both places.

**Correct design:** A single `_run_turn(stream: bool)` private method that takes a
renderer callback. `run()` and `run_streaming()` become thin wrappers that pass
the appropriate renderer. Or: unify via an async generator that yields events
(text chunks, tool-start, tool-result); callers consume the event stream.

---

### ARCH-05 — Print statements in `agent.py` (SoC violation)

`agent.py` calls `print()` 8 times. The agent core is responsible for orchestration;
rendering is the CLI layer's concern. The agent should not know about terminal output.

**Impact:** `Agent` cannot be used in headless/server mode without capturing stdout.
Testing requires stdout capture. No way to swap the renderer (TUI, web, voice).

**Correct design:** Agent emits events via a callback or yields event objects.
The CLI layer subscribes and renders. `Agent.run_streaming()` → `Iterator[AgentEvent]`
where `AgentEvent = TextChunk | ToolStart | ToolResult | Error | Done`.

---

### ARCH-06 — No error hierarchy (everything returns strings)

All tools return `str`. Errors are `f"Error: ..."` strings. The agent has no way
to distinguish a tool error from a valid string output. The LLM sees the error
message as tool output and may silently proceed with wrong data.

**Correct design:** `ToolResult(success: bool, content: str, error: str | None)`.
Tool handlers raise `ToolError(message)` on failure; `execute_tool()` catches it and
sets `success=False`. The agent checks `result.success` and can handle errors
structurally (retry, report to user, stop).

---

### ARCH-07 — No logging (debugging is impossible)

There is no `logging` import anywhere. Debug information (LLM request/response,
tool calls, latency) is only visible if you attach a debugger.

**Correct design:** Per `rules/code/logging.md`: structured logging via stdlib
`logging`. Logger hierarchy: `nasim.cli`, `nasim.agent`, `nasim.provider.*`,
`nasim.tools.*`. Log LLM request/response at `DEBUG`, tool calls at `INFO`,
errors at `ERROR`. Config: `--log-level`, `LOG_LEVEL` env var.

---

### ARCH-08 — No async support

`requests` is synchronous. Each LLM call blocks the entire process. Tool execution
is sequential even when the LLM requests multiple tool calls simultaneously.

**Impact:** Cannot support streaming + concurrent tool execution. Cannot add a web
server (MCP server, ACP server) alongside the agent loop without threads. Cannot
implement background tasks (CAP-17).

**Correct design:** `httpx.AsyncClient` for provider calls. `asyncio` event loop.
Tools that are I/O-bound (web fetch, shell exec) run concurrently via `asyncio.gather`.
The main REPL uses `asyncio.run()` at the top level.

---

### ARCH-09 — `Agent` owns rendering and conversation simultaneously (SRP violation)

`Agent` holds `self.messages` (conversation state), drives the LLM loop (orchestration),
AND calls `print()` (rendering). Three distinct responsibilities in one class.

**Correct design** (aligns with CSR pattern from `rules/software-design/csr.md`):
- `ConversationHistory` — owns `messages: list[Message]`, `token_count`, compaction.
- `AgentOrchestrator` — drives the LLM/tool loop; holds `Provider + ToolRegistry + ConversationHistory`.
- CLI/Renderer — subscribes to agent events; handles all output.

---

### ARCH-10 — CLI module has mixed responsibilities

`cli.py` handles argument parsing, REPL loop, slash commands, output formatting, and
`Agent` construction. All in 103 lines of procedural code.

**Correct design:**
- `ArgParser` — pure argument parsing (already separable).
- `SlashCommandHandler` — maps `/cmd` strings to actions.
- `Renderer` — all terminal output (prompt, tool display, streaming, errors).
- `Session` — REPL loop, ties ArgParser + SlashCommandHandler + Renderer + Agent.

---

### ARCH-11 — Hardcoded strings as configuration

Server URL `http://192.168.70.125:11434`, model `qwen2.5-coder:14b`, `max_iterations=20`,
`timeout=120`, `limit=2000` (read_file) — all hardcoded as defaults.

**Correct design:** A `Config` dataclass loaded from YAML + env vars + CLI flags.
Every configurable value has a name, a type, a default, and a source priority.

---

## Part 3 — Design Chain Gaps (New Capabilities Not Yet Designed)

The existing design chain (C4 → UC → SM → SQ → CL) was authored for the v0.1
5-tool CLI agent. The target architecture adds 7 critical new subsystems. None of
them appear in any design artifact. These gaps must be closed before implementation.

| Gap | Missing design artifacts |
|-----|--------------------------|
| Provider abstraction layer (CAP-01, ARCH-01) | C4 component, UC group `PRV`, SQ per UC, CL class |
| Search/glob/grep tools (CAP-02) | UC group `TL` additions (TL-06..TL-08), SQ diagrams |
| Web tools (CAP-03) | UC group `TL` additions (TL-09..TL-10), SQ diagrams |
| Config system (CAP-04, ARCH-11) | C4 component `ConfigLoader`, UC, CL `Config` class |
| Context management / compaction (CAP-05, ARCH-09) | C4 `ContextManager` component, SM for compaction, SQ |
| Session persistence (CAP-06) | C4 `SessionStore`, UC group `SSN`, SQ, ERD (JSON sessions) |
| Safety/permission system (CAP-07) | C4 `PermissionGate`, UC group `SAF`, SQ for each guarded tool |

Additionally, the 6 critical blockers from the design-chain audit (`audit_2026-06-20_design-chain.md`)
remain open: missing entities.md, name divergence, 12 missing SQ diagrams, missing
`ref` frames, missing `break` paths, and missing layer READMEs.

---

## Part 4 — Target Architecture

The redesigned nasim should have the following layer structure. This is the C4
component model to author before any code changes.

```
Developer
    ↓ terminal
CLI Layer
    ArgParser → Config loader (layered: global YAML → project YAML → CLI flags)
    Session   → manages REPL, history, slash commands
    Renderer  → all terminal output (streaming, diffs, tool display, colors)
    SlashCommandHandler
    ↓ AgentEvents
Agent Layer
    AgentOrchestrator  → drives the LLM/tool loop; emits events; stateless
    ConversationHistory → owns messages + token count + compaction trigger
    ContextCompactor   → summarizes old exchanges when budget exceeded
    PermissionGate     → per-tool safety check; blocks or prompts in ask mode
    PlanSession        → holds queued tool calls in plan mode (Phase 2)
    ↓ Provider API
Provider Layer (one implementation per backend)
    Provider (Protocol)
    OllamaProvider
    OpenAIProvider    (Phase 2)
    AnthropicProvider (Phase 2)
    ↓ HTTP
    External LLM API
    ↓ ToolRegistry
Tool Layer
    ToolRegistry     → instance-based; supports dynamic registration (MCP)
    Tool (ABC)       → name, description, parameters, safe, execute()
    FileTools        → ReadFileTool, WriteFileTool, EditFileTool
    SearchTools      → GrepTool, GlobTool, FindFileTool  ← NEW
    ShellTool
    DirTool
    WebTools         → WebFetchTool, WebSearchTool         ← NEW
    MCPToolAdapter   → wraps MCP server tools (Phase 2)    ← NEW
    ↓
    External: Filesystem, Shell, Web, MCP servers
    ↓
Config Layer (cross-cutting)
    ConfigLoader     → global YAML + project YAML + env vars + CLI flags
    Config           → typed dataclass: provider, model, safety_mode, context_budget, mcp_servers
    ↓
Session Layer (cross-cutting)
    SessionStore     → persists/loads message history to ~/.nasim/sessions/
    Session          → session ID, created_at, messages snapshot
```

**Package structure:**
```
nasim/
    __init__.py
    __main__.py
    cli/
        __init__.py
        args.py           ← ArgParser
        repl.py           ← Session (REPL loop)
        renderer.py       ← Renderer
        commands.py       ← SlashCommandHandler
    agent/
        __init__.py
        orchestrator.py   ← AgentOrchestrator
        history.py        ← ConversationHistory
        compactor.py      ← ContextCompactor
        events.py         ← AgentEvent types
        permission.py     ← PermissionGate
    provider/
        __init__.py
        base.py           ← Provider Protocol + factory
        ollama.py         ← OllamaProvider
        openai.py         ← OpenAIProvider (Phase 2)
    tools/
        __init__.py
        base.py           ← Tool ABC, ToolRegistry, ToolResult
        file.py           ← ReadFileTool, WriteFileTool, EditFileTool
        search.py         ← GrepTool, GlobTool, FindFileTool
        shell.py          ← ShellTool
        directory.py      ← DirTool
        web.py            ← WebFetchTool, WebSearchTool
        mcp.py            ← MCPToolAdapter (Phase 2)
    config/
        __init__.py
        loader.py         ← ConfigLoader
        schema.py         ← Config dataclass
    session/
        __init__.py
        store.py          ← SessionStore
        model.py          ← Session dataclass
```

---

## Part 5 — Prioritized Remediation Plan

### Phase 1 — Foundation (must do before any feature work)

| Item | Effort | Unblocks |
|------|--------|----------|
| Create `entities.md` with full target architecture | Low | All design |
| Author C4 (Context + Container + Components per layer) for target arch | Medium | All design |
| Author UC catalog for all 7 new subsystems + fix existing 15 UCs | Medium | All design |
| Resolve name divergence: align C4 / CL / code to entities.md | Low | Design chain |
| Refactor `nasim/` to target package structure (no new features yet) | Medium | All code |
| Implement `Provider` Protocol + `OllamaProvider` + factory | Low | CAP-01 |
| Implement `Tool` ABC + `ToolRegistry` class | Low | CAP-02..03, MCP |
| Implement `Config` dataclass + `ConfigLoader` | Low | CAP-04 |
| Implement `AgentEvent` types + remove `print()` from `agent.py` | Low | CAP-08, ARCH-05 |
| Implement `PermissionGate` (ask mode for shell + write) | Low | CAP-07 |
| Add `logging` configuration | Low | ARCH-07 |

### Phase 2 — Core Capabilities

| Item | Effort | Delivers |
|------|--------|---------|
| `GrepTool`, `GlobTool`, `FindFileTool` | Low | CAP-02 |
| `WebFetchTool`, `WebSearchTool` | Low | CAP-03 |
| `ConversationHistory` + token counting | Medium | CAP-05 |
| `ContextCompactor` (summarize old exchanges) | Medium | CAP-05 |
| `SessionStore` + `--continue`/`--session` flags | Medium | CAP-06 |
| `Renderer` with Rich (colors, tool display, diffs) | Low | CAP-08 |
| `--yes` / `--no-confirm` CLI flags | Low | CAP-07 |
| Complete SQ diagrams for all UCs (12 missing) | High | Design chain |
| Add `break` paths and `ref` frames to all SQ diagrams | Medium | Design chain |

### Phase 3 — Advanced Capabilities

| Item | Effort | Delivers |
|------|--------|---------|
| Plan mode (`PlanSession`, `/plan`, `plan` tool) | Medium | CAP-09 |
| `MCPClient` + `MCPToolAdapter` | Medium | CAP-10 |
| `OpenAIProvider`, `AnthropicProvider` | Low | CAP-01 |
| Session rewind (snapshot before each LLM turn) | Medium | CAP-15 |
| `GitTool` (status, diff, commit) | Low | CAP-21 |
| YAML agent harness (configurable system prompt, tools, model) | Medium | CAP-16 |
| Repo-map (tree-sitter symbol outline) | High | CAP-12 |

### Phase 4 — Differentiators

| Item | Effort | Delivers |
|------|--------|---------|
| Multi-agent / subagent spawning (Task tool) | High | CAP-13 |
| LSP integration | High | CAP-14 |
| RAG / semantic search (SQLite + embeddings) | High | CAP-20 |
| Scheduler / background tasks | High | CAP-17 |
| HTTP server mode (ACP/MCP server) | Medium | CAP-11 |

---

## Part 6 — Design Chain Work Required

Before any Phase 1 code changes, the following design artifacts must be authored
or fixed. They are ordered by the design chain sequence.

1. **`entities.md`** (C-3 from design-chain audit) — create with full target
   architecture: all C4 components, Python modules, actor names, UC group codes.
   This is the prerequisite for everything below.

2. **C4 diagrams** — C4 context is correct. Container diagram needs new containers:
   `Config`, `Session Store`. Component diagrams need splitting by container (R-1)
   AND must add new components for all Phase 1 capabilities. One component diagram
   per container: `c4_nasim_component_cli.puml`, `c4_nasim_component_agent.puml`,
   `c4_nasim_component_provider.puml`, `c4_nasim_component_tools.puml`,
   `c4_nasim_component_config.puml`, `c4_nasim_component_session.puml`.

3. **UC catalog** — current 15 UCs are the baseline. Add:
   - `PRV` group: PRV-01 Initialize Provider, PRV-02 Call Provider Chat,
     PRV-03 Stream Provider Chat.
   - `CFG` group: CFG-01 Load Config, CFG-02 Validate Config.
   - `SSN` group: SSN-01 Save Session, SSN-02 Load Session, SSN-03 List Sessions.
   - `SAF` group: SAF-01 Check Tool Permission, SAF-02 Prompt User Approval.
   - `CTX` group: CTX-01 Track Token Count, CTX-02 Compact Context.
   - `TL` additions: TL-06 Grep Search, TL-07 Glob Files, TL-08 Find Files,
     TL-09 Web Fetch, TL-10 Web Search.
   Fix existing verb violations (R-3) by adding project-level verb extensions to
   `entities.md`.

4. **SM** — current `sm_agent_lifecycle.puml` covers IDLE/THINKING/TOOL_EXECUTING/
   ERROR. Add: COMPACTING (context compaction in progress), AWAITING_APPROVAL
   (permission gate waiting for user), PLANNING (plan mode active).
   Document that this is a process FSM (not entity lifecycle) per R-8.

5. **SQ diagrams** — complete all 12 missing UCs (CLI-01..04, AGT-02..04, LLM-02,
   TL-02..05). Add all new UC SQ diagrams. Fix existing (C-4: add `ref` frames;
   C-5: add `break` paths; R-4: add actors).

6. **CL diagram** — rename to `cl_runtime_model.puml` (not `cl_domain_model` per R-6).
   Add: `Provider` Protocol, `Tool` ABC, `ToolResult`, `Config`, `Session`,
   `AgentEvent` hierarchy, `ContextCompactor`. Align all names to entities.md.

7. **ERD** — add `er_session_store.puml` for the session JSON store (one file per
   session ID). Mark ERD layer as present but minimal (no relational DB; JSON files
   only). Update `docs/README.md` to reflect this (R-9).

8. **READMEs** — add `docs/SQ/README.md` (SQ catalog) and `docs/CL/README.md`
   (class diagram inventory) per R-7.

---

## Appendix — Reference Feature Matrix

| Feature | nasim v0.1 | aider | codex | goose | claude-code | gemini-cli | opencode | kimi-cli |
|---------|-----------|-------|-------|-------|-------------|-----------|---------|---------|
| Multi-provider | ✗ | ✓ (litellm) | ✗ | ✓ (15+) | ✗ | ✗ | ✓ | ✓ |
| grep/glob/search | ✗ | repo-map | ✓ | via MCP | ✓ | ✓ | ✓ | ✓ |
| web fetch/search | ✗ | ✗ | ✓ | via MCP | ✓ | ✓ | ✓ | ✓ |
| Config file | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Context mgmt | ✗ | ✓ (summary) | ✓ (compact) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Session persist | ✗ | partial | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| Safety/permission | ✗ | ✓ | ✓ (sandbox) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rich UI | ✗ | ✓ | ✓ (TUI) | ✓ (TUI) | ✓ | ✓ | ✓ (TUI) | ✓ |
| Plan mode | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| MCP client | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Multi-agent | ✗ | arch mode | ✓ | via ACP | ✓ | A2A | ✗ | ✓ |
| LSP context | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Session rewind | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Voice I/O | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

---

> **Session sync note:** this audit is a working paper. After the design sprint
> produces entities.md, revised C4 diagrams, and the updated UC catalog, extract
> all resolved decisions into `sprint.md`, `entities.md`, and `anti-patterns.md`.
> Delete this file once all findings are closed.
