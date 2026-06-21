# nasim — SQ Inventory

Sequence diagrams organised by UC group. 148 diagrams across 21 groups.
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
| SSN | Session — persistence and resumption | 8 | `SSN/` |
| TL | Tool Layer — all tool implementations | 22 | `TL/` |
| VCS | Version Control — Git status, diff, commit | 4 | `VCS/` |
| WRL | Wire Log — append-only event store, fork, checkpoint | 5 | `WRL/` |

**Total: 148 SQ diagrams across 21 groups**

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version, source, review status
2. **Lifelines** — Actors, participants grouped by layer (colored boxes)
3. **Intro Note** — Scope, Preconditions, Contexts, Excludes, Rollback, Design, Returns
4. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks
5. **Summary Note** — Flow summary, state transitions, success/failure paths, key invariants
