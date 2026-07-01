# NASIM Competitive Audit & Enhancement Document

**Audit Date:** 2026-07-01  
**Audit Scope:** AI coding assistants in `~/prj/salim/nasim/code/` (31 projects, excluding `nasim/`)  
**NASIM Baseline:** C4 v13.0.0 (Context, Container, Component diagrams), Design Chain frozen through CT/API  
**NASIM Implementation Status:** Pre-alpha — design complete (v13.0.0), zero source code  
**Methodology:** Local directory inspection (READMEs, entry points, architecture files) + published knowledge for opaque projects  
**Version:** v1.0

---

## 1. Executive Summary

NASIM enters a competitive field of ~30+ AI coding assistants at an inflection point. The market has converged on a common interaction pattern — natural language to file changes via agentic tool loops — but architectural quality varies enormously. The most mature competitors (Goose, OpenCode, gemini-cli, qwen-code, codex) have built working systems with 100k+ lines of code, yet nearly all exhibit one or more of: monolithic agent loops, implicit or absent layering, bolted-on safety, shallow context management, and vendor lock-in.

NASIM's core differentiator is **architectural intentionality**. Its C4 diagrams define a strict Controller-Service-Repository (CSR) 3-layer pattern with a single convergence point at AgentController, dedicated cross-cutting services (SafetyService, ContextService, EvaluationService, WireLogRepository, EditStrategyRepository), and 14 purpose-built repositories — all designed before a single line of application code was written. No competitor in the field has published a comparable C4+UC+SM+SQ+ERD+CL+CT design chain of this depth.

The critical risk is execution: NASIM has zero application source code. Every competitor has working, shipped code. The design chain is frozen (v13.0.0) but untested against real implementation constraints. Competitors like Goose (57+ providers, MCP-native tool system, 5-layer security pipeline) and OpenCode (event-sourced sessions, context epochs, Effect-TS architecture) have already solved hard problems that NASIM's design only sketches. Conversely, competitors like claude-code and copilot-cli hide their agent loops behind closed-source paywalls — NASIM's fully open design is a structural advantage for auditability and community trust.

**Competitive stance for v1.0:** Differentiate on architecture quality, safety layering, and multi-client support — but must ship aggressively to avoid being overtaken by the rapid pace of open-source innovation in this space. The most dangerous competitors are not the vendor-locked CLIs but the open frameworks (Goose, OpenCode, Hermes Agent, Cline) that are adding architectural discipline iteration by iteration.

---

## 2. Competitor Landscape Overview

### 2.1 Categorization

| Category | Projects | Count | Maturity |
|----------|----------|-------|----------|
| **Full agentic frameworks (open, production)** | Goose (Rust), OpenCode (TS/Bun), OpenHands (Python), Hermes Agent (Python) | 4 | High — shipped, active development |
| **Vendor-specific CLIs (open core)** | gemini-cli (TS), grok-cli (TS/Bun), qwen-code (TS), kimi-cli (Python), mistral-vibe (Python), codex (Rust) | 6 | High — production, mostly open |
| **Vendor-specific CLIs (closed core)** | claude-code (Node.js), copilot-cli (binary), amazon-q-developer-cli (Rust, archived) | 3 | High — proprietary loops, thin open repos |
| **IDE-extensions with agent loops** | cline (TS/Bun), Roo-Code (TS), kilocode (TS/Effect-TS) | 3 | High — shipped, large ecosystems |
| **Terminal with AI features** | warp (Rust) | 1 | Very High — commercial product |
| **Lightweight/specialized agent CLIs** | aider (Python), code-cli (TS/Bun), claw-code (Py+Rust), crush (Go), plandex (Go), ruflo (TS), fugu (Bash) | 7 | Low-Medium — active but narrower scope |
| **Infrastructure/proxy (not agents)** | free-claude-code (Python), freellmapi (TS), SkeletonAgent (Python) | 3 | N/A — proxy/research |
| **Empty/sparse or non-coding-agent** | MiMo-Code (cloned OpenCode), SWE-agent (Python, research), openinterpreter (Rust, cloned codex) | 3 | Varied — derivatives or research |

### 2.2 Key Architecture Notes by Category

**Goose (Rust, ~3730-line agent.rs):** MCP-native tool system, 57+ LLM providers, 5-layer tool inspection pipeline (Security, Egress, Adversary, Permission, Repetition inspectors), LLM-driven context compaction, `SmartApprove` mode, moved to Linux Foundation. Most comprehensive provider support + security pipeline in the field. Weakness: monolithic agent struct, Rust complexity, full conversation in memory.

**OpenCode (TypeScript/Bun):** Event-sourced session persistence (SQLite), System Context Epochs for mathematical context guarantee, Effect-TS for functional DI, Route-based multi-protocol LLM abstraction, v2 spec-driven architecture. Best-in-class session state management and context integrity. Weakness: still in v2 migration, no sandboxed execution, heavy machinery.

**gemini-cli (TypeScript):** Well-modularized `AgentSession` + `Turn` class architecture, 83 tool files, comprehensive safety checkers (conseca integration), policy engine, checkpointing, MCP client manager, sub-agents. Strongest safety checker framework among open agents. Weakness: Google ecosystem lock-in.

**qwen-code (TypeScript, forked from gemini-cli):** 13 packages, 111 tools, 43 hook files, multi-protocol (OpenAI/Anthropic/Gemini/Qwen/Ollama), auto-memory + auto-skills, sub-agent teams + dynamic workflows, daemon mode for multi-client shared agent, desktop app, 3 SDKs. Most feature-rich open agent. Weakness: forked complexity, feature creep risk.

**codex (Rust/Bazel):** OpenAI Responses API with WebSocket prewarm, multi-agent orchestration (spawn/fork), Landlock + Windows sandbox, memory system, plugins marketplace, realtime WebRTC, collaboration mode. Most sophisticated build + sandbox system. Weakness: OpenAI-only, Bazel complexity, 100+ crates.

**Cline (TypeScript/Bun):** Full SDK (`@cline/agents`, `@cline/core`, `@cline/llms`, `@cline/shared`), browser-safe runtime, cron scheduling, MCP hub, Kanban multi-agent board, WorkOS auth. Best SDK separation and multi-surface support. Weakness: no persistent cross-session memory, VS Code coupling.

**Hermes Agent (Python):** 4486-line `run_conversation` loop, 16+ retry mechanisms, closed learning loop (creates skills from experience), 20+ plugins, multi-platform gateway (Telegram/Discord/Slack/WhatsApp), scheduled automations, 6 terminal backends (local/Docker/SSH/Modal/ etc.), 35+ providers. Most sophisticated single-agent loop and self-improvement system. Weakness: monolithic loop, Python speed, complex setup.

---

## 3. Architecture & Capability Comparison Matrix

| Dimension | NASIM (designed) | Goose | OpenCode | gemini-cli | qwen-code | codex | Hermes Agent | Cline |
|-----------|------------------|-------|----------|------------|-----------|-------|--------------|-------|
| **Lang/Stack** | Python 3.10+ | Rust/Tokio | TS/Bun/Effect-TS | TS/Node.js | TS/Node.js | Rust/Bazel | Python | TS/Bun |
| **Layering** | CSR strict 3-layer | Trait-based, monolithic | Event-sourced, layered | Modular, implicit | Modular, implicit | Crate-based | Monolithic loop | SDK packages |
| **Single Entry Gate** | AgentController | No (Agent.reply) | No (Runner) | No (AgentSession) | No (Turn system) | No (AgentControl) | No (run_conversation) | No (AgentRuntime) |
| **LLM Providers** | litellm (100+) | 57+ native | 3 protocols | Gemini-only | 5 protocols | OpenAI-only | 35+ providers | Multi (via litellm) |
| **MCP Support** | MCP Adapter + MCP Repo | Native (rmcp) | Patched SDK | Yes | Yes | Yes | Yes | Yes |
| **Tool System** | ToolService + registry | MCP extensions | Typed registry | ToolInvocation | 111 tool files | Responses API | 20+ plugins | MCP + native |
| **Safety Layer** | SafetyService (policy pipeline) | 5-inspector pipeline | Permission rules | Safety checkers + policy | Hook system | Guardian + Landlock | File safety + guardrails | Loop detect + rules |
| **Context Mgmt** | ContextService (graph) | LLM-driven compaction | Context Epochs + compaction | Checkpointing | Auto-memory | Context manager | Compression engine | Rules system |
| **Session State** | SessionService + JSONL | In-memory LRU | SQLite event-sourced | Checkpoint files | Session persistence | Memory system | Trajectory recording | Checkpoints |
| **Observability** | WireLogRepository | No | EventV2 event sourcing | No | No | No | Langfuse plugin | Telemetry service |
| **Evaluation** | EvaluationService | No built-in | No built-in | No | No | No | Background review | No |
| **Edit Safety** | EditStrategyRepository | Stop hooks | apply_patch tool | No specific | Diff strategies | Patch safety | No specific | Mistake tracker |
| **Git Depth** | GitRepository | No dedicated | gitpython | Git-aware | Git-aware | Git-aware | Git-aware | Git-aware |
| **Sub-agents** | TaskService (designed) | Via tasks tool | Planned | Sub-agent system | Agent teams | Spawn/fork | Subagent delegation | Kanban board |
| **Multi-client** | 5 adapters → AgentController | CLI + Desktop + API | CLI + Desktop | CLI only | CLI + Web + Desktop + SDKs | CLI + App | CLI + Telegram/Discord/ etc. | CLI + VS Code + Kanban |
| **Code Exists** | No (design only) | Yes (100k+ lines) | Yes (50k+ lines) | Yes (80k+ lines) | Yes (150k+ lines) | Yes (200k+ lines) | Yes (60k+ lines) | Yes (100k+ lines) |
| **C4/Design Docs** | Full C4+UC+SM+SQ+ER+CL+CT | Minimal | v2 Spec docs | Minimal | Minimal | Minimal | Minimal | Minimal |
| **Open Source** | Full | Full (Apache 2.0) | Full (Apache 2.0) | Full (Apache 2.0) | Full (Apache 2.0) | Full (Apache 2.0) | Full (Apache 2.0) | Full (Apache 2.0) |

### 3.1 Key Findings from the Matrix

1. **Layering rigor:** NASIM is the **only** project with a formalized CSR 3-layer pattern and a single controller gate. Every competitor distributes entry points and mixes concerns. This is NASIM's strongest structural differentiator.

2. **Provider support:** NASIM's reliance on litellm (100+ providers) is the right call. Goose's 57 native providers is impressive but unsustainable per-provider maintenance. OpenCode's 3-protocol route system is elegant but narrower.

3. **Safety maturity:** Only Goose (5 inspectors) and codex (Guardian + Landlock) approach NASIM's designed SafetyService depth. Most competitors have ad-hoc permission rules.

4. **Context management:** OpenCode's Context Epochs + auto-compaction is the state of the art. NASIM's ContextService (graph) is well-designed but untested against real token budgets.

5. **Observability:** NASIM's WireLogRepository has no direct equivalent in any competitor. OpenCode's event sourcing is the closest. This is a genuine competitive advantage if implemented.

6. **Evaluation loop:** No competitor has a dedicated EvaluationService. NASIM's design for retry coordination, repetition detection, and turn budget management is unique.

7. **Implementation gap:** NASIM is the only project with zero code. Every other project ships and is battle-tested. This is the single greatest risk.

---

## 4. CAR Audit

### CAR-001: Multi-Client Adapter Architecture & Deployed Protocol Surface

**Theme:** Multi-Client Adapter Robustness

**Challenge:**  
NASIM's C4 Container diagram defines five external clients (CLI, WebApp, DesktopApp, MobileApp, MCP Client) all delegating to a single NASIM Application via HTTP/JSON+SSE or stdio. This single-container, multi-adapter design is architecturally clean, but **none of these adapters exist in code**. Every competitor with multi-surface support (qwen-code: CLI + Web + Desktop + SDKs + IM; Cline: CLI + VS Code + Kanban; Goose: CLI + Desktop + API; Hermes Agent: CLI + Telegram + Discord + Slack + WhatsApp) has already shipped and debugged their protocol surfaces. qwen-code's daemon mode (`qwen serve`) serves multiple concurrent clients from one agent process via ACP/HTTP+SSE — the exact pattern NASIM designed.

The risk is that NASIM's design assumes a protocol surface (HTTP/JSON+SSE + stdio) without validation against real constraints: concurrent session handling, SSE reconnection, MCP protocol version drift, and cross-client session isolation.  
**Severity:** High  
**Business Impact:** Delayed time-to-market for multi-surface support; competitors already own the multi-surface narrative.

**Action:**  

1. **Implement CLI Adapter first** as the bootstrap adapter (Milestone 0 priority) using `click` + `rich` with REPL mode, arg parsing, and slash commands as specified in `docs/UC/cli_events.puml`. This is the lowest-risk surface and validates the AgentController contract.

2. **Implement a minimal HTTP Adapter** (FastAPI) with SSE streaming for `/v1/chat` and `/v1/tools` endpoints concurrently in Milestone 1. This enables WebApp, DesktopApp, and MobileApp clients without incremental agent-side work (they all share the HTTP Adapter).

3. **Add MCP Adapter** in Milestone 2 as a separate server process that translates MCP tool calls into AgentController dispatches. Use the official `mcp` Python SDK. Expose via stdio (for MCP Client integration) and SSE (for remote MCP clients).

4. **Preserve CSR layering:** All three adapters call `AgentController.dispatch(request)` only. No adapter ever calls a Service or Repository directly. The AgentController validates the request, selects the appropriate Service, and returns the result.

5. **Add UC-001.1 "Multi-Client Concurrent Session Isolation"** to the UC layer: ensure each adapter-bound session has independent state, cancellation, and resource tracking. This may require a `SessionRegistry` in SessionService that maps `(adapter_id, session_id) -> Session`.

**Result:**  
NASIM ships with three working adapters by Milestone 2, matching qwen-code and Goose multi-surface support while maintaining strict CSR layering (unlike any competitor). The single AgentController convergence point becomes a demonstrable strength: adding a new client (e.g., Slack bot) requires only a new Adapter + registration, no agent loop changes.  
**C4 Impact:** No diagram changes — the three adapters and AgentController already exist in the Component diagram at lines 34–37. The `SessionRegistry` would be an internal addition to SessionService (Component diagram, line 44).  
**Traceability:** C4 Component: cli_adp, http_adp, mcp_adp, agent_ctrl; UC: cli_events, session lifecycle.

---

### CAR-002: Context Graph Construction, Truncation & Injection Pipeline

**Theme:** Context Intelligence & Memory

**Challenge:**  
NASIM's ContextService (graph-based context pipeline: construction, truncation, distillation, injection, compaction) is well-named but unimplemented. The competitive landscape has made significant advances: OpenCode's System Context Epochs provide a mathematical guarantee of what the model has seen across compaction boundaries; Goose's LLM-driven compaction uses the model itself to summarize conversation history with tool-pair batching (groups of 10); gemini-cli has checkpointing with token caching; qwen-code has auto-memory extraction and auto-skill creation. Context management is arguably the hardest unsolved problem in AI coding agents — every competitor has production scars from context window overflows, truncated tool call histories, and silent information loss.

NASIM's design currently lacks specifics on: (a) when compaction triggers, (b) how the graph is constructed from conversation turns + tool results + repo intel, (c) how distilled summaries are reinjected, (d) what survives compaction vs what is discarded. Competitors that solve context well (OpenCode, Goose) have a measurable task-success advantage.  
**Severity:** Critical  
**Business Impact:** Directly impacts task success rate, the single most important user-facing metric.

**Action:**  

1. **Define `ContextWindowBudget`** as a Pydantic model in ContextService: `{ max_tokens, current_usage, compaction_threshold: 0.8, strategy: "llm_summarize" | "rolling_truncate" | "epoch_checkpoint" }`. The threshold triggers compaction automatically.

2. **Implement three compaction strategies** selectable per session:
   - `rolling_truncate` (fast, no LLM cost): trim oldest turns, keep system prompt + recent N turns + tool results. Safe default for Milestone 0.
   - `epoch_checkpoint` (OpenCode-inspired): after compaction, create a "context epoch" summary — a structured `ContextEpoch { summary, tool_results_summary, file_map, timestamp }` injected as a system message. The epoch replaces all previous turns in model-visible history.
   - `llm_summarize` (Goose-inspired): call the LLM to produce a structured summary of the conversation so far. Expensive but preserves more nuance. Reserve for high-value sessions.

3. **Build the ContextGraph** as a DAG of `ContextNode`s: each turn, tool result, repo map, and memory entry is a node with type, token_count, timestamp. The graph supports:
   - `select_path(llm_query)` — choose the most relevant subgraph for injection (contrast with naive truncation)
   - `compact()` — replace a subgraph with one summary node, adjusting token accounting
   - `inject(memory_entries, repo_map)` — weave memory and repo intelligence into the graph at appropriate attachment points

4. **Implement `repo_map_builder`** in RepoIntelligenceRepository (using tree-sitter) to produce a ranked map of the most relevant files for the current task. Aider's `repomap.py` is the proven reference here (~44% of aider's code was self-written using this technique).

5. **Preserve CSR layering:** ContextService receives the full conversation from TaskService, constructs the graph, queries RepoIntelligenceRepository for the repo map, queries MemoryRepository for relevant memories, applies the selected compaction strategy, and returns the assembled context to TaskService. TaskService never touches the graph directly.

**Result:**  
NASIM ships with a configurable, three-strategy context pipeline that matches OpenCode's epoch system and Goose's LLM-driven compaction, with the unique addition of a graph-based relevance selector. This is a clear competitive advantage in task success rate for long-running sessions.  
**C4 Impact:** ContextService already exists (Component diagram, line 47). The ContextGraph, ContextNode, and ContextWindowBudget types are Service-layer internals — no diagram change needed.  
**Traceability:** C4 Component: context_svc, repo_intel_repo, memory_repo; UC: context pipeline use cases; SM: context compaction state machine.

---

### CAR-003: Multi-Layered Safety Pipeline with Sandbox Validation

**Theme:** Safety Hardening

**Challenge:**  
NASIM's SafetyService is designed as a "policy pipeline" with permission gating, injection scanning, and egress inspection. This is architecturally sound but lacks the concrete multi-layered approach that Goose and codex have proven in production. Goose has 5 distinct inspectors (Security, Egress, Adversary, Permission, Repetition) running in a pipeline before tool execution. Codex has a dedicated `Guardian` subsystem with approval requests, review sessions, and policy templates — plus native OS-level sandboxing (Landlock on Linux, Windows sandbox). Hermes Agent has 623 lines of `file_safety.py` protecting SSH keys, credentials, and config files.

Competitors that ship with shallow safety (aider: git auto-commit only; claude-code: approval prompts only; copilot-cli: "nothing happens without approval") create real-world incidents. NASIM's safety-first design is a differentiator, but only if implemented with comparable depth.  
**Severity:** Critical  
**Business Impact:** Safety failures erode trust in the entire category. A single high-profile incident (e.g., accidental `rm -rf /` or credential leak) can destroy adoption.

**Action:**  

1. **Implement a 5-stage SafetyInspector pipeline** inside SafetyService, matching Goose's architecture but respecting CSR:
   - `Stage 1 — InjectionScanner`: scan tool call parameters for prompt injection patterns, path traversal, shell metacharacters. Reject with classified error.
   - `Stage 2 — PermissionEvaluator`: evaluate `(action, resource)` against session's permission rules (allow/deny/ask). Use wildcard matching with last-match-wins semantics (matching OpenCode's PermissionV2).
   - `Stage 3 — EgressInspector`: inspect tool outputs for sensitive data (API keys, tokens, credentials) before returning to TaskService. Redact or block based on policy.
   - `Stage 4 — RepetitionDetector`: track tool call signatures (hash of action + parameters) across a sliding window. If same signature repeats N times within M turns, escalate to soft warning, then hard stop (matching Cline's loop-detection.ts and Crush's SHA-256 approach).
   - `Stage 5 — AdversarialReview` (optional, LLM-cost): call a secondary (cheaper) LLM to review the tool call and its expected outcome before execution. Expensive but valuable for high-risk operations (file delete, config modification, network access).

2. **Implement sandboxed execution** as specified in the C4: SandboxRepository wraps `subprocess` with timeout, cgroup isolation, and filesystem scoping. The Sandbox Runtime (external system) uses `bubblewrap` (Linux) or `sandbox-exec` (macOS) for OS-level isolation. For Milestone 0, a `NoSandbox` fallback with explicit user warning is acceptable.

3. **Implement the `"ask"` approval mode** (not just allow/deny): when PermissionEvaluator returns `ask`, SafetyService suspends the tool execution, sends a structured approval request to the user via the active adapter (CLI: inline prompt; HTTP: pending task status), and waits for explicit approval or timeout.

4. **Define `FileSafetyRules`** as a priority list of protected paths and patterns: `~/.ssh/*`, `~/.aws/credentials`, `~/.config/*/tokens*`, `/etc/passwd`, etc. These are always blocked or require `ask` regardless of other permission rules.

**Result:**  
NASIM's SafetyService becomes the deepest safety implementation in any open-source AI coding agent, matching Goose's 5-inspector pipeline while adding SandboxRepository as an extra physical layer. The `ask` approval mode and `FileSafetyRules` provide practical day-to-day protection that even Goose currently lacks.  
**C4 Impact:** SafetyService (Component diagram, line 46) gains internal pipeline structure. SandboxRepository (line 58) and Sandbox Runtime (Context/Container diagrams) already exist. No new components needed.  
**Traceability:** C4 Component: safety_svc, sandbox_repo, fs_repo; SM: safety state machine; UC: safety use cases; SQ: safety sequence diagrams (SafetyService lifeline).

---

### CAR-004: Tool Registry, Dynamic Loading & MCP Extensibility

**Theme:** Tool Extensibility via MCP

**Challenge:**  
NASIM's ToolService is designed as a "tool registry, parameter validation, execution dispatch" with MCP Repository for extension tools. The C4 distinguishes built-in tools (registered by ToolService) from MCP tools (discovered via MCP Repository). This is conceptually clean but lacks detail on: (a) how tools are dynamically loaded/reloaded at runtime, (b) how MCP tool discovery interacts with the safety pipeline, (c) what happens when MCP servers disconnect or error.

The competitive landscape has converged on MCP as the universal tool protocol. Goose is MCP-native (all tools are MCP extensions, discovered via `tools/list`). Cline has MCP hub with stdio/SSE support. gemini-cli has an MCP client manager. Every major competitor supports MCP. NASIM must ship MCP support that is at least as robust as Goose's, with the added architectural benefit of CSR layering (Goose's ExtensionManager is a single large module with mixed concerns).  
**Severity:** High  
**Business Impact:** MCP is becoming the de facto standard for tool extensibility. Without first-class MCP support, NASIM cannot meaningfully compete for the "extensible agent" use case.

**Action:**  

1. **Implement ToolService** with a two-tier registry:
   - **Built-in tools** (bash, read, write, edit, glob, grep, web_fetch, web_search, question, task, plan, evaluate): registered at startup via `ToolRegistry.register(name, schema, handler)`. These have first-class parameter validation and error handling.
   - **MCP tools** (discovered dynamically): MCP Repository connects to MCP Servers via stdio or SSE, calls `tools/list`, caches the results. Each MCP tool is wrapped in an internal `MCPToolAdapter` that delegates execution back to MCP Repository.

2. **Implement live reload** for MCP tools: MCP Repository monitors server connections. On `tools/list` change notification (or periodic polling), updates the registry without agent restart. This is critical for development workflows where MCP servers are added/modified during a session.

3. **Implement tool lifecycle hooks** in ToolService:
   - `before_tool(tool_name, params) -> ToolParams | Reject`: runs through SafetyService pipeline. If rejected, returns a structured error.
   - `after_tool(tool_name, params, result) -> ToolResult`: runs post-execution safety checks (egress inspection), logs to WireLogRepository.
   - `on_tool_error(tool_name, params, error) -> bool`: decides whether to retry (transient errors) or fail permanently.

4. **Define tool permission categories** for the safety pipeline:
   - `filesystem_read` (read, glob, grep)
   - `filesystem_write` (write, edit, apply_patch)
   - `shell_exec` (bash)
   - `network` (web_fetch, web_search, mcp_tools)
   - `agent_control` (task, plan, evaluate)
   Each category has independent allow/deny/ask configuration.

**Result:**  
NASIM ToolService + MCP Repository ships with live reload, lifecycle hooks, and safety integration — capabilities that are distributed across Goose's ExtensionManager, permission system, and hook system without clear separation. The CSR layering (ToolService → MCPRepository → MCP Server) is visibly cleaner than any competitor's tool architecture.  
**C4 Impact:** ToolService (line 42) and MCPRepository (line 62) already exist. Add internal `ToolRegistry`, `MCPToolAdapter` types as Service/Repository internals. No diagram change needed.  
**Traceability:** C4 Component: tool_svc, mcp_repo, safety_svc, wire_log_repo; SM: MCP client/server state machines; UC: MCP use cases.

---

### CAR-005: Sub-Agent Orchestration & Task Decomposition Engine

**Theme:** Planning, Decomposition & Sub-Agent Orchestration

**Challenge:**  
NASIM's TaskService is described as the "agentic loop: LLM call, tool dispatch, context assembly, **subagent orchestration**." This sub-agent orchestration capability is a key differentiator — most competitors delegate to sub-agents via a simple `task` tool (Goose, grok-cli, aider's architect mode). Only qwen-code (agent teams + dynamic workflows), codex (spawn/fork control), and Hermes Agent (Python RPC subagent delegation) have sophisticated sub-agent systems.

NASIM's C4 does not specify how TaskService spawns, monitors, or coordinates sub-agents. Without this, TaskService is just a "loop" — indistinguishable from simpler competitors.  
**Severity:** High  
**Business Impact:** Sub-agent orchestration is the primary mechanism for handling complex multi-file, multi-step tasks that exceed a single LLM turn's capacity. Without it, NASIM is limited to single-threaded task execution.

**Action:**  

1. **Design `SubAgent` as a first-class entity** in TaskService (not just a tool call):
   ```
   SubAgent:
     id: UUID
     parent_task_id: UUID
     goal: str
     status: pending | running | completed | failed | needs_review
     context_subgraph: ContextNode[]  # relevant context, not full parent context
     tool_allowlist: PermissionCategory[]  # restricted tool set
     max_turns: int  # default 25
     result: str | None
   ```

2. **Implement three sub-agent spawning modes:**
   - **`delegate(goal, context, tool_allowlist)`** — create a sub-agent with a subset of tools and context. Sub-agent runs independently (can be parallel). Parent receives result when done.
   - **`fork(task_point)`** — duplicate the parent agent's state at a decision point, run both branches in parallel, compare results (codex-inspired). Useful for exploring alternative implementations.
   - **`review_task(goal)`** — spawn a read-only sub-agent (plan or architect mode) that analyzes the codebase and returns a plan without making changes. Parent reviews and optionally executes the plan.

3. **Implement `SubAgentCoordinator`** inside TaskService:
   - Maintains a pool of active sub-agents per session
   - Manages resource limits (max parallel sub-agents, total sub-agent turns per session)
   - Handles sub-agent cancellation when parent task completes or errors
   - Propagates safety constraints: sub-agents inherit parent's permission rules but can be further restricted
   - Logs all sub-agent interactions to WireLogRepository

4. **Preserve CSR layering:** TaskService owns sub-agent coordination. Each sub-agent is a lightweight instance of the same TaskService loop (reuses context assembly, tool dispatch, safety pipeline) with restricted configuration. No new layer or component needed.

**Result:**  
NASIM ships with structured sub-agent orchestration that matches qwen-code's agent teams and exceeds Goose's simple `task` tool. The `fork` mode is unique in the open-source landscape. Sub-agent coordination becomes an architectural feature, not a tool call hack.  
**C4 Impact:** TaskService (Component diagram, line 42) gains `SubAgentCoordinator` as internal structure. SubAgent entity may trigger a new UC group (`UC/subagent/`) and SM diagrams.  
**Traceability:** C4 Component: task_svc, context_svc, safety_svc, wire_log_repo; SM: sub-agent lifecycle state machine; UC: sub-agent delegation use cases.

---

### CAR-006: Evaluation Service — LLM Review, Retry Coordination & Turn Budget Management

**Theme:** Evaluation & Self-Improvement Loops

**Challenge:**  
NASIM's EvaluationService is designed for "task evaluation: success checks, LLM review, retry coordination, repetition detection, turn budget management." This is unique — **no competitor has a dedicated evaluation service**. Most competitors handle evaluation ad-hoc: aider has `auto_lint` and `auto_test`; Hermes Agent has background review for skill creation; SWE-agent's RetryAgent has a `ScoreRetryLoop`. None have a centralized evaluation engine that coordinates retries across the full task lifecycle.

This is NASIM's most architecturally distinct advantage. However, it exists only as a name in the C4 diagram. Without implementation, it provides zero value.  
**Severity:** Medium (but high competitive differentiation value)  
**Business Impact:** A working EvaluationService that measurably improves task success rates is a narrative-defining feature — "NASIM agents that check their own work."

**Action:**  

1. **Implement `EvaluationResult`** as a Pydantic model:
   ```python
   class EvaluationResult:
     task_id: str
     status: Pass | Fail | Partial | NeedsReview
     criteria: list[EvaluationCriterion]
     # each criterion: { description, status, evidence, confidence }
     llm_review: str | None  # LLM-generated critique
     suggested_retry: bool  # should TaskService retry?
     retry_strategy: FixStrategy | None  # specific fix parameters
     token_cost: int
     timestamp: datetime
   ```

2. **Implement three evaluation methods** (selectable per task):
   - **`heuristic_check(task_goal, tool_results, file_diffs)`** — rule-based checks: did the agent complete the requested file changes? Are there syntax errors? Do tests pass? Fast, zero LLM cost.
   - **`llm_review(task_goal, conversation_trace, file_diffs)`** — call a secondary LLM (cheaper model, e.g., GPT-4o-mini or Claude Haiku) to review the outcome against the goal. Emulates "code review by a colleague." Expensive but catches semantic errors.
   - **`test_verification(task_goal, test_commands)`** — run the project's test suite on the resulting code. Report pass/fail per test file. Integration with `pytest`, `npm test`, etc.

3. **Build the retry coordination engine** in EvaluationService:
   - Receives `(task_goal, attempt_number, previous_results)` from TaskService
   - Returns `EvaluationResult` with `suggested_retry: bool`
   - Implements `max_retries` and `retry_budget` per session
   - Implements **escalating review**: first retry uses heuristic, second uses LLM review, third requires user approval
   - Repetition detection: if same tool call sequence appears across retries without meaningful variation, EvaluationService detects the loop and recommends a different approach

4. **When EvaluationService recommends retry**, it provides structured feedback to TaskService: "goal X was not achieved because Y; suggest trying Z approach." TaskService injects this as additional context in the next LLM call turn.

5. **Preserve CSR layering:** EvaluationService is called by TaskService after each "complete task" signal or after tool execution batches. It never calls repositories directly — TaskService provides the data. It returns recommendations; TaskService decides whether to act on them.

**Result:**  
NASIM ships with the industry's first dedicated EvaluationService, providing measurable task success improvements through heuristic + LLM + test-based verification with intelligent retry coordination. This is a narrative-defining differentiator vs every competitor listed in this audit.  
**C4 Impact:** EvaluationService (Component diagram, line 48) gains internal `EvaluationResult`, `EvaluationCriterion`, and `RetryCoordinator` types. New UC group may be needed for evaluation/retry flows.  
**Traceability:** C4 Component: eval_svc, task_svc, llm_repo; SM: evaluation state machine; UC: evaluation use cases.

---

### CAR-007: Wire Log Repository — Observability, Replay & Session Forking

**Theme:** Observability & Replayability

**Challenge:**  
NASIM's WireLogRepository is an "append-only event store: interaction recording, replay, session forking, checkpointing." This is another unique C4 element — no competitor has an equivalent dedicated observability component. OpenCode's event sourcing (EventV2) is conceptually similar but is used for session persistence rather than observability/replay. Goose's conversation is in-memory only. Most competitors log only to console or have no replay capability.

The absence of wire logging in every competitor creates a real debugging gap: when a complex multi-turn task fails, developers cannot replay the exact sequence of LLM calls, tool executions, and intermediate states to diagnose the failure. For NASIM's target audience (safety-conscious enterprise and power users), this is a significant differentiator.  
**Severity:** Medium (high differentiation value)  
**Business Impact:** Debugging capability directly affects developer trust and iteration speed. Wire logging enables the "time-travel debugging" that no competitor offers.

**Action:**  

1. **Define the WireLog event schema** (append-only JSONL to `~/.nasim/sessions/<id>/wire.jsonl`):
   ```json
   {
     "event_id": "uuid",
     "session_id": "uuid",
     "timestamp": "ISO8601",
     "event_type": "llm_request | llm_response | tool_call | tool_result | safety_check | compaction | session_event",
     "sequence_num": 42,
     "payload": { /* type-specific content, truncated to max_size */ },
     "token_count": 1500,
     "parent_event_id": "uuid | null"  // causal chain
   }
   ```

2. **Implement WireLogRepository methods:**
   - `record(event)` — append to wire.jsonl (fire-and-forget, never blocks the agent loop)
   - `replay(session_id, from_seq, to_seq)` — stream events for replay
   - `fork(session_id, new_session_id, from_seq)` — create a new session that starts from a checkpoint in the wire log. All events after `from_seq` in the original session become the initial context for the forked session (enabling "what if I had made a different choice?" debugging).
   - `search(query)` — search across wire logs for specific events, tool calls, or LLM responses (requires indexing in HistoryRepository).
   - `checkpoint(session_id, label)` — mark a key event as a named checkpoint (e.g., "before risky file edit") for later navigation.

3. **WireLogRepository interacts with HistoryRepository** to build a search index of wire events (SQLite FTS5 for full-text search across LLM responses and tool results). This enables the `search` operation without scanning raw JSONL files.

4. **Implement a `replay` CLI command** (`nasim replay <session_id> [--from N] [--speed 2x]`) that reads wire events, reconstructs the session timeline, and plays it back in the terminal with highlighted LLM calls and tool results. This is a UX differentiator.

5. **Preserve CSR layering:** WireLogRepository is called by TaskService (records agent-provider-tool interactions) and SessionService (forks sessions, checkpoints turns). It owns the wire_log_store (Data Store). No other service or controller writes to it.

**Result:**  
NASIM ships with an append-only event store that enables full session replay, time-travel debugging, and session forking — capabilities that no competitor offers. The `replay` CLI command becomes a signature UX feature.  
**C4 Impact:** WireLogRepository (Component diagram, line 64) and wire_log_store (line 72) already exist. Add `checkpoint` and `search` methods to the component's interface — no diagram change.  
**Traceability:** C4 Component: wire_log_repo, history_repo, task_svc, session_svc; UC: session forking and replay use cases; SQ: wire logging sequence diagrams.

---

### CAR-008: Edit Strategy Repository — Staged Edits, Unified Diff & Sandbox Validation

**Theme:** Edit Reliability

**Challenge:**  
NASIM's EditStrategyRepository is designed for "diff staging, computation, and safe application: staged edits, sandboxed validation." This is a sophisticated approach that **no competitor fully implements**. Competing approaches:
- **aider**: applies edits directly (editblock, wholefile, udiff formats) with auto-commit for rollback. No staging or sandbox validation.
- **OpenCode**: uses `apply_patch` tool with `unified_diff` format. No sandbox validation before application.
- **Goose**: uses MCP file tools directly. Stop hooks can block unsafe writes, but no diff staging.
- **gemini-cli**: file tools execute directly. No staging layer.
- **Roo-Code**: has `DiffViewProvider` for preview, `DiffStrategy` abstraction, but no sandbox validation.

Edit errors (malformed diffs, partial writes, encoding corruption) are a persistent source of agent failures. NASIM's designed approach — stage diffs, validate in sandbox, apply only on success — directly addresses this but is the most ambitious edit strategy in the field.  
**Severity:** High  
**Business Impact:** Edit reliability is a top-3 user complaint about AI coding agents. Solving it is a measurable competitive moat.

**Action:**  

1. **Implement the three-phase edit cycle** in EditStrategyRepository:
   - **Phase 1 — Stage**: Receive `(file_path, old_content, new_content)` or `(file_path, unified_diff)` from ToolService. Compute the diff using Python's `difflib.unified_diff`. Store the staged edit in a session-local staging area (`~/.nasim/sessions/<id>/staging/`).
   - **Phase 2 — Validate**: Apply the staged edit to a **sandboxed copy** of the file (SandboxRepository provides isolated filesystem). If the file doesn't exist yet, create it in sandbox. Run configurable pre-commit checks: syntax parsing (tree-sitter if available), linting (ruff for Python, eslint for JS), format validation. If any check fails, return structured errors to ToolService.
   - **Phase 3 — Apply**: If validation passes, apply the diff to the real file. Create a git commit if configured. Return the final file content and diff.

2. **Implement conflict detection**: Before Stage phase, check if the file has been modified outside NASIM (e.g., by the user or another tool) since the last read. If so, flag as conflict — don't silently overwrite. Provide options: `overwrite`, `rebase_auto`, `rebase_manual`.

3. **Implement `diff_history`** per session: track all applied diffs in a local JSONL file. Support `undo_last_edit()` (inverse diff) and `rollback_to_checkpoint(label)`. This is independent of git — useful for projects without version control.

4. **Implement multiple diff strategies** selectable per project:
   - `unified_diff` (default): standard line-based diff, best for most changes
   - `search_replace_block`: for targeted replacements within large files (matching aider's editblock)
   - `whole_file`: for small files or complete rewrites

5. **Preserve CSR layering:** EditStrategyRepository receives abstract edit operations from ToolService. It calls SandboxRepository for validation, FilesystemRepository for real file I/O. It never calls SafetyService — that happens earlier in the pipeline (ToolService → SafetyService).

**Result:**  
NASIM ships with the most sophisticated edit strategy in any open-source AI coding agent, with sandboxed validation, conflict detection, multi-strategy support, and diff history with undo. This directly addresses a top-3 user pain point.  
**C4 Impact:** EditStrategyRepository (Component diagram, line 59) already exists. The three-phase cycle and diff_history are internal. New UC group may be needed for edit lifecycle.  
**Traceability:** C4 Component: edit_strategy_repo, sandbox_repo, fs_repo; SM: diff staging state machine; UC: edit strategy use cases.

---

### CAR-009: LLM Provider Abstraction — Capability Routing, Fallback Chains & Streaming Reliability

**Theme:** LLM Routing & Cost/Quality Optimization

**Challenge:**  
NASIM's LLMRepository wraps litellm for "LLM API calls + model routing: streaming, fallback chains, capability-based model selection, task classification." litellm is the right choice (supports 100+ providers, function calling, streaming). However, the competitive landscape has diverged on provider abstraction quality:
- **Goose** has 57+ native provider implementations — unsustainable but currently the best coverage.
- **OpenCode** has 3 protocol adapters (anthropic-messages, openai-compatible-chat, openai-responses) — elegant but narrow.
- **gemini-cli** is Gemini-only — zero flexibility.
- **qwen-code** has 5 protocols — good coverage.
- **codex** is OpenAI Responses API only.

NASIM's C4 design includes `task_classification` as an LLMRepository capability — the agent analyzes the task and selects the best model (cheap for simple edits, expensive for complex planning). This is advanced and no competitor has it as a built-in repository feature. However, litellm's abstraction has quirks (streaming reliability, provider-specific parameter handling) that NASIM must handle.

**Severity:** Medium  
**Business Impact:** Provider flexibility directly affects user cost and model choice. Users who are locked into a single provider (gemini-cli, codex) cannot optimize for cost/quality.

**Action:**  

1. **Implement `ModelRouter`** inside LLMRepository:
   - Maintains a configurable model capability matrix: `{ model_id, provider, capabilities: [chat, tools, streaming, thinking, image_input, code_review], cost_per_1k_input, cost_per_1k_output, context_window }`
   - `select_model(task_classification, preferences)` — given task type (chat, tool_call, code_review, plan, edit), user preferences (cost ceiling, quality floor), and required capabilities, returns the optimal model.
   - `fallback_chain(models, task)` — iterates through a list of models, trying each until one succeeds. Handles rate limits, authentication errors, and content policy violations.

2. **Implement `TaskClassifier`** (simple heuristic or LLM call):
   - Classifies incoming tasks into: `chat`, `simple_edit`, `complex_edit`, `planning`, `code_review`, `debugging`, `research`
   - Maps classifications to model preferences: e.g., `planning` → Claude Opus 4 or GPT-5; `simple_edit` → Claude Haiku or GPT-4o-mini
   - Classification can be overridden by user preference

3. **Implement streaming reliability** layer:
   - Retry on partial stream failures (network blips, server errors)
   - Timeout per chunk and total timeout
   - Graceful degradation: if streaming fails, fall back to non-streaming completion
   - Token tracking: count tokens sent/received per call per session

4. **Implement structured output support**: leverage litellm's `response_format` parameter for tools that require JSON output. Validate structured output schema before returning to TaskService.

5. **Preserve CSR layering:** LLMRepository is called by TaskService only. It abstracts all provider-specific details behind `async def complete(messages, tools, config) -> CompletionResult`. No other component touches LLM providers directly.

**Result:**  
NASIM ships with capability-based model routing, task-driven model selection, and robust fallback chains — capabilities that exceed Goose's 57 providers (which lack routing intelligence) and match qwen-code's multi-protocol support with added cost/quality optimization.  
**C4 Impact:** LLMRepository (Component diagram, line 57) gains `ModelRouter` and `TaskClassifier` as internal modules. No diagram change.  
**Traceability:** C4 Component: llm_repo, task_svc, config_svc; UC: provider routing use cases; SM: provider fallback state machine.

---

### CAR-010: Git Integration Depth & Long-Running Task State Management

**Theme:** Git Integration & Session Resilience

**Challenge:**  
NASIM's GitRepository handles "Git operations: status, diff, commit, branch." This is the minimum viable git integration — every competitor has this. What NASIM lacks is depth: automatic branch-per-task, commit signing, PR creation, conflict resolution during multi-turn edits, and session persistence across agent restarts.

The competitive baseline:
- **aider**: auto-commit every change, sensible commit messages, `git undo` command. Best git UX in the field.
- **OpenCode**: gitpython integration but no special git UX.
- **grok-cli**: git worktrees for parallel experimentation.
- **codex**: full git integration with sandboxing.

NASIM's sessions are JSONL-based, but the C4 does not specify how sessions survive agent restarts, crashes, or network disconnections. OpenCode's SQLite-backed sessions with durable inbox provide crash recovery — NASIM must match this.  
**Severity:** Medium  
**Business Impact:** Users lose trust if sessions are lost on crash. Git integration is table-stakes for a coding agent.

**Action:**  

1. **Expand GitRepository** with:
   - `auto_branch(task_description)` — create a feature branch named `nasim/{timestamp}-{slug}` for each task. Switch back on completion.
   - `auto_commit(message)` — commit all staged edits with structured message (task ID, files changed, description). Never commit half-applied changes.
   - `create_pr(branch, title, body)` — open a GitHub/GitLab PR from the task branch. Integrate with `gh` CLI or GitPython.
   - `diff_between(checkpoint_a, checkpoint_b)` — compute file-level diffs for review.
   - `conflict_check(base_branch)` — before applying edits, check if the target branch has diverged. Warn user.

2. **Implement session crash recovery** in SessionService:
   - On startup, scan `~/.nasim/sessions/` for sessions with status `running` or `interrupted`.
   - For each interrupted session, compute: last successful checkpoint, pending tool calls, unapplied edits.
   - Present recovery options to user: `(r)esume`, `(f)ork to new session`, `(d)iscard`.
   - WireLogRepository's `fork` operation is used for the `(f)` option.

3. **Implement periodic session checkpointing**: SessionService auto-checkpoints after every N turns or M tool calls. Checkpoint includes full conversation state, open tool calls, pending edits, and wire log sequence number. Stored in HistoryRepository.

4. **Preserve CSR layering:** GitRepository is called by ToolService (for auto-commit) and TaskService (for branch creation). SessionService handles recovery independently. No changes to controller or service boundaries.

**Result:**  
NASIM ships with aider-level git UX (auto-commit, meaningful messages) plus branch-per-task and PR creation — exceeding aider's git integration. Session crash recovery matches OpenCode's durability.  
**C4 Impact:** GitRepository (Component diagram, line 61) gains new methods. SessionService (line 44) gains recovery logic. No new components.  
**Traceability:** C4 Component: git_repo, session_svc, history_repo, wire_log_repo; SM: session lifecycle state machine; UC: git integration use cases.

---

## 5. Prioritized Enhancement Backlog

| CAR-ID | Theme | Priority | C4 Impact | Rationale | Type |
|--------|-------|----------|-----------|-----------|------|
| CAR-001 | Multi-Client Adapt | **P0** | None (components exist) | First shipping code validates entire architecture | Quick-win |
| CAR-002 | Context Pipeline | **P0** | None (service-internal) | Directly impacts task success rate — the #1 UX metric | Strategic |
| CAR-003 | Safety Pipeline | **P0** | None (service-internal) | Non-negotiable for trust; safety is NASIM's brand | Strategic |
| CAR-004 | Tool/MCP Registry | **P0** | None (components exist) | MCP is table-stakes for extensibility | Quick-win |
| CAR-005 | Sub-Agent Orchestration | **P1** | None (service-internal) | High differentiation, complex but building-block independent | Strategic |
| CAR-008 | Edit Strategy | **P1** | None (component exists) | Top-3 user pain point; sandbox validation is a moat | Strategic |
| CAR-009 | LLM Routing | **P1** | None (repo-internal) | Cost/quality optimization; litellm makes this tractable | Quick-win |
| CAR-007 | Wire Log/Replay | **P2** | None (component exists) | High differentiation but not blocking v1.0 | Strategic |
| CAR-006 | Evaluation Service | **P2** | None (service exists) | Unique differentiator but can be layered after core loop works | Strategic |
| CAR-010 | Git Integration | **P2** | None (component exists) | Table-stakes; current design is minimal and functional | Quick-win |

### Priority Rationale

**P0 (Mandatory for v0.1-alpha):** CAR-001, CAR-002, CAR-003, CAR-004. These are the minimum viable architecture: adapters that validate the CSR pattern, context that makes the agent useful, safety that makes it trustworthy, and tools that make it extensible. Without these, NASIM is indistinguishable from a toy.

**P1 (v0.2-beta):** CAR-005, CAR-008, CAR-009. Sub-agents enable complex tasks; edit strategy addresses the #3 user complaint; LLM routing delivers cost savings. These ship in the second wave once the core loop is validated.

**P2 (v0.5+):** CAR-006, CAR-007, CAR-010. Wire logging and evaluation are narrative-defining differentiators but not blocking initial adoption. Git depth is incremental improvement over a working foundation.

---

## 6. Proposed C4 Diagram Updates

### 6.1 No Changes Required to Existing Diagrams

All 10 CARs operate within the existing C4 v13.0.0 boundaries:

- **Context Diagram** (c4_nasim_context.puml): All 8 external systems and 1 person remain valid. No new external systems needed.
- **Container Diagram** (c4_nasim_container.puml): All 5 external clients and single NASIM Application container remain valid. No new containers.
- **Component Diagram** (c4_nasim_component.puml): All 4 Controller, 7 Service, 14 Repository, and 4 Data Store components remain valid. All CARs add internal structure to existing components.

This is a deliberate feature of the original architecture: the C4 was designed with appropriate granularity to accommodate implementation complexity within existing boundaries.

### 6.2 Future C4 Refinements (Post-v1.0)

After implementation validates the current C4, consider:

1. **Component Diagram — WireLogRepository splitting**: If wire logging grows to support replay servers, indexed search, and cross-session analytics, split into `WireLogRepository` (append-only write) + `ReplayRepository` (read/search/fork). This maintains SRP. Keep ≤12 elements per repository boundary.

2. **Component Diagram — EvaluationService splitting**: If evaluation grows to include a test runner, benchmark harness, and feedback database, consider `EvaluationService` (coordination) + `TestRunnerRepository` (execution) + `FeedbackRepository` (storage).

3. **Container Diagram — MCP Server container**: If NASIM frequently runs as a sub-agent within larger MCP ecosystems, add `NASIM MCP Server` as a separate container (same codebase, different entry point). This splits from the main HTTP+CLI deployment pattern.

---

## 7. Risks, Trade-offs & Mitigations

### 7.1 Execution Risk (Design-to-Code Gap)

**Risk:** NASIM has the most detailed design in the field and zero code. The design may contain incorrect assumptions that only surface during implementation. Competitors are shipping weekly.

**Mitigation:** Start with a minimal end-to-end vertical slice (CAR-001: CLI Adapter + CAR-004: ToolService with bash/read/write + CAR-003: basic SafetyService) in Milestone 0. Validate the AgentController → TaskService → ToolService → Repository chain with a real LLM call before building depth. Every week without a working `"hello world"` agent increases risk.

### 7.2 Complexity Risk (YAGNI)

**Risk:** The 98-class design, 150 use cases, and 10 CARs may over-engineer the initial release. Goose's single 3730-line `agent.rs` works well enough for production use.

**Mitigation:** CAR priority tiers (P0/P1/P2) exist for this reason. Ship P0 only for v0.1-alpha (~2500 lines of Python). The CSR layering and component interfaces will guide organic growth toward the full design. Do NOT implement all 98 classes before shipping.

### 7.3 Performance Risk (Event Logging Overhead)

**Risk:** WireLogRepository's append-only logging on every LLM call and tool execution could add latency, especially with synchronous disk I/O.

**Mitigation:** Make WireLogRepository fire-and-forget (write to an in-memory queue, flush asynchronously). Never block the agent loop for I/O. Provide a `--no-wire-log` flag for latency-sensitive use.

### 7.4 Provider Abstraction Risk (litellm Coupling)

**Risk:** litellm is a large dependency (100+ providers) with frequent API changes. If litellm drops a provider or changes its interface, NASIM's LLMRepository breaks.

**Mitigation:** Define an `LLMProvider` abstract interface in NASIM's codebase (`class NASIMProvider(ABC): async def complete(...)`). litellm is the default implementation. Users can implement custom providers without touching litellm. This is standard adapter pattern — the C4 already implies it.

### 7.5 Safety Usability Risk (Too Many Prompts)

**Risk:** The comprehensive 5-stage safety pipeline (CAR-003) may generate excessive approval prompts, degrading UX. SmartApprove (Goose) and YOLO mode (crush) exist because users find constant prompting frustrating.

**Mitigation:** Implement graduated safety: `permissive` (auto-approve all, log only), `normal` (ask on destructive/write/network, auto-approve read), `strict` (ask on everything). Default to `normal` with a clear warning. Allow per-project safety profiles. The SafetyService design already includes configurable modes — make them user-facing from day one.

### 7.6 Context Compaction Cost Risk

**Risk:** LLM-driven compaction (Goose's approach) costs money — each compaction is an LLM call. On large sessions with frequent compaction, this could dominate API cost.

**Mitigation:** Default to `rolling_truncate` (free). Make `llm_summarize` and `epoch_checkpoint` opt-in via config. Show compaction cost in session billing if tracking is implemented.

---

## 8. Conclusion & Recommendations

### 8.1 Is NASIM's Explicit CSR + Single-Gate + Dedicated Cross-Cutting Services a Durable Differentiator?

**Yes — but only if shipped before the rest of the field converges on equivalent architecture.**

NASIM's design strengths — strict CSR layering, single-gate AgentController, dedicated SafetyService/ContextService/EvaluationService/WireLogRepository/EditStrategyRepository — are objectively superior to every competitor's architecture. No competitor has all of these. The closest contenders (Goose, OpenCode) have subsets implemented with varying degrees of architectural purity.

However, the field is moving fast. Goose's 5-inspector safety pipeline approaches NASIM's SafetyService design. OpenCode's Context Epochs + event sourcing approach NASIM's ContextService + WireLogRepository design. The differentiation window is ~6–12 months. If NASIM ships its P0+ in that window, the architectural clarity will be a durable moat. If it takes longer, competitors will have closed the gap through iterative improvement.

### 8.2 Highest-Impact CARs for v1.0

| Rank | CAR-ID | Theme | Why High Impact |
|------|--------|-------|-----------------|
| 1 | CAR-003 | Safety Pipeline | Trust is the #1 barrier to AI coding agent adoption. A demonstrable 5-stage safety pipeline is a narrative-defining feature. |
| 2 | CAR-002 | Context Pipeline | Task success rate is #1 UX metric. Competitors' ad-hoc context handling is a visible weakness NASIM can exploit. |
| 3 | CAR-004 | Tool/MCP Extensibility | MCP is the universal protocol. NASIM must ship MCP support that is architecturally cleaner than Goose's. |
| 4 | CAR-008 | Edit Strategy | Edit reliability is a top-3 user complaint. Sandbox-validated diffs with undo is a measurable moat. |
| 5 | CAR-001 | Multi-Client Adapt | Validates the entire architecture with first working code. Without this, nothing else ships. |

### 8.3 How This Audit Feeds the Next Design-Chain Iteration

| Design Chain Layer | Impact from this Audit |
|--------------------|----------------------|
| **UC** (Use Cases) | New UC groups needed for: sub-agent orchestration (CAR-005), edit lifecycle (CAR-008), evaluation/retry flows (CAR-006), session forking (CAR-007), provider routing (CAR-009) |
| **SM** (State Machines) | New or updated SMs needed for: sub-agent lifecycle (CAR-005), diff staging (CAR-008), evaluation (CAR-006), provider fallback (CAR-009), MCP server reconnection (CAR-004), context compaction (CAR-002) |
| **SQ** (Sequence Diagrams) | Updated SQs needed for all CARs — many SQ lifelines already include the correct components (SafetyService, WireLogRepository, etc.) but need detail on the enhanced pipelines |
| **ERD** (Entity Relationship) | New entities: SubAgent (CAR-005), EvaluationResult (CAR-006), WireLogEvent (CAR-007), StagedEdit (CAR-008), ModelRoute (CAR-009) |
| **CL** (Class Diagram) | New/updated classes across Service and Repository layers — most already exist as named entries but need detailed attributes and methods |
| **CT/DATA** (Data Contracts) | New ODCS contracts for: WireLogEvent, EvaluationResult, SubAgent, StagedEdit |
| **CT/API** (API Surface) | New API endpoints for: replay (CAR-007), session fork (CAR-007), evaluation status (CAR-006), MCP tool management (CAR-004) |

---

## Appendix A: C4 Component Traceability by CAR

| CAR-ID | Components Affected | Type |
|--------|-------------------|------|
| CAR-001 | cli_adp, http_adp, mcp_adp, agent_ctrl, session_svc | Implementation |
| CAR-002 | context_svc, repo_intel_repo, memory_repo, llm_repo | Enhancement |
| CAR-003 | safety_svc, sandbox_repo, fs_repo, tool_svc | Enhancement |
| CAR-004 | tool_svc, mcp_repo, safety_svc, wire_log_repo | Implementation |
| CAR-005 | task_svc, context_svc, safety_svc, wire_log_repo | Enhancement |
| CAR-006 | eval_svc, task_svc, llm_repo | Implementation |
| CAR-007 | wire_log_repo, history_repo, session_svc, task_svc | Implementation |
| CAR-008 | edit_strategy_repo, sandbox_repo, fs_repo | Implementation |
| CAR-009 | llm_repo, task_svc, config_svc | Enhancement |
| CAR-010 | git_repo, session_svc, history_repo, wire_log_repo | Enhancement |

---

## Appendix B: Projects Examined (31 total)

| # | Project | Status | Notes |
|---|---------|--------|-------|
| 1 | aider/ | Active | Lightweight, git-native, 39 coder variants |
| 2 | amazon-q-developer-cli/ | Archived | Now Kiro CLI |
| 3 | claude-code/ | Active | Closed core, 14 plugins open |
| 4 | claw-code/ | Museum | Dual Python+Rust fork of Claude Code |
| 5 | cline/ | Active | Full SDK, Kanban, cron — most complete framework |
| 6 | code-cli/ | Active | ACP-native, React loop runner |
| 7 | codex/ | Active | Rust/Bazel, Responses API, multi-agent |
| 8 | copilot-cli/ | Active | Closed source, installer only |
| 9 | crush/ | Active | Go/Charm ecosystem, MCP, loop detection |
| 10 | free-claude-code/ | Active | Proxy server, 17 providers, not an agent |
| 11 | freellmapi/ | Active | API proxy, 16 free providers |
| 12 | fugu/ | Active | Bash wrapper around Codex, Sakana AI research |
| 13 | gemini-cli/ | Active | Full TypeScript monorepo, 83 tools |
| 14 | goose/ | Active | Rust, 57+ providers, MCP-native, 5-layer safety |
| 15 | grok-cli/ | Active | Bun/TS, Shuru sandbox, Telegram remote |
| 16 | hermes-agent/ | Active | Python, 4486-line loop, 16 retries, self-learning |
| 17 | kilocode/ | Active | Effect-TS fork of OpenCode, multi-IDE |
| 18 | kimi-cli/ | Active | Python, kosong framework, being superseded |
| 19 | MiMo-Code/ | Active | Xiaomi, Effect-TS, multi-surface |
| 20 | mistral-vibe/ | Active | Python, Textual TUI, middleware pipeline |
| 21 | opencode/ | Active | TS/Bun, event sourcing, context epochs — best session design |
| 22 | OpenHands/ | Active | Python, enterprise orchestration, external agent SDK |
| 23 | openinterpreter/ | Active | Rust fork of Codex, native sandboxing |
| 24 | plandex/ | Active | Go, plan-first architecture, server model |
| 25 | qwen-code/ | Active | TS, forked from gemini-cli, richest feature set |
| 26 | Roo-Code/ | Discontinued | 4619-line Task.ts, modes system, now ZooCode |  
| 27 | ruflo/ | Active | TS, 30+ plugins, 300+ MCP tools, swarms |
| 28 | SkeletonAgent/ | Research | Action recognition, not a coding agent |
| 29 | SWE-agent/ | Superseded | Research, SWE-bench SOTA, now mini-swe-agent |
| 30 | warp/ | Active | Rust, full terminal emulator + AI features |
| 31 | **nasim/** | **Pre-alpha** | **Design complete, zero code** |

---

*End of Competitive Audit & Enhancement Document v1.0*
