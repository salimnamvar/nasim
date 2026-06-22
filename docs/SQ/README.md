# nasim — SQ Inventory (API-First)

Sequence diagrams organised by UC group. 148 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## API-First Convention

All SQ diagrams follow the API-First delegation chain:

```
User → [Interface Container] → API (ServerRouter) → AgentOrchestrator → Repository
```

- **Single Actor:** `User` (replaces Developer + HTTP Client)
- **Entry Gate:** All interface containers route through `ServerRouter` (API Group)
- **No Bypass:** No interface may call `AgentOrchestrator`, `SessionStore`, or any core service directly
- **CSR Pattern:** Controller (ServerRouter) → Service (AgentOrchestrator) → Repository (ToolRegistry, SessionStore, MemoryStore)
- **ROD AIP-193:** All failure paths use `{error: {code, message, status}}` format

## Groups

| Group | Boundary | Diagrams | Subdirectory |
| ----- | -------- | :------: | ------------ |
| AGT | Agent Core — orchestrator, history, permissions, plans, subagents | 14 | `AGT/` |
| CLI | CLI Interface Container — REPL, parsing, rendering (routes through API) | 8 | `CLI/` |
| CFG | Configuration — config loading and validation | 3 | `CFG/` |
| CTX | Context Management — token counting and compaction | 6 | `CTX/` |
| EDT | Edit Strategy — polymorphic edit strategies | 10 | `EDT/` |
| EVL | Evaluation — task evaluation and quality checks | 9 | `EVL/` |
| HK | Hooks — pre/post hooks for tool and LLM lifecycle | 6 | `HK/` |
| MCP | Model Context Protocol — client/server extension tools | 4 | `MCP/` |
| MEM | Memory — cross-session knowledge persistence | 4 | `MEM/` |
| OBS | Observability — structured logging, metrics, trace correlation | 6 | `OBS/` |
| PLG | Plugins — plugin discovery, loading, registration | 6 | `PLG/` |
| PRV | Provider Layer — provider abstraction, chat, streaming | 4 | `PRV/` |
| RIM | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 | `RIM/` |
| RTG | Model Router — model selection, fallback, routing | 4 | `RTG/` |
| SAF | Safety — permission checks and user approval | 3 | `SAF/` |
| SBX | Sandbox — OS-level process isolation | 4 | `SBX/` |
| SRV | API Group (Entry Gate) — REST API, SSE streaming | 11 | `SRV/` |
| SSN | Session — persistence and resumption | 9 | `SSN/` |
| TL | Tool Layer — all tool implementations | 22 | `TL/` |
| VCS | Version Control — Git status, diff, commit | 4 | `VCS/` |
| WRL | Wire Log — append-only event store, fork, checkpoint | 5 | `WRL/` |

**Total: 148 SQ diagrams across 21 groups**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version (7.0.0), source, review status
2. **Lifelines** — Single `User` actor, participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Classification, Design, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks
5. **Summary Note** — Flow summary, state transitions, success/failure paths, key invariants

## API-First Transformation (2026-06-23)

CAR refinement loop transforming nasim to API-First architecture.

### Changes Applied

| Layer | Change | Impact |
|-------|--------|--------|
| C4 Context | Single `User` actor replaces `Developer` + `HTTP Client` | All diagrams |
| C4 Container | 4 interface containers (CLI, WebApp, DesktopApp, MobileApp) → API → Backend | Architecture |
| C4 Component | Server Group renamed to API Group (Entry Gate) | Component diagrams |
| UC | CLI group reduced to 3 interface-only UCs; SRV renamed to API Group with 11 ROD UCs | UC diagrams |
| SM | All entry/exit transitions use `API-06` as sole entry gate | SM diagrams |
| SQ | All 148 diagrams: `Developer` → `User`, `HTTPClient` → `User`, version → 7.0.0 | SQ diagrams |

### Invariants Enforced

- **No Bypass:** No interface container may call core services directly
- **Single Entry:** `ServerRouter` is the sole entry gate for all business operations
- **CSR Chain:** Controller (ServerRouter) → Service (AgentOrchestrator) → Repository (ToolRegistry, SessionStore)
- **ROD Compliance:** All API interactions use standard methods or custom methods (AIP-136) with AIP-193 errors

### Cross-Layer Sync Results

- **C4 ↔ SQ:** All lifelines in SQ diagrams exist as C4 components ✓
- **UC ↔ SQ:** 148 UCs → 148 SQs — 1:1 mapping ✓
- **SM ↔ SQ:** All state transitions in SQs match valid SM transitions ✓
- **Method Consistency:** API-06, AGT-01, PRV-02 identical across layers ✓
- **API-First:** All entry chains go through ServerRouter ✓

### Design Chain Consistency: 100%
