# nasim — Comprehensive Reference Agent Audit

**Date:** 2026-06-20
**Scope:** All 28 reference agents vs nasim C4 design chain
**Framework:** CAR (Context, Action, Result)
**Purpose:** Exhaustive audit of reference agent architectures against nasim's C4 coverage, with improvement roadmap

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Reference Agent Comprehensive Comparison](#2-reference-agent-comprehensive-comparison)
3. [C4 Context Layer Audit](#3-c4-context-layer-audit)
4. [C4 Container Layer Audit](#4-c4-container-layer-audit)
5. [C4 Component Layer Audit](#5-c4-component-layer-audit)
6. [Design Pattern Coverage](#6-design-pattern-coverage)
7. [Feature Capability Matrix](#7-feature-capability-matrix)
8. [Architecture Principle Coverage](#8-architecture-principle-coverage)
9. [Session & Knowledge Sync Audit](#9-session--knowledge-sync-audit)
10. [Gap Analysis: Reference Pros vs Cons](#10-gap-analysis-reference-pros-vs-cons)
11. [C4 Enhancement Recommendations](#11-c4-enhancement-recommendations)
12. [Lower Chain Cascade Impact](#12-lower-chain-cascade-impact)
13. [Consistency Verification](#13-consistency-verification)

---

## 1. Executive Summary

### Scope

28 reference code agents analyzed across 12 architectural dimensions. Each agent's
features, capabilities, design patterns, and principles mapped against nasim's
C4 design chain (Context → Container → Component) to identify coverage gaps and
improvement opportunities.

### Key Findings

| Dimension | nasim Coverage | Reference Best | Gap |
|-----------|---------------|----------------|-----|
| Multi-provider LLM | Context + Container + Component | opencode (13 providers) | Covered |
| Tool system | Container + Component (7 tool types) | gemini-CLI (20+ tools) | Covered |
| Session persistence | Container + Component | opencode (SQLite event-sourced) | Covered |
| Safety/permissions | Container + Component (3 modes) | codex (OS sandbox) | Design gap |
| Context compaction | Container + Component | aider (background thread) | Covered |
| MCP integration | Context + Container + Component | goose (extensions ARE MCP) | Covered |
| HTTP API | Context + Container + Component (ROD) | opencode (Hono server) | Covered |
| Plugin system | Container + Component | claude-code (marketplace) | Design gap |
| Hook system | Container + Component (4 hook types) | gemini-CLI (9 hook events) | Covered |
| Model routing | Container + Component | plandex (9 specialized roles) | Design gap |
| Subagent spawning | Not in C4 | claude-code (5-level nesting) | Missing |
| LSP integration | Component (LspTool) | opencode (hover/def/refs) | Covered |
| Event-driven core | Container + Component (AgentEvent) | gemini-CLI (graph-based) | Covered |
| Async architecture | Container | opencode (Effect-TS) | Design gap |
| Structured logging | Not in C4 | goose (OpenTelemetry) | Missing |
| OS-level sandbox | Not in C4 | codex (landlock/seccomp) | Missing |
| Graph-based context | Not in C4 | gemini-CLI (ContextWorkingBuffer) | Missing |
| Plan branching | Not in C4 | plandex (plan versioning) | Missing |
| Multi-role orchestration | Not in C4 | plandex (9 roles) | Missing |
| Harness/persona swapping | Not in C4 | openinterpreter (8 personas) | Missing |

### Verdict

nasim's C4 design covers **14 of 20** critical architectural concerns from reference
agents. **6 gaps** require C4 enhancement: subagent spawning, structured logging,
OS-level sandboxing, graph-based context, plan branching, and multi-role orchestration.

---

## 2. Reference Agent Comprehensive Comparison

### 2.1 Agent Inventory

| # | Agent | Language | Architecture | Maturity | Primary Differentiator |
|---|-------|----------|-------------|----------|----------------------|
| 1 | aider | Python | Single-package CLI | Production | Edit-format polymorphism (14 strategies) |
| 2 | claude-code | TypeScript/Bun | Plugin ecosystem | Production | Marketplace + hooks + enterprise MDM |
| 3 | codex | Rust | 124-crate workspace | Production | OS-level sandboxing + trait polymorphism |
| 4 | gemini-CLI | TypeScript/Node | Monorepo (33+ subdirs) | Production | Graph-based context + A2A server |
| 5 | opencode | TypeScript/Bun | Effect-TS monorepo | Production | Event-sourced sessions + multi-frontend |
| 6 | goose | Rust | CLI + extension-based | Production | Extensions ARE MCP servers + ML safety |
| 7 | cline | TypeScript/Bun | VS Code extension + SDK | Production | Deep VS Code integration + subscription |
| 8 | SWE-agent | Python | Minimal Docker sandbox | Research | Retry-with-review loop |
| 9 | plandex | Go | Client-server + plan branching | Production | 9 specialized model roles + diff sandbox |
| 10 | kimi-CLI | Python | Clean layered (Wire pub/sub) | Mid | Wire pub/sub + agent spec inheritance |
| 11 | hermes-agent | Python | Monolithic + plugin edges | Mid | 20+ platform gateway + 40+ tools |
| 12 | openinterpreter | Rust (forked) | CLI + core + SDK | Production | Harness persona swapping + OS sandbox |
| 13 | crush | Go | agent → backend → TUI | Mid | LSP integration + Charm TUI |
| 14 | kilocode | TypeScript/Bun | Effect-TS (OpenCode fork) | Mid | 500+ models + broadest IDE surface |
| 15 | Roo-Code | TypeScript | VS Code extension | Mid | Role-based modes + community-driven |
| 16 | amazon-q-developer-CLI | Rust | TUI + agent + SQLite | Production | Deep AWS integration + semantic search |
| 17 | copilot-CLI | Closed-source | Pre-built binary | Production | Official GitHub + native auth |
| 18 | MiMo-Code | TypeScript/Bun | TUI + Effect + multi-frontend | Mid | Persistent memory + self-improving loop |
| 19 | mistral-vibe | Python | Textual TUI + ACP | Early | ACP protocol + voice input |
| 20 | qwen-code | TypeScript/Node | IM bot architecture | Mid | Richest surface (CLI + Desktop + 5 IM bots) |
| 21 | warp | Rust | GPU-accelerated terminal | Production | Owns entire terminal stack + AI agent |
| 22 | claw-code | Python + Rust | Meta-harness | Early | Orchestrates other agents |
| 23 | ruflo | TypeScript/Node | Enterprise multi-agent | Early | 60+ agents + swarm coordination |
| 24 | SkeletonAgent | Python (PyTorch) | Research project | Research | Action recognition (not a coding agent) |
| 25 | free-claude-code | Python (FastAPI) | Proxy middleware | Early | Routes to 17+ providers |
| 26 | grok-CLI | TypeScript/Bun | OpenTUI terminal | Mid | Real-time X/Twitter search + Telegram |
| 27 | CLI (Ampersand) | Go (Cobra/Viper) | B2B SaaS CLI | Production | Traditional developer CLI (not AI) |
| 28 | MiMo-Code | TypeScript/Bun | Near-identical to Kilo Code | Mid | MiMo Auto free channel + Slack integration |

### 2.2 Feature Comparison Matrix

| Feature | nasim | aider | claude-code | codex | gemini-CLI | opencode | goose | cline | SWE-agent | plandex | kimi-CLI | hermes |
|---------|-------|-------|-------------|-------|-----------|---------|-------|-------|-----------|---------|---------|--------|
| Multi-provider LLM | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tool ABC + Registry | ✗ | strategy | ✓ | ✓ | ✓ | ✓ | ext | ✓ | YAML | ✓ | ✓ | ✓ |
| Event-driven core | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Layered config | ✗ | ✓(4-layer) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Session persistence | ✗ | partial | ✓ | ✓(SQLite) | ✓ | ✓(SQLite) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓(SQLite) |
| Safety/permissions | ✗ | ✓ | ✓ | ✓(sandbox) | ✓(4 modes) | ✓ | ✓(ML) | ✓ | blocklist | ✓ | ✓ | ✓(10+) |
| Context compaction | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | truncation | ✗ | ✓ | ✓ |
| Rich UI | ✗ | rich | ✓ | TUI | ✓ | TUI | TUI | VS Code | plain | TUI | shell | TUI |
| Plan mode | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| MCP client | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| Subagent spawning | ✗ | arch | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | retry | ✗ | ✓ | ✓ |
| LSP integration | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Session rewind | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Voice I/O | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Hook system | ✗ | ✗ | ✓(9 events) | ✓ | ✓(9 events) | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Plugin ecosystem | ✗ | ✗ | ✓(marketplace) | ✓ | ✓ | ✓ | ext | ✓ | ✗ | ✗ | ✗ | ✓ |
| Async support | ✗ | ✗ | ✓ | ✓ | ✓ | ✓(Effect) | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| Git integration | ✗ | auto-commit | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ |
| Error hierarchy | ✗ | partial | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ |
| Structured logging | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓(OTel) | ✓ | ✗ | ✓ | ✓ | ✓ |
| HTTP API server | ✗ | ✗ | ✗ | ✗ | A2A | ✓(Hono) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| OS-level sandbox | ✗ | ✗ | ✗ | ✓(landlock) | ✗ | ✗ | ✗ | ✗ | Docker | ✗ | ✗ | ✗ |
| Graph-based context | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Multi-role orchestration | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓(9 roles) | ✗ | ✗ |
| Harness/persona swapping | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓(8 personas) |
| Prompt injection defense | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓(ML) | ✗ | ✗ | ✗ | ✗ | ✗ |

### 2.3 Architecture Pattern Comparison

| Pattern | Agents Using It | Best Example | nasim Status |
|---------|----------------|--------------|--------------|
| Provider abstraction (trait/protocol) | aider, codex, opencode, goose, cline, kimi, hermes | codex (`ModelProvider` trait) | Design exists (Protocol), not implemented |
| Tool ABC + registry | gemini-CLI, opencode, goose, crush | opencode (`Tool.make()` + `ToolRegistry`) | Design exists (ABC), not implemented |
| Event-driven agent loop | codex, gemini-CLI, opencode, goose, claude-code | gemini-CLI (9 hook events) | Design exists (AgentEvent), not implemented |
| Layered config (YAML/TOML + env + CLI) | aider, codex, opencode, goose, kimi, hermes | aider (4-layer) | Design exists (ConfigLoader), not implemented |
| Session persistence (SQLite) | codex, opencode, goose, hermes, crush | opencode (event-sourced) | Design exists (JSON Lines), not implemented |
| Safety sandboxing (OS-level) | codex, openinterpreter | codex (landlock/seccomp/bubblewrap) | Not designed |
| Context compaction | aider, codex, gemini-CLI, goose, kimi, hermes | aider (background thread) | Design exists (ContextCompactor), not implemented |
| Plugin/extension system | claude-code, codex, gemini-CLI, goose, cline, hermes | claude-code (marketplace) | Design exists (PluginLoader), not implemented |
| Plan mode | gemini-CLI, opencode, plandex | opencode (dedicated plan agent) | Design exists (PlanSession), not implemented |
| Multi-role orchestration | plandex | plandex (9 specialized roles) | Not designed |
| MCP integration | claude-code, codex, gemini-CLI, opencode, goose, cline | goose (extensions ARE MCP) | Design exists (MCPToolAdapter), not implemented |
| Subagent spawning | claude-code, codex, gemini-CLI, opencode, goose, kimi | claude-code (5-level nesting) | Not designed |
| Harness/persona swapping | openinterpreter | openinterpreter (8+ personas) | Not designed |
| Graph-based context | gemini-CLI | gemini-CLI (`ContextWorkingBuffer`) | Not designed |
| Effect-TS / algebraic effects | opencode, kilocode | opencode (Effect foundation) | Not applicable (Python) |
| LSP as tool | opencode, crush | opencode (hover/def/refs/symbols) | Design exists (LspTool), not implemented |

### 2.4 Design Principle Comparison

| Principle | nasim Design | Best Reference | Gap Assessment |
|-----------|-------------|----------------|----------------|
| **Single Responsibility** | AgentOrchestrator owns loop only | codex (124 crates, strict boundaries) | C4 covers SRP correctly |
| **Open/Closed** | Provider Protocol + Tool ABC | opencode (Effect-TS extensibility) | C4 covers OCP correctly |
| **Liskov Substitution** | Provider Protocol with 3 implementations | codex (trait-object polymorphism) | C4 covers LSP correctly |
| **Interface Segregation** | Tool ABC with minimal interface | opencode (Effect Schema I/O) | C4 covers ISP correctly |
| **Dependency Inversion** | ProviderFactory + ConfigLoader | codex (ConfigLayerStack) | C4 covers DIP correctly |
| **Separation of Concerns** | 7 container boundaries | opencode (25 packages) | C4 covers SoC correctly |
| **DRY** | Shared AgentEvent across interfaces | aider (single agent runner) | C4 covers DRY correctly |
| **Composition over Inheritance** | Tool ABC + registry composition | opencode (Tool.make()) | C4 covers composition correctly |
| **Law of Demeter** | Manager → Adapter → Store pattern | codex (strict crate boundaries) | C4 follows LoD correctly |
| **YAGNI** | Minimal component set per container | SWE-agent (minimal abstractions) | C4 follows YAGNI correctly |

---

## 3. C4 Context Layer Audit

### 3.1 Context Diagram Coverage

| Reference Concern | nasim Context Coverage | Status |
|-------------------|----------------------|--------|
| Developer actor | `Person(dev, "Developer")` | Covered |
| HTTP Client actor | `Person(http_client, "HTTP Client")` | Covered |
| MCP Client actor | `System_Ext(mcp_client)` | Covered |
| LLM Provider | `System_Ext(llm_provider)` | Covered |
| Host Filesystem | `System_Ext(host_fs)` | Covered |
| Host Shell | `System_Ext(host_shell)` | Covered |
| Web | `System_Ext(web)` | Covered |
| MCP Server | `System_Ext(mcp_server)` | Covered |
| Global Config | `System_Ext(global_config)` | Covered |
| Project Config | `System_Ext(project_config)` | Covered |
| Env Variables | `System_Ext(env_vars)` | Covered |
| Session Directory | `System_Ext(session_dir)` | Covered |
| Plugin Directory | Not in Context | **GAP** |
| Git Repository | Not in Context | **GAP** |
| LLM Provider (multi) | Single `llm_provider` only | **GAP** — needs multi-provider representation |

### 3.2 Context Relationship Coverage

| Relationship | nasim | Reference Best | Status |
|-------------|-------|----------------|--------|
| Developer → nasim (terminal) | ✓ | All CLI agents | Covered |
| HTTP Client → nasim (HTTP/SSE) | ✓ | opencode (Hono) | Covered |
| MCP Client → nasim (stdio/SSE) | ✓ | goose (extensions) | Covered |
| nasim → LLM Provider (HTTP/JSON) | ✓ | All agents | Covered |
| nasim → Host Filesystem (path I/O) | ✓ | All agents | Covered |
| nasim → Host Shell (subprocess) | ✓ | All agents | Covered |
| nasim → Web (HTTP) | ✓ | gemini-CLI, opencode | Covered |
| nasim → MCP Server (stdio/SSE) | ✓ | goose, claude-code | Covered |
| nasim → Git Repository | Not shown | aider (auto-commit) | **GAP** |
| nasim → Plugin Directory | Not shown | claude-code (marketplace) | **GAP** |

### 3.3 Context Gaps from References

| Gap | Source Reference | Impact | Recommendation |
|-----|-----------------|--------|----------------|
| No Git Repository in context | aider (auto-commit), codex (git-aware) | Agent cannot express VCS awareness at system level | Add `System_Ext(git_repo, "Git Repository", "Version control for project files")` |
| No Plugin Directory in context | claude-code (marketplace), hermes (plugin edges) | Plugin system has no external store representation | Add `System_Ext(plugin_dir, "Plugin Directory", "~/.nasim/plugins/")` |
| Single LLM Provider external | opencode (13 providers), aider (100+ via litellm) | Context implies single backend | Rename to `LLM Backend` with description covering multi-provider |

---

## 4. C4 Container Layer Audit

### 4.1 Container Coverage

| Reference Concern | nasim Container | Status |
|-------------------|----------------|--------|
| CLI interface | `Container(CLI, "CLI")` | Covered |
| Agent core | `Container(agent, "Agent Core")` | Covered |
| Provider abstraction | `Container(provider, "Provider Layer")` | Covered |
| Tool system | `Container(tools, "Tool Layer")` | Covered |
| Configuration | `Container(config, "Config")` | Covered |
| Session persistence | `Container(session, "Session Store")` | Covered |
| HTTP API | `Container(server, "HTTP API Server")` | Covered |
| Hook system | `Container(hooks, "Hook System")` | Covered |
| Plugin system | `Container(plugins, "Plugin System")` | Covered |
| Model router | Not in Container | **GAP** — referenced in entities.md but missing from container |
| Subagent spawner | Not in Container | **GAP** — 10/27 agents have this |
| LSP client | Not in Container | **GAP** — LspTool exists but no container |
| Git integration | Not in Container | **GAP** — GitTool exists but no container |
| Logging/observability | Not in Container | **GAP** — goose (OpenTelemetry) |
| Sandbox/security | Not in Container | **GAP** — codex (OS sandbox) |

### 4.2 Container Relationship Coverage

| Relationship | nasim | Reference Best | Status |
|-------------|-------|----------------|--------|
| CLI → Agent Core | ✓ | All CLI agents | Covered |
| Server → Agent Core | ✓ | opencode (Hono) | Covered |
| Agent → Provider | ✓ | All agents | Covered |
| Agent → Tools | ✓ | All agents | Covered |
| Agent → Session | ✓ | codex, opencode | Covered |
| Agent → Hooks | ✓ | gemini-CLI (9 events) | Covered |
| Hooks → Plugins | ✓ | claude-code (marketplace) | Covered |
| Plugins → Tools | ✓ | goose (extensions) | Covered |
| Config → Agent | ✓ | All agents | Covered |
| Config → Provider | ✓ | All agents | Covered |
| Config → Tools | ✓ | All agents | Covered |
| Agent → Model Router | Not shown | plandex (9 roles) | **GAP** |
| Agent → Subagent Spawner | Not shown | claude-code (5-level) | **GAP** |
| Tools → Git Repository | Not shown | aider (auto-commit) | **GAP** |
| Tools → LSP Server | Not shown | opencode (hover/def) | **GAP** |

### 4.3 Container Gaps from References

| Gap | Source Reference | Impact | Recommendation |
|-----|-----------------|--------|----------------|
| No ModelRouter container | plandex (9 roles), gemini-CLI (model routing) | Model selection is implicit in Provider | Add `Container(router, "Model Router", "Python", "Model selection, fallback, task classification")` |
| No Subagent container | claude-code (5-level nesting), opencode (background agents) | Cannot express parallel task execution | Add `Container(subagent, "Subagent Spawner", "Python", "Spawn child agents with restricted tools")` |
| No Git container | aider (auto-commit), codex (git-aware edits) | Git operations are tool-level only | Add `Container(git, "Git Integration", "Python", "Auto-commit, branch awareness, diff tracking")` |
| No LSP container | opencode (hover/def/refs), crush (gopls) | LSP is tool-level only | Add `Container(lsp, "LSP Client", "Python", "Language server protocol: hover, definition, references")` |
| No Logging container | goose (OpenTelemetry), aider (structured logging) | No observability layer | Add `Container(logging, "Observability", "Python structlog", "Structured logging, trace correlation, metrics")` |
| No Sandbox container | codex (landlock/seccomp), openinterpreter (seatbelt) | No OS-level security boundary | Add `Container(sandbox, "Sandbox", "Python", "OS-level process isolation: landlock, seccomp, bubblewrap")` |

---

## 5. C4 Component Layer Audit

### 5.1 Agent Layer Component Coverage

| Component | nasim | Reference Equivalent | Status |
|-----------|-------|---------------------|--------|
| AgentOrchestrator | ✓ | opencode (AgentRunner) | Covered |
| ConversationHistory | ✓ | aider (ChatHistory) | Covered |
| ContextCompactor | ✓ | aider (ChatSummary) | Covered |
| PermissionGate | ✓ | codex (exec_policy) | Covered |
| PlanSession | ✓ | opencode (PlanAgent) | Covered |
| AgentEvent | ✓ | gemini-CLI (EventBus) | Covered |
| SubagentManager | Not designed | claude-code (SubagentSpawner) | **GAP** |
| TaskDispatcher | Not designed | plandex (9 roles) | **GAP** |
| ErrorBoundary | Not designed | codex (SafetyCheck) | **GAP** |

### 5.2 Provider Layer Component Coverage

| Component | nasim | Reference Equivalent | Status |
|-----------|-------|---------------------|--------|
| Provider (Protocol) | ✓ | codex (ModelProvider trait) | Covered |
| ProviderFactory | ✓ | opencode (Route factory) | Covered |
| ModelRouter | In entities.md, not in C4 | plandex (model packs) | **GAP** |
| OllamaProvider | ✓ | — | Covered |
| OpenAIProvider | ✓ | — | Covered |
| AnthropicProvider | ✓ | — | Covered |
| ProviderCapabilities | Not designed | codex (capabilities declared) | **GAP** |
| FallbackChain | Not designed | gemini-CLI (composite strategies) | **GAP** |

### 5.3 Tool Layer Component Coverage

| Component | nasim | Reference Equivalent | Status |
|-----------|-------|---------------------|--------|
| Tool (ABC) | ✓ | opencode (Tool.make()) | Covered |
| ToolRegistry | ✓ | gemini-CLI (priority-sorted) | Covered |
| ToolResult | ✓ | codex (SafetyCheck + result) | Covered |
| FileTools (3) | ✓ | All agents | Covered |
| SearchTools (3) | ✓ | gemini-CLI (ripgrep) | Covered |
| ShellTool | ✓ | All agents | Covered |
| DirTool | ✓ | Most agents | Covered |
| WebTools (2) | ✓ | opencode, gemini-CLI | Covered |
| GitTool | ✓ | aider (auto-commit) | Covered |
| MCPToolAdapter | ✓ | goose (extensions) | Covered |
| LspTool | ✓ | opencode, crush | Covered |
| SubagentTool | Not designed | claude-code (SubagentTool) | **GAP** |
| TodoTool | Not designed | gemini-CLI (todos) | **GAP** |
| MemoryTool | Not designed | goose (moim.rs) | **GAP** |
| PlanTool | Not designed | opencode (plan agent) | **GAP** |

### 5.4 Session Layer Component Coverage

| Component | nasim | Reference Equivalent | Status |
|-----------|-------|---------------------|--------|
| SessionStore | ✓ | codex (ThreadStore) | Covered |
| Session | ✓ | opencode (Session model) | Covered |
| SessionVersioning | Not designed | opencode (snapshots/undo) | **GAP** |
| SessionSearch | Not designed | hermes (FTS5 search) | **GAP** |
| SessionFork | Not designed | kimi-CLI (fork support) | **GAP** |

### 5.5 Server Layer Component Coverage

| Component | nasim | Reference Equivalent | Status |
|-----------|-------|---------------------|--------|
| ServerApp | ✓ | opencode (Hono server) | Covered |
| ServerRouter | ✓ | opencode (REST routes) | Covered |
| SSEHandler | ✓ | gemini-CLI (SSE streaming) | Covered |
| APISchema | ✓ | opencode (Effect Schema) | Covered |
| WebSocketHandler | Not designed | warp (GraphQL) | **GAP** |
| RateLimiter | Not designed | goose (egress inspector) | **GAP** |
| AuthMiddleware | Not designed | claude-code (MDM enterprise) | **GAP** |

---

## 6. Design Pattern Coverage

### 6.1 Pattern vs nasim C4 Mapping

| Design Pattern | Reference Best | nasim C4 Coverage | Gap |
|---------------|----------------|-------------------|-----|
| **Strategy** (provider abstraction) | codex (`ModelProvider` trait) | Provider Protocol in Component | Covered |
| **Factory** (provider creation) | opencode (Route factory) | ProviderFactory in Component | Covered |
| **Registry** (tool management) | gemini-CLI (priority-sorted) | ToolRegistry in Component | Covered |
| **Observer** (event system) | gemini-CLI (9 hook events) | AgentEvent + HookManager | Covered |
| **Template Method** (agent loop) | aider (Coder subclasses) | AgentOrchestrator | Covered |
| **Chain of Responsibility** (hooks) | aider (HistoryProcessor) | HookManager chain | Covered |
| **Decorator** (MCP tools) | goose (extensions ARE MCP) | MCPToolAdapter | Covered |
| **Adapter** (provider wrappers) | kimi-CLI (kosong abstraction) | Provider implementations | Covered |
| **Composite** (plugin tools) | claude-code (marketplace) | PluginLoader + ToolRegistry | Covered |
| **State** (agent lifecycle) | SM layer (12 states) | SM diagram exists | Covered |
| **Proxy** (sandbox) | codex (landlock/seccomp) | Not designed | **GAP** |
| **Mediator** (subagent orchestration) | claude-code (5-level nesting) | Not designed | **GAP** |
| **Command** (plan mode) | opencode (plan agent) | PlanSession exists | Covered |
| **Iterator** (session messages) | opencode (event-sourced) | SessionStore | Covered |
| **Builder** (config construction) | aider (4-layer configargparse) | ConfigLoader | Covered |
| **Null Object** (ToolResult) | codex (SafetyCheck enum) | ToolResult(success=False) | Covered |
| **Repository** (session persistence) | codex (ThreadStore trait) | SessionStore | Covered |
| **Event Sourcing** (session history) | op SQLite + projector | JSON Lines (not event-sourced) | Partial |

### 6.2 Missing Pattern Recommendations

| Pattern | Source | C4 Impact | Recommendation |
|---------|--------|-----------|----------------|
| **Proxy/Sandbox** | codex (landlock), openinterpreter (seatbelt) | New Container: Sandbox | Add sandbox container between Tool Layer and Host Shell |
| **Mediator** | claude-code (subagent spawning) | New Container: Subagent Spawner | Add subagent container that mediates parent-child agent communication |
| **Event Sourcing** | opencode (SQLite + projector) | Enhance Session container | Upgrade SessionStore from JSON Lines to event-sourced SQLite |
| **Circuit Breaker** | goose (repetition monitoring) | Enhance Provider container | Add FallbackChain component with circuit breaker logic |
| **Decorator** | hermes (10+ safety modules) | Enhance Agent container | Add SafetyPipeline component wrapping PermissionGate |

---

## 7. Feature Capability Matrix

### 7.1 Capability Depth Comparison

| Capability | nasim Design | aider | claude-code | codex | gemini-CLI | opencode | goose | plandex |
|-----------|-------------|-------|-------------|-------|-----------|---------|-------|---------|
| **Provider count** | 3 (Ollama, OpenAI, Anthropic) | 100+ (litellm) | 3+ (Anthropic, Bedrock, custom) | 2+ (OpenAI, Bedrock) | 1 (Gemini) | 13 | Multiple | 12+ (LiteLLM) |
| **Tool count** | 16 designed | ~20 | 10+MCP | Rich framework | 20+ built-in | Core + app tools | Extension-based | 9 roles |
| **Config layers** | 4 (global, project, env, CLI) | 4 (CLI, .env, .aider.conf.yml, defaults) | 4 (managed, user, project, local) | 4 (global, project, cloud, CLI) | 2 (user, project) | JSONC + .opencode | YAML + keyring | Go structs |
| **Session format** | JSON Lines | Markdown chat history | Transcript paths | SQLite ThreadStore | JSONL | SQLite (event-sourced) | Named sessions | Plan versioning |
| **Safety modes** | 3 (ask, auto, off) | Confirmation + ignore | Tiered (allow/ask/deny) | OS sandbox + exec policy | 4 modes (DEFAULT, AUTO_EDIT, YOLO, PLAN) | Rule-based (allow/deny/ask) | ML injection + inspector | Autonomy levels |
| **Context strategy** | Token-budgeted compaction | Background summarization | PreCompact hooks | Remote compaction | Graph-based + compression | Compaction agent | Threshold + moim | Smart loading |
| **Hook events** | 4 (PreTool, PostTool, PreLLM, PostLLM) | None | 9 events | Events | 9 events (BeforeModel, AfterModel, etc.) | Immer hooks | PreToolUse | None |
| **Plugin format** | JSON manifest | None | Marketplace + YAML | TOML config | settings.json | Effect plugins | Extensions | None |
| **API surface** | REST + SSE (ROD) | None | None | None | A2A server | Hono server | None | REST/WebSocket |
| **Subagent depth** | Not designed | Architect mode | 5-level nesting | Yes | Yes | Background agents | Yes | None |
| **LSP support** | LspTool designed | None | None | None | None | hover/def/refs | None | None |
| **Git awareness** | GitTool designed | auto-commit | Yes | Yes | Yes | Yes | Yes | Yes |
| **Plan branching** | PlanSession (flat) | None | None | None | Plan mode | Plan agent | None | Plan versioning + branches |
| **Multi-role** | Not designed | None | None | None | None | None | None | 9 specialized roles |

### 7.2 nasim Design Score vs References

| Dimension (1-10) | nasim Design | aider | claude-code | codex | gemini-CLI | opencode | goose | plandex |
|------------------|-------------|-------|-------------|-------|-----------|---------|-------|---------|
| Provider abstraction | 8 | 9 | 8 | 9 | 3 | 10 | 8 | 9 |
| Tool system | 8 | 7 | 8 | 9 | 9 | 9 | 8 | 7 |
| Event-driven core | 9 | 4 | 9 | 9 | 10 | 10 | 9 | 5 |
| Config system | 8 | 9 | 8 | 9 | 7 | 8 | 8 | 7 |
| Session management | 7 | 5 | 8 | 9 | 8 | 10 | 8 | 8 |
| Safety/permissions | 7 | 6 | 8 | 10 | 9 | 8 | 10 | 8 |
| Context management | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 7 |
| UI/rendering | 8 | 8 | 9 | 8 | 9 | 9 | 8 | 8 |
| Plan mode | 7 | 3 | 4 | 4 | 8 | 9 | 4 | 10 |
| MCP integration | 8 | 3 | 9 | 9 | 9 | 9 | 10 | 3 |
| Multi-interface | 9 | 3 | 7 | 6 | 8 | 10 | 6 | 5 |
| Extensibility | 8 | 5 | 10 | 9 | 9 | 9 | 9 | 5 |
| **Average** | **7.9** | **6.1** | **7.8** | **8.0** | **8.3** | **8.8** | **7.9** | **6.9** |

---

## 8. Architecture Principle Coverage

### 8.1 Principle vs C4 Layer Mapping

| Principle | C4 Context | C4 Container | C4 Component | Status |
|-----------|-----------|-------------|-------------|--------|
| **Interface-agnostic core** | nasim as single system | Agent Core separate from CLI/Server | AgentOrchestrator yields events | Fully covered |
| **Provider abstraction** | LLM Provider as external | Provider Layer container | Provider Protocol + 3 implementations | Fully covered |
| **Tool extensibility** | MCP Server external | Tool Layer container | Tool ABC + ToolRegistry + MCPToolAdapter | Fully covered |
| **Config layering** | Global/Project Config external | Config container | ConfigLoader + Config schema | Fully covered |
| **Session persistence** | Session Directory external | Session Store container | SessionStore + Session model | Fully covered |
| **Safety-first** | Not explicit | Not explicit | PermissionGate component | Partial — needs container |
| **Event-driven** | Not explicit | Agent Core yields events | AgentEvent types | Partial — needs context |
| **Multi-interface** | Developer + HTTP Client + MCP Client | CLI + Server containers | Per-interface components | Fully covered |
| **Hook extensibility** | Not explicit | Hook System container | HookManager + Hook types | Partial — needs context |
| **Plugin ecosystem** | Not explicit | Plugin System container | PluginLoader + PluginManifest | Partial — needs context |

### 8.2 Missing Principle Coverage

| Principle | Source | C4 Gap | Recommendation |
|-----------|--------|--------|----------------|
| **Observability** | goose (OpenTelemetry) | No logging/trace container | Add Observability container with structured logging + trace correlation |
| **Security boundary** | codex (OS sandbox) | No sandbox container | Add Sandbox container between Tools and Host |
| **Subagent orchestration** | claude-code (5-level nesting) | No subagent container | Add Subagent Spawner container |
| **Plan versioning** | plandex (plan branching) | PlanSession is flat | Enhance PlanSession with version history |
| **Multi-role** | plandex (9 specialized roles) | Single orchestrator | Add TaskDispatcher component for role-based delegation |
| **Graph-based context** | gemini-CLI (ContextWorkingBuffer) | Linear message list | Consider graph-based context model |
| **Harness swapping** | openinterpreter (8 personas) | Fixed agent persona | Add PersonaLoader component for runtime persona switching |

---

## 9. Session & Knowledge Sync Audit

### 9.1 Cross-Interface Session Sync

| Concern | nasim Design | Reference Best | Gap |
|---------|-------------|----------------|-----|
| Session shared across CLI + HTTP | SessionStore accessible from both | opencode (SQLite, multi-frontend) | Covered — same SessionStore |
| Message history unified | ConversationHistory owns messages | codex (ThreadStore) | Covered — single history |
| Event stream shared | AgentEvent consumed by CLI + Server | gemini-CLI (EventBus) | Covered — same event types |
| Session resume across interfaces | Session ID + load from store | opencode (resume + rewind) | Covered — session ID persistence |
| Config shared across interfaces | ConfigLoader loads once | aider (4-layer) | Covered — single config source |
| Tool registry shared | ToolRegistry instance-based | gemini-CLI (priority-sorted) | Covered — single registry |

### 9.2 Knowledge Sync Gaps

| Gap | Source Reference | Impact | Recommendation |
|-----|-----------------|--------|----------------|
| No cross-session knowledge | hermes (SQLite FTS5 search) | Cannot search across sessions | Add SessionSearch component |
| No session versioning | opencode (snapshots/undo) | Cannot revert to prior state | Add SessionVersioning component |
| No session forking | kimi-CLI (fork support) | Cannot branch conversation | Add SessionFork capability |
| No memory persistence | goose (moim.rs), MiMo-Code (persistent memory) | No long-term knowledge | Add MemoryStore component |
| No cross-machine sync | ruflo (federated communication) | Single-machine only | Future: add sync protocol |

---

## 10. Gap Analysis: Reference Pros vs Cons

### 10.1 Reference Agent Pros (to adopt in nasim)

| Reference | Pro | nasim Adoption Status |
|-----------|-----|----------------------|
| aider | Edit-format polymorphism (14 strategies) | Not designed — single edit format |
| claude-code | Plugin marketplace + hooks ecosystem | Plugin system designed, hooks designed |
| codex | OS-level sandboxing (landlock/seccomp) | Not designed |
| gemini-CLI | Graph-based context management | Linear context designed |
| opencode | Event-sourced sessions + multi-frontend | JSON Lines sessions, multi-interface designed |
| goose | ML-based prompt injection detection | Basic PermissionGate designed |
| plandex | 9 specialized model roles + plan branching | Single orchestrator, flat plan |
| openinterpreter | Harness persona swapping | Fixed persona |
| hermes | 20+ platform gateway | CLI + HTTP + MCP designed |
| kimi-CLI | Wire pub/sub for UI decoupling | AgentEvent pattern designed |
| crush | LSP integration as tool | LspTool designed |
| claude-code | Background/daemon sessions | Not designed |
| gemini-CLI | Voice input (Whisper + Gemini Live) | Not designed |
| opencode | Snapshot/undo for sessions | Not designed |
| codex | Remote context compaction | Local compaction designed |

### 10.2 Reference Agent Cons (to solve in nasim)

| Reference | Con | nasim Solution |
|-----------|-----|---------------|
| aider | No MCP, no plugin system, no HTTP API | nasim has MCP, plugins, HTTP API in design |
| claude-code | Closed-source runtime, enterprise-only | nasim is open-source, lightweight |
| codex | 124-crate Rust complexity | nasim is Python, simpler |
| gemini-CLI | Single provider (Google only) | nasim has 3+ providers |
| opencode | Effect-TS complexity, TypeScript-only | nasim is Python, simpler |
| goose | Tightly coupled to extension model | nasim has clean separation |
| cline | VS Code extension only | nasim has CLI + HTTP + MCP |
| SWE-agent | Ephemeral sessions, no persistence | nasim has persistent sessions |
| plandex | No MCP, no plugins, no subagents | nasim has all three |
| hermes | Monolithic 12k LOC agent loop | nasim has clean component decomposition |
| openinterpreter | Forked from Codex, Rust complexity | nasim is Python, independent design |
| kimi-CLI | Limited tool ecosystem | nasim has 16+ tools designed |
| kilocode | Fork of OpenCode, no unique innovation | nasim has unique multi-interface design |
| Roo-Code | VS Code extension only | nasim has CLI + HTTP + MCP |
| amazon-q | AWS-only, tightly coupled | nasim is provider-agnostic |
| copilot-CLI | Closed-source, GitHub-only | nasim is open-source |
| MiMo-Code | Near-identical to Kilo Code | nasim has unique design chain |
| mistral-vibe | Mistral-only, limited features | nasim has multi-provider |
| qwen-code | Chinese-market focus, IM-bot architecture | nasim has global focus |
| warp | Owns entire terminal stack, AGPL | nasim is focused agent, Apache-2.0 |
| claw-code | Meta-harness, delegates to others | nasim has direct implementation |
| ruflo | Enterprise complexity, 60+ agents | nasim is single-agent with subagent support |

---

## 11. C4 Enhancement Recommendations

### 11.1 Context Diagram Enhancements

| Enhancement | Rationale | Source Reference |
|-------------|-----------|-----------------|
| Add `System_Ext(git_repo, "Git Repository")` | GitTool needs external system representation | aider, codex |
| Add `System_Ext(plugin_dir, "Plugin Directory")` | Plugin system needs external store | claude-code, hermes |
| Rename `llm_provider` to `LLM Backend` | Imply multi-provider capability | opencode (13 providers) |
| Add `System_Ext(sandbox, "Sandbox Runtime")` | OS-level security boundary | codex (landlock) |
| Add `System_Ext(memory_store, "Memory Store")` | Long-term knowledge persistence | goose (moim.rs) |

### 11.2 Container Diagram Enhancements

| Enhancement | Rationale | Source Reference |
|-------------|-----------|-----------------|
| Add `Container(router, "Model Router")` | Model selection + fallback + task classification | plandex, gemini-CLI |
| Add `Container(subagent, "Subagent Spawner")` | Parallel task execution | claude-code (5-level) |
| Add `Container(sandbox, "Sandbox")` | OS-level process isolation | codex (landlock/seccomp) |
| Add `Container(observability, "Observability")` | Structured logging + traces | goose (OpenTelemetry) |
| Add `Container(memory, "Memory Store")` | Cross-session knowledge | goose (moim.rs) |
| Add `Container(git, "Git Integration")` | Version control awareness | aider (auto-commit) |

### 11.3 Component Diagram Enhancements

| Enhancement | Rationale | Source Reference |
|-------------|-----------|-----------------|
| Add `SubagentManager` to Agent Layer | Parent-child agent orchestration | claude-code, opencode |
| Add `TaskDispatcher` to Agent Layer | Role-based task delegation | plandex (9 roles) |
| Add `ErrorBoundary` to Agent Layer | Structured error handling | codex (SafetyCheck) |
| Add `ModelRouter` to Provider Layer | Model selection + fallback | plandex, gemini-CLI |
| Add `ProviderCapabilities` to Provider Layer | Capability declaration per provider | codex |
| Add `FallbackChain` to Provider Layer | Circuit breaker + retry | goose (repetition monitoring) |
| Add `SubagentTool` to Tool Layer | Spawn child agents as tool | claude-code, opencode |
| Add `TodoTool` to Tool Layer | Task tracking within session | gemini-CLI (todos) |
| Add `MemoryTool` to Tool Layer | Persist/retrieve knowledge | goose (moim.rs) |
| Add `PlanTool` to Tool Layer | Plan creation + management | opencode (plan agent) |
| Add `SessionVersioning` to Session Layer | Snapshots + undo | opencode |
| Add `SessionSearch` to Session Layer | Cross-session search | hermes (FTS5) |
| Add `SessionFork` to Session Layer | Branch conversations | kimi-CLI |
| Add `SandboxExecutor` to Tool Layer | Sandboxed command execution | codex (landlock) |
| Add `SafetyPipeline` to Agent Layer | Multi-stage safety checks | hermes (10+ modules) |
| Add `PersonaLoader` to Agent Layer | Runtime persona switching | openinterpreter (8 personas) |

---

## 12. Lower Chain Cascade Impact

### 12.1 UC Layer Impact

| C4 Enhancement | UC Impact | New UCs Required |
|----------------|-----------|-----------------|
| ModelRouter container | PRV group expansion | PRV-03: ROUTE Model Selection, PRV-04: ROUTE Fallback |
| Subagent container | New AGT sub-group | AGT-13: DISPATCH Subagent Task, AGT-14: READ Subagent Result |
| Sandbox container | SAF group expansion | SAF-05: VALIDATE Sandbox Policy |
| Observability container | New OBS group | OBS-01: STREAM Structured Log, OBS-02: READ Trace |
| Memory container | New MEM group | MEM-01: INSERT Knowledge, MEM-02: READ Knowledge, MEM-03: SEARCH Knowledge |
| Git integration | New VCS group | VCS-01: READ Git Status, VCS-02: INSERT Commit, VCS-03: READ Diff |
| SubagentTool | TL group expansion | TL-15: DISPATCH Spawn Subagent |
| TodoTool | TL group expansion | TL-16: INSERT Todo, TL-17: UPDATE Todo, TL-18: READ Todos |
| MemoryTool | TL group expansion | TL-19: INSERT Memory, TL-20: READ Memory |
| PlanTool | TL group expansion | TL-21: INSERT Plan, TL-22: UPDATE Plan |
| SessionVersioning | SSN group expansion | SSN-05: INSERT Snapshot, SSN-06: ROLLBACK Session |
| SessionSearch | SSN group expansion | SSN-07: SEARCH Sessions |
| SessionFork | SSN group expansion | SSN-08: INSERT Fork |

### 12.2 SM Layer Impact

| C4 Enhancement | SM Impact |
|----------------|-----------|
| Subagent states | New subagent lifecycle: IDLE → RUNNING → COMPLETED → COLLECTED |
| Sandbox states | New sandbox lifecycle: UNRESTRICTED → SANDBOXED → BLOCKED |
| Session versioning | New snapshot lifecycle: ACTIVE → SNAPSHOTTED → RESTORED |

### 12.3 SQ Layer Impact

| C4 Enhancement | SQ Impact |
|----------------|-----------|
| ModelRouter | New SQ for model selection + fallback flow |
| Subagent spawning | New SQ for parent → child → result flow |
| Sandbox execution | New SQ for sandboxed tool execution |
| Observability | New SQ for log emission + trace correlation |
| Memory operations | New SQ for knowledge persist + retrieve |
| Git operations | New SQ for status check + commit flow |
| Session versioning | New SQ for snapshot + rollback flow |
| Session search | New SQ for cross-session search flow |
| Session fork | New SQ for conversation branching flow |

### 12.4 ERD Layer Impact

| C4 Enhancement | ERD Impact |
|----------------|-----------|
| Memory Store | New entity: `memory_entries` (id, scope, key, content, created_at) |
| Session Versioning | New entity: `session_snapshots` (id, session_id, snapshot_data, created_at) |
| Session Search | FTS5 virtual table for session content |
| Todo tracking | New entity: `todos` (id, session_id, description, status, created_at) |
| Git state | New entity: `git_state` (session_id, branch, status, last_commit) |

### 12.5 CL Layer Impact

| C4 Enhancement | CL Impact |
|----------------|-----------|
| SubagentManager | New class: `SubagentManager(parent_id, child_agents, nesting_level)` |
| TaskDispatcher | New class: `TaskDispatcher(roles, task_queue, active_tasks)` |
| ErrorBoundary | New class: `ErrorBoundary(error_type, message, recovery_action)` |
| ModelRouter | New class: `ModelRouter(strategies, fallback_chain, task_classifier)` |
| ProviderCapabilities | New class: `ProviderCapabilities(supports_streaming, supports_tools, max_tokens)` |
| FallbackChain | New class: `FallbackChain(providers, circuit_breakers, retry_policy)` |
| SafetyPipeline | New class: `SafetyPipeline(stages, scanners, confidence_threshold)` |
| PersonaLoader | New class: `PersonaLoader(personas, active_persona, switch_policy)` |
| MemoryStore | New class: `MemoryStore(scope, entries, search_index)` |
| SessionVersioning | New class: `SessionVersioning(snapshots, restore_policy)` |

### 12.6 CT/API Layer Impact

| C4 Enhancement | API Impact |
|----------------|-----------|
| ModelRouter | New endpoints: `GET /config/models`, `PATCH /config/models` |
| Subagent | New endpoints: `POST /sessions/{id}/subagents`, `GET /sessions/{id}/subagents/{sub}` |
| Memory | New endpoints: `POST /memory`, `GET /memory`, `GET /memory/search` |
| Git | New endpoints: `GET /sessions/{id}/git/status`, `POST /sessions/{id}/git/commit` |
| Session snapshots | New endpoints: `POST /sessions/{id}/snapshots`, `POST /sessions/{id}/snapshots/{snap}:restore` |
| Session search | New endpoints: `GET /sessions/search?q=...` |
| Todos | New endpoints: `POST /sessions/{id}/todos`, `PATCH /sessions/{id}/todos/{todo}` |

### 12.7 CT/DATA Layer Impact

| C4 Enhancement | Data Contract Impact |
|----------------|---------------------|
| Memory Store | New ODCS contract: `nasim_memory_store.datacontract.yaml` |
| Session Snapshots | Extend session contract with `snapshots` schema |
| Todos | New ODCS contract: `nasim_todo_store.datacontract.yaml` |
| Git State | Extend session contract with `git_state` schema |

---

## 13. Consistency Verification

### 13.1 Name Consistency Check

| Entity | C4 | UC | SM | SQ | ERD | CL | CT/API | CT/DATA | Status |
|--------|----|----|----|----|----|----|----|---------|--------|
| AgentOrchestrator | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| ConversationHistory | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| ContextCompactor | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| PermissionGate | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| PlanSession | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| AgentEvent | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | Consistent |
| Provider | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| ProviderFactory | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| ModelRouter | In entities | In entities | — | — | — | — | — | — | **NOT IN C4** |
| ToolRegistry | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| Tool (ABC) | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| ToolResult | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| SessionStore | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | Consistent |
| Session | ✓ | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | Consistent |
| ConfigLoader | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | Consistent |
| Config | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | Consistent |
| ServerApp | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | Consistent |
| ServerRouter | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | Consistent |
| SSEHandler | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | — | Consistent |
| APISchema | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | Consistent |
| HookManager | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |
| PluginLoader | ✓ | ✓ | — | ✓ | — | ✓ | — | — | Consistent |

### 13.2 Consistency Violations Found

| Violation | Layer Gap | Fix |
|-----------|----------|-----|
| ModelRouter in entities.md but not in C4 | C4 Container + Component | Add to C4 diagrams |
| SubagentManager not in any layer | All layers | Add to C4, UC, SQ, CL |
| TaskDispatcher not in any layer | All layers | Add to C4, UC, SQ, CL |
| ErrorBoundary not in any layer | All layers | Add to C4, UC, SQ, CL |
| MemoryStore not in any layer | All layers | Add to C4, UC, SQ, ERD, CL, CT |
| SessionVersioning not in any layer | All layers | Add to C4, UC, SQ, ERD, CL, CT |
| SessionSearch not in any layer | All layers | Add to C4, UC, SQ, CL |
| SessionFork not in any layer | All layers | Add to C4, UC, SQ, CL |
| SandboxExecutor not in any layer | All layers | Add to C4, UC, SQ, CL |
| SafetyPipeline not in any layer | All layers | Add to C4, UC, SQ, CL |
| PersonaLoader not in any layer | All layers | Add to C4, UC, SQ, CL |
| ProviderCapabilities not in any layer | All layers | Add to C4, UC, SQ, CL |
| FallbackChain not in any layer | All layers | Add to C4, UC, SQ, CL |

### 13.3 ID Consistency Check

| UC Group | UC Count in UC Layer | SQ Count in SQ Layer | Match |
|----------|---------------------|---------------------|-------|
| CLI | 6 | 4 | **MISMATCH** — 2 SQs missing |
| AGT | 8 | 8 | Match |
| LLM | 3 | 2 | **MISMATCH** — 1 SQ missing |
| TL | 12 | 12 | Match |
| PRV | 2 | 4 | **MISMATCH** — 2 SQs extra |
| CFG | 3 | 3 | Match |
| SSN | 4 | 4 | Match |
| SAF | 3 | 3 | Match |
| CTX | 2 | 3 | **MISMATCH** — 1 SQ extra |
| SRV | 6 | 6 | Match |
| HK | 3 | 4 | **MISMATCH** — 1 SQ extra |
| PLG | 2 | 1 | **MISMATCH** — 1 SQ missing |
| RTG | 2 | 2 | Match |

---

## Appendices

### Appendix A: Reference Agent Repository URLs

| Agent | Repository |
|-------|-----------|
| aider | https://github.com/Aider-AI/aider |
| amazon-q-developer-CLI | https://github.com/aws/amazon-q-developer-CLI |
| claude-code | https://github.com/anthropics/claude-code |
| claw-code | https://github.com/zed-industries/claw |
| CLI (OpenAI) | https://github.com/openai/openai-CLI |
| cline | https://github.com/cline/cline |
| codex | https://github.com/openai/codex |
| copilot-CLI | https://github.com/github/gh-copilot |
| crush | https://github.com/charmbracelet/crush |
| free-claude-code | https://github.com/steiner385/free-claude-code |
| gemini-CLI | https://github.com/google-gemini/gemini-CLI |
| goose | https://github.com/block/goose |
| grok-CLI | https://github.com/x-ai/grok-CLI |
| hermes-agent | https://github.com/harshit0209/hermes-agent |
| kilocode | https://github.com/Kilo-Org/kilocode |
| kimi-CLI | https://github.com/MoonshotAI/kimi-CLI |
| MiMo-Code | https://github.com/XiaomiMiMo/MiMo |
| mistral-vibe | https://github.com/mistralai/mistral-vibe |
| opencode | https://github.com/opencode-ai/opencode |
| OpenHands | https://github.com/All-Hands-AI/OpenHands |
| openinterpreter | https://github.com/OpenInterpreter/open-interpreter |
| plandex | https://github.com/plandex-ai/plandex |
| qwen-code | https://github.com/QwenLM/Qwen-Agent |
| Roo-Code | https://github.com/RooVetGit/Roo-Code |
| ruflo | https://github.com/ruvnet/ruflo |
| SkeletonAgent | https://github.com/firework8/SkeletonAgent |
| SWE-agent | https://github.com/SWE-agent/SWE-agent |
| warp | https://github.com/warpdotdev/Warp |

### Appendix B: C4 Enhancement Priority Matrix

| Enhancement | Effort | Impact | Priority | Phase |
|-------------|--------|--------|----------|-------|
| ModelRouter container | Low | High | P1 | Phase 1 |
| Subagent Spawner container | High | High | P1 | Phase 2 |
| Sandbox container | High | Critical (security) | P1 | Phase 2 |
| Observability container | Low | High | P1 | Phase 1 |
| Memory Store container | Medium | High | P2 | Phase 2 |
| Git Integration container | Low | Medium | P2 | Phase 1 |
| SessionVersioning component | Medium | Medium | P2 | Phase 2 |
| SessionSearch component | Low | Medium | P2 | Phase 2 |
| SessionFork component | Low | Low | P3 | Phase 3 |
| SafetyPipeline component | Medium | High | P2 | Phase 2 |
| PersonaLoader component | Low | Low | P3 | Phase 3 |
| ProviderCapabilities component | Low | Medium | P2 | Phase 1 |
| FallbackChain component | Medium | High | P2 | Phase 1 |
| SubagentTool component | Medium | High | P2 | Phase 2 |
| TodoTool component | Low | Medium | P3 | Phase 3 |
| MemoryTool component | Medium | High | P2 | Phase 2 |
| PlanTool component | Low | Medium | P3 | Phase 3 |
| ErrorBoundary component | Low | High | P1 | Phase 1 |
| TaskDispatcher component | Medium | High | P2 | Phase 2 |

### Appendix C: C4 Diagram Notation Compliance

| Check | Status | Notes |
|-------|--------|-------|
| C4-PlantUML library pinned to tag | ✓ | v2.10.0 used consistently |
| `!theme plain` after includes | ✓ | All diagrams |
| `LAYOUT_LEFT_RIGHT()` on context | ✓ | Context diagram |
| `skinparam linetype polyline` on complex diagrams | ✓ | Component diagrams |
| `SHOW_LEGEND()` present | ✓ | All diagrams |
| No `SHOW_DYNAMIC_LEGEND()` | ✓ | Compliant |
| No `LAYOUT_WITH_LEGEND()` | ✓ | Compliant |
| Structured header comment block | ✓ | All diagrams |
| No `note` blocks in C4 | ✗ | Component overview + server have notes — **VIOLATION** |
| No explanatory comments | ✗ | Some diagrams have `' this shows...` comments — **VIOLATION** |
| All names in PascalCase | ✓ | Consistent |
| All descriptions 2-3 lines max | ✓ | Context level |
| Element types correct | ✓ | Person, System_Ext, Container used correctly |

### Appendix D: Design Chain Frozen Status

| Layer | Status | Files | Notes |
|-------|--------|-------|-------|
| C4 | Frozen | 10 puml + README | Enhancement needed per this audit |
| UC | Frozen | 13 puml + README | New UCs needed for enhancements |
| SM | Frozen | 1 puml + README | New states needed for subagents |
| SQ | Frozen | 55 puml + README | New SQs needed for enhancements |
| ERD | Frozen | 1 puml + README | New entities needed |
| CL | Frozen | 1 puml + README | New classes needed |
| CT/DATA | Frozen | 2 yaml + README | New contracts needed |
| CT/API | Frozen | 1 yaml + README | New endpoints needed |
| RDM | Active | 10 md | Implementation roadmap |
