# nasim — Deep Domain Audit: ML, RL, NLP, and Software Design

**Date:** 2026-06-20  
**Scope:** All 28 reference agents vs nasim — per-agent technical deep-dive  
**Framework:** CAR (Challenge — Action — Result) with numeric scoring  
**Perspectives:** Machine Learning, Reinforcement Learning, NLP, Software Architecture  
**Target:** Identify every gap; produce a concrete 10/10 design enhancement roadmap  

---

## Scoring System

Each agent is scored on **20 dimensions** (1–10). nasim's current design-phase score
is assessed against the same dimensions. Gap = reference best − nasim score.

| Dim | Dimension | Domain |
|-----|-----------|--------|
| D01 | Provider Abstraction | Software Design |
| D02 | Tool System Depth | Software Design |
| D03 | Context Management Algorithms | NLP / ML |
| D04 | Memory Architecture | ML / NLP |
| D05 | Safety / Permission System | Software Design |
| D06 | Multi-Agent Coordination | ML / AI Systems |
| D07 | Session Persistence Quality | Software Design |
| D08 | Hook / Extension System | Software Design |
| D09 | Repository Intelligence (Repo Map / AST) | NLP |
| D10 | Edit Format Strategy Diversity | NLP |
| D11 | Model Routing / Task Classification | ML |
| D12 | Evaluation / RL-like Feedback Loop | RL |
| D13 | Web / Search Integration | Software Design |
| D14 | Observability (Logging / Metrics / Tracing) | Software Design |
| D15 | Sandbox / OS-level Execution Isolation | Software Design |
| D16 | Event Architecture Quality | Software Design |
| D17 | Plugin / Marketplace Ecosystem | Software Design |
| D18 | Design Chain Consistency (C4→Code) | Software Design |
| D19 | NLP Sophistication (Tokenization / Semantics / RAG) | NLP / ML |
| D20 | Async / Concurrent Architecture | Software Design |

---

## Part 1 — Per-Agent Deep Technical Analysis

---

### 1. aider (Python — Production)

**CAR — Challenge:** Build a CLI coding assistant that can reliably edit files with multiple LLMs without function-calling dependency.

**CAR — Action:**
- **Edit-format polymorphism** — 14 `Coder` subclasses (EditBlock, WholeFile, Diff, UDiff, Editor, Architect, Ask, etc.) selected at runtime based on model capability. Each is a Strategy pattern with its own prompt set.
- **Repo-map with PageRank** — `RepoMap.get_ranked_tags()` builds a symbol reference graph using tree-sitter AST captures. Then runs `networkx.pagerank()` with personalization vectors weighted toward files currently in chat. Result: a ranked, token-budgeted summary of the whole repo injected into context. This is the most sophisticated NLP information retrieval system in the reference corpus.
- **ChatSummary binary split** — `summarize_real()` recursively halves the message history. Older half is summarized by a weaker model; newer half is kept verbatim. Depth limited to 3 to prevent infinite recursion.
- **4-layer config** — `CLI > .env > .aider.conf.yml (CWD/root/home) > defaults`. Auto-prefix `AIDER_` for env vars.
- **Architect mode** — Two-model pipeline: architect LLM creates a plan in natural language; editor LLM applies it as code edits. This is a primitive multi-agent role decomposition.
- **Auto-lint + auto-commit** — Post-edit verification loop: lint error → LLM re-edits. Git auto-commit on each accepted edit.

**CAR — Result:**
- Best-in-class NLP code intelligence (PageRank repo-map)
- Edit strategy diversity (14) unmatched by any other agent
- No function-calling dependency → works with any model

**Trade-offs vs nasim:**
- aider has no HTTP API, no MCP, no multi-interface — nasim surpasses here
- aider has no OS-level sandbox
- aider's multi-agent is rudimentary (architect + editor only)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | litellm, 100+ providers |
| D02 | 4 | No function-calling; text parsing only |
| D03 | 9 | PageRank + binary split + token budgeting |
| D04 | 3 | Chat history file only, no semantic memory |
| D05 | 5 | .aiderignore, read_only, dry-run |
| D06 | 3 | Architect+Editor — 2-role only |
| D07 | 4 | Markdown history file, --restore-chat-history |
| D08 | 2 | No hook system |
| D09 | **10** | tree-sitter + PageRank — best in class |
| D10 | **10** | 14 edit strategies — best in class |
| D11 | 5 | Model selection by capability flag |
| D12 | 4 | Auto-lint retry only |
| D13 | 3 | No built-in web search |
| D14 | 3 | Basic logging |
| D15 | 2 | No sandbox |
| D16 | 4 | Event-based IO via io.py |
| D17 | 2 | No plugin system |
| D18 | 2 | No design docs |
| D19 | 8 | tree-sitter tokenization, AST-aware context |
| D20 | 4 | Mostly sync |

**aider Overall: 5.4/10**

---

### 2. claude-code (TypeScript/Bun — Production)

**CAR — Challenge:** Build a world-class CLI agent with enterprise reach: MDM deployment, plugin marketplace, deep hooks, background agents.

**CAR — Action:**
- **Plugin marketplace** — 14 official + community plugins. Each plugin is a Markdown file with YAML frontmatter defining tools, hooks, and skills. Prompt-based agent definitions.
- **9-event hook system** — UserPromptSubmit, PreToolUse, PostToolUse, Notification, Stop, SubagentStop, PreCompact, PostCompact, MCP events. Hooks can be shell scripts or LLM calls.
- **5-level subagent nesting** — Agents can spawn agents up to depth 5. Session IDs and transcript paths for chain tracking.
- **Tiered permissions** — allow/ask/deny per tool per session. Bash sandbox with network domain allowlists.
- **MDM enterprise** — Jamf/Intune deployment profiles for managed settings. No-install for enterprise lock-down.
- **Background daemon** — Agents run headlessly in tmux; `claude --resume` to reattach.
- **Skill auto-activation** — Skills activate from YAML frontmatter triggers; no explicit `/skill` command needed.

**CAR — Result:**
- Most complete ecosystem with marketplace + MDM + hooks + background agents
- Enterprise-ready deployment model

**Trade-offs vs nasim:**
- Closed-source runtime (Bun binary) — no design chain
- Hook system is less structured than nasim's typed event system
- No explicit multi-model routing

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 7 | Anthropic + Bedrock + gateways |
| D02 | 8 | Bash, Read/Write/Edit, Web, MCP |
| D03 | 6 | PreCompact hook, skill auto-activation |
| D04 | 5 | Skills as memory artifacts |
| D05 | 9 | Tiered per-tool, MDM, Bash sandbox |
| D06 | **9** | 5-level nesting, SubagentStop hook |
| D07 | 7 | Session IDs + transcript paths, 30-day cleanup |
| D08 | **10** | 9 events, LLM-in-the-loop hooks |
| D09 | 5 | No explicit repo-map; relies on LLM |
| D10 | 4 | Single edit format (replacement) |
| D11 | 5 | Model fallback chains |
| D12 | 5 | PostToolUse hook for validation |
| D13 | 8 | WebSearch + WebFetch built-in |
| D14 | 6 | Session transcripts |
| D15 | 7 | Bash sandbox with network allowlist |
| D16 | 8 | Hook event bus |
| D17 | **10** | Plugin marketplace |
| D18 | 2 | Closed source — no design docs |
| D19 | 5 | No explicit AST/NLP |
| D20 | 8 | Bun async runtime |

**claude-code Overall: 6.6/10**

---

### 3. codex (Rust — Production)

**CAR — Challenge:** Build the most architecturally correct, sandboxed, and extensible open-source code agent with strict crate boundaries.

**CAR — Action:**
- **124-crate workspace** — Every capability is a separate Rust crate: `agent-graph-store`, `memories`, `sandboxing`, `context-fragments`, `hooks`, `skills`, `plugins`, `otel`, `linux-sandbox`. Zero circular dependencies enforced by Cargo.
- **Agent-graph-store** — Tracks agent execution state as a directed graph. Each agent run is a node; tool calls are edges. Enables replay, inspection, and debugging of complex multi-step agent flows.
- **OS-level multi-layer sandbox** — `linux-sandbox` crate: landlock (filesystem restriction by path), seccomp (syscall filtering), bubblewrap (namespace isolation). macOS: seatbelt/sandbox-exec. Windows: Windows Sandbox Runtime. Three independent isolation layers.
- **ModelProvider trait** — Protocol-based polymorphism (Rust trait objects). OpenAI + Bedrock + Ollama implementations. `ProviderCapabilities` struct per model.
- **ContextFragment injection system** — `context-fragments` crate: typed fragments (system prompt, user context, tool results) assembled into conversation with token budgeting.
- **Remote compaction** — Context can be compacted by a remote service (cloud compaction) or locally. `compact.rs` with threshold-based triggers.
- **ConfigLayerStack** — global → project → cloud → CLI merge semantics. TOML-based, strongly typed.
- **Thread-store trait** — `LocalThreadStore` (SQLite) implements thread CRUD. `LiveThread` wraps active sessions.

**CAR — Result:**
- Best-in-class sandbox (3 independent OS-level layers)
- Most architecturally disciplined codebase (124 crates, zero circularity)
- Agent-graph-store is a unique execution provenance system

**Trade-offs vs nasim:**
- Rust-only — no Python ecosystem integration
- Graph store has no ML ranking / intelligence applied to it
- memories crate exists but appears minimal (no RAG/embedding)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | ModelProvider trait, OpenAI+Bedrock+Ollama |
| D02 | 9 | Tool framework: ToolDefinition, ToolSpec, ToolExecutor |
| D03 | 8 | ContextFragment system, remote compaction |
| D04 | 4 | memories crate exists but minimal |
| D05 | 8 | exec_policy.rs, SafetyCheck enum |
| D06 | 7 | Multi-agent via app-server, collaboration mode |
| D07 | 9 | ThreadStore trait, SQLite-backed, lifecycle |
| D08 | 9 | hooks crate, skills crate |
| D09 | 4 | file-search crate, no AST-based ranking |
| D10 | 5 | Apply-patch crate, limited strategies |
| D11 | 6 | ModelProvider routing |
| D12 | 4 | No explicit reviewer/evaluator |
| D13 | 6 | Web via tools |
| D14 | 9 | otel crate — full OpenTelemetry |
| D15 | **10** | landlock + seccomp + bubblewrap + seatbelt |
| D16 | 9 | Typed crate events + mpsc channels |
| D17 | 9 | core-plugins crate, plugin installation |
| D18 | 3 | README + docs but no C4 chain |
| D19 | 5 | file-search, no AST PageRank |
| D20 | **10** | Tokio async-first, Actor-like |

**codex Overall: 7.1/10**

---

### 4. gemini-cli (TypeScript/Node.js — Production)

**CAR — Challenge:** Build the richest context management and multi-agent system for Google's Gemini with A2A protocol support.

**CAR — Action:**
- **Graph-based ContextWorkingBuffer** — `packages/core/src/context/pipeline/contextWorkingBuffer.ts`: The conversation history is modeled as a typed graph. Nodes are context fragments (system prompt, tool results, user messages). Behaviors (registered in `behaviorRegistry.ts`) transform the graph. `PipelineOrchestrator` runs processors sequentially.
- **ToolDistillationService** — When a tool output is massive (> 1M chars), a secondary Gemini call distills it. Below threshold, proportional truncation. This is a two-LLM ML pipeline for information compression.
- **ModelRouterService** — `packages/core/src/routing/`: Composite strategy with 4 routing modes: classifier (model predicts best model), fallback (ordered list), approval (user approves), override (config forces). `routingStrategy.ts` defines the interface.
- **Agent2Agent (A2A) server** — `packages/a2a-server/`: Full A2A protocol implementation. Agents can invoke remote agents, receive task results via SSE. Scheduler manages concurrent agent tasks. Registry + acknowledgement system.
- **9-type tool distillation** — Tools are distilled differently: read_file and read_many_files are exempt; others get proportional truncation + optional LLM summarization.
- **4 approval modes** — DEFAULT (ask for unsafe), AUTO_EDIT (auto for edits), YOLO (no approval), PLAN (all tools queued). PolicyEngine with TOML priority rules.
- **Memory context manager** — `memoryContextManager.ts`: separate from chat history. Manages injected memory facts across sessions. Priority-sorted.
- **Hot-start and incremental context** — `contextManager.hotstart.test.ts`, `contextManager.incremental.test.ts`: Context can be initialized from a snapshot (hot start) or built incrementally.

**CAR — Result:**
- Most sophisticated context architecture (graph + pipeline + distillation)
- A2A server enables true distributed multi-agent systems
- Composite model routing matches task to model

**Trade-offs vs nasim:**
- Google Gemini only (no provider abstraction)
- TypeScript/Node.js — no Python ML library integration
- No OS-level sandbox (Docker/Podman optional)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 3 | Gemini only (OAuth/API key/Vertex) |
| D02 | **10** | 20+ built-in tools + priority registry |
| D03 | **10** | Graph-based pipeline + distillation + hot-start |
| D04 | 8 | MemoryContextManager + cross-session injection |
| D05 | 8 | 4 approval modes + PolicyEngine TOML rules |
| D06 | **9** | A2A server, scheduler, registry, remote invocation |
| D07 | 8 | ChatRecordingService (JSONL) + rewind points |
| D08 | 9 | BeforeModel, AfterModel, BeforeToolSelection hooks |
| D09 | 5 | No AST-based ranking |
| D10 | 4 | Standard edit format |
| D11 | **10** | Composite routing (classifier + fallback + approval + override) |
| D12 | 5 | PolicyEngine, no explicit reviewer |
| D13 | 9 | Built-in web + memory tools |
| D14 | 7 | Tracer + eventBus |
| D15 | 6 | Docker/Podman optional sandbox |
| D16 | **10** | Graph-based pipeline + EventBus |
| D17 | 7 | A2A plugin registration |
| D18 | 3 | No formal design chain |
| D19 | **9** | Distillation + NLP pipeline + hot-start |
| D20 | 9 | Async TypeScript + EventBus |

**gemini-cli Overall: 7.4/10**

---

### 5. opencode (TypeScript/Bun — Production)

**CAR — Challenge:** Build the most structured, type-safe agent runtime with event-sourced sessions, multi-frontend, and Effect-TS functional programming.

**CAR — Action:**
- **Effect-TS architecture** — Every operation is an `Effect<A, E, R>`. Services are `Layer<>` objects. Dependency injection via `Context<>`. This is the most type-safe agent runtime in the corpus.
- **Event-sourced sessions** — `PartTable`, `SessionTable` backed by Drizzle ORM on SQLite. Every message part is immutable and appended; never updated. Full replay from part sequence.
- **Precise compaction thresholds** — `PRUNE_MINIMUM=20,000` chars, `PRUNE_PROTECT=40,000` chars, `TOOL_OUTPUT_MAX_CHARS=2,000`, `MIN_PRESERVE_RECENT_TOKENS=2,000`, `MAX_PRESERVE_RECENT_TOKENS=8,000`, `DEFAULT_TAIL_TURNS=2`. These constants reflect careful calibration of context window economics.
- **Multi-frontend** — `packages/tui/`, `packages/cli/`, `packages/web/`, `packages/desktop/` — all share the same agent core via `packages/opencode/`. The session/compaction.ts is UI-agnostic.
- **EventV2Bridge** — Bridges EventV1 and EventV2 schemas for migration. All events are typed `SessionEvent` discriminated unions.
- **Plugin system** — `packages/plugin/`: typed plugin API with Effect integration.
- **Slack integration** — `packages/slack/`: session results posted to Slack.
- **Child session model** — Sessions have parent-child relationships. `childTitlePrefix` for spawned child sessions. Child title naming convention is structural.

**CAR — Result:**
- Most type-safe and principled runtime (Effect-TS)
- Event sourcing makes sessions fully auditable and replayable
- Multi-frontend without code duplication

**Trade-offs vs nasim:**
- Effect-TS has high learning curve; hard to contribute to
- Python ecosystem completely excluded
- No ML-specific capabilities (no embedding, no ranking)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | Multi-provider via LLM package |
| D02 | 8 | Tool system in session/tools.ts |
| D03 | 9 | Precise compaction constants, event-sourced |
| D04 | 4 | No persistent memory beyond sessions |
| D05 | 7 | Subagent permissions, config-based |
| D06 | 7 | Child sessions, subagent-permissions |
| D07 | **10** | Event-sourced, Drizzle ORM, SQLite, full replay |
| D08 | 7 | Plugin hooks |
| D09 | 3 | No repo-map or AST system |
| D10 | 4 | Standard edit |
| D11 | 6 | Provider-level routing |
| D12 | 4 | No reviewer |
| D13 | 7 | Web tools |
| D14 | 7 | Effect-TS error typing = built-in traceability |
| D15 | 5 | Config-based sandbox |
| D16 | **10** | Effect-TS + EventV2Bridge — best event system |
| D17 | 8 | Plugin package |
| D18 | 3 | CONTEXT.md but no C4 chain |
| D19 | 5 | No AST/NLP |
| D20 | **10** | Effect-TS is async-first functional |

**opencode Overall: 6.6/10**

---

### 6. goose (Rust — Production)

**CAR — Challenge:** Build a security-hardened, MCP-first code agent with ML-informed retry logic and RL-like success evaluation.

**CAR — Action:**
- **SuccessCheck + RetryConfig** — `types.rs`: `RetryConfig { max_retries, checks: Vec<SuccessCheck>, on_failure }`. `SuccessCheck::Shell { command }` runs a shell command and checks exit code. This is the closest any reference agent gets to a **reward signal in RL** — a post-task verifier that determines if the agent succeeded. The `on_failure` cleanup hook adds rollback semantics.
- **MOIM (Model of Internal Mood)** — `moim.rs`: Injects a `<turn-budget>` tag per turn showing `turns_taken / max_turns`. System prompt teaches the LLM to adjust behavior as budget depletes: "reduce exploration, batch tool calls, make reasonable assumptions." This is **turn-budget as contextual constraint** analogous to exploration-exploitation trade-off in RL.
- **Tool pair summarization** — `context_mgmt/mod.rs`: `TOOLCALL_SUMMARIZATION_BATCH_SIZE=10`. Tool call + result pairs are summarized together (not individually) to preserve semantic coherence. `DEFAULT_COMPACTION_THRESHOLD=0.8` triggers when context reaches 80% of window.
- **Repetition inspector** — `tool_monitor::RepetitionInspector`: Detects when the agent is making the same tool calls repeatedly. Triggers reset in RetryManager. This is loop detection.
- **Extension IS MCP** — Every goose extension is an MCP server. No proprietary extension format. Zero lock-in.
- **Multi-layer provider** — `goose-providers/`: `base.rs` defines `Provider` trait. `canonical/` has default implementations. `conversation/token_usage.rs` tracks token costs per provider.
- **ML safety checks** — `checks/mod.rs`: Extension malware check (`extension_malware_check.rs`). Validates extensions before loading.

**CAR — Result:**
- Only agent with explicit **reward signal** (SuccessCheck) and **rollback** (on_failure)
- MOIM is the only **RL-like turn budget** constraint system
- Repetition inspector prevents infinite loops (a common RL divergence problem)
- Extensions = MCP is the most principled extension architecture

**Trade-offs vs nasim:**
- Rust-only limits Python ML integration
- No graph-based context
- No semantic memory / RAG

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | goose-providers crate, canonical provider |
| D02 | 8 | Platform extensions + MCP tools |
| D03 | 8 | MOIM + tool-pair summarization + 0.8 threshold |
| D04 | 5 | goose-apps for app context, no semantic RAG |
| D05 | 8 | Tool confirmation router, safety checks |
| D06 | 8 | SubagentHandler + SubagentExecutionTool |
| D07 | 7 | Session in goose-server |
| D08 | 9 | 4 hook events: pre/post LLM/tool |
| D09 | 3 | No AST-based ranking |
| D10 | 3 | No edit format diversity |
| D11 | 6 | Provider selection via config |
| D12 | **10** | SuccessCheck + RetryConfig + on_failure + RepetitionInspector — best RL proxy |
| D13 | 7 | Web tools |
| D14 | **10** | OpenTelemetry full integration (tracing crate) |
| D15 | 7 | Sandboxed execution via policies |
| D16 | 9 | Tokio mpsc + Arc<Mutex> |
| D17 | 8 | MCP-native extensions |
| D18 | 3 | AGENTS.md but no C4 |
| D19 | 4 | No AST; token counting per provider |
| D20 | **10** | Tokio async |

**goose Overall: 7.1/10**

---

### 7. cline (TypeScript/Bun — Production)

**CAR — Challenge:** Build a VS Code native agent with deep IDE integration and subscription-based access.

**CAR — Action:**
- **VS Code extension architecture** — `apps/vscode/`: Full extension with sidebar, status bar, webview panel. Uses VS Code extension API for file system, editor, and terminal.
- **SDK** — `apps/cli/` and SDK for headless use. Same agent core serves both VS Code and CLI.
- **Effect-TS** (from opencode fork) — Same functional programming model as opencode.
- **Cline Hub** — `apps/cline-hub/`: Marketplace for community prompts, tools, and agents.
- **Subscription model** — Cline's commercial model wraps free API access.

**CAR — Result:**
- Best-in-class IDE integration (VS Code native)
- Subscription model enables broader user base

**Trade-offs vs nasim:**
- VS Code-specific — not terminal-first
- Derived from opencode — same limitations

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | Multi-provider |
| D02 | 8 | VS Code + CLI tool sets |
| D03 | 8 | Inherited from opencode |
| D04 | 4 | No cross-session memory |
| D05 | 7 | Permission per operation |
| D06 | 6 | No explicit multi-agent |
| D07 | 9 | SQLite sessions |
| D08 | 7 | Hook system |
| D09 | 4 | VS Code language server integration |
| D10 | 5 | Multiple edit modes |
| D11 | 7 | Model selection |
| D12 | 4 | No reviewer |
| D13 | 8 | Web tools |
| D14 | 6 | VS Code output channel |
| D15 | 5 | No OS-level sandbox |
| D16 | 9 | Effect-TS events |
| D17 | 8 | Cline Hub marketplace |
| D18 | 2 | No design chain |
| D19 | 7 | VS Code LSP integration |
| D20 | 9 | Bun async |

**cline Overall: 6.6/10**

---

### 8. SWE-agent (Python — Research)

**CAR — Challenge:** Build an agent for autonomous software engineering benchmarks with genuine ML evaluation.

**CAR — Action:**
- **Reviewer class** — `sweagent/agent/reviewer.py`: `ReviewSubmission` collects the full trajectory. `ReviewerResult { accept: bool | float, outputs, messages }`. Supports `float` accept (probability), enabling stochastic selection. `ChooserOutput` picks from multiple attempts via a separate LLM. `PreselectorOutput` pre-filters candidates. Uses `numpy` for multi-attempt scoring.
- **Best-of-N sampling** — Multiple agent runs on the same problem, then a reviewer selects the best solution. This is **Best-of-N sampling** (BoN), a key technique from RLHF and process reward models.
- **Trajectory structure** — `Trajectory: list[TrajectoryStep]`. Each step is typed. Aggregate info dict tracks submission quality.
- **Problem statement abstraction** — `problem_statement.py`: Clean abstraction for software engineering issues. Input to reviewer for context.
- **Action sampler** — `action_sampler.py`: Samples multiple candidate actions. Reviewer selects. This is the RL exploration step.
- **History processors** — `history_processors.py`: Transform history before LLM call. Supports `_set_cache_control` for Anthropic prompt caching.
- **Benchmark configs** — `config/`: Per-benchmark YAML configs define reward criteria, allowed tools, max steps.

**CAR — Result:**
- Only agent with genuine **Best-of-N sampling** and **probability-valued reviewer**
- Most ML-rigorous evaluation framework
- Trajectory-level quality assessment

**Trade-offs vs nasim:**
- Research code — not production-hardened
- No persistent sessions, no plugin system, no HTTP API
- Reviewer is slow (requires multiple LLM calls)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 5 | Any model via config |
| D02 | 4 | Minimal toolset (Docker env) |
| D03 | 5 | History processors, cache control |
| D04 | 2 | No memory |
| D05 | 3 | Config-based limits |
| D06 | 3 | Single agent + reviewer |
| D07 | 3 | Per-run trajectory |
| D08 | 3 | Benchmark hooks |
| D09 | 3 | No repo-map |
| D10 | 3 | Standard edit |
| D11 | 4 | Model config per benchmark |
| D12 | **10** | Best-of-N + float accept + numpy reviewer — best ML eval |
| D13 | 2 | No web tools |
| D14 | 4 | Trajectory logging |
| D15 | 6 | Docker sandbox |
| D16 | 4 | Event callbacks |
| D17 | 2 | No plugins |
| D18 | 3 | Research paper + config docs |
| D19 | 5 | Prompt caching, benchmark-aware |
| D20 | 5 | Async where needed |

**SWE-agent Overall: 3.8/10** (Research-grade, not production)

---

### 9. plandex (Go — Production)

**CAR — Challenge:** Build a plan-centric agent with 9 specialized model roles, plan versioning, and a diff sandbox.

**CAR — Action:**
- **9 specialized model roles** — `app/server/model/`: Each has its own prompts. Roles include: Planner, Builder, Namer, Summarizer, Describer, Validator, Commit-messager, AutoContinue, PlanningMode. Each role can use a different LLM optimized for its task.
- **Plan versioning** — Plans are versioned objects. `tell.go` handles plan execution with streaming. `build.go` handles the build phase (applying plan to code). Plans can branch and merge.
- **Diff sandbox** — All edits are applied to a sandboxed copy of the file tree first. User reviews the diff before applying to actual files. `apply_exec.go` manages this.
- **Client-server architecture** — `app/cli/` is the thin client; `app/server/` is the stateful server with plan storage in SQLite.
- **Plan execution stream** — Plan execution streams plan events (start, stop, edit, error) to the CLI via SSE.
- **litellm proxy** — `app/server/litellm_proxy.py`: Python litellm wrapper called from Go server for provider-agnostic model access.

**CAR — Result:**
- Best plan-centric architecture (9 roles, versioning, diff sandbox)
- Diff sandbox is the safest edit model (see before apply)
- Model-per-role is the most sophisticated multi-model routing

**Trade-offs vs nasim:**
- No MCP, no HTTP client API (is a server itself)
- Heavy client-server split increases deployment complexity
- Go + Python litellm bridge adds operational complexity

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 8 | litellm proxy, all providers |
| D02 | 7 | File + shell + web tools |
| D03 | 7 | Summary per plan phase |
| D04 | 3 | Plan history only |
| D05 | 6 | User approval on diff |
| D06 | 5 | Plan-level parallelism |
| D07 | 8 | SQLite plan store |
| D08 | 6 | Plan hooks |
| D09 | 4 | File context loading |
| D10 | 6 | Diff sandbox strategy |
| D11 | **10** | 9 specialized roles — best multi-model routing |
| D12 | 6 | Diff review + validation role |
| D13 | 5 | Web search |
| D14 | 5 | Server-side logging |
| D15 | 6 | Diff sandbox (not OS-level) |
| D16 | 7 | SSE stream events |
| D17 | 4 | No marketplace |
| D18 | 3 | README docs |
| D19 | 5 | Token counting |
| D20 | 8 | Go goroutines |

**plandex Overall: 6.0/10**

---

### 10. kimi-cli (Python — Mid)

**CAR — Challenge:** Build a production CLI agent with Wire pub/sub persistence, Soul system for agent identity, and first-class session forking.

**CAR — Action:**
- **Wire pub/sub persistence** — `wire/` package: JSON-RPC over file (`wire/file.py`). Every event (StepBegin, StepInterrupted, CompactionBegin/End, StatusUpdate, SteerInput) is appended to `wire.jsonl`. This is an **append-only event log** enabling full replay.
- **Session fork** — `session_fork.py`: `enumerate_turns()` scans wire.jsonl for `TurnBegin` records. `/undo` and `/fork` slash commands call this. `CHECKPOINT_USER_PATTERN` marks restore points. Any session can be forked at any historical turn.
- **Soul system** — `soul/` package: `KimiSoul` is the agent runtime. Has `Context`, `Toolset`, `DynamicInjection`, `compaction`. Sub-modules: `AfkModeInjectionProvider`, `PlanModeInjectionProvider`. Soul is the identity layer — the agent's personality and context are first-class objects.
- **Subagent registry** — `subagents/`: builder, runner, registry, store. `AgentSpec` inheritance for capability declaration.
- **Agent spec inheritance** — Subagents declare capabilities via spec inheritance. Parent agent decides which tools/context to expose to child.
- **tenacity retry** — `stop_after_attempt + wait_exponential_jitter`: Adaptive retry with jitter prevents thundering herd in API rate limiting.
- **AFK mode injection** — When user is AFK, the injection provider changes agent behavior (reduces output, focuses on task completion).
- **Skill flow** — `skill/flow.py`: `FlowNode`, `FlowEdge`, `parse_choice` — skills can have conditional branching flows.

**CAR — Result:**
- Best wire persistence (append-only, replayable event log)
- Best session fork / undo implementation
- Soul system is unique agent identity architecture

**Trade-offs vs nasim:**
- No graph-based context
- No OS-level sandbox
- Provider limited to Moonshot/Kimi LLMs primarily

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 6 | Moonshot + configurable |
| D02 | 8 | 40+ tools via MCP and built-in |
| D03 | 7 | Soul compaction + SimpleCompaction |
| D04 | 6 | Soul dynamic injection + AFK mode |
| D05 | 7 | Approval runtime + tool rejection |
| D06 | 8 | Subagent builder/runner/registry |
| D07 | **10** | Wire.jsonl + session fork + undo + checkpoint — best replay |
| D08 | 8 | HookEngine + 4+ events |
| D09 | 4 | No AST ranking |
| D10 | 4 | Standard edit |
| D11 | 5 | Model selection per capability |
| D12 | 5 | tenacity retry + AFK mode |
| D13 | 7 | Web tools |
| D14 | 6 | Wire log as audit trail |
| D15 | 3 | No OS-level sandbox |
| D16 | 9 | Wire pub/sub + EventBus |
| D17 | 6 | Plugin + MCP |
| D18 | 3 | AGENTS.md |
| D19 | 6 | Token estimation + context pruning |
| D20 | 9 | asyncio throughout |

**kimi-cli Overall: 6.5/10**

---

### 11. hermes-agent (Python — Mid)

**CAR — Challenge:** Build the most feature-dense Python agent with 40+ tools, 20+ platform gateways, and a pluggable memory architecture.

**CAR — Action:**
- **MemoryManager** — `agent/memory_manager.py`: Single integration point. One external plugin at a time (prevents tool schema bloat). `build_system_prompt()`, `prefetch_all(user_message)`, `sync_all(user_msg, assistant_response)`, `queue_prefetch_all()`. Background `ThreadPoolExecutor` for async prefetch. Drain timeout `_SYNC_DRAIN_TIMEOUT_S=5.0` for graceful shutdown.
- **Multi-provider adapters** — `agent/`: `anthropic_adapter.py`, `bedrock_adapter.py`, `gemini_native_adapter.py`, `gemini_cloudcode_adapter.py`, `codex_runtime.py`, `copilot_acp_client.py`. 20+ platform gateways.
- **Context engine** — `agent/context_engine.py` + `context_compressor.py`: Two-stage context management. Engine loads relevant context; compressor reduces when needed.
- **Skill bundles** — `skill_bundles.py`, `skill_commands.py`, `skill_preprocessing.py`: Skills are loadable bundles with preprocessing.
- **Trajectory** — `agent/trajectory.py`: Full trajectory recording per session.
- **Error classifier** — `agent/error_classifier.py`: Classifies errors for retry decisions.
- **Iteration budget** — `agent/iteration_budget.py`: Tracks tool calls per turn; enforces limits.
- **Usage pricing** — `agent/usage_pricing.py`: Real-time cost tracking per provider.
- **Image/Video/Speech providers** — `image_gen_provider.py`, `video_gen_provider.py`, `tts_provider.py`, `transcription_provider.py`: Multi-modal tools.

**CAR — Result:**
- Most feature-dense Python agent
- MemoryManager is the cleanest pluggable memory architecture
- Error classifier enables intelligent retry

**Trade-offs vs nasim:**
- Monolithic structure (100+ files, no clear separation)
- No design chain; hard to maintain
- Memory is pluggable but not semantic (no embeddings)

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | **10** | 20+ provider adapters |
| D02 | **10** | 40+ tools, multi-modal |
| D03 | 7 | Context engine + compressor |
| D04 | 7 | MemoryManager + prefetch/sync lifecycle |
| D05 | 7 | Tool guardrails, file safety |
| D06 | 6 | Skill bundles, no explicit subagent |
| D07 | 6 | Trajectory per session |
| D08 | 5 | Shell hooks |
| D09 | 4 | No AST ranking |
| D10 | 5 | Multiple format support |
| D11 | 7 | Provider routing + error classifier |
| D12 | 7 | Error classifier + iteration budget + retry |
| D13 | 9 | Web search provider + registry |
| D14 | 6 | Stream diagnostics |
| D15 | 5 | File safety only |
| D16 | 5 | Conversation loop |
| D17 | 7 | Skill bundles + plugin LLM |
| D18 | 1 | No design chain |
| D19 | 7 | Think scrubber, usage pricing |
| D20 | 8 | asyncio |

**hermes-agent Overall: 6.3/10**

---

### 12. openinterpreter (Rust — Production, codex fork)

Note: `openinterpreter/` directory is structurally identical to `codex/codex-rs/`. This appears to be a re-brand/fork of codex. All codex scores apply.

**openinterpreter Overall: same as codex = 7.1/10**

---

### 13. crush (Go — Mid)

**CAR — Challenge:** Build a Go agent with genuine LSP integration and Charm TUI.

**CAR — Action:**
- **LSP client** — `internal/lsp/`: `client.go`, `manager.go`, `handlers.go`. Full Language Server Protocol client. Sends `textDocument/hover`, `textDocument/definition`, `textDocument/references` requests to running language servers. `manager.go` discovers and starts LSP servers per file type.
- **Session persistence** — `internal/session/`: Session store in `internal/db/` (SQLite). Resume previous sessions.
- **Skills system** — `internal/skills/`: Named skill bundles (like claude-code skills).
- **Pubsub** — `internal/pubsub/`: Event pub/sub for UI updates.
- **OAuth** — `internal/oauth/`: Browser OAuth flow for API auth.
- **Server mode** — `internal/server/`: crush can run as a server.

**CAR — Result:**
- Best-in-class Go LSP integration (native, not a tool call)
- Clean Go package structure

**Trade-offs vs nasim:**
- No multi-agent, no ML capabilities, no repo-map

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 6 | Go API client |
| D02 | 7 | File + shell + web + LSP |
| D03 | 5 | History management |
| D04 | 3 | No memory |
| D05 | 6 | Permission manager |
| D06 | 3 | Single agent |
| D07 | 7 | SQLite sessions |
| D08 | 5 | Hooks |
| D09 | 3 | No AST ranking |
| D10 | 4 | Standard edit |
| D11 | 5 | Model selection |
| D12 | 3 | No reviewer |
| D13 | 6 | Web tools |
| D14 | 6 | pubsub events |
| D15 | 4 | No OS sandbox |
| D16 | 7 | pubsub |
| D17 | 5 | Skills |
| D18 | 2 | README |
| D19 | **9** | Full LSP integration — best code intelligence via LSP |
| D20 | 8 | Go goroutines |

**crush Overall: 5.2/10**

---

### 14. kilocode (TypeScript/Bun — Mid, opencode fork)

**Differentiator:** 500+ models via provider aggregation. Same architecture as opencode.

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | **10** | 500+ models via aggregation |
| All others | same as opencode | |

**kilocode Overall: 6.8/10**

---

### 15. Roo-Code (TypeScript — Mid)

**Differentiator:** Role-based modes (code, architect, ask, debug). Community-driven. VS Code extension.

- Modes are named agent personas with different system prompts and tool subsets.
- Orchester mode coordinates between role-agents.

| Dim | Score | Notes |
|-----|-------|-------|
| D06 | 7 | Multi-role modes (architect, coder, debug) |
| D11 | 7 | Mode-based model selection |
| All others | similar to cline | |

**Roo-Code Overall: 6.2/10**

---

### 16. amazon-q-developer-cli (Rust — Production)

**CAR — Challenge:** Build an AWS-native code agent with semantic search and deep cloud integration.

**CAR — Action:**
- **Semantic search client** — `crates/semantic-search-client/`: Embedding-based semantic code search. Queries the local codebase using vector similarity. This is **RAG (Retrieval-Augmented Generation)** for code.
- **TUI** — `crates/chat-cli-ui/`: Rich terminal UI in Rust.
- **AWS-native adapters** — `crates/amzn-codewhisperer-client/`, `crates/amzn-consolas-client/`: AWS-specific API clients with streaming.
- **Telemetry** — `crates/aws-toolkit-telemetry-definitions/`: AWS telemetry framework.

**CAR — Result:**
- Only agent with native **semantic search / RAG** for code
- Tightest AWS integration

**Trade-offs vs nasim:**
- AWS-locked; not portable
- No open-source provider abstraction

| Dim | Score | Notes |
|-----|-------|-------|
| D01 | 3 | AWS CodeWhisperer only |
| D02 | 7 | File + shell + AWS tools |
| D03 | 6 | History management |
| D04 | 5 | Semantic search for context |
| D05 | 7 | AWS IAM-based |
| D06 | 5 | Agent crate |
| D07 | 7 | SQLite sessions |
| D08 | 5 | Hooks |
| D09 | 6 | Semantic search |
| D10 | 4 | Standard edit |
| D11 | 5 | AWS model routing |
| D12 | 4 | No reviewer |
| D13 | 7 | Web |
| D14 | 9 | AWS telemetry |
| D15 | 5 | AWS-backed sandbox |
| D16 | 7 | Rust events |
| D17 | 5 | AWS plugin system |
| D18 | 2 | README |
| D19 | **10** | Semantic search client — only agent with native RAG for code |
| D20 | 9 | Tokio async |

**amazon-q Overall: 5.9/10**

---

### 17. MiMo-Code (TypeScript/Bun — Mid)

**Differentiator:** Persistent memory + self-improving loop. Fork of opencode with memory additions.

- Adds cross-session memory persistence (facts stored in SQLite, injected into future sessions).
- "Self-improving loop" — agent reflects on past sessions and updates its behavioral preferences.

**MiMo-Code Overall: 6.8/10**

---

### 18. mistral-vibe (Python — Early)

**Differentiator:** ACP (Agent Communication Protocol) + voice input (Whisper).

- `vibe/acp/`: Full ACP protocol for agent-to-agent communication.
- `vibe/core/`: Textual TUI.
- Voice input via Whisper API.

| Dim | Score | Notes |
|-----|-------|-------|
| D06 | 7 | ACP protocol for multi-agent |
| D19 | 7 | Voice (Whisper) + ACP |

**mistral-vibe Overall: 4.2/10**

---

### 19. qwen-code (TypeScript/Node.js — Mid)

**Differentiator:** Richest surface area — CLI + Desktop + 5 IM bots (Slack, Teams, Discord, WeChat, Feishu).

- `packages/cli/`, `packages/desktop/` + bot integrations.
- Same gemini-cli core with Qwen model substitution.

**qwen-code Overall: 6.5/10**

---

### 20. warp (Rust — Production)

**Differentiator:** Owns the entire terminal stack (GPU-accelerated renderer + AI agent).

- The AI agent runs inside the terminal, with direct access to terminal state, command history, and output.
- GPU-accelerated rendering via Metal/WebGPU.
- `skills-lock.json`: Locked skill versions.

**warp Overall: 6.0/10** (terminal-specific, not a general agent)

---

### 21. claw-code (Python+Rust — Early)

**Differentiator:** `claw-rag-service` — a standalone RAG service with embeddings stored in SQLite, HTTP API for semantic search, and web UI.

- Three separate products: `claw` (full CLI), `claw-analog` (restricted CI-safe), `claw-rag-service` (RAG).
- `retrieve_context` tool calls the RAG service.

| Dim | Score | Notes |
|-----|-------|-------|
| D04 | 8 | RAG service with embeddings + SQLite |
| D09 | 8 | Semantic code search via RAG |
| D19 | 9 | Embeddings + vector similarity for code |

**claw-code Overall: 4.5/10** (early stage)

---

### 22. ruflo (TypeScript/Node.js — Early)

**CAR — Challenge:** Build a multi-agent swarm harness for 100+ specialized agents with self-learning memory.

**CAR — Action:**
- **Learning loop** — `User → Ruflo → Router → Swarm → Agents → Memory → LLM → Learning Loop`. After each task, the agent stores "what worked" in memory. Future routing uses this learned preference.
- **RuVector graph DB** — Vector database for agent memory. Agents query by semantic similarity.
- **Federation** — Agents on different machines communicate securely without data leakage.
- **98 agent definitions** — Specialized agents for different task types.
- **Swarm coordination** — Router dispatches to swarm; swarm coordinates agents.

**CAR — Result:**
- Only agent with explicit self-learning feedback loop
- Federation enables distributed multi-machine multi-agent

**Trade-offs vs nasim:**
- Wrapper around claude-code/codex — not standalone
- Learning loop is marketing-level description; implementation shallow

| Dim | Score | Notes |
|-----|-------|-------|
| D06 | **10** | 100+ agents, swarm, federation |
| D12 | 8 | Self-learning memory loop |
| D04 | 8 | RuVector graph DB |

**ruflo Overall: 4.8/10** (early stage wrapper)

---

### 23. SkeletonAgent (PyTorch — Research)

**CAR — Challenge:** Apply agentic LLM interaction to skeleton-based action recognition.

**CAR — Action:**
- **Questioner agent** — Identifies most frequently confused action classes. Feeds confusion matrix to LLM as context for more targeted discriminative cues.
- **Selector agent** — Parses LLM response to extract joint-level constraints. Feeds constraints back to recognizer.
- **Feedback loop** — Recognition model performance informs which classes the Questioner asks about next. This is a genuine **closed-loop RL system**: recognizer → confusion matrix → Questioner → LLM guidance → Selector → joint constraints → recognizer.
- **5 benchmark evaluations** — NTU RGB+D, NTU RGB+D 120, Kinetics-Skeleton, FineGYM, UAV-Human.

**CAR — Result:**
- Only agent with a genuine closed-loop RL-like feedback between model performance and LLM guidance
- Most rigorous ML architecture in the corpus (domain-specific)

**Trade-offs vs nasim:**
- Not a code agent — domain-specific (action recognition)
- Not applicable to software engineering directly
- But the feedback pattern (performance → query → guidance → model) is transferable

| Dim | Score | Notes |
|-----|-------|-------|
| D12 | **10** | Closed-loop RL: confusion matrix → LLM → joints → recognizer |

**SkeletonAgent Overall: 2.0/10** (not a code agent — domain-specific score)

---

### 24. free-claude-code (Python — Early)

**Differentiator:** Proxy middleware routing to 17+ providers via FastAPI.

- `api/`: FastAPI routes mirroring Anthropic's API.
- `core/`: Provider routing logic.
- Routes requests transparently to any provider.

**free-claude-code Overall: 2.5/10**

---

## Part 2 — nasim Design Score vs Reference Corpus

### nasim Current Design Scores (Design-Phase Assessment)

nasim at v0.1 PoC has minimal implementation (450 LOC). The scores below rate the **design** in `docs/` and `ENTITIES.md`, not the current PoC code.

| Dim | nasim Design Score | Reference Best | Gap | Best Agent |
|-----|--------------------|----------------|-----|------------|
| D01 Provider Abstraction | 9 | 10 (hermes: 20+ adapters) | -1 | hermes |
| D02 Tool System Depth | 8 | 10 (hermes: 40+ tools) | -2 | hermes/gemini |
| D03 Context Management | 7 | 10 (gemini graph + distillation) | -3 | gemini |
| D04 Memory Architecture | 7 | 8 (claw-code RAG, ruflo RuVector) | -1 | claw-code |
| D05 Safety / Permission | 8 | 9 (claude-code MDM + sandbox) | -1 | claude-code |
| D06 Multi-Agent | 8 | 10 (gemini A2A + ruflo swarm) | -2 | gemini/ruflo |
| D07 Session Persistence | 8 | 10 (opencode event-sourced) | -2 | opencode |
| D08 Hook / Extension | 8 | 10 (claude-code 9 events) | -2 | claude-code |
| D09 Repository Intelligence | 4 | 10 (aider PageRank) | **-6** | aider |
| D10 Edit Format Diversity | 4 | 10 (aider 14 strategies) | **-6** | aider |
| D11 Model Routing | 8 | 10 (gemini composite routing) | -2 | gemini |
| D12 Evaluation / RL Loop | 3 | 10 (goose SuccessCheck + SWE reviewer) | **-7** | goose/SWE |
| D13 Web / Search | 7 | 9 (hermes web registry) | -2 | hermes |
| D14 Observability | 7 | 10 (goose + codex OTel) | -3 | goose/codex |
| D15 Sandbox | 7 | 10 (codex landlock+seccomp+bubblewrap) | -3 | codex |
| D16 Event Architecture | 8 | 10 (opencode Effect-TS + kimi Wire) | -2 | opencode |
| D17 Plugin Ecosystem | 7 | 10 (claude-code marketplace) | -3 | claude-code |
| D18 Design Chain | **10** | 3 (no reference has C4→Code chain) | **+7** | nasim |
| D19 NLP Sophistication | 5 | 10 (aider AST+PageRank, amzn-q RAG) | **-5** | aider/amzn-q |
| D20 Async Architecture | 7 | 10 (opencode Effect-TS, codex Tokio) | -3 | opencode/codex |

**nasim Design Overall: 7.05/10**

---

## Part 3 — CAR Framework: Gaps and Enhancement Roadmap

### Challenge: nasim has the best design chain (10/10 D18) but critical gaps in ML/NLP intelligence, RL feedback, and edit diversity.

### Action: 9 design enhancements that close every remaining gap.

---

### Enhancement E-01 — Repo Intelligence Engine (fills D09 gap: +6 points)

**Reference Pattern:** aider PageRank, claw-code RAG, amazon-q semantic search  
**Gap:** nasim has GrepTool/GlobTool but no structured code intelligence pipeline.

**Design addition:**

```
RepoIntelligenceManager
  → ASTIndexAdapter → ASTStore (tree-sitter, per-file tags)
  → SymbolGraphAdapter → SymbolGraph (nodes=symbols, edges=references)
  → RankingService (PageRank + personalization vectors per session)
  → EmbeddingAdapter → EmbeddingStore (SQLite with vector columns)
  → SemanticSearchService (cosine similarity on embeddings)
  → RepoMapBuilder (token-budgeted context injection)
```

**Components to add to ENTITIES.md:**
- `RepoIntelligenceManager` — owns all code intelligence
- `ASTIndexAdapter` — tree-sitter extraction per language
- `SymbolGraph` — NetworkX-like graph of symbols + references
- `RankingService` — PageRank with chat-personalization
- `EmbeddingAdapter` — embedding model (local or API)
- `SemanticSearchService` — vector similarity search
- `RepoMapBuilder` — token-budgeted repo map injection

**UC group:** `RIM` (Repo Intelligence Management)

**NLP significance:** Moves from keyword search (GrepTool) to graph-ranked semantic retrieval. Personalized PageRank means the repo map dynamically adjusts to which files are most relevant to the current conversation — bridging information retrieval theory and practical context injection.

---

### Enhancement E-02 — Edit Strategy Polymorphism (fills D10 gap: +6 points)

**Reference Pattern:** aider 14 strategies  
**Gap:** nasim has EditFileTool (single strategy: exact string replace).

**Design addition:**

```
EditStrategyManager
  → EditStrategyRegistry (name → EditStrategy)
  → implementations:
      SearchReplaceCoder     (SEARCH/REPLACE blocks)
      WholeFileCoder         (rewrite entire file)
      UnifiedDiffCoder       (unified diff format)
      FencedBlockCoder       (fenced code blocks)
      FunctionLevelCoder     (AST-targeted function replacement)
      DiffSandboxCoder       (like plandex: stage-then-apply)
      ArchitectCoder         (plan-then-implement two-phase)
      InlinePatchCoder       (apply-patch format)
```

**Components to add:**
- `EditStrategyManager` — selects best strategy per model capability
- `EditStrategy` (ABC) — abstract base with `apply(original, instructions) → result`
- 8 concrete strategy implementations
- `StrategySelector` — uses ProviderCapabilities to pick optimal strategy

**NLP significance:** Different LLMs produce different output formats reliably. Strategy polymorphism allows nasim to extract the highest-quality edit from any model's natural output format — a key insight from aider's research.

---

### Enhancement E-03 — RL-Proxy Feedback Loop (fills D12 gap: +7 points)

**Reference Pattern:** goose SuccessCheck + SWE-agent Reviewer + SkeletonAgent closed-loop  
**Gap:** nasim has no post-task quality evaluation.

**Design addition:**

```
EvaluationEngine
  → TaskEvaluator (evaluates whether task is complete)
      → SuccessCheckRunner (shell exit code checks, like goose)
      → LLMReviewer (LLM-as-judge, like SWE-agent)
      → TestRunner (run test suite, check pass/fail)
  → RetryCoordinator (max_retries, retry_strategy, on_failure)
  → QualitySignal (accept: bool | float, feedback: str)
  → RepetitionDetector (detects tool-call loops, like goose)
  → TurnBudgetInjector (like goose MOIM: inject turn budget per-turn)
```

**RL theory connection:**
- `SuccessCheckRunner` = terminal reward signal (sparse reward)
- `LLMReviewer` = process reward model (dense feedback)
- `RetryCoordinator` = policy rollout with max_steps
- `RepetitionDetector` = loop detection (prevents policy divergence)
- `TurnBudgetInjector` = exploration budget (constrains total action count)
- Together: **RLHF-proxy loop without gradient updates** — the agent's behavior is shaped by external evaluators, approximating a policy improvement step.

**UC group:** `EVL` (Evaluation)

---

### Enhancement E-04 — Wire Event Log (fills D16 gap: +2 points)

**Reference Pattern:** kimi-cli Wire.jsonl, opencode event-sourced parts  
**Gap:** nasim has SessionStore (JSON) but no append-only event log.

**Design addition:**

```
WireLog
  → WireAppender (append-only jsonl writer)
  → WireReader (sequential scan for replay)
  → TurnIndex (maps turn_number → byte_offset for O(1) seek)
  → SessionForkManager (fork at any turn via WireReader + TurnIndex)
```

**Components to add:**
- `WireLog` — the append-only per-session event stream
- `WireAppender` — write-only interface (enforces append-only)
- `WireReader` — read-only with random seek via TurnIndex
- `SessionForkManager` — `/fork` and `/undo` via turn enumeration

**Design significance:** Separates SessionStore (summary/metadata) from WireLog (full event replay). SessionStore remains small; WireLog is the ground truth. Enables time-travel debugging and session branching.

---

### Enhancement E-05 — Semantic Memory with RAG (fills D04 gap: +1 point, D19: +5 points)

**Reference Pattern:** claw-code RAG service, amazon-q semantic search, ruflo RuVector  
**Gap:** nasim has MemoryTool (design) but no embedding-based retrieval.

**Design addition:**

```
MemoryStore (enhanced)
  → EpisodicMemoryAdapter → EpisodicStore (session summaries + embeddings)
  → SemanticMemoryAdapter → SemanticStore (facts + embeddings + metadata)
  → WorkingMemoryAdapter → WorkingStore (in-session scratch, no persist)
  → MemoryRetriever
      → BM25Retriever (keyword-based, fast)
      → EmbeddingRetriever (vector similarity, semantic)
      → HybridRetriever (RRF fusion of BM25 + embedding scores)
  → MemoryIndexer (indexes new facts after each session)
```

**ML significance:**
- BM25 = classical IR (term frequency × inverse document frequency)
- Embedding retrieval = dense neural IR (semantic similarity)
- Hybrid RRF (Reciprocal Rank Fusion) = best of both: keyword exactness + semantic generalization
- Together this approximates a lightweight **Retrieval-Augmented Generation** system for agent memory.

**UC group:** `MEM` (already in ENTITIES.md — enhance scope)

---

### Enhancement E-06 — Graph-based Context Pipeline (fills D03 gap: +3 points)

**Reference Pattern:** gemini-cli ContextWorkingBuffer + PipelineOrchestrator  
**Gap:** nasim has ConversationHistory (list) + ContextCompactor (summary). No graph structure.

**Design addition:**

```
ContextGraph (replaces ConversationHistory as the runtime model)
  → ContextNode (typed: SystemPrompt, UserMessage, AssistantMessage, ToolCall, ToolResult, Memory, RepoMap, WorkingContext)
  → ContextEdge (typed: follows, calls, returns, summarizes, injects)
  → ContextProcessor (ABC)
      → TruncationProcessor (removes old nodes respecting protection budget)
      → DistillationProcessor (secondary LLM call for massive tool outputs)
      → InjectionProcessor (injects RepoMap, Memory nodes at turn start)
      → CompactionProcessor (replaces batch of nodes with summary node)
  → PipelineOrchestrator (runs processors sequentially per turn)
  → TokenBudgetTracker (counts tokens per node, sums for window budget)
```

**NLP significance:** A graph over conversation fragments is more expressive than a flat list. Edges encode causal relationships (tool-call → tool-result). This enables:
- Selective retention (keep tool-result nodes longer if they're referenced)
- Causal compaction (compress a chain of tool-call/result pairs together)
- Injection targeting (inject memory at the right graph position)

---

### Enhancement E-07 — OpenTelemetry Observability (fills D14 gap: +3 points)

**Reference Pattern:** goose + codex full OpenTelemetry  
**Gap:** nasim has ObservabilityManager in design but not wired into C4.

**Design addition (already in design, needs wiring):**

```
ObservabilityManager (wired into all layers)
  → TraceExporter (OTLP trace export)
  → MetricRecorder (token counts, latency, cost per provider)
  → StructuredLogger (JSON structured logs with trace_id, span_id)
  → CostTracker (real-time cost per provider per session, like hermes)
```

**Metrics to capture:**
- `nasim.agent.turn_count` — turns per session
- `nasim.agent.token_count.input/output` — tokens per turn
- `nasim.provider.latency_ms` — per-provider latency histogram
- `nasim.tool.execution_time_ms` — per-tool execution latency
- `nasim.context.utilization_ratio` — context window fill ratio
- `nasim.cost.usd_per_session` — session cost in USD

---

### Enhancement E-08 — Composite Model Routing (fills D11 gap: +2 points)

**Reference Pattern:** gemini composite routing, plandex 9 roles  
**Gap:** nasim has ModelRouter in design but limited routing strategies.

**Design addition (enhances existing ModelRouter):**

```
ModelRouter (enhanced)
  → RoutingStrategy (ABC)
      → TaskClassifierStrategy (ML: classify task type → model)
      → CapabilityMatchStrategy (match task requirements to model capabilities)
      → CostOptimizationStrategy (prefer cheapest model that satisfies capability)
      → FallbackChainStrategy (ordered fallback with circuit breaker)
      → RoleStrategy (plandex-like: different model per agent role)
  → ModelRoleRegistry (maps agent role → preferred model)
      Roles: Planner, Coder, Reviewer, Summarizer, Embedder, Validator
  → ContextWindowStrategy (pick model with sufficient context window)
```

**ML significance:** TaskClassifierStrategy uses a lightweight text classifier (even regex-based rules or a tiny model) to predict task type (coding, documentation, reasoning, tool-selection) and routes accordingly. This is the same principle as mixture-of-experts routing applied to LLM selection.

---

### Enhancement E-09 — Diff Sandbox Strategy (fills D10 + D15 partial: +1 point each)

**Reference Pattern:** plandex diff sandbox  
**Gap:** nasim's EditFileTool applies changes directly; no stage-then-review cycle.

**Design addition:**

```
DiffSandboxManager
  → EditStagingArea (in-memory file tree copy)
  → DiffComputer (computes diff between original and staged)
  → DiffPresenter (renders diff to Renderer for user review)
  → StagedApplicator (applies staged changes to actual files on approval)
```

This is a safety feature AND an edit strategy: the `DiffSandboxCoder` applies to staging, shows diff, then applies only on user approval. Integrates with PermissionGate (`ask` mode → always show diff; `auto` → apply directly).

---

## Part 4 — Feature Score Matrix (All Agents + nasim)

| Agent | D01 | D02 | D03 | D04 | D05 | D06 | D07 | D08 | D09 | D10 | D11 | D12 | D13 | D14 | D15 | D16 | D17 | D18 | D19 | D20 | **Total** |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----------|
| aider | 8 | 4 | 9 | 3 | 5 | 3 | 4 | 2 | **10** | **10** | 5 | 4 | 3 | 3 | 2 | 4 | 2 | 2 | 8 | 4 | 5.4 |
| claude-code | 7 | 8 | 6 | 5 | 9 | **9** | 7 | **10** | 5 | 4 | 5 | 5 | 8 | 6 | 7 | 8 | **10** | 2 | 5 | 8 | 6.6 |
| codex | 8 | 9 | 8 | 4 | 8 | 7 | 9 | 9 | 4 | 5 | 6 | 4 | 6 | 9 | **10** | 9 | 9 | 3 | 5 | **10** | 7.1 |
| gemini-cli | 3 | **10** | **10** | 8 | 8 | **9** | 8 | 9 | 5 | 4 | **10** | 5 | 9 | 7 | 6 | **10** | 7 | 3 | **9** | 9 | 7.4 |
| opencode | 8 | 8 | 9 | 4 | 7 | 7 | **10** | 7 | 3 | 4 | 6 | 4 | 7 | 7 | 5 | **10** | 8 | 3 | 5 | **10** | 6.6 |
| goose | 8 | 8 | 8 | 5 | 8 | 8 | 7 | 9 | 3 | 3 | 6 | **10** | 7 | **10** | 7 | 9 | 8 | 3 | 4 | **10** | 7.1 |
| cline | 8 | 8 | 8 | 4 | 7 | 6 | 9 | 7 | 4 | 5 | 7 | 4 | 8 | 6 | 5 | 9 | 8 | 2 | 7 | 9 | 6.6 |
| SWE-agent | 5 | 4 | 5 | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 4 | **10** | 2 | 4 | 6 | 4 | 2 | 3 | 5 | 5 | 3.8 |
| plandex | 8 | 7 | 7 | 3 | 6 | 5 | 8 | 6 | 4 | 6 | **10** | 6 | 5 | 5 | 6 | 7 | 4 | 3 | 5 | 8 | 6.0 |
| kimi-cli | 6 | 8 | 7 | 6 | 7 | 8 | **10** | 8 | 4 | 4 | 5 | 5 | 7 | 6 | 3 | 9 | 6 | 3 | 6 | 9 | 6.5 |
| hermes | **10** | **10** | 7 | 7 | 7 | 6 | 6 | 5 | 4 | 5 | 7 | 7 | 9 | 6 | 5 | 5 | 7 | 1 | 7 | 8 | 6.3 |
| crush | 6 | 7 | 5 | 3 | 6 | 3 | 7 | 5 | 3 | 4 | 5 | 3 | 6 | 6 | 4 | 7 | 5 | 2 | **9** | 8 | 5.2 |
| amazon-q | 3 | 7 | 6 | 5 | 7 | 5 | 7 | 5 | 6 | 4 | 5 | 4 | 7 | 9 | 5 | 7 | 5 | 2 | **10** | 9 | 5.9 |
| claw-code | 6 | 5 | 5 | 8 | 5 | 3 | 4 | 3 | 8 | 3 | 4 | 3 | 5 | 4 | 3 | 4 | 3 | 2 | **9** | 5 | 4.5 |
| ruflo | 6 | 7 | 5 | 8 | 6 | **10** | 6 | 7 | 3 | 3 | 5 | 8 | 5 | 5 | 4 | 6 | 7 | 2 | 7 | 6 | 4.8* |
| **nasim (design)** | 9 | 8 | 7 | 7 | 8 | 8 | 8 | 8 | 4 | 4 | 8 | 3 | 7 | 7 | 7 | 8 | 7 | **10** | 5 | 7 | 7.05 |
| **nasim (enhanced)** | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 9 | 9 | 9 | 8 | **10** | 9 | 9 | **9.0** |

*ruflo is primarily a wrapper; score is constrained by implementation depth.

---

## Part 5 — Trade-off Analysis: nasim's Position

### Where nasim Already Leads

**1. Design Chain Completeness (D18 = 10/10)**
nasim is the only agent in the corpus with a complete C4 → UC → SM → SQ → ERD → CL → CT/DATA → CT/API → Code chain. Every reference agent has at most a README and some architecture notes. This is not a vanity metric — it means nasim's architecture is auditable, cascadable, and self-correcting in a way no reference agent achieves.

**Trade-off:** The design chain creates overhead during implementation. Every code change requires cascading through design layers. This is appropriate for a production OSS artifact but would slow down a hackathon project.

**2. Multi-Interface Architecture (D01 + D16)**
nasim is the only agent that explicitly designs for CLI + HTTP API + MCP server from the ground up with a shared UI-agnostic core (AgentOrchestrator → AgentEvent). All reference agents either build a single interface or bolt on additional interfaces as afterthoughts.

**Trade-off:** Multi-interface requires more wiring. The shared core constraint (no print() in agent) requires discipline that pure CLI agents don't need.

**3. Litellm Universal Proxy (D01 = 9)**
nasim's Provider/LiteLLMProxy design routes all providers through litellm. hermes-agent writes 20+ individual adapters; nasim avoids all that maintenance burden. ModelCatalog pulls pricing/caps from litellm's database.

**Trade-off:** litellm dependency means nasim inherits litellm's bugs and latency. Direct adapters like hermes can optimize per-provider.

### Where nasim Has Structural Gaps

**1. Repository Intelligence (D09 = 4 → target 9)**
nasim's GrepTool/GlobTool find files but don't rank them by relevance. aider's PageRank repo-map is in a different class: it knows which symbols are most referenced by the files in chat. nasim loses here on every code intelligence task where file ranking matters.

**2. Evaluation Loop (D12 = 3 → target 9)**
nasim has no mechanism to check whether a completed task is correct. goose's SuccessCheck + SWE-agent's Reviewer both close this loop. Without it, nasim cannot know if it should retry or move on.

**3. Edit Diversity (D10 = 4 → target 9)**
All models produce different edit formats naturally. nasim's single EditFileTool strategy will fail on models that produce whole-file rewrites or unified diffs. aider proves this matters: 14 strategies for 14 model behaviors.

**4. Wire Event Log (D07 = 8 → target 9, D16 = 8 → target 9)**
nasim has SessionStore (JSON summary) but no append-only event log. kimi's session fork requires wire.jsonl to enumerate turns. Without it, nasim cannot implement `/undo` properly.

**5. Semantic Memory (D04 = 7 → target 9)**
nasim's MemoryTool is designed but lacks embeddings. RAG requires an embedding model + vector store. claw-code and amazon-q both implement this.

---

## Part 6 — ML / RL / NLP Perspective Synthesis

### ML Patterns in the Reference Corpus

| Pattern | Reference | Score | nasim Gap |
|---------|-----------|-------|-----------|
| PageRank on symbol graph | aider | 10 | Major (D09) |
| Best-of-N sampling | SWE-agent | 10 | Major (D12) |
| Secondary LLM distillation | gemini | 9 | Partial (D03) |
| Composite model routing | gemini | 10 | Minor (D11) |
| Vector similarity retrieval | amazon-q, claw | 10 | Major (D19) |
| Self-learning memory loop | ruflo | 8 | Major (D12) |
| Closed-loop feedback | SkeletonAgent | 10 | Major (D12) |

### RL Patterns Observed

| Pattern | Reference | RL Analogue | nasim Gap |
|---------|-----------|-------------|-----------|
| SuccessCheck + RetryConfig | goose | Sparse reward + policy rollout | Major |
| LLMReviewer (accept: float) | SWE-agent | Process reward model | Major |
| Turn budget injection (MOIM) | goose | Exploration budget | Major |
| RepetitionInspector | goose | Loop/divergence detection | Moderate |
| on_failure cleanup | goose | Rollback / environment reset | Minor (PermissionGate handles partial) |
| AFK mode injection | kimi | Context-adaptive policy | Moderate |
| Confusion → query → constraint | SkeletonAgent | Closed RL loop (most rigorous) | Major |

### NLP Patterns Observed

| Pattern | Reference | NLP Technique | nasim Gap |
|---------|-----------|---------------|-----------|
| AST tag extraction | aider | Structured parsing (tree-sitter) | Major (D09) |
| Symbol reference graph | aider | Dependency graph construction | Major (D09) |
| Personalized PageRank | aider | Graph-based IR with query-biased random walk | Major (D09) |
| Tool output distillation | gemini | Extractive + abstractive summarization | Moderate (D03) |
| Wire event replay | kimi | Temporal state restoration | Moderate (D07) |
| Session forking | kimi | Branching POMDP history | Moderate (D07) |
| Hybrid BM25 + dense retrieval | (implied) | Reciprocal Rank Fusion | Major (D19) |
| Embedding-based code search | amazon-q, claw | Dense code retrieval | Major (D19) |

---

## Part 7 — Enhancement Cascade (Design Chain Updates)

Adding E-01 through E-09 requires updates to every design chain layer below C4.

### New UC Groups Required

| Group | Additions |
|-------|-----------|
| `RIM` | Repo Intelligence Management (15 UCs: index, rank, search, inject, invalidate...) |
| `EDT` | Edit Strategy (6 UCs: select-strategy, apply, validate, stage, review, revert) |
| `EVL` | Evaluation (8 UCs: run-checks, invoke-reviewer, record-result, retry, reset...) |
| `WRL` | Wire Log (6 UCs: append, read, seek, fork, checkpoint, replay) |

### New SM States Required

- `EVALUATING` — agent is running SuccessChecks after task completion
- `REVIEWING` — LLMReviewer is scoring the submission
- `RETRYING` — EvaluationEngine decided to retry
- `STAGING` — DiffSandboxCoder has edits in staging area
- `AWAITING_DIFF_APPROVAL` — user must approve the staged diff

### Entities to Add to entities.md

Per enhancement:
- E-01: RepoIntelligenceManager, ASTIndexAdapter, SymbolGraph, RankingService, EmbeddingAdapter, SemanticSearchService, RepoMapBuilder (7)
- E-02: EditStrategyManager, EditStrategy, 8 concrete implementations, StrategySelector (11)
- E-03: EvaluationEngine, TaskEvaluator, SuccessCheckRunner, LLMReviewer, TestRunner, RetryCoordinator, QualitySignal, RepetitionDetector, TurnBudgetInjector (9)
- E-04: WireLog, WireAppender, WireReader, TurnIndex, SessionForkManager (5)
- E-05: EpisodicMemoryAdapter, SemanticMemoryAdapter, WorkingMemoryAdapter, MemoryRetriever, BM25Retriever, EmbeddingRetriever, HybridRetriever, MemoryIndexer (8)
- E-06: ContextGraph, ContextNode, ContextEdge, ContextProcessor, TruncationProcessor, DistillationProcessor, InjectionProcessor, CompactionProcessor, PipelineOrchestrator, TokenBudgetTracker (10)
- E-07: (already designed — wire OTel into all components, add CostTracker)
- E-08: RoutingStrategy, TaskClassifierStrategy, CapabilityMatchStrategy, CostOptimizationStrategy, RoleStrategy, ModelRoleRegistry, ContextWindowStrategy (7)
- E-09: DiffSandboxManager, EditStagingArea, DiffComputer, DiffPresenter, StagedApplicator (5)

**Total new entities: 62**

---

## Part 8 — Path to 10/10

### Current: 7.05 → Enhanced: 9.0 → Target 10.0

The gap from 9.0 to 10.0 requires closing two remaining partial gaps:

**To reach 10/10 on D13 (Web/Search):**
Add a web search provider registry (like hermes) with fallback: SerpAPI → Tavily → DuckDuckGo → Brave. Implement `WebSearchProvider` protocol.

**To reach 10/10 on D17 (Plugin Ecosystem):**
Implement a plugin registry (GitHub-hosted index like claude-code marketplace) + CLI commands: `nasim plugin search <term>`, `nasim plugin install <name>`, `nasim plugin update`. Community submission via PR.

**To reach 10/10 on D06 (Multi-Agent):**
Add A2A protocol support (not just SubagentCoordinator) — agents calling remote nasim instances. `A2AServer` + `A2AClient` following gemini's pattern.

**To reach 10/10 on D20 (Async):**
Switch from synchronous provider calls to `httpx.AsyncClient`. This is already planned (httpx planned in CLAUDE.md) — execute it.

### Why nasim Cannot Quite Reach 10/10 on Every Dimension Simultaneously

Some 10/10 dimensions are in tension:

- aider's 14 edit strategies (D10=10) require no function calling. nasim uses function calling. EditStrategyManager can score 9/10 with 8 strategies covering all realistic model output formats.
- hermes's 20+ platform adapters (D01=10) require maintaining 20+ codebases. nasim's litellm proxy scores 9/10 by covering all providers through one interface — higher maintainability, slightly less per-provider optimization.
- SWE-agent's Reviewer (D12=10) is research-grade and slow. nasim's EvaluationEngine gets 9/10 by combining SuccessCheckRunner (fast) + LLMReviewer (optional, triggered for high-stakes tasks).

**A 9.5/10 is a more honest target — and higher than any single reference agent.**

### What "10/10 Design" Looks Like for nasim

nasim already has the **only 10/10 on D18** (design chain). After implementing E-01 through E-09:

| Dimension | Score | How |
|-----------|-------|-----|
| D01 | 9 | LiteLLMProxy covers 100+ providers |
| D02 | 9 | 20+ tools across all categories |
| D03 | 9 | ContextGraph + DistillationProcessor + PipelineOrchestrator |
| D04 | 9 | HybridRetriever (BM25 + embedding) + EpisodicMemory |
| D05 | 9 | SafetyCoordinator + OS sandbox + DiffSandbox |
| D06 | 9 | SubagentCoordinator (5-level) + A2A protocol |
| D07 | 9 | WireLog (append-only) + SessionStore (summary) |
| D08 | 9 | 9 hook events (matching claude-code) + typed events |
| D09 | 9 | RepoMapBuilder (PageRank + AST) + SemanticSearch (RAG) |
| D10 | 9 | EditStrategyManager (8 strategies) + DiffSandbox |
| D11 | 9 | Composite routing (7 strategies) + ModelRoleRegistry |
| D12 | 9 | EvaluationEngine (SuccessCheck + LLMReviewer + TurnBudget) |
| D13 | 9 | WebSearchProvider registry + WebFetchTool |
| D14 | 9 | OTel traces + metrics + structured logs + CostTracker |
| D15 | 9 | OS sandbox (landlock+seccomp) + DiffSandbox |
| D16 | 9 | WireLog + typed AgentEvent + PipelineOrchestrator |
| D17 | 9 | Plugin marketplace (GitHub-hosted registry) |
| D18 | **10** | Complete design chain (only agent to achieve this) |
| D19 | 9 | AST PageRank + embedding RAG + HybridRetriever |
| D20 | 9 | httpx.AsyncClient throughout |

**nasim Enhanced Total: 9.1/10 — highest in the corpus**

---

## Conclusion

### What nasim Has That No Reference Agent Has

1. **Complete design chain** (C4→UC→SM→SQ→ERD→CL→CT/DATA→CT/API→Code) — unique in the entire 28-agent corpus.
2. **Multi-interface architecture designed from the start** — CLI + HTTP + MCP all sharing the same event-yielding core.
3. **Entity registry with full layer traceability** — every component name tracks through all design layers.
4. **Formal state machine** for agent lifecycle — no reference agent models agent lifecycle as a state machine.
5. **PermissionGate with three modes** designed as a first-class component — not bolted on.

### What the Reference Corpus Has That nasim Needs

1. **PageRank repo-map** (aider) → E-01 RepoIntelligenceManager
2. **Edit strategy polymorphism** (aider) → E-02 EditStrategyManager
3. **SuccessCheck RL feedback loop** (goose) → E-03 EvaluationEngine
4. **Append-only wire event log** (kimi) → E-04 WireLog
5. **Embedding-based RAG memory** (claw-code, amazon-q) → E-05 MemoryStore RAG
6. **Graph-based context pipeline** (gemini) → E-06 ContextGraph
7. **Full OpenTelemetry wiring** (goose, codex) → E-07 (wire existing design)
8. **Composite model routing** (gemini, plandex) → E-08 ModelRouter enhance
9. **Diff sandbox review cycle** (plandex) → E-09 DiffSandboxManager

### Priority Order for Implementation

| Priority | Enhancement | D-gap closed | Design Impact |
|----------|-------------|-------------|---------------|
| P1 | E-03 EvaluationEngine | D12 +7 | New UC group EVL, new SM states |
| P1 | E-01 RepoIntelligenceManager | D09 +6 | New UC group RIM, C4 component |
| P2 | E-02 EditStrategyManager | D10 +6 | Extends TL group |
| P2 | E-05 MemoryStore RAG | D19 +4, D04 +2 | Extends MEM group |
| P3 | E-06 ContextGraph | D03 +3 | Replaces ConversationHistory in design |
| P3 | E-04 WireLog | D07 +1, D16 +1 | New UC group WRL |
| P4 | E-07 OTel Wiring | D14 +3 | Component wiring only |
| P4 | E-08 ModelRouter | D11 +2 | Extends PRV group |
| P5 | E-09 DiffSandbox | D10 +1, D15 +1 | Extends TL + SAF groups |
