# Reference Agents — Deep Dive Audit

**Date:** 2026-06-20
**Scope:** All 27 reference agents cloned in `prj/salim/nasim/code/`
**Purpose:** Architectural analysis of every reference agent to inform nasim's design improvements

---

## Executive Summary

27 reference agents analyzed across 10 dimensions. The corpus spans 5 languages
(Rust, TypeScript, Python, Go, mixed), 3 architectural paradigms (monolith, monorepo,
client-server), and maturity levels from proof-of-concept to production. Key finding:
**no single agent excels at everything** — the best design borrows patterns from multiple
agents. The most architecturally sophisticated are **codex** (Rust, 124-crate workspace),
**gemini-CLI** (TypeScript, graph-based context), **opencode** (Effect-TS, event-sourced),
**goose** (Rust, security-hardened), and **plandex** (Go, plan-centric multi-role).

---

## Agent Profiles

### Tier 1 — Production-Grade Agents (most instructive)

#### 1. aider
- **Language:** Python | **Repo:** `aider/` (~45 modules)
- **Architecture:** Single-package CLI. `Coder` base class with 14 edit-format subclasses.
- **LLM:** litellm adapter (100+ providers). `ModelSettings` dataclass per model.
- **Tools:** Not function-calling based. SEARCH/REPLACE block format via prompt engineering.
  Shell commands extracted from LLM output via regex.
- **Context:** `ChatSummary` (weak model) summarizes old messages. Chat history split into
  `cur_messages` / `done_messages`. Token counting via litellm.
- **Session:** Markdown-based chat history file. `--restore-chat-history`.
- **Safety:** Auto-commit git, `.aiderignore`, `read_only_fnames`, `--dry-run`,
  `io.confirm_ask()`, auto-lint after edits.
- **Config:** 4-layer: CLI > `.env` > `.aider.conf.yml` (CWD/git-root/home) > defaults.
  Auto `AIDER_` env prefix.
- **Differentiators:** Edit-format polymorphism (14 strategies), repo-map (tree-sitter),
  architect mode (two-model pipeline), Anthropic prompt caching.
- **Patterns:** Strategy, Factory Method, Template Method, Lazy Loading, Chain of Responsibility.

#### 2. claude-code
- **Language:** TypeScript/Bun (closed-source runtime) | **Repo:** plugins/examples/docs
- **Architecture:** Plugin ecosystem with 14 official plugins. Hooks system (9 events).
  Markdown-based agent definitions with YAML frontmatter.
- **LLM:** Anthropic primary, Bedrock, custom gateways. Model fallback chains.
- **Tools:** Bash, Read/Write/Edit, WebSearch/WebFetch, MCP tools. Tool naming: `mcp__plugin_<name>__<tool>`.
- **Context:** PreCompact hooks, skill auto-activation, context reminders. Session IDs
  with transcript paths.
- **Session:** Background/daemon sessions with tmux integration. 30-day cleanup.
- **Safety:** Tiered permissions (allow/ask/deny per tool). Sandbox for Bash (network
  domain allowlists). MDM enterprise settings. PreToolUse/PostToolUse hooks.
- **Config:** Hierarchical: managed > user > project > local. MDM deployment (Jamf, Intune).
- **Differentiators:** Plugin marketplace, prompt-based hooks (LLM-in-the-loop validation),
  enterprise MDM, background agent sessions, skills auto-activation.
- **Patterns:** Observer (hooks), Plugin architecture, Event-driven, Skills system.

#### 3. codex
- **Language:** Rust | **Repo:** `codex-rs/` (~124 crates)
- **Architecture:** Cargo workspace with strict crate boundaries. Core has no TUI imports.
  TypeScript SDK alongside.
- **LLM:** `ModelProvider` trait. OpenAI + Bedrock implementations. Factory pattern.
  Capabilities declared per provider.
- **Tools:** Rich framework: `ToolDefinition`, `ToolSpec`, `ToolExecutor`. MCP tools,
  dynamic tools, plugin installation tools, tool search/discovery.
- **Context:** `context_manager/` with auto-compaction (`compact.rs`). Remote compaction.
  `ContextFragment` system for injection. `response_history.rs` truncation.
- **Session:** `ThreadStore` trait with SQLite-backed `LocalThreadStore`. Thread lifecycle
  (create/resume/archive/delete). `LiveThread` for active sessions.
- **Safety:** Multi-layered: landlock/seccomp (Linux), bubblewrap, seatbelt (macOS),
  restricted token (Windows). `exec_policy.rs` with prefix/network rules. `SafetyCheck`
  enum for patch safety.
- **Config:** `ConfigLayerStack` with merge semantics (global → project → cloud → CLI).
  TOML-based. MCP, hooks, exec policy, TUI keybindings, skills.
- **Differentiators:** OS-level sandboxing (not just policy), 124-crate workspace,
  remote compaction, skills system, plugin architecture, app-server daemon.
- **Patterns:** Trait-object polymorphism, Layered config, Event-driven, Actor-like
  concurrency, Platform abstraction, Strict dependency boundaries.

#### 4. gemini-CLI
- **Language:** TypeScript/Node.js | **Repo:** npm workspaces, 33+ core subdirs
- **Architecture:** Monorepo: core engine + CLI + A2A server + SDK + VS Code companion.
  Graph-based context management.
- **LLM:** Google Gemini only (`@google/genai`). OAuth/API key/Vertex AI auth.
  Model routing with composite strategies (classifier, fallback, approval, override).
- **Tools:** 20+ built-in (shell, read/write/edit, glob, grep, ripgrep, web, memory,
  plan mode, skills, todos, tracker, shell background). Priority-sorted registry.
- **Context:** Graph-based `ContextWorkingBuffer` + `PipelineOrchestrator`. Chat compression
  service. Tool output masking. Memory context manager. Token estimation.
- **Session:** `ChatRecordingService` (JSONL). Resume, rewind points. Per-project storage.
- **Safety:** 4 approval modes (DEFAULT, AUTO_EDIT, YOLO, PLAN). `PolicyEngine` with
  priority-based TOML rules. Sandbox (Docker/Podman/Windows). Folder trust discovery.
- **Config:** Hierarchical: user + project `settings.json`. `Config` class as DI container.
  `GEMINI.md` for project context.
- **Differentiators:** Hook system (BeforeModel, AfterModel, BeforeToolSelection), A2A
  server, voice input (Whisper + Gemini Live), model routing, sandboxed execution,
  sub-agents, skills system.
- **Patterns:** Composite strategy (routing), Observer (hooks), DI container, Graph-based context.

#### 5. opencode
- **Language:** TypeScript/Bun | **Repo:** 25 packages, Effect-TS foundation
- **Architecture:** Monorepo: core + llm + opencode + tui (SolidJS) + server (Hono) +
  desktop + web. Effect-TS for structured concurrency.
- **LLM:** `Route` combining Protocol + Endpoint + Auth + Transport. 13 providers.
  Schema-validated body construction.
- **Tools:** Two layers: core tools (bash, read/write/edit, glob, grep, web, apply-patch,
  todo, lsp) + app tools (plan, task/subagent, mcp, guard). Effect Schema for I/O.
- **Context:** Skills from markdown. Compaction agent. Permission-aware prompt injection.
- **Session:** SQLite via Drizzle ORM. WAL mode. Event-sourced projector pattern.
  Location-scoped databases.
- **Safety:** Rule-based permissions (allow/deny/ask). Wildcard matching. "Always saves
  rules per-project". Plan agent denies edits. Read-only explore agents.
- **Config:** JSONC files + `.opencode/` dirs. Hierarchical. Effect Schema validated.
  Model, agents, permissions, MCP, LSP, formatters, plugins, compaction.
- **Differentiators:** Effect-TS structured concurrency, event-sourced sessions, permission
  "always remember", plan-then-build agents, LSP as tool, background subagents,
  snapshot/undo, multi-frontend (TUI/web/desktop/server).
- **Patterns:** Effect-TS (algebraic effects), Event sourcing, Strategy (agents),
  Registry, Plugin hooks via Immer.

#### 6. goose
- **Language:** Rust | **Repo:** 10 Cargo crates
- **Architecture:** CLI + server + UI. Extension-based (extensions ARE MCP servers).
  Tool shim for providers lacking native tools.
- **LLM:** `Provider` trait. Multiple backends. Tool shim layer. Local inference via candle.
- **Tools:** Extension-based. Built-in: developer, code execution, chat recall,
  summarization, analyze (AST), todo, orchestrator, summon (subagent). Confirmation
  routing, inspection, repetition monitoring.
- **Context:** `context_mgmt/` with threshold-based compaction, conversation fixing,
  prompt manager. `moim.rs` (memory-of-important-messages).
- **Session:** `SessionManager` with naming, diagnostics, search, legacy import,
  Nostr-based sharing. Extension state per-session.
- **Safety:** `PromptInjectionScanner` (pattern + optional ML), `SecurityInspector`,
  `AdversaryInspector`, `EgressInspector`. Confidence thresholds. Extension malware check.
- **Config:** YAML + keyring for secrets. `GooseMode` (auto-approve/suggest/chat).
  `PermissionManager` + `PermissionInspector` + `PermissionJudge`.
- **Differentiators:** Prompt injection with ML, recipe system, ACP support,
  OpenTelemetry, elicitation system, scheduler, gateway (Telegram).
- **Patterns:** Extension-as-MCP, Security layering, Tool shim, Memory-of-important-messages.

#### 7. cline
- **Language:** TypeScript/Bun | **Repo:** VS Code extension + CLI + hub
- **Architecture:** 5 SDK packages: shared → llms → agents → core → host apps.
  Gateway pattern for provider abstraction.
- **LLM:** Vendor adapters (Anthropic, OpenAI, Google, Bedrock, Vertex, Mistral, etc.).
  Registry with manifest-driven catalogs. Lazy handler factories.
- **Tools:** Stateless agent iteration loop. Extension registry. MCP client. Plugin system.
- **Context:** Session checkpoint-restore. Session versioning/snapshots.
- **Session:** Session stores, team support, cron subsystem.
- **Safety:** Gitleaks, security module, feature-flag controls. Relies on VS Code sandbox.
- **Config:** Provider settings manager with legacy migration. Remote-config schemas.
- **Differentiators:** Deep VS Code integration (webview, diff previews, file tree).
  Plugin architecture for host apps. Subscription billing. ClineHub for remote/team.
- **Patterns:** Gateway, Extension registry, SDK layering.

#### 8. SWE-agent
- **Language:** Python | **Repo:** agent/, environment/, tools/, run/
- **Architecture:** Minimal. LLM + shell commands in Docker sandbox (`swe-rex`).
  `RetryAgent` with review/retry loops.
- **LLM:** litellm adapter. Cost tracking, per-instance limits, API key rotation.
- **Tools:** YAML-defined `Bundle`s of bash commands. `ToolFilterConfig` blocklist.
  No function-calling — raw bash execution.
- **Context:** Jinja2 templates. `HistoryProcessor` chain. Observation truncation.
- **Session:** Ephemeral Docker container. No persistence.
- **Safety:** Command blocklist, syntax pre-check (`bash -n`), timeout, cost limits.
  Review-on-submit.
- **Config:** Pydantic + YAML overrides.
- **Differentiators:** Research-grade SWE-bench tool. Retry-with-review loop. Minimal abstractions.
- **Patterns:** Template Method, Chain of Responsibility (HistoryProcessor).

#### 9. plandex
- **Language:** Go | **Repo:** client-server (REST/WebSocket)
- **Architecture:** CLI → Go server → LiteLLM proxy. Plan branching/versioning.
  Cumulative diff review sandbox.
- **LLM:** 12+ providers via LiteLLM. Multi-model packs (DailyDriver, Reasoning, Strong,
  etc.). Role-level temperature tuning.
- **Tools:** 9 specialized model roles (planner, architect, coder, builder, summarizer,
  names, commit-messages, auto-continue). No raw shell to LLM.
- **Context:** Tree-sitter project maps. 2M token effective context. Smart loading.
  Context caching.
- **Session:** Persistent plans with version history and branches. Docker-based server.
- **Safety:** Cumulative diff sandbox. Autonomy levels (full/semi/plus/basic/none/custom).
  No direct shell access.
- **Config:** Go structs. Model packs with role-level tuning.
- **Differentiators:** Plan-centric with branching, multi-role orchestration, tree-sitter
  indexing, diff sandbox. Real-world multi-file focus.
- **Patterns:** Plan branching, Multi-role orchestration, Diff sandbox.

### Tier 2 — Specialized / Mid-Maturity

#### 10. kimi-CLI
- **Language:** Python | **Repo:** ~38 source modules
- **Architecture:** Clean layers: CLI (Typer) → Runtime → KimiSoul (agent loop).
  Wire abstraction decouples soul from UI frontends.
- **LLM:** `kosong` abstraction (`ChatProvider`). Kimi, OpenAI, Anthropic, Google, VertexAI.
  OAuth support.
- **Tools:** `KimiToolset` loads by import path. MCP via `fastmcp`. Subagent spawning
  via `LaborMarket`. Approval system.
- **Context:** `Context` class with checkpoints. Auto-compaction at 85% threshold.
- **Session:** `Session` with subagent instances. Fork support.
- **Safety:** `ApprovalRuntime` for tool execution. Directory containment.
- **Config:** TOML + Pydantic validation.
- **Differentiators:** Agent specs (YAML), Wire pub/sub for UI, DMail (checkpointed replies).
- **Patterns:** Wire pub/sub, Agent spec inheritance, Subagent-as-tool.

#### 11. hermes-agent
- **Language:** Python | **Repo:** ~75 entries, 98 agent modules, 90 tool files
- **Architecture:** Monolithic core with plugin edges. `AIAgent` (~12k LOC) central loop.
  `HermesCLI` (~11k LOC) orchestrates session.
- **LLM:** Plugin-based provider registry. 20+ providers. Credential pool with rotation.
  API modes: chat_completions, codex_responses.
- **Tools:** Registry-based auto-discovery. 40+ tools (browser, code execution, delegation,
  vision, TTS, video gen). Toolsets with platform composition. Guardrails + approval.
- **Context:** Pluggable `ContextEngine` ABC. `ContextCompressor` default. Threshold-based.
  Prompt caching sacred.
- **Session:** SQLite + FTS5 search. Resume, fork. Multi-platform routing (20+ platforms).
- **Safety:** 10+ safety modules (file, path, threat patterns, URL, website policy,
  message sanitization, redact, SSL guard, OSV check).
- **Config:** YAML + deep-merge defaults. Profile system. Setup wizard.
- **Differentiators:** Multi-platform gateway, plugin ecosystem, Electron desktop, Ink/React
  TUI, skin/theme, cron scheduler, ~17k tests.
- **Patterns:** "Narrow waist" architecture, Footprint Ladder (extend > skill > plugin > MCP),
  Plugin discovery at import.

#### 12. openinterpreter
- **Language:** Rust (forked from OpenAI Codex) | **Repo:** 114+ crates
- **Architecture:** CLI → core → model-provider → sandboxing → tools. SDK (Python/TS).
  ACP server for editor integration.
- **LLM:** OpenAI Responses API + Bedrock. Provider capabilities declared.
- **Tools:** Dynamic tool discovery, MCP, harness-specific tool sets (8+ agent personas).
- **Context:** `context_manager/`, harness-specific prompts, compaction (remote + local),
  `AGENTS.md` loading.
- **Session:** SQLite-backed thread store.
- **Safety:** OS-level sandbox (seatbelt/landlock/bubblewrap/Windows). Exec policy.
  Network policy. Guardian extension.
- **Config:** Layered TOML. Profile system. MCP config, skills, permissions.
- **Differentiators:** Harness emulation (swap agent personas at runtime), OS-level
  sandboxing, code-mode.
- **Patterns:** Harness abstraction, Platform sandbox, Plugin architecture.

#### 13. crush
- **Language:** Go | **Repo:** ~43 internal packages
- **Architecture:** agent → backend → config → session → tools → hooks → lsp → skills.
  Unix-socket REST API + Charm TUI.
- **LLM:** Multi-provider via `fantasy` abstraction. 6+ providers. Mid-session switching.
  Reasoning effort configurable.
- **Tools:** 20+ built-in (bash, edit, glob, grep, rg, fetch, web search, LSP, MCP).
  Go structs with markdown templates.
- **Context:** Auto-discovery of context files (CLAUDE.md, .cursorrules, AGENTS.md).
  Auto-summarization at threshold.
- **Session:** SQLite-backed. Parent-child relationships, todo tracking, token/cost accounting.
- **Safety:** Permission service (grant/deny/persistent). PreToolUse hooks.
- **Config:** JSON config + crush.md instructions. Hot-reloadable hooks.
- **Differentiators:** LSP integration (gopls etc.), Charm TUI, mid-session model switching,
  todo tracking.
- **Patterns:** Hook system (allow/deny/halt/input-rewrite), LSP as context.

#### 14. kilocode
- **Language:** TypeScript/Bun | **Repo:** 23 packages
- **Architecture:** TUI-first (OpenTUI + Solid.js). Effect ecosystem. Drizzle+SQLite. Hono HTTP.
- **LLM:** 500+ models. Zero-markup pricing. Mid-task model switching.
- **Tools:** Same as OpenCode lineage.
- **Context:** Same as OpenCode lineage.
- **Session:** Same as OpenCode lineage (SQLite).
- **Safety:** Same as OpenCode lineage.
- **Config:** Same as OpenCode lineage.
- **Differentiators:** 500+ model support, broadest IDE surface (VS Code + JetBrains + CLI),
  i18n (20+ languages).
- **Patterns:** Effect-TS, OpenCode fork lineage.

#### 15. Roo-Code
- **Language:** TypeScript | **Repo:** VS Code extension + monorepo
- **Architecture:** VS Code extension with webview UI. Turbo monorepo. `.roomodes` system.
- **LLM:** Multiple providers via Cline lineage.
- **Tools:** Same as Cline lineage + MCP.
- **Context:** Same as Cline lineage.
- **Session:** Same as Cline lineage.
- **Safety:** Gitleaks + Cline lineage.
- **Config:** Same as Cline lineage + `.roomodes` for agent personas.
- **Differentiators:** Role-based "Modes" (Code, Architect, Ask, Debug, Custom). Community-driven.
- **Patterns:** Mode/role polymorphism.

#### 16. amazon-q-developer-CLI
- **Language:** Rust | **Repo:** chat-CLI, agent, UI crates
- **Architecture:** TUI (crossterm + rustyline), tokio async, AWS SDK, SQLite, WebSocket.
- **LLM:** AWS Bedrock (tightly coupled).
- **Tools:** MCP client via `rmcp`. Semantic search client.
- **Context:** Agent-based context assembly.
- **Session:** SQLite local state.
- **Safety:** `tool_permission_checker.rs`. Per-tool checks.
- **Config:** AWS-native (SSO, Cognito, telemetry).
- **Differentiators:** Deep AWS integration. Ships as CLI + GUI. Semantic search.
- **Patterns:** AWS-native, Enterprise auth.

#### 17. copilot-CLI
- **Language:** Closed-source binary (MIT repo)
- **Architecture:** Pre-built binary via npm/Homebrew/WinGet.
- **LLM:** Multi-model (Claude Sonnet default, `/model` to switch).
- **Tools:** LSP support, GitHub MCP server, custom MCP extensibility.
- **Context:** N/A (closed source).
- **Session:** N/A.
- **Safety:** Full user-approval control.
- **Config:** N/A.
- **Differentiators:** Official GitHub product, native GitHub auth (repo/issue/PR),
  "Autopilot" experimental mode.
- **Patterns:** GitHub ecosystem integration.

#### 18. MiMo-Code
- **Language:** TypeScript/Bun | **Repo:** near-identical to Kilo Code
- **Architecture:** TUI + Effect + Drizzle+SQLite + Hono. Desktop + web + Slack.
- **LLM:** Same as Kilo Code lineage.
- **Tools:** Same as Kilo Code lineage.
- **Context:** Same as Kilo Code lineage.
- **Session:** Same as Kilo Code lineage.
- **Safety:** Same as Kilo Code lineage.
- **Config:** Same as Kilo Code lineage.
- **Differentiators:** "MiMo Auto" free channel, persistent memory, self-improving loop,
  Slack integration.
- **Patterns:** Same as Kilo Code.

#### 19. mistral-vibe
- **Language:** Python 3.12+ | **Repo:** Single package with `vibe/` source
- **Architecture:** Textual TUI, ACP protocol, MCP, OpenTelemetry, Pydantic.
- **LLM:** Tightly coupled to Mistral models.
- **Tools:** MCP support. ACP for multi-agent.
- **Context:** N/A (limited docs).
- **Session:** N/A.
- **Safety:** N/A.
- **Config:** N/A.
- **Differentiators:** Python-native, ACP protocol, voice input, PyInstaller distribution.
- **Patterns:** ACP, Textual TUI.

#### 20. qwen-code
- **Language:** TypeScript/Node 22+ | **Repo:** Monorepo with IM channels
- **Architecture:** Ink terminal UI, xterm.js, Docker sandbox. IM bot architecture.
- **LLM:** Multi-protocol (OpenAI/Anthropic/Gemini/Qwen/local).
- **Tools:** Auto-Memory, Auto-Skills, SubAgents, Agent Teams.
- **Context:** N/A.
- **Session:** Daemon mode for background operation.
- **Safety:** Docker sandbox.
- **Config:** N/A.
- **Differentiators:** Richest surface (CLI + Desktop + Daemon + IDE + 5 IM bots).
  Chinese-market focus. Self-dogfooding.
- **Patterns:** IM channel plugins, Daemon mode.

### Tier 3 — Niche / Supplementary

#### 21. warp
- **Language:** Rust (AGPL-3.0) | **Repo:** ~50 crates
- **Architecture:** GPU-accelerated terminal (wgpu). Native UI framework. GraphQL.
  Diesel/SQLite. Firebase. OpenTelemetry.
- **Differentiators:** Owns entire terminal stack. Block-based output. Built-in AI agent ("Oz").
  MCP server. Workflow engine. Cloud sync.

#### 22. claw-code
- **Language:** Python + Rust | **Repo:** 68 modules
- **Architecture:** Meta-harness delegating to LazyCodex and Gajae-Code.
- **Differentiators:** Orchestrates other agents. Plugins, skills, hooks, voice, vim mode.

#### 23. ruflo
- **Language:** TypeScript/Node | **Repo:** npm package
- **Architecture:** Enterprise multi-agent orchestration for Claude Code.
- **Differentiators:** 60+ specialized agents, 34 plugins, swarm coordination,
  self-learning memory, vector store, federated cross-machine communication.

#### 24. SkeletonAgent
- **Language:** Python (PyTorch) | **Repo:** Research project
- **Not a coding agent.** Skeleton-based action recognition using LLM co-agent.

#### 25. free-claude-code
- **Language:** Python (FastAPI) | **Repo:** Proxy middleware
- **Not an agent.** Routes Claude Code/Codex traffic to 17+ alternative providers.

#### 26. grok-CLI
- **Language:** TypeScript/Bun | **Repo:** OpenTUI terminal
- **Architecture:** Terminal coding agent connecting to xAI Grok API.
- **Differentiators:** Real-time X/Twitter search, sub-agents, Telegram remote control,
  Batch API for cheap runs.

#### 27. CLI (Ampersand)
- **Language:** Go (Cobra/Viper) | **Repo:** B2B SaaS CLI
- **Not an AI agent.** Traditional developer CLI for integrations platform.

---

## Cross-Agent Feature Matrix

| Feature | nasim | aider | claude-code | codex | gemini-CLI | opencode | goose | cline | SWE-agent | plandex | kimi-CLI | hermes |
|---------|-------|-------|-------------|-------|-----------|---------|-------|-------|-----------|---------|---------|--------|
| **Multi-provider LLM** | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **grep/glob/search** | ✗ | repo-map | ✓ | ✓ | ✓ | ✓ | ext | ✓ | ✗ | tree-sitter | ✓ | ✓ |
| **Web fetch/search** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ext | ✓ | ✗ | ✗ | ✓ | ✓ |
| **Config file** | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Context compaction** | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | truncation | ✗ | ✓ | ✓ |
| **Session persistence** | ✗ | partial | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Safety/permissions** | ✗ | ✓ | ✓ | ✓ (sandbox) | ✓ | ✓ | ✓ (ML) | ✓ | blocklist | ✓ | ✓ | ✓ |
| **Rich UI** | ✗ | rich | ✓ | TUI | ✓ | TUI | TUI | VS Code | plain | TUI | shell | TUI |
| **Plan mode** | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **MCP client** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| **Multi-agent/subagent** | ✗ | arch mode | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | retry | ✗ | ✓ | ✓ |
| **LSP integration** | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Session rewind** | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Voice I/O** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Event system** | ✗ | ✗ | ✓ (hooks) | ✓ | ✓ (hooks) | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| **Plugin ecosystem** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ext | ✓ | ✗ | ✗ | ✗ | ✓ |
| **Async support** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Git integration** | ✗ | auto-commit | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| **Subagent spawning** | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | retry | ✗ | ✓ | ✓ |
| **Error hierarchy** | ✗ | partial | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| **Structured logging** | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |

---

## Architecture Patterns Summary

| Pattern | Agents Using It | Best Example |
|---------|----------------|--------------|
| Provider abstraction (trait/protocol) | aider, codex, opencode, goose, cline, kimi, hermes | codex (`ModelProvider` trait) |
| Tool ABC + registry | gemini-CLI, opencode, goose, crush | opencode (`Tool.make()` + `ToolRegistry`) |
| Event-driven agent loop | codex, gemini-CLI, opencode, goose, claude-code | gemini-CLI (9 hook events) |
| Layered config (YAML/TOML + env + CLI) | aider, codex, opencode, goose, kimi, hermes | aider (4-layer) |
| Session persistence (SQLite) | codex, opencode, goose, hermes, crush | opencode (event-sourced) |
| Safety sandboxing (OS-level) | codex, openinterpreter | codex (landlock/seccomp/bubblewrap) |
| Context compaction | aider, codex, gemini-CLI, goose, kimi, hermes | aider (background thread) |
| Plugin/extension system | claude-code, codex, gemini-CLI, goose, cline, hermes | claude-code (marketplace) |
| Plan mode | gemini-CLI, opencode, plandex | opencode (dedicated plan agent) |
| Multi-role orchestration | plandex | plandex (9 specialized roles) |
| MCP integration | claude-code, codex, gemini-CLI, opencode, goose, cline | goose (extensions ARE MCP) |
| Subagent spawning | claude-code, codex, gemini-CLI, opencode, goose, kimi | claude-code (5-level nesting) |
| Harness/persona swapping | openinterpreter | openinterpreter (8+ personas) |
| Graph-based context | gemini-CLI | gemini-CLI (`ContextWorkingBuffer`) |
| Effect-TS / algebraic effects | opencode, kilocode | opencode (Effect foundation) |
| LSP as tool | opencode, crush | opencode (hover/def/refs/symbols) |

---

## Key Takeaways for nasim

1. **No agent skips provider abstraction.** nasim is the only one hardcoded to one backend.
2. **Every production agent has config files.** CLI-only config is a proof-of-concept pattern.
3. **Safety is non-negotiable.** Even SWE-agent (research tool) has blocklists and timeouts.
4. **Event-driven is the standard.** Direct `print()` in agent code is unique to nasim.
5. **MCP is the extension standard.** 12/27 agents support it. nasim has none.
6. **Plan mode is emerging.** gemini-CLI, opencode, plandex show it works. nasim should plan for it.
7. **Session persistence is expected.** In-memory-only is a toy pattern.
8. **Context compaction prevents degradation.** Unbounded message growth breaks long sessions.
9. **The best designs compose patterns from multiple agents** — no single agent covers everything.
10. **Goose's ML-based prompt injection scanning** is the state of the art for safety.
