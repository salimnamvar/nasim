# nasim — Pairwise Audit vs 28 Reference Agents

**Date:** 2026-06-20
**Scope:** nasim (post p1.md corrections) vs all 28 reference agents
**Framework:** CAR (Context, Action, Result)

---

## Scorecard

| Verdict | Count | Agents |
|---------|-------|--------|
| **nasim wins** | 19 | aider, cline, SWE-agent, kimi-cli, hermes-agent, crush, Roo-Code, amazon-q, copilot-cli, mistral-vibe, qwen-code, warp, claw-code, SkeletonAgent, free-claude-code, grok-cli, cli (Ampersand), openinterpreter (partial) |
| **Agent wins** | 9 | claude-code, codex, gemini-cli, opencode, goose, plandex, kilocode, MiMo-Code, ruflo |

---

## Pairwise Comparison

| Agent | nasim Pros | nasim Cons | Verdict |
|-------|-----------|------------|---------|
| **aider** | MCP, plugin system, HTTP API, event-driven core, session persistence, multi-interface, plan mode | aider has 14 edit-format strategies, litellm 100+ providers, auto-commit git, repo-map, 4-layer config, background compaction | **nasim wins** |
| **claude-code** | Open-source, lightweight Python, cleaner C4, MCP+HTTP API, plan mode | Plugin marketplace, 5-level subagent nesting, 9 hook events, daemon sessions, enterprise MDM, skills auto-activation | **claude-code wins** |
| **codex** | Python simplicity vs 124-crate Rust, multi-interface, plan mode, plugin system | OS-level sandboxing (landlock/seccomp), remote compaction, trait-object polymorphism, app-server daemon, skills | **codex wins** |
| **gemini-cli** | Multi-provider (not locked to Google), MCP, plugin system, simpler | Graph-based context, voice input, A2A server, 20+ tools, 9 hooks, Docker sandbox, sub-agents, skills | **gemini-cli wins** |
| **opencode** | Python simplicity vs Effect-TS, cleaner architecture, multi-interface, plan mode | Event-sourced SQLite sessions, 13 providers, LSP as tool, snapshot/undo, background subagents, Hono server | **opencode wins** |
| **goose** | Multi-interface vs extension-only, cleaner separation, plan mode, plugin system | ML-based prompt injection, OpenTelemetry, extensions-as-MCP, moim.rs memory, ACP, scheduler | **goose wins** |
| **cline** | Multi-interface vs VS Code-only, plan mode, event-driven, MCP, standalone | Deep VS Code integration, 5 SDK packages, subscription billing, ClineHub remote/team | **nasim wins** |
| **SWE-agent** | Persistent sessions, MCP, plugins, event-driven, config, compaction, safety, multi-interface | Retry-with-review loop, Docker sandbox, cost tracking, minimal abstractions | **nasim wins** |
| **plandex** | MCP, plugins, subagents (designed), multi-interface, event-driven, simpler | 9 specialized roles, plan branching/versioning, 2M token context, tree-sitter, diff sandbox | **plandex wins** |
| **kimi-cli** | Multi-interface, plugin system, HTTP API, plan mode, richer hooks | Wire pub/sub, agent spec inheritance, session fork, LaborMarket subagent, DMail | **nasim wins** |
| **hermes-agent** | Clean decomposition vs monolithic 12k LOC, multi-interface, plugins, plan mode | 20+ platform gateway, 40+ tools, SQLite FTS5 search, 10+ safety modules, Electron desktop | **nasim wins** |
| **openinterpreter** | Independent design vs Rust fork, multi-interface, MCP, plugins, plan mode | Harness persona swapping (8+), OS-level sandbox, ACP server, code-mode | **openinterpreter wins** |
| **crush** | Multi-interface vs Unix-socket, plan mode, plugins, hooks | LSP integration, Charm TUI, mid-session model switch, todo tracking, hot-reload hooks | **nasim wins** |
| **kilocode** | Unique C4 design chain, multi-interface, plan mode, not a fork | 500+ models, broadest IDE surface, i18n (20+ languages), Effect-TS, mid-task switch | **kilocode wins** |
| **Roo-Code** | Multi-interface vs VS Code-only, plan mode, event-driven, plugins, standalone | Role-based modes (.roomodes), deep VS Code, community-driven, session versioning | **nasim wins** |
| **amazon-q** | Provider-agnostic vs AWS lock-in, multi-interface, MCP, plan mode, open-source | Deep AWS integration (SSO/Cognito), semantic search, CLI+GUI, Rust performance | **nasim wins** |
| **copilot-cli** | Open-source vs closed-source binary, MCP, plugins, multi-interface, plan mode | Official GitHub product, native GitHub auth, Autopilot mode, multi-model | **nasim wins** |
| **MiMo-Code** | Unique C4 design chain, multi-interface, cleaner architecture, not a fork | Persistent memory, self-improving loop, Slack integration, MiMo Auto free channel | **MiMo-Code wins** |
| **mistral-vibe** | Multi-provider vs Mistral-only, multi-interface, session persistence, safety, richer tools | ACP protocol, voice input, PyInstaller, Textual TUI, OpenTelemetry | **nasim wins** |
| **qwen-code** | Multi-interface with clean architecture vs IM-bot architecture, plan mode, plugins, hooks | Richest surface (CLI+Desktop+Daemon+IDE+5 IM bots), Auto-Memory, Auto-Skills, Agent Teams | **nasim wins** |
| **warp** | Focused agent vs full terminal stack (AGPL), multi-interface, MCP, plugins, Apache-2.0 | GPU-accelerated terminal, GraphQL, OpenTelemetry, workflow engine, cloud sync | **nasim wins** |
| **claw-code** | Direct implementation vs meta-harness, full design chain, MCP, plugins, multi-interface | Orchestrates other agents, vim mode, voice, plugins, skills, hooks | **nasim wins** |
| **ruflo** | Single-agent with clean design vs enterprise complexity (60+ agents), MCP, plugins | 60+ agents, 34 plugins, swarm coordination, self-learning memory, vector store | **ruflo wins** |
| **SkeletonAgent** | Full coding agent vs action recognition research | (different domain) | **nasim wins** |
| **free-claude-code** | Full agent vs proxy middleware | (not an agent) | **nasim wins** |
| **grok-cli** | Multi-provider vs xAI lock-in, MCP, plugins, plan mode | X/Twitter search, Telegram remote control, Batch API, sub-agents | **nasim wins** |
| **cli (Ampersand)** | AI agent vs traditional B2B CLI | (different domain) | **nasim wins** |

---

## Key Patterns

### nasim wins against:
- **Non-agents** (SkeletonAgent, free-claude-code, cli)
- **Single-interface/IDE-locked** (cline, Roo-Code)
- **Provider-tightly-coupled** (amazon-q, copilot-cli, grok-cli, mistral-vibe)
- **Monolithic/forked** (hermes, claw-code)
- **Simple/minimal** (aider, SWE-agent, kimi-cli, crush)

### nasim loses against:
- **OS-level sandboxing** (codex, openinterpreter)
- **Graph-based context** (gemini-cli)
- **Event-sourced sessions + Effect-TS** (opencode)
- **ML-based safety** (goose)
- **Marketplace ecosystem** (claude-code)
- **Multi-role orchestration + plan branching** (plandex)
- **Broadest model support + IDE surface** (kilocode)
- **Persistent memory + self-improvement** (MiMo-Code)
- **Swarm coordination** (ruflo)

---

## nasim Competitive Position

### Core Strengths (surpass all references)
1. **Multi-interface architecture** — CLI + HTTP API + MCP from one core (no other agent does this cleanly)
2. **Provider-agnostic** — 100+ providers via litellm (vs aider's litellm, but nasim adds HTTP+MCP)
3. **Complete design chain** — C4 → UC → SM → SQ → ERD → CL → CT (no reference agent has this)
4. **Python simplicity** — Clean component decomposition vs Rust/TypeScript complexity
5. **Open-source Apache-2.0** — vs closed-source (copilot-cli) or AGPL (warp)

### Top 6 Gaps (from agents that beat nasim)
1. **OS-level sandboxing** (codex, openinterpreter) — nasim needs SandboxExecutor
2. **Memory persistence** (MiMo-Code, goose) — nasim needs MemoryStore
3. **Subagent spawning** (claude-code, opencode, gemini-cli) — nasim needs SubagentCoordinator
4. **Structured logging/telemetry** (goose OpenTelemetry) — nasim needs observability pipeline
5. **Plan branching/versioning** (plandex) — nasim needs enhanced PlanSession
6. **Graph-based context** (gemini-cli) — nasim needs context graph model

---

## Recommended C4 Enhancements to Close Gaps

| Gap | Source Agent | C4 Impact | Priority |
|-----|-------------|-----------|----------|
| OS-level sandbox | codex, openinterpreter | Sandbox Group already in C4 — needs implementation | P1 |
| Memory persistence | MiMo-Code, goose | Memory Group already in C4 — needs implementation | P1 |
| Subagent spawning | claude-code, opencode | SubagentCoordinator already in C4 — needs implementation | P1 |
| Observability pipeline | goose | Observability Group already in C4 with tenas pattern — needs implementation | P1 |
| Plan branching | plandex | Enhance PlanSession component | P2 |
| Graph-based context | gemini-cli | Enhance ContextCompactor component | P2 |
