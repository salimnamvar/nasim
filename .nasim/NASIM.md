# nasim — Project Knowledge Base

> **Unified knowledge entry point for all registered agents.** This document defines project intent, design decisions, architectural patterns, and how agents should approach work in this project.

## Project Overview

**Name:** nasim  
**Description:** Research code agent. Original implementation built by investigating patterns across 25+ reference agents (aider, cline, SWE-agent, goose, OpenHands, plandex, opencode, codex, gemini-cli, kimi-cli, hermes-agent, and others) without copying any of them.  
**Purpose:** Credible first open-source artifact for personal brand → WAF Tech (Wadi Al Faiha Technologies) repositioning. Demonstrates full-cycle ownership from research and architecture to working code.

**Status:** v0.1 functional PoC + complete target design chain. Major capability gaps remain vs. reference corpus (see `docs/audit/`).

## How This Document Works

**NASIM.md is your entry point** — it loads in this order:

1. **Project-specific knowledge** — This file, plus `rules/` and `docs/` folders
2. **Global knowledge** — Via symlinks in `.nasim/global/` that point to the registered agent's shared knowledge
3. **Sub-agent coordination** — For specialized analysis, invoked via skills like `/code-review`, `/security-review`, etc.

### Knowledge Directory Structure

```
.nasim/
├── NASIM.md                              ← You are here
├── CORE-DIRECTIVE.md                     ← Symlink to agent's shared directive
├── global/                               ← Symlinks to shared knowledge
│   ├── rules → ~/.*/shared/rules/
│   ├── skills → ~/.*/shared/skills/
│   ├── commands → ~/.*/shared/commands/
│   ├── hooks → ~/.*/shared/hooks/
│   ├── docs → ~/.*/shared/docs/
│   ├── machines → ~/.*/shared/machines/
│   ├── templates → ~/.*/shared/templates/
│   └── tools → ~/.*/shared/tools/
├── rules/                                ← Project-specific rules
│   ├── entities.md                       ← Canonical entity registry
│   ├── anti-patterns.md                  ← Project-specific anti-patterns
│   └── software-design/                  ← Design-specific rules
├── docs/                                 ← Project documentation
├── skills/                               ← Project-specific skills (optional)
├── commands/                             ← Project-specific commands (optional)
└── .gitignore                            ← Excludes symlinks from git
```

## Loading Global Knowledge

When you see references like `@rules/code/python.md`, the agent loads them via `.nasim/global/`:

```
@rules/code/python.md → .nasim/global/rules/code/python.md → ~/.*/shared/rules/code/python.md
```

Symlinks automatically adjust to the running agent (Claude → ~/.claude/shared/, Grok → ~/.grok/shared/, etc.).

## Repository & Setup

- **URL:** Personal public GitHub: `salimnamvar/nasim`
- **License:** Apache-2.0 (chosen for permissive OSS + explicit patent grant suitable for agent research under a commercial services company)
- **Python Environment**

```
requires-python = ">=3.10"
```

No hard-coded conda env name. Use project setup scripts:

```bash
bash scripts/setup/setup_env.sh
pip install -e ".[dev]"
python -m nasim --help
python run.py
```

## Design Chain

All major layers documented. Current focus: close capability gaps while staying faithful to the architecture.

| Layer | Location | Status |
| ----- | -------- | ------ |
| C4 Architecture | `docs/c4/` | Complete (context → component) |
| Use Cases | `docs/uc/` | Complete — 42 UCs |
| State Machine | `docs/sm/` | Complete — agent lifecycle (9 states) |
| Sequence Diagrams | `docs/sq/` | Complete — 1:1 with UCs (42 diagrams) |
| Class / Runtime Model | `docs/cl/` | Complete |
| Entities | `docs/entities.md` | Complete |
| Implementation | `nasim/` + `run.py` | v0.1 PoC (hardcoded Ollama, minimal tools) |

```
C4 → UC → SM → SQ → ERD (minimal) → CL (runtime) → Code
```

No REST API, no CT contracts. Persistence is file-based (JSON sessions).

## Sub-Agent Workflows

This project may use specialized sub-agents for specific tasks:

### When Sub-Agents Are Used

- **Code Review:** Dedicated agents for reviewing changes against design contracts
- **Security Analysis:** Specialized agents for auditing capabilities and threat models
- **Research:** Agents for exploring dependencies, APIs, or architectural alternatives
- **Parallel Refactoring:** Breaking down large refactors across multiple focused agents

### Available Sub-Agent Commands

```
/code-review [level]          ← Spawn code review agent (low/medium/high/ultra)
/security-review              ← Spawn security audit agent
/explore <pattern>            ← Spawn code exploration agent
/research <question>          ← Spawn research agent
```

All sub-agent findings feed back to the primary agent for decision-making.

## Key Architectural Decisions (do not regress)

- Provider abstraction (protocol + factory) — current PoC is still OllamaClient only
- Tool registry with `safe` flag + PermissionGate (ask | auto | off)
- Event-driven agent loop (no print() inside core)
- Layered config (global/project/env/CLI)
- Session store under `~/.nasim/sessions/`
- Context compaction via secondary summarization
- Async-ready (httpx planned)

See `docs/README.md`, `docs/audit/audit_2026-06-20_capability-and-architecture.md`, and individual diagram READMEs for invariants.

## Current Gaps (from audit)

Tier-1 missing:
- Multi-provider abstraction
- Search/grep/glob/find tools (ripgrep or equivalent)
- Web fetch + web search
- Proper repo map / symbol awareness
- Safety/permission system
- Session resume / history
- Context management / compaction
- Config system
- Plan / approval UX
- MCP / extension tools

Implementation must follow the design docs. Do not extend the v0.1 PoC code as canonical.

## Active Rules

### Global Rules
From `@rules/` (shared via symlinks from `~/.claude/shared/rules/`):

| Rule | Applied when |
| ---- | ------------ |
| `@rules/code/python.md` | All Python (nasim/, scripts/, tests/) |
| `@rules/doc/markdown.md` | Documentation |
| `@rules/doc/readme.md` | README files |
| `@rules/software-design/*` | When touching C4/UC/SM/SQ/ERD/CL diagrams or contracts |

### Project Rules
Located in `.nasim/rules/`:

| Rule | Purpose |
| ---- | ------- |
| `entities.md` | Canonical entity registry (C4/UC/SM/SQ/CL/Code) |
| `anti-patterns.md` | Project anti-patterns (general + local) |
| `sprint.md` | Current sprint/focus (create when active) |
| `software-design/csr-project.md` | CSR pattern adapted for nasim CLI/Agent architecture |

## Authority of Design Documents

`docs/` (C4/UC/SM/SQ/CL), `docs/audit/`, `docs/entities.md`, and this file record **target intent and historical decisions**.

When the PoC code and design conflict, **design wins** until we explicitly update the design documents and audit notes.

When implementing or reviewing:
- Follow the documented component boundaries.
- Prefer clean abstractions (Provider, Tool, AgentOrchestrator, PermissionGate, Config, SessionStore) over quick hacks.
- Keep the CLI thin; agent core must be testable and event-yielding.
- Record deviations in sprint notes or a decision log.

## Available Skills

This project uses skills from both global knowledge and project-specific sources:

### Global Skills (`@skills/`)
- `/task` — Task creation and tracking
- `/code-review` — Code review (low/medium/high/ultra)
- `/security-review` — Security audit  
- `/conventional-commit` — Commit message helper
- `/simplify` — Code simplification suggestions

### Project Skills (`.nasim/skills/`)
- (None currently — add as needed)

## Development Commands

```bash
bash scripts/clean.sh
bash scripts/lint.sh
bash scripts/setup/setup_env.sh
python -m nasim --help
python run.py
```

## For Agents New to This Project

1. Read this NASIM.md top to bottom
2. Check `.nasim/rules/entities.md` — understand the domain model
3. Skim `docs/c4/` or `docs/architecture.md` — understand the design
4. Check `.nasim/rules/anti-patterns.md` — learn from past gotchas
5. Load relevant global rules for your task
6. Check `docs/decisions.md` or design docs for *why* things are the way they are

## KB Update Policy

Write to `.nasim/rules/` immediately on material decisions.

Do not accumulate — write immediately.

Last full sync: 2026-06-24T21:25:00+04:00
