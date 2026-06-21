# nasim — Frontier AI Agent Comparative Audit (2026)

**Date:** 2026-06-21
**Scope:** Comprehensive comparative audit of nasim against 28 reference code agents
**Framework:** CAR (Challenge → Action → Result) for all proposed improvements
**Method:** Direct code inspection of 28 cloned reference agent repositories;
structural analysis of nasim design chain (C4 → UC → SM → SQ → ERD → CL → CT → Code);
dimension-by-dimension scoring; ranked priority roadmap.

---

## Executive Summary

nasim occupies a paradox: it has the most complete design chain of any agent in the corpus
(148 sequence diagrams, 24 C4 diagrams, 148 UCs, 4 state machines, 5 ERDs, full OAS 3.1.0 spec)
but zero implementation. The reference corpus spans 28 agents across 5 languages, 3 architectural
paradigms, and maturity levels from research PoC to enterprise production.

Against the 2026 frontier standard, nasim scores well on architectural intent and design quality,
and poorly on every runtime dimension because no code exists. The design is architecturally
superior to most references in several respects: the event-driven provider abstraction,
comprehensive safety pipeline, and full HTTP API design are better planned than
what most agents have shipped. However, a design that cannot run is not an agent.

**Overall score: 12 / 100 (design: 60, implementation: 0, coverage: 0)**

| Dimension | Score | Status | Leading Reference |
|-----------|-------|--------|------------------|
| Tooling & capabilities | 0 / 10 | No implementation | gemini-cli, opencode |
| Provider abstraction | 1 / 10 | Designed, not built | opencode (13), aider (litellm) |
| Context management | 0 / 10 | No implementation | aider, codex |
| Safety & permissions | 0 / 10 | No implementation | codex (OS sandbox), goose (ML) |
| Session continuity | 0 / 10 | No implementation | opencode (event-sourced) |
| Planning & reasoning | 0 / 10 | No implementation | opencode, plandex |
| Multi-agent orchestration | 1 / 10 | Designed only | codex, gemini-cli |
| IDE integration | 0 / 10 | None designed | cline, Roo-Code |
| Performance & efficiency | 2 / 10 | Design decisions made | codex (Rust) |
| Observability | 0 / 10 | No implementation | goose (OTel), codex |
| Extension / plugin ecosystem | 1 / 10 | Designed only | claude-code, codex |
| Benchmark results | 0 / 10 | Not applicable | SWE-agent, plandex |

**Critical finding:** nasim must begin implementation immediately. Every additional design
iteration without working code widens the gap with agents that ship weekly.

---

## Methodology

### Reference Corpus

28 agents were cloned into `/home/salim/prj/salim/nasim/code/` and studied by:

1. Reading README, architecture documentation, and changelog.
2. Inspecting main entry points, LLM integration, tool definitions, and safety mechanisms.
3. Measuring lines of code, package structure, and architectural patterns.
4. Running available quick-start commands where documented.

### Scoring Rubric

Each dimension scored 0–10:
- **0** — not present in nasim
- **1–2** — designed but not implemented
- **3–4** — partially implemented, missing major pieces
- **5–6** — implemented with gaps vs frontier standard
- **7–8** — on par with leading reference agents
- **9–10** — sets the frontier standard

### nasim State as of Audit

- Design chain: **complete and frozen** (24 C4 diagrams, 148 UCs, 4 SMs, 148 SQs, 5 ERDs,
  full runtime class diagram, 5 ODCS contracts, OAS 3.1.0 spec)
- Implementation: **zero** — no Python source packages in `nasim/`, no `run.py`
- Testing: **zero**
- Prior PoC (v0.1): ~450 LOC, 4 modules, Ollama-only, 5 tools — **discarded**; design-chain
  replaced it as the reference for what to build.

---

## Reference Agent Profiles

### Tier 1 — Production-Grade (most instructive)

#### aider

**Language:** Python | **LOC:** ~13,000 | **Maturity:** Production (6.8M PyPI installs)

The most widely deployed Python coding agent. aider's primary differentiator is
edit-format polymorphism: 14 `Coder` subclasses (whole-file, search-replace, unified-diff,
architect two-model, context-only, ask-only, etc.) implement the Strategy pattern against
a common `base_coder.py` interface. The LLM never sees the file system directly; it produces
a structured edit block that the coder subclass applies.

The `repomap.py` module (867 LOC) uses tree-sitter to extract symbol graphs from the entire
codebase and compress them into a context-efficient outline. This is the single most
operationally important missing feature in nasim — without repo-map or equivalent,
the agent cannot reason about a codebase it cannot fit in context.

aider uses litellm for 100+ provider support with one import. Context management uses a
`ChatSummary` class that summarizes old messages via a weaker/cheaper secondary LLM call.
The 4-layer config system (`CLI > .env > .aider.conf.yml per CWD/git-root/home > defaults`)
is the gold standard for Python CLI configuration.

Key weakness: no function-calling tool system (LLM produces text; aider parses it).
This is an architectural limitation that prevents dynamic tool extension.

#### claude-code

**Language:** TypeScript/Bun | **LOC:** closed-source core | **Maturity:** Production (Anthropic)

The authoritative reference for hook systems and plugin architectures. claude-code exposes
9 hook events (PreToolUse, PostToolUse, UserPromptSubmit, Stop, etc.) where each hook can
be either a bash command or an LLM-driven prompt — the latter enables real validation logic
written in natural language. The plugin marketplace (14 official plugins) extends
capabilities without modifying the core.

Enterprise MDM deployment (Jamf, Intune) makes it the only agent in the corpus with
genuine enterprise multi-machine deployment story. The hierarchical config
(managed > user > project > local) is the cleanest permission-layering of any agent studied.

Skills system (SKILL.md files) enables Claude to auto-load prompt-engineered capabilities
when keywords appear in the prompt. Background sessions with tmux integration allow
long-running tasks to survive terminal disconnection.

Relevant to nasim: the hooks design maps directly to nasim's `HookManager` component.
The Skills system maps to a simpler version of what nasim's plugin system should do.

#### codex (OpenAI)

**Language:** Rust (124 crates) + TypeScript SDK | **LOC:** ~47,000 Rust | **Maturity:** Production

The most architecturally rigorous agent in the corpus. codex-rs enforces strict crate
boundaries through a 124-crate Cargo workspace. The core library has no TUI imports —
a hard boundary enforced by the build system, not convention.

OS-level sandboxing (landlock + seccomp on Linux, seatbelt on macOS, restricted token on
Windows) is the unique frontier capability that no Python agent has. `exec_policy.rs`
defines prefix-based allow/deny rules; `compact.rs` handles context compaction including
remote compaction via a secondary model call.

The `ThreadStore` trait with SQLite-backed `LocalThreadStore` provides type-safe session
persistence. `ContextFragment` injection allows dynamic context addition without modifying
the conversation history. The `ConfigLayerStack` (global TOML → project TOML → cloud → CLI)
with merge semantics is the most complete config system in the corpus.

Skills system maps YAML-defined capabilities to tool definitions. The app-server daemon
mode allows the agent to pre-warm and accept connections without cold-start overhead.

#### gemini-cli (Google)

**Language:** TypeScript/Node.js | **LOC:** ~33,000 | **Maturity:** Production (Google)

The most feature-complete single-vendor agent. The graph-based `ContextWorkingBuffer` with
`PipelineOrchestrator` is the most sophisticated context management architecture in the corpus —
context is modeled as a graph of nodes with edges representing dependencies, enabling
precise truncation that preserves semantic relationships.

20+ built-in tools including a native `ripgrep` wrapper, glob, web fetch + Google Search
grounding, memory context manager, plan mode, skills, todos, tracker, shell (background jobs).
The hook system (BeforeModel, AfterModel, BeforeToolSelection) with composite routing strategy
is the most configurable execution pipeline studied.

The Agent-to-Agent (A2A) server makes gemini-cli the only agent that exposes an A2A endpoint
for multi-agent orchestration scenarios. Voice input via Whisper + Gemini Live is the most
accessible multimodal feature in the corpus.

4 approval modes (DEFAULT, AUTO_EDIT, YOLO, PLAN) provide granular safety configuration.
Policy engine with priority-sorted TOML rules enables per-project safety overrides.

#### opencode

**Language:** TypeScript/Bun + Effect-TS | **LOC:** ~25,000 | **Maturity:** Production

The most architecturally innovative agent. Effect-TS (algebraic effects library) replaces
try/catch and async/await with a typed effect system — every function declares its effects,
errors, and dependencies as types. This makes the entire system traceable by the type checker.

Event-sourced session persistence via SQLite (Drizzle ORM, WAL mode) means every agent
action is an immutable event; the current state is always a projection of the event log.
Session snapshots enable exact undo of any turn. The snapshot/undo feature is unique in
the corpus.

25 packages in a Bun monorepo: core, llm, opencode (CLI/TUI), server (Hono), desktop
(Tauri), web, console, SDK, slack, plugin, etc. The same agent core serves CLI, TUI, web,
desktop, HTTP server, and Slack simultaneously — the reference implementation of what
nasim's multi-interface design intends.

13 LLM providers with schema-validated body construction per provider. LSP integration
as a tool (`lsp_hover`, `lsp_definition`, `lsp_references`) provides semantic code
intelligence without tree-sitter dependency. The plan agent mode uses a dedicated model
with edit permissions disabled — the cleanest read-only planning mode in the corpus.

#### goose (AAIF/Linux Foundation)

**Language:** Rust (10 crates) | **LOC:** ~35,000 | **Maturity:** Production

The most security-hardened agent. goose's `PromptInjectionScanner` uses both pattern matching
and optional ML (configurable confidence threshold) — the only agent in the corpus with
ML-based injection detection. The `SecurityInspector`, `AdversaryInspector`, and
`EgressInspector` form a multi-layer safety stack that no other agent approaches.

The extension architecture (extensions ARE MCP servers — every extension runs as a local
MCP server) is the cleanest extensibility model: adding a capability means creating an
MCP server, not modifying goose's core. The recipe system (yaml-defined multi-step
automation) and scheduler enable workflow automation.

The `moim.rs` (memory-of-important-messages) module is an elegant solution to context
compaction — instead of summarization, it marks high-value messages for retention
regardless of context pressure. OpenTelemetry integration provides production-grade
observability with trace/span correlation.

ACP (Agent Communication Protocol) support via the `acp` crate enables agent-to-agent
communication in multi-agent scenarios.

#### cline

**Language:** TypeScript/Bun | **LOC:** ~20,000 | **Maturity:** Production (VS Code)

The reference for IDE-integrated agents. 5 SDK layers (shared → llms → agents → core →
host apps) with a gateway pattern for provider abstraction. VS Code integration provides
diff previews in the editor, file tree manipulation, webview panels, and access to the
active editor context — capabilities only available inside the IDE.

The ClineHub platform for remote/team sessions and the subscription billing model
represent the commercial evolution of open-source coding agents. Session checkpoint-restore
and versioning/snapshots enable safe long-running task management.

The plugin architecture for host apps (any host can embed the agent by implementing the
host interface) is more composable than provider-specific integrations.

#### SWE-agent (Princeton/Stanford)

**Language:** Python | **LOC:** ~8,000 | **Maturity:** Research

The benchmark reference. SWE-agent's primary contribution is its retry-with-review loop:
when a patch fails CI, a reviewer agent analyzes the failure and produces a critique, which
feeds the coder agent on the next retry. This feedback architecture consistently outperforms
simple retry on SWE-bench.

YAML-defined tool bundles (`Bundle`) make the agent configuration fully declarative —
the entire agent behavior can be specified without touching Python. `HistoryProcessor`
chain applies a sequence of transformations to conversation history before each LLM call.
`ToolFilterConfig` blocklist prevents known-dangerous commands.

The Docker sandbox (`swe-rex`) provides environment isolation for untrusted code execution.
Cost tracking per instance (token counts, API costs) with configurable limits enables
research budget management. Note: the SWE-agent maintainers have since created mini-swe-agent
as the recommended successor.

#### plandex

**Language:** Go | **LOC:** ~18,000 | **Maturity:** Production

The reference for multi-role orchestration and plan-centric development. 9 specialized model
roles (planner, architect, coder, builder, summarizer, names, commit-messages, auto-continue)
each optimized for their task with independent temperature and model selection. This is the
most granular model routing in the corpus.

Plan branching and versioning (creating divergent execution paths and comparing results)
is unique to plandex. The cumulative diff sandbox reviews all proposed changes against
the repository state before applying — a diff-level safety check that prevents partial
application of conflicting edits.

Tree-sitter project maps provide 2M effective context by compressing large codebases
into symbol graphs. The client-server architecture (Go CLI → Go server with LiteLLM proxy)
enables remote execution and plan sharing.

### Tier 2 — Specialized / Mid-Maturity

#### kimi-cli (Moonshot AI)

**Language:** Python (~38 modules) | **Maturity:** Mid | **GitHub:** moonshot-ai/kimi-cli

The cleanest Python agent architecture in the corpus after nasim's design. kimi-cli
demonstrates the "Wire" pattern: the `Wire` abstraction fully decouples the agent soul
(`KimiSoul`) from any specific UI. UI frontends subscribe to wire events; the soul produces
only typed events. This maps exactly to nasim's `AgentEvent` generator pattern.

`LaborMarket` enables subagent spawning with fork support: a new `KimiSoul` instance is
created for a sub-task, runs to completion, and its result is returned to the parent.
`fork()` creates a new session branching from the current state — the first pure-Python
implementation of fork-based session branching studied.

Auto-compaction fires at 85% context budget using a configurable summarization strategy.
OAuth authentication integration via a browser-based flow enables secure API key management
without storing credentials in config files. The evolution into kimi-code (specialized for
coding) signals maturity: the generic agent core is stable, and specialized overlays are
layered on top.

Relevant to nasim: the Wire/Soul decoupling pattern, LaborMarket subagent spawning,
and fork-based session branching are all directly applicable and already designed.

#### crush (Charmbracelet)

**Language:** Go | **Maturity:** Mid | **GitHub:** charmbracelet/crush

The most ergonomic TUI in the corpus. Built on Bubbletea (Charm's TUI framework), crush
demonstrates that terminal UI can be as polished as web UI. The session-based context model
(one SQLite DB per project directory) provides instant project switching without explicit
`--project` flags.

LSP integration is crush's primary differentiator: instead of parsing source files,
crush queries the language server (if running) for hover information, symbol definitions,
and references. This provides semantic accuracy that tree-sitter cannot achieve for
dynamically-typed languages (Python type inference, JavaScript module resolution).

MCP support (http/stdio/sse transports) makes crush immediately compatible with the
growing MCP ecosystem. Cross-platform reach including Android (via Termux) and FreeBSD
demonstrates Go's portability advantage. The Charm aesthetic (gradients, borders, colors)
is worth studying for nasim's rich renderer design.

Relevant to nasim: LSP-as-tool approach, SQLite per-project session store, MCP transport
support. The TUI aesthetic is aspirational for nasim's renderer.

#### Roo-Code

**Language:** TypeScript | **Maturity:** Mid | **GitHub:** RooVetGit/Roo-Code

A community-driven fork of Cline that diverged significantly on the role-based mode system.
4 core modes (Code, Architect, Ask, Debug) plus Custom modes define what each mode can do:
- Code mode: all tools, full write access.
- Architect mode: read tools only, planning tools only, no WriteFileTool.
- Ask mode: read-only, no file modification ever.
- Debug mode: read + shell (for running tests), no write.

The mode constraint is enforced at the tool registration level — Architect mode never
has WriteFileTool in its ToolRegistry. This is cleaner than runtime gating and maps
directly to nasim's `PersonaManager` design.

500+ model support via a broad provider catalog (distinct from litellm — Roo-Code
implements its own provider list). The community has contributed integrations faster
than the core team can maintain, leading to both breadth and inconsistency.

Relevant to nasim: the mode-based tool restriction pattern is the implementation target
for `PersonaManager.apply()`. The per-mode `ToolRegistry` filter is the right design.

#### OpenHands

**Language:** TypeScript frontend + Python backend | **Maturity:** Production (platform)

Not a coding agent — an agent orchestration platform. OpenHands exposes an ACP
(Agent Communication Protocol) control plane that any ACP-compatible agent can register
with. The unified frontend (OpenHands UI) allows selecting which backend agent runs
(Claude Code, Codex, Gemini CLI, OpenHands native) while maintaining a consistent
session and tool interface.

The `CodeActAgent` (native OpenHands agent) uses a Docker sandbox for code execution —
the agent writes code to a sandbox container, runs it, reads the output, and iterates.
This is the most reliable approach for code generation tasks where execution validation
is required.

Prebuilt automations (Slack → GitHub issue decomposition → PR creation) represent
the highest-level automation in the corpus. The automation graph is declarative YAML.

Relevant to nasim: ACP server implementation in `nasim/server/` (Phase 3) would make
nasim an OpenHands-compatible backend. The Docker sandbox approach is a safer alternative
to OS-level landlock for Python agents.

#### amazon-q-developer-cli (now Kiro CLI)

**Language:** Rust | **Maturity:** Deprecated as OSS

The most notable OSS contribution from Amazon before abandonment: SQLite-backed semantic
search of shell history. Every shell command typed in any session is stored with context
(cwd, exit code, timestamp, session ID). The agent can recall relevant past commands
semantically ("how did I compile this project last time?") rather than relying on the
shell's sequential `history` file.

Deep AWS IAM integration allows the agent to reason about AWS resource access and suggest
permission adjustments. Now closed-source as Kiro CLI. The semantic shell history approach
is not implemented in any other agent studied and represents a niche but high-value capability.

Relevant to nasim: semantic shell history could be added to the `SessionStore` (store
every `ShellTool` invocation with result) and exposed via a `RecallTool`.

#### openinterpreter

**Language:** Rust core (forked codex-rs) + Python harness | **Maturity:** Production

The harness around codex-rs adds three capabilities not in the original:
1. **Persona swapping**: 8 configurable personas (standard, coding, research, chat,
   technical, creative, analysis, casual) each with distinct system prompts and tool
   availability. Switching personas at runtime (without restarting the agent) via
   `/persona <name>` slash command demonstrates that the persona system must be dynamic.
2. **Computer use**: cursor control, screenshot capture, GUI automation. The only agent
   in the corpus with full desktop automation.
3. **Multi-modal input**: voice transcription via Whisper, image analysis via vision-capable
   models. Images can be passed as tool results (screenshot → analysis).

The OS-level sandbox is inherited from codex-rs (landlock, seccomp, seatbelt) — the
persona system runs on top of the same safety substrate.

Relevant to nasim: persona swapping at runtime (not just at startup) and the `/persona`
slash command are the exact interaction design nasim should implement for `PersonaManager`.

#### warp

**Language:** Rust | **Maturity:** Production (commercial)

Warp owns the entire terminal stack (replaces the shell itself), which gives it context
that no CLI-overlay agent can match: command timing, exit codes, cwd per command, git
integration native to the shell rendering. The Warp AI agent can see the exact command
history and output without shell history limitations.

The "blocks" abstraction (each command + output is a navigable block) is a UI innovation
that makes long terminal sessions scannable. The agent can attach to any block as context.
Commercial model: Warp AI is a paid feature of the Warp terminal.

Relevant to nasim: Warp is out of scope for a CLI-overlay agent, but the blocks metaphor
is worth adapting for the rich renderer — render each agent turn as a collapsible block
rather than a flat stream.

#### hermes-agent

**Language:** Python | **Maturity:** Early

One notable architectural decision in the source: a comment in `context_engine.py` marks
prompt caching as "a sacred constraint" — meaning the system prompt must never change
between turns (to maximize Anthropic cache hit rate). This is an operational optimization
that most agents miss: prompt cache credits only apply when the system prompt is byte-identical.

Relevant to nasim: `LiteLLMProxy` should expose a `cache_system_prompt: bool` config
option. When enabled, the system prompt is frozen after session start and all dynamic
context (repo map, memory, persona) is injected as the first user message rather than
into the system prompt. This enables Anthropic cache hits.

#### mini-swe-agent (SWE-agent maintainers)

**Language:** Python | **Maturity:** Active development (recommended over SWE-agent)

The minimal reimplementation of SWE-agent by the original authors. Removes the complex
YAML Bundle system in favor of a simpler tool definition model. `BashTool` as a single
comprehensive tool (shell + file operations) is the opposite design choice from nasim's
specialized tools — a deliberate tradeoff: one tool is simpler for the LLM but allows
more dangerous operations.

The retry-with-review loop is preserved from SWE-agent: `RetryAgent` catches failures
and calls a `ReviewerAgent` with the failure context to generate a critique before the
next attempt. This is the most impactful architectural pattern from the SWE-bench research.

Relevant to nasim: the retry-with-review pattern maps to nasim's `RetryCoordinator` and
`EvaluationEngine` (EVL-01 through EVL-04). Priority P3.5.

---

## Criteria of Success for Frontier Code Agents (2026)

Derived from the reference corpus. Each criterion describes what the frontier standard is
and why it matters operationally.

---

### C1 — Tooling Richness and Coverage

**Standard:** Minimum viable tool set for any real codebase:
- File I/O: read, write, edit (line-precise diff or search/replace)
- Search: grep (ripgrep-backed), glob, find, semantic symbol search
- Shell: exec with timeout, background jobs
- Web: fetch (URL to markdown), search (configurable backend)
- Git: status, diff, log, branch, commit, push
- LSP: hover, definition, references, symbols
- MCP: dynamic extension tools from any MCP server
- Memory: persist/recall facts across sessions
- Todo/plan: structured task tracking
- Subagent: spawn specialized sub-instances

**Frontier examples:** gemini-cli (20+ built-in tools), opencode (core + app tool layers),
codex (ToolDefinition + ToolSpec + ToolExecutor + plugin discovery).

**Why it matters:** A coding agent that cannot search a codebase is useless on any
non-trivial project. Grep/glob alone eliminates 80% of the "I can't find the code" failures.
Web fetch eliminates "I don't know the API" failures. LSP eliminates symbol-resolution
hallucinations.

---

### C2 — Provider Abstraction and Model Support

**Standard:** Protocol/trait/interface for LLM backends with at minimum:
- OpenAI-compatible (catches OpenAI, local vLLM, LM Studio, Ollama with OpenAI-compat API)
- Native Anthropic (Claude models, prompt caching)
- Google Gemini
- Local Ollama (native API)
- Streaming support for all
- Model capability declaration (supports_tools, supports_vision, max_context)
- Fallback chains (provider A fails → provider B)
- Per-task model routing (cheap model for summaries, strong model for coding)

**Frontier examples:** opencode (13 providers, Effect-TS Route abstraction), aider (litellm
100+), codex (ModelProvider trait with capability declarations), goose (15 providers + tool shim
for providers without native tool support).

**Why it matters:** Locking to one provider is a DX failure and a capability ceiling. The
fastest-improving model changes every 2–4 months; provider lock-in means lagging 2 model
generations behind the frontier.

---

### C3 — Context Management

**Standard:**
- Token counting (model-specific; tiktoken or provider-reported)
- Budget enforcement (hard limit per model's context window)
- Compaction trigger (configurable threshold, e.g. 80%)
- Compaction strategy: summarize old exchanges via secondary LLM call (preserve semantic core)
- Repo-map or equivalent: compress entire codebase into symbol outline that fits in context
- Conversation history class with cur/done split or event sourcing
- Context fragment injection for structured context additions

**Frontier examples:** aider (ChatSummary + repo-map 867 LOC), codex (compact.rs + remote
compaction + ContextFragment), gemini-cli (graph-based ContextWorkingBuffer + PipelineOrchestrator),
opencode (event-sourced projector + compaction agent + snapshot/undo).

**Why it matters:** Unbounded context growth crashes sessions silently. Token budget
enforcement is the difference between an agent that works on small tasks and one that
completes a multi-hour refactoring job.

---

### C4 — Safety and Permissions

**Standard:**
- Per-tool safety annotation (safe vs. unsafe)
- User approval modes: ask (prompt before unsafe ops), auto (never prompt), off (everything allowed)
- Permission rules: allow/deny per tool or pattern, per project
- Prompt injection detection: pattern matching at minimum, ML-based preferred
- Egress inspection: what the agent is about to write/execute
- OS-level sandbox (landlock/seccomp on Linux, seatbelt on macOS) for shell commands
- Diff sandbox for file changes (review accumulated diff before applying)
- Rate limiting / iteration budget (prevent runaway loops)

**Frontier examples:** codex (OS-level sandbox multi-platform + exec_policy.rs), goose
(ML injection scanner + SecurityInspector + AdversaryInspector + EgressInspector), opencode
(rule-based permissions with always-remember per project), gemini-cli (4 approval modes +
policy engine + folder trust discovery).

**Why it matters:** `rm -rf` executed by a confused LLM is unrecoverable. The safety
system is not a feature; it is the prerequisite for trusting the agent with write access
to any production codebase. Without it, nasim cannot be recommended for real use.

---

### C5 — Session Continuity and Memory

**Standard:**
- Session persistence: state survives process restart
- Session resume: `--continue` to pick up exactly where left off
- Session listing and search: find sessions by project, date, task
- Session fork: branch from a previous turn (undo + alternative path)
- Session snapshot/undo: revert the last N turns
- Memory store: persist facts across sessions (scope: global, project, session)
- Memory recall: search by keyword or semantic similarity

**Frontier examples:** opencode (event-sourced SQLite, snapshot/undo, location-scoped DBs),
codex (SQLite ThreadStore with create/resume/archive/delete lifecycle), goose (session naming,
diagnostics, search, Nostr sharing, moim for high-value message retention), kimi-cli
(fork support).

**Why it matters:** "I already explained that yesterday" is a quality-of-life issue that
degrades user trust. Without session persistence, every conversation starts from scratch.
Without memory, the agent cannot accumulate project-specific knowledge.

---

### C6 — Planning and Reasoning

**Standard:**
- Plan mode: read-only exploration before executing changes
- Plan presentation: structured list of proposed changes for user approval
- Plan branching: diverge execution paths, compare outcomes
- Structured task queue: ordered list of steps the agent plans to execute
- Multi-step reasoning: think before acting (CoT, extended thinking, o-series models)
- Retry-with-review: when a step fails, analyze the failure before retrying

**Frontier examples:** plandex (full plan branching + versioning, 9 roles), opencode
(plan agent mode with edit permissions disabled), gemini-cli (PLAN approval mode),
SWE-agent (retry-with-review loop via RetryAgent + reviewer), codex (planning mode flag).

**Why it matters:** An agent that acts immediately without planning makes expensive,
hard-to-reverse mistakes. Plan mode shifts the agent from reactive (execute immediately)
to deliberate (propose → review → execute).

---

### C7 — Multi-Agent Orchestration

**Standard:**
- Subagent spawning: create specialized sub-instances with constrained capabilities
- Role-based delegation: different model/persona for different task types
- Nesting limits: prevent recursive depth explosion (e.g., max 5 levels)
- Result collection: structured aggregation of subagent outputs
- Concurrency: parallel subagent execution where tasks are independent
- ACP support: agent-to-agent communication protocol

**Frontier examples:** plandex (9 specialized roles with independent model + temperature),
codex (subagent task dispatch), gemini-cli (A2A server), goose (orchestrator extension +
summon tool), opencode (background subagents), kimi-cli (LaborMarket).

**Why it matters:** Single-agent architectures hit a ceiling on complex, multi-file
refactorings where different concerns require different expertise. Multi-agent orchestration
is the path from "coding assistant" to "autonomous engineering team."

---

### C8 — IDE Integration

**Standard:**
- VS Code extension: diff previews, file tree, inline chat, webview
- Editor-native context: active file, selection, cursor position
- Deep diff preview before apply
- Diagnostic integration: read compiler errors / linter output
- Language server access: symbols, hover, go-to-definition
- Terminal embedding (Warp)

**Frontier examples:** cline (VS Code extension, webview, diff previews), Roo-Code (VS Code
modes), vscode-ide-companion (gemini-cli's companion), warp (owns the entire terminal stack),
claude-code (VS Code extension + MCP server for editors).

**Why it matters:** Terminal-only agents lose the active editor context. IDE-integrated
agents know exactly what file the user is looking at, what error is highlighted, and what
symbols are in scope — context that dramatically improves task quality.

---

### C9 — Performance and Efficiency

**Standard:**
- Async I/O: non-blocking LLM calls, concurrent tool execution
- Streaming: first token visible within 100ms of LLM response start
- Incremental rendering: smooth output without buffering full response
- Cold start: ready in < 500ms
- Prompt caching: send the same system prompt once; use cache credits for subsequent calls
- Background pre-warming: daemon mode to eliminate cold start

**Frontier examples:** codex (Rust, async trait objects, app-server daemon), opencode
(Effect-TS structured concurrency, Bun runtime), goose (Rust, async), aider (Anthropic
prompt caching explicit support), hermes-agent (context_engine.py marks caching as
a sacred constraint).

**Why it matters:** An agent that takes 10 seconds before streaming the first token is
unusable in interactive mode. Async I/O enables concurrent tool execution (run N tools
in parallel) and HTTP server mode alongside the agent loop.

---

### C10 — Observability

**Standard:**
- Structured logging: JSON output, configurable level, per-module loggers
- Request correlation: request_id / trace_id in every log line
- LLM call logging: debug-level logging of every prompt/response (opt-in)
- Tool call logging: log every tool invocation with args and result
- Token/cost metrics: track tokens used, estimated cost per session
- Wire log: raw API wire-level transcript for debugging
- OpenTelemetry: spans for LLM calls, tool calls, agent turns
- Prometheus metrics: token counts, latency histograms, error rates

**Frontier examples:** goose (OpenTelemetry trace/span, named spans per agent turn),
codex (wire log transcript, token/cost tracking), aider (structured logging to file),
gemini-cli (telemetry module, cost estimation).

**Why it matters:** An agent running in production (or even daily development) that
produces no telemetry is a black box. When something goes wrong, the developer has
no signal. Structured logging with trace correlation is the minimum to make a session
debuggable.

---

### C11 — Extension and Plugin Ecosystem

**Standard:**
- Plugin manifest: declarative capability declaration (tools, hooks, prompts)
- Dynamic tool registration: add tools at runtime without restart
- Hook integration: plugins can hook PreToolUse / PostToolUse / PreModel / PostModel
- Community marketplace: discovery and installation of third-party plugins
- MCP as universal extension protocol: any MCP server becomes a capability source
- Plugin isolation: plugin failures cannot crash the agent

**Frontier examples:** claude-code (marketplace, 14 official plugins, SKILL.md auto-activation),
codex (plugin installation tools, tool search/discovery, skills system), goose (extensions ARE
MCP servers — cleanest model), gemini-cli (skills system, MCP client), cline (plugin registry
for host apps).

**Why it matters:** No single agent team can implement every tool for every workflow.
Extensions allow the community to contribute capabilities without modifying the core.
MCP as the universal protocol means any MCP server (file system, databases, APIs)
becomes available to all agents simultaneously.

---

### C12 — Benchmark and Real-World Validation

**Standard:**
- SWE-bench Lite/Full scores (software engineering tasks from real GitHub issues)
- HumanEval / MBPP (pure code generation)
- Internal regression suite (agent-own codebase tasks)
- Cost efficiency metrics (quality per dollar per benchmark task)
- Real-world usage telemetry (session completion rates, user retention)

**Frontier examples:** SWE-agent (designed specifically for SWE-bench, academic publication),
aider (top OpenRouter usage, 88% self-written last release), plandex (multi-file focus
measured on real codebases), opencode (dogfooding — opencode is used to develop opencode).

**Why it matters:** Without benchmarks, "better" is a claim without evidence. SWE-bench
provides an objective signal for software engineering capability that is correlated with
real-world usefulness.

---

## nasim Current State Assessment

### Design Chain State (Strong)

nasim has the most comprehensive pre-implementation design chain of any agent in the corpus.
No reference agent has this level of design documentation before code. This is a genuine
competitive advantage for the design quality of the eventual implementation.

| Layer | Artifacts | Quality |
|-------|-----------|---------|
| C4 Architecture | 24 diagrams (98% pass in last audit) | High |
| Use Cases | 148 UCs across 21 groups (100% pass) | High |
| State Machines | 4 diagrams (agent, session, plan, plugin) | High |
| Sequence Diagrams | 148 diagrams, 1:1 with UCs (97% pass) | High |
| ERD | 5 store schemas | Good |
| Class Diagram | 90+ runtime classes | Good |
| Data Contracts | 5 ODCS v3.1.0 + 2 YAML schemas | Good |
| HTTP API | OAS 3.1.0, 23 endpoints, 8 resources, ROD | Good |
| Implementation Roadmap | 10 milestone docs | Active |

### Implementation State (Zero)

The `nasim/` Python package does not exist. There is no `run.py`. There are no test files.
The v0.1 PoC (4 modules, 450 LOC) was discarded after the design sprint.

**Consequence:** Every capability score is 0 or 1. The design intent is excellent.
The execution is nonexistent.

### Architectural Intent Assessment

Against C1–C12 criteria, nasim's design intends to address:

| Criterion | Design Intent | Status |
|-----------|--------------|--------|
| C1 Tooling | 21 tool types including LSP, subagent, memory, plan, repo-map | Designed |
| C2 Provider | litellm universal proxy, LiteLLMProxy, ProviderFactory | Designed |
| C3 Context | ContextGraph, PipelineOrchestrator, compaction, token budget | Designed |
| C4 Safety | SafetyCoordinator + PermissionGate + InjectionScanner + EgressInspector + SandboxExecutor | Designed |
| C5 Session | SessionStore + SessionVersioning + SessionFork + MemoryStore | Designed |
| C6 Planning | PlanSession + SubagentCoordinator + SandboxExecutor | Designed |
| C7 Multi-agent | SubagentCoordinator + TaskDispatcher + nesting limit 5 | Designed |
| C8 IDE | Not designed (CLI + HTTP only) | Gap |
| C9 Performance | httpx async, streaming, litellm caching | Designed |
| C10 Observability | StructuredLogger + MetricsCollector + TraceCorrelator + OTelExporter + WireLog | Designed |
| C11 Extensions | PluginLoader + HookManager + MCPClientRuntime + MCPServerRuntime | Designed |
| C12 Benchmarks | Not designed | Gap |

---

## Comparative Scorecard

Scores are operational (can the agent do this today?).
nasim design points are noted separately where relevant.

| Criterion | nasim | aider | claude-code | codex | gemini-cli | opencode | goose | cline | SWE-agent | plandex |
|-----------|-------|-------|-------------|-------|------------|---------|-------|-------|-----------|---------|
| C1 Tooling | 0 | 7 | 8 | 8 | 9 | 9 | 7 | 7 | 5 | 6 |
| C2 Provider | 1 | 8 | 7 | 8 | 4 | 9 | 8 | 8 | 7 | 7 |
| C3 Context | 0 | 8 | 7 | 9 | 9 | 8 | 7 | 6 | 5 | 7 |
| C4 Safety | 0 | 5 | 8 | 10 | 8 | 9 | 10 | 5 | 5 | 7 |
| C5 Session | 0 | 4 | 7 | 9 | 7 | 10 | 8 | 7 | 2 | 8 |
| C6 Planning | 1 | 3 | 4 | 4 | 7 | 8 | 4 | 3 | 6 | 10 |
| C7 Multi-agent | 1 | 2 | 8 | 7 | 8 | 7 | 7 | 2 | 5 | 6 |
| C8 IDE | 0 | 3 | 7 | 5 | 6 | 7 | 3 | 10 | 2 | 2 |
| C9 Performance | 2 | 5 | 7 | 9 | 7 | 9 | 9 | 6 | 4 | 6 |
| C10 Observability | 0 | 5 | 7 | 8 | 7 | 7 | 9 | 5 | 3 | 5 |
| C11 Extensions | 1 | 2 | 10 | 8 | 8 | 8 | 9 | 7 | 2 | 3 |
| C12 Benchmarks | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 6 |
| **Total** | **6** | **59** | **83** | **85** | **80** | **91** | **81** | **66** | **49** | **73** |

**Notes:**
- nasim score of 6 reflects 1–2 points per designed-but-not-built criterion.
- opencode leads overall because of event-sourcing, multi-frontend, and Effect-TS concurrency.
- codex leads on safety (OS-level sandbox) and performance (Rust + compaction).
- cline leads on IDE integration but lags on most other criteria.
- SWE-agent leads on benchmarks but lags on production capabilities.

---

## Gap Analysis by Dimension

---

### GAP-01: Provider Abstraction (C2) — Critical

**Challenge:**
nasim's design specifies `LiteLLMProxy` as the universal provider adapter. The design is
correct: litellm wraps 100+ providers with one interface. However, no implementation exists.
The v0.1 PoC used a hardcoded `OllamaClient`. Every agent capability downstream depends on
the provider interface being correct: streaming events, tool call deserialization, token
counting, and prompt caching all depend on a stable `LLMResponse` and `ToolCall` model.

**Action:**
1. Create `nasim/provider/base.py`:
   ```python
   from typing import Protocol, Iterator
   from dataclasses import dataclass

   @dataclass
   class ToolCall:
       id: str
       name: str
       arguments: dict

   @dataclass
   class LLMResponse:
       text: str | None
       tool_calls: list[ToolCall]
       input_tokens: int
       output_tokens: int
       finish_reason: str

   class Provider(Protocol):
       model_name: str
       context_limit: int
       supports_tools: bool
       supports_streaming: bool

       def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse: ...
       def chat_stream(self, messages: list[dict], tools: list[dict]) -> Iterator[str | ToolCall]: ...
   ```
2. Create `nasim/provider/litellm_proxy.py` wrapping `litellm.completion()` and
   `litellm.completion_stream()`. Map litellm's response schema to `LLMResponse`.
3. Create `nasim/provider/factory.py`: `ProviderFactory.from_config(config: Config) → Provider`.
4. Add `litellm` to `pyproject.toml` dependencies.
5. Write tests in `tests/provider/test_litellm_proxy.py` against a mock litellm call.

**Result:**
- nasim immediately supports every provider litellm supports (OpenAI, Anthropic, Ollama,
  Gemini, Bedrock, Azure, Groq, Mistral, Cohere, etc.) via one implementation.
- Adding a new provider = zero code change (litellm handles it).
- Matches the reference standard: aider uses litellm identically; plandex uses litellm
  via a Go server; SWE-agent uses litellm with cost tracking.
- Design-chain traceability: PRV-01 → PRV-04 → `sq_prv01.puml` → `LiteLLMProxy`.

---

### GAP-02: Tool System (C1) — Critical

**Challenge:**
nasim has 5 tools in the discarded PoC: read_file, write_file, edit_file, list_dir, shell.
These are free functions in a global dict. No ABC, no `ToolResult`, no `safe` flag, no MCP
extension support. The reference standard is 12–21 tools with an instance-based registry and
structured results. Without grep/glob/find, the agent cannot locate code in any real codebase.

**Action:**
1. Create `nasim/tools/base.py`:
   ```python
   from abc import ABC, abstractmethod
   from dataclasses import dataclass

   @dataclass
   class ToolResult:
       success: bool
       content: str
       error: str | None = None

   class Tool(ABC):
       name: str
       description: str
       parameters: dict  # JSON Schema
       safe: bool

       @abstractmethod
       def execute(self, **kwargs) -> ToolResult: ...
   ```
2. Create `nasim/tools/registry.py`: `ToolRegistry` with `register(tool: Tool)`,
   `execute(name, args) → ToolResult`, `definitions() → list[dict]` (for LLM function calling).
3. Implement priority tools in order:
   - `nasim/tools/search.py`: `GrepTool` (subprocess ripgrep), `GlobTool` (pathlib.glob),
     `FindFileTool` (os.walk with pattern matching).
   - `nasim/tools/file.py`: `ReadFileTool`, `WriteFileTool`, `EditFileTool` (search-replace).
   - `nasim/tools/shell.py`: `ShellTool` with timeout and output truncation.
   - `nasim/tools/web.py`: `WebFetchTool` (httpx + html2text), `WebSearchTool` (configurable
     backend: DuckDuckGo or SerpAPI).
   - `nasim/tools/git.py`: `GitTool` wrapping subprocess git.
   - `nasim/tools/directory.py`: `DirTool` (list with depth limit).
4. Implement `nasim/tools/mcp.py`: `MCPToolAdapter(Tool)` wrapping `mcp.ClientSession` tools
   into the nasim `Tool` interface. Use the `mcp` SDK.

**Result:**
- 11 core tools (grep, glob, find, read, write, edit, shell, web-fetch, web-search, git, dir).
- Dynamic MCP tool registration for any community extension.
- Structured `ToolResult` eliminates string error propagation.
- `safe` annotation per tool enables permission gating without hardcoded lists.
- Design-chain traceability: TL-01 → TL-12 → 12 SQ diagrams.

---

### GAP-03: Configuration System (C4) — Critical

**Challenge:**
The discarded PoC has no config files. Every session requires re-specifying `--server` and
`--model`. 25/28 reference agents persist configuration. Without config, the agent cannot
be installed and used by a second person without reading the source code to find defaults.

**Action:**
1. Create `nasim/config/schema.py`:
   ```python
   from pydantic import BaseModel
   from pydantic_settings import BaseSettings, SettingsConfigDict

   class ProviderConfig(BaseModel):
       name: str = "ollama"
       model: str = "qwen2.5-coder:7b"
       base_url: str | None = None
       api_key: str | None = None

   class Config(BaseSettings):
       model_config = SettingsConfigDict(env_prefix="NASIM_", env_file=".env")
       provider: ProviderConfig = ProviderConfig()
       safety_mode: str = "ask"     # ask | auto | off
       context_budget: int = 80000  # tokens
       max_iterations: int = 20
       session_dir: str = "~/.nasim/sessions"
       log_level: str = "INFO"
   ```
2. Create `nasim/config/loader.py`: `ConfigLoader` with 4-layer merge:
   - Layer 1 (lowest): built-in defaults
   - Layer 2: `~/.nasim/config.yaml`
   - Layer 3: `.nasim/config.yaml` (project-local)
   - Layer 4 (highest): `NASIM_*` env vars + CLI flags
3. Load once at startup; pass `Config` instance through dependency injection to all components.
4. Add `pydantic-settings` and `pyyaml` to `pyproject.toml`.

**Result:**
- Persistent configuration survives session restarts.
- Project-level overrides for different repositories.
- Environment variable support for CI/CD and containers.
- Matches aider's 4-layer system, which is the most copied pattern in the corpus.
- Design-chain traceability: CFG-01 → CFG-03 → `sq_cfg01.puml` → `ConfigLoader`.

---

### GAP-04: Event-Driven Agent Core (C9) — Critical

**Challenge:**
The AgentOrchestrator must yield `AgentEvent` objects; it must never call `print()`.
This is the architectural invariant that enables the same core to serve CLI, HTTP SSE,
and MCP simultaneously. The v0.1 PoC violated this with 8 `print()` calls in `agent.py`.
Without the event system, adding the HTTP server (Phase 3) requires rewriting the agent.

**Action:**
1. Create `nasim/agent/events.py`:
   ```python
   from dataclasses import dataclass

   class AgentEvent: pass

   @dataclass
   class TextChunk(AgentEvent):
       text: str

   @dataclass
   class ToolStart(AgentEvent):
       name: str
       args: dict

   @dataclass
   class ToolResultEvent(AgentEvent):
       name: str
       success: bool
       content: str

   @dataclass
   class ApprovalRequest(AgentEvent):
       tool_name: str
       args: dict

   @dataclass
   class Error(AgentEvent):
       message: str
       recoverable: bool = True

   @dataclass
   class Done(AgentEvent):
       final_text: str
       total_tokens: int
   ```
2. Create `nasim/agent/orchestrator.py`: `AgentOrchestrator.run(task: str) → Iterator[AgentEvent]`.
   - Inner loop: call provider, yield TextChunk events from stream, yield ToolStart → execute
     → yield ToolResultEvent.
   - On permission required in `ask` mode: yield `ApprovalRequest`; CLI renders prompt and
     returns user answer; agent waits for signal.
   - Zero `print()`, `input()`, or sys.stdout calls anywhere in agent/ package.
3. Create `nasim/cli/renderer.py`: `Renderer` subscribes to `AgentEvent` generator and
   renders using `rich`. `TextChunk` → streaming markdown. `ToolStart` → dim status line.
   `ApprovalRequest` → `[y/N]` prompt with rich Panel.

**Result:**
- Agent core is UI-agnostic and testable (no stdout capture needed in tests).
- Same agent serves CLI, HTTP SSE, and MCP by plugging in a different subscriber.
- Matches: opencode (Effect-TS events), gemini-cli (9 hook events), codex (event structs).
- Design-chain traceability: AGT-01 → AGT-15 → events.py → orchestrator.py.

---

### GAP-05: Context Window Management (C3) — Critical

**Challenge:**
Without token counting and compaction, sessions longer than ~50 exchanges will exceed
the model's context window. The symptom is silent degradation (the model starts ignoring
old context) or an explicit API error. No reference agent ships without context management.

**Action:**
1. Create `nasim/agent/history.py`:
   ```python
   from dataclasses import dataclass, field
   import tiktoken  # or litellm.token_counter

   @dataclass
   class ConversationHistory:
       messages: list[dict] = field(default_factory=list)
       token_count: int = 0
       context_budget: int = 80000

       def add_message(self, role: str, content: str) -> None:
           msg = {"role": role, "content": content}
           self.messages.append(msg)
           self.token_count += self._count_tokens(content)

       def check_budget(self) -> bool:
           return self.token_count < self.context_budget * 0.8

       def _count_tokens(self, text: str) -> int:
           # Use litellm.token_counter for model-accurate counting
           ...
   ```
2. Create `nasim/agent/compactor.py`: `ContextCompactor` triggered when `check_budget()`
   returns False. Summarizes the oldest 40% of messages via a secondary provider call
   (configurable: use a cheap model). Replaces the summarized range with a single summary
   message. Preserves the most recent 60% untouched.
3. Hook `ContextCompactor` into `AgentOrchestrator.run()` — check before each LLM call.

**Result:**
- Sessions of arbitrary length without degradation.
- Token budget enforced per model's actual context window.
- Compaction preserves task continuity without data loss.
- Matches: aider (ChatSummary), codex (compact.rs), gemini-cli (compaction service),
  kimi-cli (85% threshold auto-compaction).

---

### GAP-06: Session Persistence (C5) — Critical

**Challenge:**
Quit = lose everything. Every reference agent that targets production use persists sessions.
Without persistence, the agent cannot be used for tasks spanning multiple sessions, and every
debugging session must re-establish context from scratch.

**Action:**
1. Create `nasim/session/model.py`:
   ```python
   from dataclasses import dataclass, field
   from datetime import datetime
   import uuid

   @dataclass
   class Session:
       id: str = field(default_factory=lambda: str(uuid.uuid4()))
       created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
       project_path: str = ""
       messages: list[dict] = field(default_factory=list)
       title: str = ""
   ```
2. Create `nasim/session/store.py`: `SessionStore` using JSON Lines files in
   `~/.nasim/sessions/<session-id>/session.jsonl`. Atomic write (write to `.tmp`, rename).
   Methods: `save(session)`, `load(session_id) → Session`, `load_latest() → Session | None`,
   `list_sessions() → list[Session]`.
3. Wire into `AgentOrchestrator`: auto-save after each agent turn. On startup with
   `--continue`, load latest session; with `--session <id>`, load by ID.
4. Add CLI commands: `nasim --list-sessions` → tabular output; `nasim --continue` → resume.

**Result:**
- Sessions survive process restart.
- Resume any session by ID or load the most recent.
- Multiple sessions per project, listed with creation time and title.
- Matches: codex (SQLite ThreadStore), opencode (event-sourced SQLite), kimi-cli (fork support).

---

### GAP-07: Safety and Permission System (C4) — Critical

**Challenge:**
`shell_exec` in the v0.1 PoC runs any command without asking. `write_file` overwrites
without confirmation. This is dangerous for any real use. A confused LLM can silently
delete files, run `git reset --hard`, or exfiltrate data.

**Action:**
1. Create `nasim/agent/permission.py`:
   ```python
   from enum import Enum

   class SafetyMode(Enum):
       ASK = "ask"    # prompt before every unsafe tool
       AUTO = "auto"  # approve all (scripted use)
       OFF = "off"    # block all unsafe tools

   class PermissionGate:
       def __init__(self, mode: SafetyMode) -> None:
           self._mode = mode

       def check(self, tool: Tool) -> bool:
           if tool.safe:
               return True
           if self._mode == SafetyMode.ASK:
               return False  # caller must yield ApprovalRequest
           if self._mode == SafetyMode.AUTO:
               return True
           return False  # SafetyMode.OFF blocks all unsafe tools
   ```
2. Wire into `AgentOrchestrator.run()`: before executing any tool, call
   `permission_gate.check(tool)`. If False, yield `ApprovalRequest`; wait for
   CLI renderer to resolve; then proceed or skip.
3. Mark all tools: `ReadFileTool.safe = True`, `WriteFileTool.safe = False`,
   `ShellTool.safe = False`, `GrepTool.safe = True`, etc.
4. Add injection scanner in `nasim/agent/safety.py`: `InjectionScanner` with a
   rule-based pattern list targeting prompt injection attempts in tool outputs.
5. Add `--yes` / `-y` flag to CLI for scripted use (sets `SafetyMode.AUTO`).
6. Add iteration budget enforcement: max N tool calls per session (configurable, default 20).

**Result:**
- No dangerous operation executes without user consent in `ask` mode.
- `auto` mode enables scripted, CI/CD usage.
- Injection scanner catches the most common tool-output injection patterns.
- Matches: codex (exec_policy), gemini-cli (4 approval modes), opencode (rule-based).
- Design-chain traceability: SAF-01 → SAF-03 → `sq_saf01.puml` → `PermissionGate`.

---

### GAP-08: CLI and Renderer (C1) — High

**Challenge:**
The discarded PoC has a minimal REPL with plain print output. The reference standard is
rich terminal rendering (markdown, syntax highlighting, progress indicators, diff views).
Without rich output, the agent feels like a toy compared to aider or opencode.

**Action:**
1. Create `nasim/cli/renderer.py`: `Renderer` using `rich.Console` with:
   - `TextChunk` → `rich.Markdown` live streaming
   - `ToolStart` → `rich.Status` spinner with tool name
   - `ToolResultEvent` → collapsible panel (success = dim; failure = red)
   - `ApprovalRequest` → `rich.Prompt.ask` with formatted tool name and args
   - `Error` → `rich.Panel` with red border
   - `Done` → token count + cost estimate in dim footer
2. Create `nasim/cli/repl.py`: `REPLSession` main loop using `click` for arg parsing.
   Use `prompt_toolkit` or `readline` for input history and multi-line editing.
3. Add slash commands via `nasim/cli/commands.py`: `/help`, `/quit`, `/model <name>`,
   `/sessions`, `/clear`, `/compact` (manual compaction trigger), `/safe <mode>`.
4. Add `--one-shot "task"` flag for single-turn scripted use.

**Result:**
- Professional terminal experience on par with aider's Rich output.
- Slash commands match claude-code and gemini-cli conventions.
- Renderer is fully decoupled from agent core (events only).

---

### GAP-09: Structured Logging and Observability (C10) — High

**Challenge:**
The discarded PoC has no logging. Debugging a failed session requires reading raw stdout.
Production use and self-improvement both depend on structured telemetry.

**Action:**
1. Configure stdlib logging in `nasim/__init__.py` using `dictConfig`:
   - `StructuredLogger` as a JSON formatter for production mode.
   - Human-readable format for development mode (controlled by `LOG_LEVEL`).
2. Add per-module loggers using `logging.getLogger(__name__)` in every module.
3. Add `request_id` via `contextvars` — inject at agent turn start, include in every
   log line for that turn.
4. Log every LLM call at DEBUG level: model, token counts, finish reason.
5. Log every tool call at INFO level: tool name, args (truncated), success, elapsed ms.
6. Create `nasim/agent/wire_log.py`: `WireLog` appends raw request/response JSON to
   `~/.nasim/sessions/<id>/wire.jsonl` — exact wire-level transcript for debugging.
7. Create `nasim/agent/metrics.py`: `MetricsCollector` tracking tokens used, tool calls,
   errors, elapsed time per session. Summary printed at Done event.

**Result:**
- Every session is fully reproducible from the wire log.
- Token/cost summary per session builds user trust.
- Structured logging with request_id enables post-hoc debugging.
- Matches: goose (OpenTelemetry), codex (wire log), aider (logging to file).

---

### GAP-10: Repo Map / Symbol Awareness (C3) — High

**Challenge:**
Without a repo map, the agent must be told exactly which files to read. For any codebase
larger than ~10 files, the user becomes the file system. aider's repo-map is the single
most operationally valuable feature in the corpus for coding tasks.

**Action:**
1. Create `nasim/tools/repo_map.py`: `RepoMapTool(Tool)`:
   - Uses `subprocess` to call tree-sitter CLI or `ctags` to extract symbols.
   - Falls back to Python regex-based extraction for Python files if tree-sitter unavailable.
   - Produces a compressed symbol graph: `path → [class, function, method]` outline.
   - Ranks symbols by estimated relevance using PageRank on import graph (optional Phase 2).
2. Include repo map in system prompt when a project directory is detected.
3. `RepoMapTool.safe = True` (read-only).
4. Token budget for repo map: configurable, default 4000 tokens.

**Result:**
- Agent can locate any symbol in any codebase without being told the file path.
- Eliminates "I don't know where that function is" failures.
- Matches: aider (867 LOC tree-sitter repo-map), plandex (tree-sitter project maps),
  opencode (semantic search via LSP).
- Design-chain traceability: RIM-01 → RIM-06 → `RepoIntelligenceManager`.

---

### GAP-11: Web Tools (C1) — High

**Challenge:**
No web access means the agent cannot look up documentation, error messages, package APIs,
or any external information. Web fetch alone covers 80% of the "I don't know the API" problem.

**Action:**
1. Create `nasim/tools/web.py`:
   - `WebFetchTool(Tool)`: httpx GET, html2text conversion, token-limited output.
     `safe = True` (read-only). Args: `url: str`, `max_tokens: int = 4000`.
   - `WebSearchTool(Tool)`: configurable backend (default: DuckDuckGo DDG API;
     optional: SerpAPI with `NASIM_SERPAPI_KEY`). Returns ranked results with title/url/snippet.
     `safe = True`. Args: `query: str`, `num_results: int = 5`.
2. Add `httpx` and `html2text` to `pyproject.toml`.
3. Respect robots.txt for `WebFetchTool` (optional, configurable).

**Result:**
- Agent can look up any URL or search for documentation during a task.
- Matches: gemini-cli (Google Search grounding), opencode (web fetch + search), codex,
  cline, kimi-cli. Missing from: aider (notable gap), SWE-agent (intentionally excluded).

---

### GAP-12: Git Integration (C1) — Medium

**Challenge:**
Git context (current branch, staged files, recent commits) is highly relevant for coding
tasks. Auto-commit after each edit is aider's killer feature — every change is recoverable.
Without git awareness, the agent has no safety net for file mutations.

**Action:**
1. Create `nasim/tools/git.py`: `GitTool(Tool)` with sub-commands:
   - `status` → `git status --porcelain`
   - `diff` → `git diff` (staged or unstaged, configurable)
   - `log` → `git log --oneline -N`
   - `commit` → `git add <files> && git commit -m <message>`
   - `branch` → `git branch --show-current`
2. Auto-commit mode (off by default, enable with `--auto-commit`): commit after each
   successful file write/edit. Commit message generated by LLM from diff context.
3. Inject git status into system prompt on startup if inside a git repo.

**Result:**
- Every change is committed and recoverable.
- Agent can reason about branch state, staged changes, and recent history.
- Matches: aider (auto-commit is default), codex (git integration), claude-code.

---

### GAP-13: Plan Mode (C6) — Medium

**Challenge:**
Without plan mode, the agent starts executing immediately on complex tasks. For multi-file
refactorings, users want to review the proposed approach before any files are touched.
Plan mode is present in gemini-cli, opencode, and plandex — all three leading agents.

**Action:**
1. Create `nasim/agent/plan.py`: `PlanSession` dataclass with ordered list of steps.
   Each step: description, target file(s), estimated impact.
2. Add `PLAN` approval mode to `PermissionGate`: in plan mode, file writes and shell
   commands are intercepted and queued as plan steps rather than executed.
3. Add `/plan` slash command: switches to plan mode, accumulates steps, presents plan
   to user for approval before execution begins.
4. Plan tool: `PlanTool(Tool)` (safe=True) for the LLM to explicitly add steps to the
   current plan. Args: `description: str`, `files: list[str]`.

**Result:**
- Users can review the complete proposed change set before any files are modified.
- Matches: opencode (plan agent mode, edits disabled), plandex (full plan branching),
  gemini-cli (PLAN approval mode).
- Design-chain traceability: AGT-07 → AGT-08 → `PlanSession`.

---

### GAP-14: Subagent Spawning (C7) — Medium

**Challenge:**
Complex tasks (audit, test, refactor, document) benefit from parallel specialized
sub-instances. The design specifies `SubagentCoordinator` with nesting limit 5.
The implementation must enforce the nesting limit to prevent runaway spawning.

**Action:**
1. Create `nasim/agent/subagent.py`: `SubagentCoordinator` with `spawn(task, persona,
   max_depth)` method. Enforces nesting limit (raise if depth >= 5).
2. Create `nasim/tools/base.py`: `SubagentTool(Tool)` (safe=False) — LLM calls this
   to dispatch a specialized sub-task. Args: `task: str`, `persona: str`, `tools: list[str]`.
3. Personas map to system prompt overrides (read-only Researcher, file-write-only Coder,
   shell-only Executor, etc.).
4. Result collection: `SubagentCoordinator.collect(subagent_id) → str` — blocks until
   subagent completes.

**Result:**
- Complex tasks delegated to specialized sub-instances with constrained capabilities.
- Nesting limit prevents infinite recursion.
- Matches: codex (subagent dispatch), gemini-cli (A2A subagents), opencode (background
  subagents), kimi-cli (LaborMarket), goose (summon tool).

---

### GAP-15: MCP Integration (C11) — Medium

**Challenge:**
MCP (Model Context Protocol) is the de facto standard for extending agents with custom tools.
Without MCP client support, nasim cannot consume any of the 1000+ existing MCP servers
(filesystem, databases, GitHub, Slack, Linear, etc.).

**Action:**
1. Create `nasim/tools/mcp.py`:
   - `MCPClientRuntime`: connects to MCP server via stdio or SSE.
   - `MCPDiscovery`: reads `.nasim/mcp.yaml` to find configured MCP servers.
   - `MCPToolAdapter(Tool)`: wraps each MCP tool as a nasim `Tool` instance.
   - Dynamic registration: discovered MCP tools added to `ToolRegistry` at startup.
2. Create `nasim/server/mcp_server.py`: expose nasim tools as an MCP server for external
   clients (reverse direction — nasim AS an MCP server).
3. Add `mcp` SDK to `pyproject.toml`.
4. Config schema: `mcp.servers: list[MCPServerConfig]` with name, transport, command/url.

**Result:**
- Any MCP server's tools available to nasim without code changes.
- nasim itself becomes an MCP server — composable into other agent systems.
- Matches: goose (extensions are MCP servers), codex, gemini-cli, opencode, cline.
- Design-chain traceability: MCP-01 → MCP-04 → `sq_mcp01.puml` → `MCPClientRuntime`.

---

### GAP-16: HTTP API Server (C1) — Low (Phase 3)

**Challenge:**
The HTTP API is designed (OAS 3.1.0, 23 endpoints, 8 resources, ROD decisions) but not
implemented. The HTTP API enables web clients, desktop apps, Slack bots, and CI/CD
pipelines to consume nasim without the CLI.

**Action:**
1. Create `nasim/server/app.py`: FastAPI ASGI application with lifespan.
2. Create `nasim/server/router.py`: `ServerRouter` mounting all route groups.
3. Implement session CRUD: `POST /v1/sessions`, `GET /v1/sessions/{id}`, etc.
4. Implement SSE streaming: `POST /v1/sessions/{id}:send` returns event stream.
   Map `AgentEvent` subtypes to SSE event types.
5. Add `uvicorn` and `fastapi` to `pyproject.toml`.

**Result:**
- Web clients, desktop apps, and external integrations consume nasim via HTTP.
- Same agent core; same event system; different subscriber.
- Matches: opencode (Hono server), gemini-cli (A2A server).
- Design-chain traceability: SRV-01 → SRV-11 → `sq_srv01.puml` → `ServerApp`.

---

### GAP-17: Memory Persistence (C5) — Low (Phase 2)

**Challenge:**
Project-specific facts (coding conventions, architecture decisions, key entities) should
persist across sessions. Without memory, the agent rediscovers the same information every
session.

**Action:**
1. Create `nasim/tools/memory.py`: `MemoryTool(Tool)` with `persist(content, scope)`
   and `recall(query, scope)` sub-commands.
2. Create `nasim/session/memory_store.py`: SQLite with FTS5 for keyword search.
   Scope isolation: global (`~/.nasim/memory/`), project (`.nasim/memory/`), session.
3. Inject relevant memory into system prompt at session start (top-K recall by relevance).

**Result:**
- Project conventions remembered across sessions.
- Matches: gemini-cli (memory context manager), goose (moim), opencode (skills from markdown).
- Design-chain traceability: MEM-01 → MEM-04 → `MemoryStore`.

---

### GAP-18: IDE Integration (C8) — Gap (Not Designed)

**Challenge:**
nasim has no IDE integration designed. cline dominates VS Code with 10+ million installs.
Roo-Code has role-based modes specifically suited for different IDE workflows. Without IDE
integration, nasim is limited to the terminal-only user segment.

**Action:**
1. Design: Add VS Code extension to the C4 context diagram as a new container.
2. Design: VS Code extension communicates with nasim HTTP server.
3. Implementation: TypeScript VS Code extension connecting to `localhost:nasim-port`.
4. Minimal MVP: show agent output in a VS Code webview; read active file path for context.

**Result:**
- Captures the IDE-native user segment.
- Reduces the competitive gap with cline and Roo-Code.
- This is Phase 4+ work; do not defer implementation of C1–C7 for this.

---

### GAP-19: Benchmark Infrastructure (C12) — Gap (Not Designed)

**Challenge:**
nasim has no benchmark infrastructure. Without SWE-bench integration, capability claims
are unvalidated. The WAF Tech positioning ("research code agent") requires demonstrated
benchmark performance.

**Action:**
1. Create `evals/` directory with SWE-bench Lite integration script.
2. Use the official `swebench` package for issue loading and evaluation.
3. Instrument agent runs with cost tracking per issue (using litellm's built-in tracking).
4. Report: pass@1 rate, average cost per issue, average turn count.
5. Baseline target: 10% SWE-bench Lite pass@1 (above SWE-agent's 2022 baseline,
   below current SOTA at ~70% with frontier models).

**Result:**
- Objective capability validation.
- Supports the "research code agent" positioning.
- Basis for improvement iterations: fix benchmark failures systematically.
- Matches: SWE-agent (designed for this), plandex (real-world multi-file focus),
  aider (tracks its own performance on coding benchmarks).

---

## Priority Roadmap

Priorities are determined by: (1) blocking other capabilities, (2) operational impact,
(3) difficulty, (4) design-chain traceability readiness.

---

### P0 — Prerequisite (Must complete before anything else)

**Nothing else is possible without these. Execute in strict order.**

| # | Action | Rationale | Design Ref |
|---|--------|-----------|-----------|
| P0.1 | Create Python package skeleton: `nasim/` with all packages from `entities.md`. `pyproject.toml` with entry point. `__main__.py` composition root. | Every other P0 item depends on this. | RDM/01-project-skeleton.md |
| P0.2 | Implement `Config` dataclass + `ConfigLoader` (4-layer) | All components need config; provider needs `model` setting | CFG-01–03 |
| P0.3 | Implement `Provider` Protocol + `LiteLLMProxy` + `ProviderFactory` | AgentOrchestrator depends on Provider | PRV-01–04 |
| P0.4 | Implement `Tool` ABC + `ToolResult` + `ToolRegistry` | All tools depend on this base | TL-01 ref |
| P0.5 | Implement `AgentEvent` hierarchy | Renderer depends on events; agent depends on emitting them | AGT-01 ref |
| P0.6 | Implement `AgentOrchestrator.run()` as event generator | The agent loop itself | AGT-01–02 |
| P0.7 | Implement `ConversationHistory` + `ContextCompactor` | Without this, sessions crash on long tasks | CTX-01–06 |
| P0.8 | Implement CLI: `ArgParser` + `REPLSession` + `Renderer` (rich) | Entry point for human testing | CLI-01–04 |

**Target:** Working `nasim "task"` command with Ollama. 2–3 weeks.

---

### P1 — Core Capability (Required for production readiness)

**Complete within 4 weeks of P0.**

| # | Action | Rationale | Design Ref |
|---|--------|-----------|-----------|
| P1.1 | Implement `SearchTools` (GrepTool, GlobTool, FindFileTool) | Biggest single functional gap | TL-06–08 |
| P1.2 | Implement `WebFetchTool` + `WebSearchTool` | Second biggest functional gap | TL-09–10 |
| P1.3 | Implement `GitTool` | Safety net for file mutations | TL-11 |
| P1.4 | Implement `SessionStore` + `--continue` flag | Resume sessions | SSN-01–04 |
| P1.5 | Implement `PermissionGate` (ask/auto/off) | Safety prerequisite for real use | SAF-01–03 |
| P1.6 | Implement `RepoMapTool` (tree-sitter or ctags) | Enables real-codebase tasks | RIM-01 |
| P1.7 | Implement `MCPToolAdapter` + `MCPClientRuntime` | Extension ecosystem access | MCP-01–03 |
| P1.8 | Implement `StructuredLogger` + `WireLog` + `MetricsCollector` | Observability prerequisite | OBS-01–03 |
| P1.9 | Implement `InjectionScanner` (pattern-based) | Safety prerequisite | SAF-02 ref |
| P1.10 | Write pytest suite: provider, tools, agent, CLI (> 80% coverage) | Quality gate | RDM/08 |

**Target:** nasim usable for real tasks by one external beta user. 4 weeks post-P0.

---

### P2 — Competitive Parity

**Complete within 8 weeks of P0.**

| # | Action | Rationale | Design Ref |
|---|--------|-----------|-----------|
| P2.1 | Implement `SessionVersioning` (snapshot/undo) | Matches opencode differentiator | SSN-05–06 |
| P2.2 | Implement `PlanSession` + `/plan` slash command | Matches gemini-cli, opencode, plandex | AGT-07–08 |
| P2.3 | Implement `MemoryStore` (SQLite FTS5) + `MemoryTool` | Cross-session knowledge | MEM-01–04 |
| P2.4 | Implement `SubagentCoordinator` + `SubagentTool` | Multi-agent capability | AGT-09–10 |
| P2.5 | Implement `HookManager` (PreToolUse, PostToolUse, PreModel, PostModel) | Extensibility | HK-01–04 |
| P2.6 | Implement `PluginLoader` + plugin manifest | Plugin ecosystem | PLG-01–04 |
| P2.7 | Implement `SandboxExecutor` (bubblewrap or subprocess with limits) | OS-level isolation | SBX-01–04 |
| P2.8 | Implement `EditStrategyManager` + `SearchReplaceCoder` (aider-style) | Multi-strategy editing | EDT-01–04 |
| P2.9 | Implement `PersonaManager` (system prompt + tool restriction per persona) | Roo-Code parity | AGT-11–13 |
| P2.10 | Implement evals/ SWE-bench Lite integration | Objective capability measurement | — |

**Target:** nasim publishable as a serious OSS agent. 8 weeks post-P0.

---

### P3 — Differentiation

**After P2; nasim becomes a frontier-setter in selected dimensions.**

| # | Action | Rationale | Design Ref |
|---|--------|-----------|-----------|
| P3.1 | Implement HTTP API server (FastAPI + SSE) | Multi-interface; matches opencode | SRV-01–11 |
| P3.2 | Implement `MCPServerRuntime` (nasim AS MCP server) | nasim becomes composable | MCP-04 |
| P3.3 | Implement `ContextGraph` + `PipelineOrchestrator` | Frontier context management | CTX-01–06 |
| P3.4 | Implement `ModelRouter` + `FallbackChain` | Per-task model selection | RTG-01–06 |
| P3.5 | Implement `EvaluationEngine` + `RetryCoordinator` | SWE-agent parity | EVL-01–04 |
| P3.6 | Implement `WireLog` + `ASTIndexAdapter` + `SemanticSearchService` | Deep repo intelligence | RIM-01–06 |
| P3.7 | VS Code extension MVP | IDE integration gap | — |
| P3.8 | Implement `EgressInspector` + ML injection scanner | goose-level security | SAF-02 |
| P3.9 | OpenTelemetry integration (OTelExporter) | goose-level observability | OBS-04 |
| P3.10 | Implement `DiffSandboxManager` + `DiffComputer` + `DiffPresenter` | plandex parity | SBX-05–09 |

---

### GAP-20: Edit Strategy Polymorphism (C1) — Medium

**Challenge:**
aider's 14 edit strategies are the most impactful engineering decision in the reference corpus.
Different tasks require different edit formats: small patches need search-replace; whole-file
rewrite is simpler for small files; architect mode decouples planning from execution. nasim's
design specifies `EditStrategyManager` in the EDT group (EDT-01 through EDT-04) but the
strategy object hierarchy is unimplemented.

**Action:**
1. Create `nasim/tools/edit.py` with strategy classes:
   - `WholeFileCoder`: send full file content; receive full file back. Best for < 100 LOC files.
   - `SearchReplaceCoder`: find `<<<SEARCH>>>` / `<<<REPLACE>>>` blocks in LLM output.
     Apply as atomic substitutions. Best for targeted edits in large files.
   - `UnifiedDiffCoder`: parse unified diff output from LLM; apply with `patch`. Requires
     correct line numbers — fragile but compact.
   - `EditFileCoder` (default): structured tool call with `path`, `old_str`, `new_str` args.
     Most reliable with function-calling models.
2. Create `nasim/tools/edit_strategy.py`: `EditStrategyManager` selects strategy based on
   file size, model capability, and config. Small file (< 80 LOC) → WholeFileCoder;
   function-calling model → EditFileCoder; fallback → SearchReplaceCoder.
3. All strategies return `ToolResult` with success, applied changes list, and error message.
4. `EditFileTool` delegates to `EditStrategyManager`; strategy is transparent to the agent.

**Result:**
- Correct edits on 95%+ of LLM-generated changes (vs ~60–70% with a single strategy).
- Strategy selection adapts to model capability automatically.
- Matches: aider (14 strategies, the primary differentiator), opencode (diff strategy per
  provider), SWE-agent (patch-based editing).
- Design-chain traceability: EDT-01 → EDT-04 → `EditStrategyManager`.

---

### GAP-21: Hook System (C11) — Medium

**Challenge:**
claude-code's hook system is the most copied feature in the corpus. Hooks allow users and
plugins to intercept the agent's execution at 9 points without modifying core code. nasim
designs `HookManager` in the HK group (HK-01 through HK-04) but the implementation does
not exist.

**Action:**
1. Create `nasim/hooks/base.py`:
   ```python
   from dataclasses import dataclass
   from enum import Enum
   from typing import Callable, Awaitable

   class HookPoint(Enum):
       PRE_TOOL_USE = "pre_tool_use"
       POST_TOOL_USE = "post_tool_use"
       PRE_MODEL = "pre_model"
       POST_MODEL = "post_model"

   @dataclass
   class HookContext:
       tool_name: str | None = None
       tool_args: dict | None = None
       tool_result: "ToolResult | None" = None
       messages: list[dict] | None = None
       model_response: str | None = None

   @dataclass
   class HookResult:
       proceed: bool = True  # False = block the action
       modified_context: HookContext | None = None
       error: str | None = None
   ```
2. Create `nasim/hooks/manager.py`: `HookManager` with `register(point, handler)` and
   `run(point, context) → HookResult`. Execute all registered handlers in order;
   first `proceed=False` blocks the action.
3. Hook types:
   - `CommandHook`: runs a shell command; output is logged; non-zero exit blocks.
   - `PromptHook`: sends context to LLM for validation; LLM response "BLOCK" blocks.
4. Wire `HookManager` into `AgentOrchestrator`:
   - Before tool execute: `run(PRE_TOOL_USE, context)` — if blocked, skip tool.
   - After tool execute: `run(POST_TOOL_USE, context)`.
   - Before LLM call: `run(PRE_MODEL, context)`.
   - After LLM response: `run(POST_MODEL, context)`.
5. Load hooks from `~/.nasim/hooks/` (global) and `.nasim/hooks/` (project).

**Result:**
- Custom validation, logging, and transformation without core code changes.
- Matches: claude-code (9 hook points), gemini-cli (4 hook types), goose (extension hooks).
- Plugin authors can add hooks; users can configure per-project bash hooks.
- Design-chain traceability: HK-01 → HK-04 → `HookManager` → `sq_hk01.puml`.

---

### GAP-22: Persona and Role System (C6) — Medium

**Challenge:**
plandex's 9-role architecture and Roo-Code's mode-based roles demonstrate the value of
purpose-specific agent configurations. A "Research" persona should be read-only; a
"Coder" persona should not run shell commands; a "Reviewer" persona should analyze
without modifying. Without personas, a single misconfigured system prompt handles all tasks.

**Action:**
1. Create `nasim/agent/persona.py`:
   ```python
   from dataclasses import dataclass, field

   @dataclass
   class Persona:
       name: str
       system_prompt: str
       allowed_tools: list[str]     # tool names; empty = all allowed
       blocked_tools: list[str]     # tool names always blocked
       model_override: str | None   # use specific model for this persona
       temperature: float = 0.7
   ```
2. Create `nasim/agent/persona_manager.py`: `PersonaManager` with `load_persona(name)`,
   `apply(persona, config, tool_registry)`. Updates `ToolRegistry` filter and model
   selection for the session.
3. Built-in personas:
   - `coder`: all tools, `ShellTool.safe` enforcement strict
   - `researcher`: read-only tools (ReadFileTool, GrepTool, GlobTool, WebFetchTool)
   - `architect`: read-only tools + PlanTool, no WriteFileTool
   - `reviewer`: read-only tools + diff output only
4. Load custom personas from `~/.nasim/personas/*.yaml` and `.nasim/personas/*.yaml`.
5. CLI flag: `--persona <name>` or `/persona <name>` slash command.

**Result:**
- Task-appropriate capability scoping reduces accidental tool misuse.
- Custom personas for specialized workflows (database, infrastructure, testing).
- Matches: plandex (9 roles), Roo-Code (Code/Architect/Ask/Debug modes), openinterpreter
  (8 personas), claude-code (read-only vs read-write implicit modes).
- Design-chain traceability: AGT-11 → AGT-13 → `PersonaManager`.

---

### GAP-23: Wire Log and Debug Transparency (C10) — Medium

**Challenge:**
When an agent takes wrong action, the developer needs to see the exact prompt sent to the
LLM and the exact response received. Without a wire log, debugging is guesswork. codex's
wire log transcript is the most complete debugging artifact in the corpus.

**Action:**
1. Create `nasim/agent/wire_log.py`: `WireLog` that appends to
   `~/.nasim/sessions/<id>/wire.jsonl`.
   Each entry is a JSON object with `timestamp`, `direction` (request|response),
   `model`, `messages` (full array), `tools` (full schema), `response` (full object),
   `token_counts`.
2. Wire into `LiteLLMProxy`: log before and after every `litellm.completion()` call.
3. Log level `DEBUG`: disable in production by default; enable with `--debug` flag or
   `NASIM_LOG_LEVEL=DEBUG`.
4. Add CLI command `nasim debug --session <id>` that pretty-prints the wire log with
   rich formatting (messages as panels, tool calls highlighted, token counts in dim footer).
5. Wire log entries are never truncated (unlike stdout output which truncates tool results).

**Result:**
- Every LLM interaction is fully reconstructable from the wire log.
- Debugging provider issues (wrong model, bad tool schema, context too long) requires
  minutes, not hours.
- Matches: codex (wire log), aider (`--verbose` logs raw API calls), claude-code (hook
  PostToolUse logs).

---

### GAP-24: Cost Tracking and Budget Enforcement (C10) — Low

**Challenge:**
Running an agent without cost visibility is irresponsible for any production use.
A confused agent can run 100 tool calls and 50 LLM calls before the user notices
something is wrong. litellm provides per-call token counts; they must be aggregated.

**Action:**
1. Create `nasim/agent/metrics.py`: `MetricsCollector` with:
   - Per-turn: input tokens, output tokens, cost estimate (litellm `cost_per_token`).
   - Per-session: accumulated totals.
   - Tool call counts per tool name.
   - Session elapsed time.
2. Emit `MetricsTick` event (new `AgentEvent` subtype) after each LLM call with current
   totals. Renderer shows in dim status bar.
3. Emit `Done` event with full session summary: total tokens, estimated cost, tool calls.
4. Config: `max_cost_per_session: float | None` — if set, raise when budget exceeded.
5. Config: `max_iterations: int = 20` — raise after N tool calls in one session.

**Result:**
- Users see cost in real time and can abort expensive sessions.
- Budget enforcement prevents runaway loops from incurring large API costs.
- Matches: codex (cost tracking per run), SWE-agent (cost per issue with limits),
  gemini-cli (cost estimation in telemetry).

---

### GAP-25: Concurrent Tool Execution (C9) — Low

**Challenge:**
When the LLM requests multiple tool calls in a single response (parallel function calling),
nasim must execute them concurrently. Sequential execution of 5 independent file reads
wastes 4x the time. Python's `asyncio` supports this natively.

**Action:**
1. Migrate `AgentOrchestrator` to `async def run() → AsyncIterator[AgentEvent]`.
2. Migrate `LiteLLMProxy.chat_stream()` to `async def`.
3. Migrate all `Tool.execute()` to `async def execute()` or wrap in
   `asyncio.get_event_loop().run_in_executor()` for blocking tools.
4. When LLM returns N tool calls in one response: `asyncio.gather(*[tool.execute(args)
   for name, args in tool_calls])` — execute all concurrently.
5. Collect results and yield `ToolResultEvent` for each as it completes.
6. Use `httpx.AsyncClient` in `WebFetchTool` and `WebSearchTool` (already planned).

**Result:**
- N independent tool calls execute in parallel; wall time ~ max(tool times) not sum.
- For agents that fetch multiple URLs or read multiple files per turn: 3–10x speedup.
- Matches: opencode (Effect-TS structured concurrency), gemini-cli (async Node.js),
  goose (Rust tokio async runtime), codex (Rust async).

---

## Architectural Comparison: nasim vs Reference Corpus

### Paradigm Distribution

The 28-agent reference corpus uses 5 architectural paradigms:

| Paradigm | Agents | nasim position |
|----------|--------|---------------|
| Event loop + stdout print | aider, older Python agents | Explicitly rejected (AP-28) |
| Event emitter / generator | nasim (design), opencode (Effect-TS), codex | Target paradigm |
| Function calling orchestrator | gemini-cli, cline, claude-code | Subset of event emitter |
| Multi-role orchestrator | plandex, OpenHands | Influences SubagentCoordinator design |
| Declarative agent (YAML-driven) | SWE-agent (Bundle), mini-swe-agent | Influences PersonaManager design |

nasim's design correctly identifies the event generator paradigm as the most future-proof.
The same architecture serves CLI rendering (stream to stdout), HTTP SSE (stream to client),
MCP (stream to MCP client), and testing (collect events in list).

### Language and Runtime Distribution

| Language | Agents | nasim assessment |
|----------|--------|-----------------|
| Python | nasim (target), aider, SWE-agent, kimi-cli, openinterpreter | Correct choice for ML/AI ecosystem |
| TypeScript/Bun | opencode, claude-code, gemini-cli, cline, Roo-Code | JS ecosystem; Bun runtime is fast |
| Rust | codex, goose, amazon-q, openinterpreter (core) | Maximum performance; complex build |
| Go | plandex, crush | Fast, simple; good concurrency |

Python is correct for nasim. The Rust advantage (codex, goose) is primarily in OS-level
sandbox implementation and raw throughput. Python with async httpx and litellm achieves
acceptable performance for interactive sessions. The design already specifies `httpx`
for async I/O, which closes the largest performance gap between Python and Rust.

### Provider Abstraction Patterns

All mature agents converge on the same pattern:

```
Provider (Protocol/trait/interface)
    ↑
ProviderFactory (instantiates by config string)
    ↑
litellm / native client
    ↑
Model Provider API
```

nasim's design matches this exactly. The specific implementation choices:
- litellm as the universal proxy (same as aider, plandex server, SWE-agent).
- `Provider` as a Protocol (same structural typing as codex's Rust trait, opencode's
  Effect-TS interface, goose's Rust trait).
- `ProviderFactory` as the single instantiation point (same as cline's Gateway pattern,
  opencode's ProviderFactory).

No reference agent has a more complete provider abstraction design. The implementation
is straightforward given the design.

### Safety Architecture Comparison

| Agent | Safety approach | Gaps |
|-------|----------------|------|
| codex | OS sandbox (landlock/seccomp/seatbelt), exec_policy.rs prefix rules | No ML injection detection |
| goose | ML injection scanner + SecurityInspector + EgressInspector + AdversaryInspector | No OS sandbox for shell |
| gemini-cli | 4 modes + policy engine TOML rules + folder trust discovery | No OS sandbox |
| opencode | Rule-based permissions, always-remember per project | No injection detection |
| cline | MCP tool approval, diff preview before apply | No injection detection, no OS sandbox |
| nasim (design) | SafetyPipeline + PermissionGate + InjectionScanner + EgressInspector + SandboxExecutor | Not implemented |

nasim's designed safety pipeline is more comprehensive than any single reference agent.
The `SafetyPipeline` combining `PermissionGate`, `InjectionScanner`, and `EgressInspector`
combines goose's multi-layer approach with codex's OS sandbox. This is the best-designed
safety system in the corpus — once built.

### Session Persistence Patterns

| Agent | Persistence | Resume | Fork/undo |
|-------|------------|--------|----------|
| opencode | SQLite event-sourced WAL | Session resume by ID | Snapshot/undo |
| codex | SQLite ThreadStore | `--continue` | Archive only |
| goose | Session naming + search | Resume by name | No |
| kimi-cli | Fork support | `--fork` | Session fork |
| aider | Git history (implicit) | Re-run with same dir | Via git revert |
| nasim (design) | JSON Lines + SessionVersioning | `--continue`, `--session` | SessionFork |

nasim's design targets a session store richer than codex (no SQLite required — JSON Lines
is simpler and more debuggable) and adds `SessionFork` as a first-class operation.
The tradeoff: JSON Lines lacks SQLite's full-text search and atomic concurrent writes.
For a single-user CLI agent, JSON Lines is the correct simplicity tradeoff.

---

## Anti-Pattern Violations Found in Reference Corpus

These are mistakes observed in production reference agents. nasim's design avoids all
of them. Document them here as negative examples — do not replicate during implementation.

### APR-01 — Global tool registry (aider, older Python agents)

aider's tools are module-level functions registered in a global dict at import time.
This prevents per-session tool configuration and makes testing require import-level
mocking. **nasim fix:** `ToolRegistry` is an instance class injected via constructor.

### APR-02 — Hardcoded provider URLs (kimi-cli v0.1, aider without litellm)

Hardcoded `https://api.moonshot.cn/v1` base URL in source code. Cannot be overridden
without patching. **nasim fix:** All provider config via layered `Config` dataclass.

### APR-03 — Conversation history without compaction (multiple research agents)

Append-only `self.messages` list with no token budget enforcement. Sessions fail silently
or crash on context overflow with no recovery. **nasim fix:** `ConversationHistory` with
`check_budget()` + `ContextCompactor` triggered at 80%.

### APR-04 — LLM I/O in tool execute() (early openinterpreter)

Tool `execute()` calls the LLM directly for sub-tasks instead of returning a structured
result. Creates unbounded recursive calls and makes the tool untestable.
**nasim fix:** `Tool.execute()` is pure computation; no LLM calls inside tools.

### APR-05 — No error boundary in agent loop (simple script agents)

When a tool raises an exception, the agent loop crashes the entire session. No structured
error path. **nasim fix:** `Error` event emitted; agent loop continues with error context
added to conversation history; only `max_iterations` or user abort stops the session.

### APR-06 — Provider response schema assumed (fragile deserialization)

Multiple agents assume `response.choices[0].message.content` without checking for
tool_calls, checking for None, or handling provider-specific response shapes.
**nasim fix:** `LiteLLMProxy` normalizes all responses to `LLMResponse`; downstream
code only sees the normalized type.

### APR-07 — Print() in agent core (violates AP-28)

aider, kimi-cli v0.1, SWE-agent use `print()` in core agent logic. The symptom is
that adding a second UI (web interface) requires a complete rewrite.
**nasim fix:** `AgentOrchestrator.run()` yields `AgentEvent`; zero `print()`.

### APR-08 — Synchronous HTTP in agent loop (blocks event loop)

Several agents use `requests` (blocking HTTP) inside tools that run in an async agent loop.
This serializes all tool execution. **nasim fix:** `httpx.AsyncClient` for all HTTP;
tools that use blocking I/O wrapped in `run_in_executor`.

---

## Implementation File Map

For each P0/P1 deliverable, the exact file path and minimal interface:

```
nasim/
    __init__.py
    __main__.py                         # click CLI + composition root
    provider/
        __init__.py
        base.py                         # Provider Protocol, LLMResponse, ToolCall
        litellm_proxy.py                # LiteLLMProxy(Provider)
        factory.py                      # ProviderFactory.from_config()
        models.py                       # LLMResponse, ToolCall dataclasses
    agent/
        __init__.py
        orchestrator.py                 # AgentOrchestrator (central service)
        events.py                       # AgentEvent hierarchy
        history.py                      # ConversationHistory + token counting
        compactor.py                    # ContextCompactor
        permission.py                   # PermissionGate (SafetyMode enum)
        safety.py                       # InjectionScanner, EgressInspector
        persona.py                      # Persona dataclass
        persona_manager.py              # PersonaManager
        plan.py                         # PlanSession
        subagent.py                     # SubagentCoordinator
        wire_log.py                     # WireLog
        metrics.py                      # MetricsCollector
    tools/
        __init__.py
        base.py                         # Tool ABC, ToolResult
        registry.py                     # ToolRegistry (instance-based)
        file.py                         # ReadFileTool, WriteFileTool, EditFileTool
        search.py                       # GrepTool, GlobTool, FindFileTool
        shell.py                        # ShellTool
        web.py                          # WebFetchTool, WebSearchTool
        git.py                          # GitTool
        directory.py                    # DirTool
        repo_map.py                     # RepoMapTool
        memory.py                       # MemoryTool
        mcp.py                          # MCPToolAdapter, MCPClientRuntime
        edit.py                         # Edit strategy classes
        edit_strategy.py                # EditStrategyManager
    config/
        __init__.py
        schema.py                       # Config, ProviderConfig (pydantic-settings)
        loader.py                       # ConfigLoader (4-layer merge)
    session/
        __init__.py
        model.py                        # Session dataclass
        store.py                        # SessionStore (JSON Lines)
        memory_store.py                 # MemoryStore (SQLite FTS5)
    cli/
        __init__.py
        args.py                         # ArgParser (click)
        repl.py                         # REPLSession
        renderer.py                     # Renderer (rich)
        commands.py                     # SlashCommandHandler
    hooks/
        __init__.py
        base.py                         # HookPoint, HookContext, HookResult
        manager.py                      # HookManager
    plugins/
        __init__.py
        manifest.py                     # PluginManifest (pydantic)
        loader.py                       # PluginLoader
    server/
        __init__.py
        app.py                          # FastAPI ASGI app (Phase 3)
        router.py                       # ServerRouter (Phase 3)
        sse.py                          # SSEHandler (Phase 3)

tests/
    provider/
        test_litellm_proxy.py
        test_provider_factory.py
    agent/
        test_orchestrator.py
        test_events.py
        test_history.py
        test_compactor.py
        test_permission.py
    tools/
        test_file_tools.py
        test_search_tools.py
        test_shell_tool.py
        test_web_tools.py
        test_registry.py
    config/
        test_config_loader.py
    session/
        test_session_store.py
    cli/
        test_renderer.py
        test_repl.py
```

---

## Conclusion

nasim enters 2026 in the best and worst position simultaneously. The best: no other
agent in the 28-agent reference corpus has a comparably rigorous pre-implementation design.
The C4 diagrams, 148 sequence diagrams, ODCS contracts, and OAS spec are the artifact of
a disciplined engineering process that most production agents never did. The design is
architecturally sound, avoids every anti-pattern documented in the corpus, and already
incorporates the lessons from all 28 reference agents.

The worst: zero implementation. Against the 2026 frontier scoring rubric, nasim scores
6/120 operational points. Every reference agent with working code scores higher — including
the research-grade SWE-agent with its 49-point score.

The roadmap is clear and unambiguous:

1. **P0 (2–3 weeks):** Build the skeleton — provider, tools, events, agent loop, CLI.
   Result: a working agent that can use Ollama to read/write files and execute shell commands.

2. **P1 (4 weeks post-P0):** Add search tools, web tools, session persistence, safety gates,
   repo-map, and MCP. Result: an agent usable for real tasks in real codebases.

3. **P2 (8 weeks post-P0):** Add planning, memory, hooks, plugins, subagents, sandbox,
   edit strategies, and SWE-bench evals. Result: a publishable OSS agent competitive with
   the Tier 2 corpus.

4. **P3 (12+ weeks post-P0):** HTTP API, MCP server, context graph, model routing,
   retry-with-review, VS Code extension. Result: a frontier-setting agent that exceeds
   any single reference in combined capability depth.

The design chain is done. The implementation window is open. Do not add another design
document before writing the first line of production Python.

---

**Audit sign-off:** 2026-06-21 | Salim Namvar | nasim v0.1 → v0.2 design sprint complete
