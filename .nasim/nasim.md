# nasim — Unified Project Context

> **Entry point for all agents (Claude, Grok, MiMo).** Replaces legacy `.claude/CLAUDE.md`, `.grok/AGENTS.md`, `.mimo/MEMORY.md`.

## Project

**Name:** nasim  
**Description:** Research code agent. Original implementation built by investigating patterns across 25+ reference agents (aider, cline, SWE-agent, goose, OpenHands, plandex, opencode, codex, gemini-cli, kimi-cli, hermes-agent, and others) without copying any of them.  
**Purpose:** Credible first open-source artifact for personal brand → WAF Tech (Wadi Al Faiha Technologies) repositioning. Demonstrates full-cycle ownership from research and architecture to working code.

**Status:** v0.1 functional PoC + complete target design chain. Major capability gaps remain vs. reference corpus (see `docs/audit/`).

## Repository

- Personal public GitHub now: `salimnamvar/nasim`
- Planned move to company org (WAF Tech) later
- License: Apache-2.0 (chosen for permissive OSS + explicit patent grant suitable for agent research that will live under a commercial services company)

## Python Environment

```
requires-python = ">=3.10"
```

No hard-coded conda env name. Use project setup scripts or any Python 3.10+.

```bash
bash scripts/setup/setup_env.sh
pip install -e ".[dev]"
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

## Development Commands

```bash
bash scripts/clean.sh
bash scripts/lint.sh
bash scripts/setup/setup_env.sh
python -m nasim --help
python run.py
```

## KB Update Policy

Write to `.nasim/rules/` immediately on material decisions.

Do not accumulate — write immediately.

Last full sync: 2026-06-24T21:25:00+04:00
