# nasim — SQ Inventory

Sequence diagrams organised by UC group. 149 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## Groups

| Group | Boundary | Diagrams | Subdirectory |
| ----- | -------- | :------: | ------------ |
| AGT | Agent Core — orchestrator, history, permissions, plans, subagents | 15 | `AGT/` |
| CLI | CLI Layer — REPL, parsing, rendering | 8 | `CLI/` |
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
| SRV | HTTP Server — REST API, SSE streaming | 11 | `SRV/` |
| SSN | Session — persistence and resumption | 9 | `SSN/` |
| TL | Tool Layer — all tool implementations | 22 | `TL/` |
| VCS | Version Control — Git status, diff, commit | 4 | `VCS/` |
| WRL | Wire Log — append-only event store, fork, checkpoint | 5 | `WRL/` |

**Total: 149 SQ diagrams across 21 groups**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version, source, review status
2. **Lifelines** — Actors, participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Design, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks
5. **Summary Note** — Flow summary, state transitions, success/failure paths, key invariants

## Meta-Software Designer Audit (2026-06-21)

Cross-referencing all 6 reference agent prompt outputs (dee.md, mis.md, gro.md, qwe.md, cop.md, gem.md) against the existing 149 SQ diagrams. Key findings and fixes applied:

### Critical Fixes Applied

| Diagram | Violation | Fix |
|---------|-----------|-----|
| SRV-06 | Title "DISPATCH" mismatches UC catalog "SEND"; phantom `AgentService` lifeline | Renamed to SEND; removed AgentService; routes ServerRouter → AgentOrchestrator directly |
| MCP-01 | Missing actor; no ErrorBoundary; no AIP-193 errors | Added Developer actor + CLI entry chain; added ErrorBoundary; added AIP-193 error mapping |
| CLI-01 | Inlined agent loop logic instead of `ref` blocks | Replaced inlined logic with `ref` blocks for AGT-01, CLI-02, OBS-01 |
| AGT-02 | God Object: AgentOrchestrator calls PermissionGate directly | Delegated to SafetyCoordinator (AGT-15) which composes PermissionGate |
| AGT-05 | Orphan SQ with no UC entry | Reclassified as Process Decomposition (internal step of AGT-15) |
| TL-01 | Incorrect "Primary Orchestrator" classification; invalid actor | Changed to Process Decomposition; removed actor and CLI entry chain |
| PRV-02 | Incorrect "Primary Orchestrator" classification; invalid actor | Changed to UC-level Sub-flow; removed actor |

### Standards Enforced

- **CSR Pattern**: Controller (CLI/HTTP) → Service (Agent) → Repository (Tools/Session). No God Objects.
- **ErrorBoundary**: All failure paths terminate at ErrorBoundary (AGT-14). No inline error handling.
- **SafetyCoordinator**: All safety checks delegated to SafetyCoordinator (AGT-15). No direct PermissionGate calls from AgentOrchestrator.
- **SM State Colors**: `hnote` blocks with hex colors at state transition points during diagram flow.
- **ROD AIP-193**: All server-facing failure paths use `{error: {code, message, status}}` format.
- **ref Frames**: Cross-cutting concerns (OBS-01, AGT-15, HK-04/05) use `ref` blocks, never inlined.
- **Actor Rules**: Process Decomposition diagrams have no actor. UC-level Sub-flows have actor + entry chain.

### UC↔SQ Mapping

148 UCs in catalog, 149 SQ diagrams. AGT-05 is an orphan (no UC entry) — reclassified as Process Decomposition.
