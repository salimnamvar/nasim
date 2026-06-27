# nasim — SQ Inventory (API-First)

Sequence diagrams organised by UC group. 148 diagrams across 21 groups.
Each diagram covers one UC's collaboration order, guards, alt paths, and rollback.

Back to [docs/](../README.md).

## API-First Convention

All SQ diagrams follow the API-First delegation chain:

```
User → [Interface Container] → API (ServerRouter) → AgentOrchestrator → Repository
```

- **Single actor:** `User` routes through `ServerRouter` (API Group)
- **No bypass:** No interface may call core services directly
- **CSR pattern:** Controller → Service → Repository
- **ROD AIP-193:** All failure paths use `{error: {code, message, status}}`

## Groups

| Group | Canonical (C4) Name | Boundary | Diagrams |
| ----- | :-----------------: | -------- | :------: |
| AGT | Agent | Agent Core — orchestrator, history, permissions, plans, subagents | 14 |
| CLI | CLI | CLI Interface Container — REPL, parsing, rendering | 8 |
| CFG | Config | Configuration — config loading and validation | 3 |
| CTX | ContextGraph | Context Management — token counting and compaction | 6 |
| EDT | EditStrategy | Edit Strategy — polymorphic edit strategies | 10 |
| EVL | Evaluation | Evaluation — task evaluation and quality checks | 9 |
| HK | Hooks | Hooks — pre/post hooks for tool and LLM lifecycle | 6 |
| MCP | MCP | Model Context Protocol — client/server extension tools | 4 |
| MEM | Memory | Memory — cross-session knowledge persistence | 4 |
| OBS | Observability | Observability — structured logging, metrics, trace correlation | 6 |
| PLG | Plugins | Plugins — plugin discovery, loading, registration | 6 |
| PRV | Provider | Provider Layer — provider abstraction, chat, streaming | 4 |
| RIM | RepoIntelligence | Repo Intelligence — codebase indexing, symbol graphs, embedding | 6 |
| RTG | Router | Model Router — model selection, fallback, routing | 4 |
| SAF | Safety | Safety — permission checks and user approval | 3 |
| SBX | Sandbox | Sandbox — OS-level process isolation | 4 |
| SRV | API | API Group (Entry Gate) — REST API, SSE streaming | 11 |
| SSN | Session | Session — persistence and resumption | 9 |
| TL | Tool | Tool Layer — all tool implementations | 22 |
| VCS | Git | Version Control — Git status, diff, commit | 4 |
| WRL | WireLog | Wire Log — append-only event store, fork, checkpoint | 5 |

**Total: 148 SQ diagrams across 21 groups**

## Naming Convention

SQ diagrams use canonical C4 group names for directories and file prefixes:

```
docs/SQ/{CanonicalGroup}/sq_{canonical_group}{nn}_{description}.puml
```

Examples:
- `docs/SQ/Agent/sq_agent01_process_user_task.puml`
- `docs/SQ/API/sq_api03_get_session.puml`
- `docs/SQ/Tool/sq_tool10_dispatch_tool_call.puml`

## SQ Diagram Convention

Each SQ diagram follows this structure:

1. **Header** — Title, boundary, purpose, version (9.1.0), source, review status
2. **Lifelines** — Single `User` actor, participants grouped by CSR layer (colored
   boxes)
3. **Body** — Collaboration order with activate/deactivate, alt/break/loop blocks,
   ref fragments
4. **hnote** — Minimal lifecycle state change annotations (hex colour + FROM → TO)

### Common Styles

All diagrams include `common/sq_styles.puml` for consistent CSR layer colours,
skinparam settings, and visual output across all 148 diagrams.
