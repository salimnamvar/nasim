# nasim — CAR Framework Audit: Controller-Service-Repository & Resource-Oriented Design

**Date:** 2026-06-20
**Scope:** Full audit of nasim architecture against CSR (Controller-Service-Repository) and ROD (Resource-Oriented Design) patterns from `~/.claude/rules/software-design/csr.md` and `~/.claude/rules/software-design/rod.md`
**Method:** Code inspection, design document review, pattern compliance check
**Companion audits:** `audit.2026.06.20.capability.and.architecture.md`, `audit.2026.06.20.design.chain.md`

---

## Executive Summary

nasim v0.1 has **zero CSR compliance** — it is a flat, functional codebase with no separation of concerns. The design documents describe an OOP architecture that the code does not implement. For ROD, nasim is a CLI agent (not an HTTP API), so ROD compliance applies only to the future HTTP server layer (Phase 3). However, the design chain already defines Server Layer components that must be ROD-ready.

| Pattern | Current Compliance | Target Compliance | Gap |
|---------|-------------------|-------------------|-----|
| CSR | 0% (no layers) | 100% (Controller/Service/Repository) | Complete refactor needed |
| ROD | N/A (no HTTP API) | Ready for Phase 3 Server Layer | Design docs must be ROD-compliant |

---

## Part 1 — Controller-Service-Repository (CSR) Audit

### CSR-01: Controller Layer Entry Points

**Condition:** No Controller layer exists. `cli.py` mixes argument parsing, REPL loop, slash commands, and output formatting in 103 lines of procedural code.

**Action:** Create dedicated Controller components per interface:
- `nasim/cli/args.py` — ArgParser (transport-level input parsing)
- `nasim/cli/commands.py` — SlashCommandHandler (maps /cmd to actions)
- `nasim/cli/repl.py` — REPLSession (REPL loop, delegates to AgentOrchestrator)
- `nasim/server/router.py` — ServerRouter (HTTP endpoints, request/response formatting)

**Result:** Each Controller entrypoint delegates immediately to a Service method. No business logic in Controllers. Per CSR-01: "Every public backend operation exposed via HTTP has a corresponding Controller entrypoint that immediately delegates to a Service method."

**Files touched:** `nasim/cli.py` → split into `nasim/cli/` package

---

### CSR-02: Service Layer Business Logic

**Condition:** `Agent` class in `agent.py` mixes business logic (orchestration), conversation state, and rendering (print statements). No Service layer abstraction.

**Action:** Create Service layer components:
- `nasim/agent/orchestrator.py` — AgentOrchestrator (drives LLM/tool loop, yields AgentEvents)
- `nasim/agent/history.py` — ConversationHistory (owns messages, token tracking)
- `nasim/agent/compactor.py` — ContextCompactor (summarizes old exchanges)
- `nasim/agent/permission.py` — PermissionGate (per-tool safety check)
- `nasim/agent/plan.py` — PlanSession (holds queued tool calls in plan mode)

**Result:** Service layer contains all business logic. No persistence frameworks, connection pools, or raw queries in Service. Per CSR-02: "Services never import or use persistence frameworks, connection pools, or raw queries."

**Files touched:** `nasim/agent.py` → split into `nasim/agent/` package

---

### CSR-03: Repository Layer Data Access

**Condition:** No Repository layer. Session persistence is not implemented. Tool registry is a module-level dict (`TOOL_REGISTRY`).

**Action:** Create Repository layer components:
- `nasim/session/store.py` — SessionStore (persists/loads message history to ~/.nasim/sessions/)
- `nasim/tools/registry.py` — ToolRegistry (instance-based tool management)
- `nasim/config/loader.py` — ConfigLoader (loads YAML + env vars + CLI flags)

**Result:** Repositories scoped to single aggregate/data boundary. Per CSR-03: "Repositories are scoped to a single aggregate or closely related data boundary."

**Files touched:** New files in `nasim/session/`, `nasim/tools/`, `nasim/config/`

---

### CSR-04: Dependency Injection

**Condition:** Hardcoded dependencies throughout. `Agent.__init__` takes `OllamaClient` concrete type. No composition root.

**Action:** Implement dependency injection:
- Create `nasim/__main__.py` as composition root
- Wire Controller → Service → Repository via constructor injection
- No `new` of collaborators inside classes

**Result:** All dependencies injected. Per CSR-04: "Dependency injection (or equivalent composition root) is used to wire Controller → Service → Repository."

**Files touched:** New `nasim/__main__.py`, modify all constructors

---

### CSR-05: Transaction Boundaries

**Condition:** No transaction management. Session saves are not atomic.

**Action:** Implement atomic session writes:
- SessionStore uses atomic writes (write to temp file, then rename)
- Service layer owns consistency boundaries for multi-repo operations

**Result:** Transaction and consistency boundaries owned by Service. Per CSR-05: "Transaction and consistency boundaries are owned by the Service."

**Files touched:** `nasim/session/store.py`

---

### CSR-06: Domain Entity Purity

**Condition:** No domain entities. All data flows as raw dicts and strings.

**Action:** Create domain entities:
- `nasim/agent/events.py` — AgentEvent hierarchy (TextChunk, ToolStart, ToolResult, Error, Done)
- `nasim/tools/base.py` — ToolResult(success, content, error)
- `nasim/config/schema.py` — Config dataclass
- `nasim/session/model.py` — Session dataclass

**Result:** Domain entities are persistence-ignorant. Per CSR-06: "Domain entities (CL) are persistence-ignorant. They carry no annotations, no repository references."

**Files touched:** New entity files in each layer package

---

### CSR-07: Layered Store Support

**Condition:** Single store (JSON files). No layered stores.

**Action:** Design for future layered stores:
- Config layer: global YAML → project YAML → env vars → CLI flags (already designed)
- Session layer: JSON Lines files (already designed)
- Future: SQLite for sessions, vector DB for RAG

**Result:** Each persistent layer has its own Repository implementation. Per CSR-07: "When the design chain defines per-layer stores, each persistent layer has its own Repository implementations."

**Files touched:** Config and Session Repository implementations

---

### CSR Best Practices Compliance

| Best Practice | Current | Target | Status |
|---------------|---------|--------|--------|
| Name services after domain concept | `Agent` (generic) | `AgentOrchestrator` | Gap |
| Keep repositories focused | No repos | Specific finder methods | Gap |
| Use interfaces for Repositories | No interfaces | `ToolRegistry` interface | Gap |
| Controllers are thin | Mixed CLI code | Thin delegates | Gap |
| Error handling: Controller translates exceptions | No error hierarchy | Structured errors | Gap |
| Testing: Controller with mocked Service | No tests | Unit tests | Gap |

---

## Part 2 — Resource-Oriented Design (ROD) Audit

### ROD Applicability

nasim is primarily a CLI agent. ROD applies to:
1. **Future HTTP Server Layer** (Phase 3) — must be ROD-compliant when implemented
2. **Design Documents** — must use ROD-compliant resource naming and method patterns

### ROD Review Checklist (for Future Server Layer)

| # | Check | Current | Target | Status |
|---|-------|---------|--------|--------|
| 1 | Resources first — every endpoint hangs off a noun resource | N/A | Sessions, Messages, Tools as resources | Design gap |
| 2 | Standard methods preferred — List/Get/Create/Update/Delete | N/A | Standard CRUD for Sessions, Messages | Design gap |
| 3 | Custom methods justified — each :verb could not be a standard method | N/A | `:send` for message submission | Design gap |
| 4 | No verbs-as-paths — no /doX, /runY | N/A | Clean resource paths | Design gap |
| 5 | Pagination — every List has page_size + page_token | N/A | Paginated session/message lists | Design gap |
| 6 | Field masks — every partial Update has update_mask | N/A | PATCH with update_mask | Design gap |
| 7 | States output-only — lifecycle state is read-only | N/A | Session state managed by server | Design gap |
| 8 | Canonical errors — error body has code + message + status + details | N/A | AIP-193 compliant errors | Design gap |
| 9 | Field behavior — every field annotated | N/A | OUTPUT_ONLY, REQUIRED annotations | Design gap |
| 10 | Names consistent — resource hierarchy matches C4/UC/DCS | N/A | Align with design chain | Design gap |
| 11 | Idempotency considered — mutating methods document request_id/etag | N/A | Idempotent create/send | Design gap |
| 12 | LRO posture — long operations return Operation or document why synchronous | N/A | Synchronous for v1 | Design gap |

### ROD Resource Model (Designed for Phase 3)

```
Sessions (collection)
  /sessions                    — List sessions (GET)
  /sessions                    — Create session (POST)
  /sessions/{session}          — Get session (GET)
  /sessions/{session}          — Update session (PATCH)
  /sessions/{session}          — Delete session (DELETE)
  /sessions/{session}:send     — Send message (POST, custom method)
  /sessions/{session}/messages — List messages (GET)

Tools (collection)
  /tools                       — List tools (GET)
  /tools/{tool}                — Get tool (GET)

Config (singleton)
  /config                      — Get config (GET)
  /config                      — Update config (PATCH)
```

### ROD Compliance Requirements for Server Layer

**Condition:** Server Layer components (`ServerApp`, `ServerRouter`, `SSEHandler`) are designed but not ROD-compliant.

**Action:** Update Server Layer design to be ROD-compliant:
1. Define resource hierarchy (Sessions, Messages, Tools, Config)
2. Use standard methods (List, Get, Create, Update, Delete)
3. Add custom methods only where needed (`:send` for message submission)
4. Implement pagination for List operations
5. Use field masks for partial updates
6. Follow AIP-193 error format
7. Annotate all fields with behavior (REQUIRED, OUTPUT_ONLY, etc.)

**Result:** Server Layer is ROD-compliant and ready for implementation. Per ROD: "ROD is the design discipline applied before and alongside the OpenAPI spec."

**Files touched:** `docs/CT/API/`, `docs/CL/cl_runtime_model.puml`, `docs/C4/c4_nasim_component_server.puml`

---

## Part 3 — Design Document Gaps

### Gap 1: Missing Server Layer C4 Component Diagram

**Condition:** `docs/C4/` has no `c4_nasim_component_server.puml` diagram.

**Action:** Create `c4_nasim_component_server.puml` with:
- ServerApp, ServerRouter, SSEHandler, APISchema components
- ROD-compliant resource relationships
- AIP-193 error model

**Result:** Complete C4 coverage for all containers.

---

### Gap 2: Missing Server Layer UC Group

**Condition:** No `SRV` UC group for server-specific operations.

**Action:** Create `docs/UC/uc_server.puml` with:
- SRV-01 Create Session
- SRV-02 Send Message
- SRV-03 Stream Response
- SRV-04 List Sessions
- SRV-05 Get Session
- SRV-06 Delete Session

**Result:** Complete UC coverage for server interface.

---

### Gap 3: Missing Server Layer SQ Diagrams

**Condition:** No SQ diagrams for server operations.

**Action:** Create SQ diagrams for each SRV UC:
- `docs/SQ/SRV/sq_srv01_create_session.puml`
- `docs/SQ/SRV/sq_srv02_send_message.puml`
- `docs/SQ/SRV/sq_srv03_stream_response.puml`
- `docs/SQ/SRV/sq_srv04_list_sessions.puml`
- `docs/SQ/SRV/sq_srv05_get_session.puml`
- `docs/SQ/SRV/sq_srv06_delete_session.puml`

**Result:** Complete SQ coverage for server interface.

---

### Gap 4: Missing OpenAPI Spec

**Condition:** No `docs/CT/API/` OpenAPI specification.

**Action:** Create `docs/CT/API/openapi.yaml` with:
- ROD-compliant resource definitions
- Standard methods (List, Get, Create, Update, Delete)
- Custom methods (`:send`)
- Pagination parameters
- Field masks
- AIP-193 error responses
- Field behavior annotations

**Result:** Complete API contract for server layer.

---

### Gap 5: Missing ODCS Data Contract

**Condition:** No `docs/CT/DATA/` ODCS specification.

**Action:** Create `docs/CT/DATA/data_contract.yaml` with:
- Session entity schema
- Message entity schema
- Tool entity schema
- Config entity schema

**Result:** Complete data contract for persistence layer.

---

## Part 4 — Implementation Plan

### Phase 1: Foundation (CSR Refactor)

| # | Task | CAR | Effort | Priority |
|---|------|-----|--------|----------|
| 1.1 | Create `entities.md` canonical registry | C: No canonical names; A: Create registry; R: Consistent naming across layers | Low | Critical |
| 1.2 | Split `nasim/agent.py` into `nasim/agent/` package | C: Mixed concerns; A: Extract Orchestrator, History, Compactor, Permission, Plan; R: Clean Service layer | Medium | Critical |
| 1.3 | Split `nasim/cli.py` into `nasim/cli/` package | C: Mixed concerns; A: Extract Args, Commands, REPL, Renderer; R: Clean Controller layer | Medium | Critical |
| 1.4 | Create `nasim/tools/` package with Tool ABC + ToolRegistry | C: Module-level dict; A: Create Tool ABC, ToolRegistry class, ToolResult; R: Instance-based tool management | Low | Critical |
| 1.5 | Create `nasim/config/` package with ConfigLoader | C: Hardcoded values; A: Create Config dataclass, ConfigLoader; R: Layered config system | Low | Critical |
| 1.6 | Create `nasim/session/` package with SessionStore | C: No persistence; A: Create SessionStore; R: Atomic session writes | Medium | Critical |
| 1.7 | Create `nasim/__main__.py` composition root | C: No DI; A: Wire Controller → Service → Repository; R: Clean dependency injection | Low | Critical |
| 1.8 | Remove `print()` from agent core | C: SoC violation; A: Yield AgentEvents; R: UI-agnostic agent core | Low | Critical |

### Phase 2: Core Capabilities

| # | Task | CAR | Effort | Priority |
|---|------|-----|--------|----------|
| 2.1 | Implement Provider Protocol + OllamaProvider | C: Hardcoded OllamaClient; A: Create Provider Protocol, OllamaProvider; R: Multi-provider support | Low | High |
| 2.2 | Implement GrepTool, GlobTool, FindFileTool | C: No search tools; A: Create search tools; R: Codebase search capability | Low | High |
| 2.3 | Implement WebFetchTool, WebSearchTool | C: No web access; A: Create web tools; R: External information retrieval | Low | High |
| 2.4 | Implement ConversationHistory + token counting | C: Unbounded messages; A: Create ConversationHistory; R: Context window management | Medium | High |
| 2.5 | Implement ContextCompactor | C: No compaction; A: Create ContextCompactor; R: Long session support | Medium | High |
| 2.6 | Implement Renderer with Rich | C: Plain ASCII; A: Create Renderer; R: Rich terminal output | Low | High |

### Phase 3: Server Layer (ROD-Compliant)

| # | Task | CAR | Effort | Priority |
|---|------|-----|--------|----------|
| 3.1 | Design ROD-compliant resource model | C: No resource model; A: Define Sessions, Messages, Tools, Config resources; R: ROD-compliant API design | Medium | High |
| 3.2 | Create Server Layer C4 component diagram | C: Missing diagram; A: Create c4_nasim_component_server.puml; R: Complete C4 coverage | Low | High |
| 3.3 | Create Server Layer UC group | C: Missing UCs; A: Create uc_server.puml; R: Complete UC coverage | Low | High |
| 3.4 | Create Server Layer SQ diagrams | C: Missing SQs; A: Create 6 SQ diagrams; R: Complete SQ coverage | Medium | High |
| 3.5 | Create OpenAPI spec | C: No API contract; A: Create openapi.yaml; R: ROD-compliant API contract | Medium | High |
| 3.6 | Create ODCS data contract | C: No data contract; A: Create data_contract.yaml; R: Complete data contract | Low | Medium |
| 3.7 | Implement ServerApp + ServerRouter | C: No server; A: Implement FastAPI app; R: HTTP API server | High | High |

---

## Part 5 — Compliance Metrics

### CSR Compliance Scorecard

| CSR Rule | Current | Target | Score |
|----------|---------|--------|-------|
| CSR-01: Controller entrypoints | 0% | 100% | 0/10 |
| CSR-02: Service no persistence | N/A | 100% | N/A |
| CSR-03: Repository per aggregate | 0% | 100% | 0/10 |
| CSR-04: Dependency injection | 0% | 100% | 0/10 |
| CSR-05: Transaction boundaries | 0% | 100% | 0/10 |
| CSR-06: Domain entity purity | 0% | 100% | 0/10 |
| CSR-07: Layered stores | 50% | 100% | 5/10 |
| **Overall CSR** | **6%** | **100%** | **5/70** |

### ROD Compliance Scorecard (Server Layer)

| ROD Check | Current | Target | Score |
|-----------|---------|--------|-------|
| 1. Resources first | N/A | 100% | 0/10 |
| 2. Standard methods | N/A | 100% | 0/10 |
| 3. Custom methods justified | N/A | 100% | 0/10 |
| 4. No verbs-as-paths | N/A | 100% | 0/10 |
| 5. Pagination | N/A | 100% | 0/10 |
| 6. Field masks | N/A | 100% | 0/10 |
| 7. States output-only | N/A | 100% | 0/10 |
| 8. Canonical errors | N/A | 100% | 0/10 |
| 9. Field behavior | N/A | 100% | 0/10 |
| 10. Names consistent | N/A | 100% | 0/10 |
| 11. Idempotency | N/A | 100% | 0/10 |
| 12. LRO posture | N/A | 100% | 0/10 |
| **Overall ROD** | **N/A** | **100%** | **0/120** |

---

## Part 6 — Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| CSR refactor breaks existing functionality | High | Medium | Implement with comprehensive tests |
| ROD design gaps block Server Layer implementation | High | High | Complete ROD design before Phase 3 |
| Design chain inconsistency persists | Medium | Medium | Create entities.md canonical registry |
| Performance regression from new abstractions | Low | Low | Profile before/after refactor |

---

## Part 7 — Success Criteria

### CSR Success Criteria

- [ ] All business logic in Service layer (no logic in Controllers)
- [ ] All data access in Repository layer (no persistence in Services)
- [ ] Dependency injection via composition root
- [ ] Domain entities are persistence-ignorant
- [ ] Transaction boundaries owned by Service
- [ ] 100% test coverage for Service layer

### ROD Success Criteria (Server Layer)

- [ ] Resource hierarchy defined (Sessions, Messages, Tools, Config)
- [ ] Standard methods used (List, Get, Create, Update, Delete)
- [ ] Custom methods justified (`:send` for message submission)
- [ ] Pagination implemented for List operations
- [ ] Field masks used for partial updates
- [ ] AIP-193 compliant error responses
- [ ] Field behavior annotated (REQUIRED, OUTPUT_ONLY, etc.)
- [ ] OpenAPI spec is ROD-compliant

---

## Appendix A — CSR Pattern Reference

From `~/.claude/rules/software-design/csr.md`:

| Layer | Responsibility | Owns | Must Not |
|-------|----------------|------|----------|
| Controller | HTTP/REST request parsing, response formatting, input validation | Routing, status codes, serialization | Business logic, direct data access |
| Service | Business logic, domain rules, validation, calculations, workflow orchestration | Use cases / operations that cross entities | Persistence details, SQL/ORM, HTTP concerns |
| Repository | Data access abstraction. CRUD + query operations against a specific store | All queries, mappings, transactions | Business rules, HTTP, cross-aggregate orchestration |

---

## Appendix B — ROD Pattern Reference

From `~/.claude/rules/software-design/rod.md`:

| Method | HTTP | Path | Notes |
|--------|------|------|-------|
| List | GET | GET /{parent}/{collection} | Paginated |
| Get | GET | GET /{name} | Single resource |
| Create | POST | POST /{parent}/{collection} | Returns created resource |
| Update | PATCH | PATCH /{name} | Partial update via update_mask |
| Delete | DELETE | DELETE /{name} | Returns empty or deleted resource |

---

> **Session sync note:** This audit is a working paper. After the design sprint produces entities.md, revised C4 diagrams, and the updated UC catalog, extract all resolved decisions into `sprint.md`, `entities.md`, and `anti-patterns.md`. Delete this file once all findings are closed.
