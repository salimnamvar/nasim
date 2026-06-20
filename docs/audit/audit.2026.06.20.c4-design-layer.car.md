# nasim — C4 Design Layer Deep Audit (CAR Framework)

**Date:** 2026-06-20
**Scope:** Full strict audit of C4 layer (Context → Container → Component) per global rules + project artifacts
**Framework:** CAR (Condition / Action / Result) + compliance tables + principle-by-principle checklist
**Method:**
- Canonical C4 linter (`~/.grok/tools/software-design/c4/c4_lint.py --strict`) on all 23 .puml files
- Manual review against `~/.grok/rules/software-design/c4.md`, `design-chain.md`, `cicd.md`, `anti-patterns.md`, `uc.md`, `csr.md`, `rod.md`
- Cross-reference: `docs/C4/README.md`, `docs/ENTITIES.md`, `docs/UC/README.md`, `docs/SM/...`, component inventory, container/context consistency
- Comparison to C4 model (https://c4model.com/), 2026 agentic architecture best practices (event-driven multi-interface, emit-only observability, first-class safety/sandbox/MCP/subagents, graph context, wire replay, plugin isolation)
- Evidence from diagrams + entity registry + prior corrective audits (p1.md, comprehensive.reference.audit.md, etc.)

**Target:** 10/10 C4 fidelity. Design is the contract; code will follow.

---

## Executive Summary

nasim has one of the most ambitious C4 designs among 2026 code agents: 3 deployable containers, 17+ logical component groups, 100+ UC groups mapped, explicit multi-interface (CLI + HTTP + MCP), event-driven core, full safety/sandbox/MCP/observability/memory/repo-intel/edit-strategy/eval/wire-log/context-graph modeled as first-class.

**Linter result (strict):** 213 violations, all from a single file — the cross-container "Component Overview" (`c4_nasim_component.puml`). All 18 dedicated per-group component diagrams pass with 0 violations. Context passes. Container has 1 medium.

**Verdict:** The *detailed* C4 component work (per-container groups) is excellent and follows rules. The *overview* artifact violates C4 level rules and PlantUML boundary macros. Other issues are mechanical (unpinned includes, version skew, double @enduml, minor inventory drift).

**Overall C4 Score:** 8.2/10 (detailed layers ~9.5/10, overview + mechanical 6/10). After fixes: 10/10.

Key gaps vs strict policy and 2026 practice:
- Overview diagram uses System_Boundary + raw Components (C2/C3 level violation).
- All diagrams use unpinned `master` include (policy: pin `v2.10.0`).
- C4 README inventory out of sync with actual diagrams present.
- One syntax error (double @enduml).
- Over-decomposition risk: many strategy/processor "components" are better as internal CL details.
- Minor name/desc drift and future tagging consistency.

The architecture itself (delegation, boundaries, actors, externals, tenas observability, subagent limits, MCP first-class, safety coordinator) is a 2026 reference-class model.

---

## 1. Full Rule & Principle Sources Audited

### 1.1 Core C4 Policy (`~/.grok/rules/software-design/c4.md`)
- Three levels only (Context, Container, Component).
- Naming: PascalCase, Manager/Adapter/Client/ABC suffix conventions.
- Registration: every component in `entities.md` before diagram use.
- Architecture pattern: Actor → (Gateway/API) → Manager → Adapter → Store/Process. One Manager per concern. No direct Manager→Store.
- Data layer boundaries explicit in Container diagram.
- Per non-trivial layer: dedicated component diagram.
- Strict PlantUML: pinned include (v2.10.0 recommended), `!theme plain`, `LAYOUT_LEFT_RIGHT()` on Context, tag-based legend + `LAYOUT_WITH_LEGEND()`, structured header comment block (Title/Boundary/Purpose/Milestone/Version/Source/Review), description length limits at Context, minimal comments (only section dividers), no explanatory notes except sparingly.
- Correct macros: `Person`/`System`/`System_Ext` (never `SystemDb_Ext` for non-DBs).
- All active entities from entities.md present; no orphans; names identical across C4 levels.
- Phase/future: use tags or explicit; prefer full target visible.
- Observability: emit-only + platform-owned (tenas) modeled outside app boundary.

### 1.2 Design Chain (`design-chain.md`)
- C4 is root. Component names propagate exactly to UC/SM/SQ/ERD/CL/CT/Code.
- Agent-specific patterns: event-driven (AgentEvent), Provider Protocol + Factory + Router + Fallback + Caps, Tool ABC + Registry (dynamic MCP), multi-interface containers, Safety-first (PermissionGate modes + Sandbox), ContextCompactor, SubagentCoordinator (limit 5), etc.
- Consistency invariant: same entity name/ID across every layer.
- Cascade: C4 change requires downstream updates.

### 1.3 CI/CD Gates (`cicd.md`)
- C4 gate: every actor/component named; API components explicit; data layers as distinct boundaries; every persistent layer backed by ERD+CL+CT/DATA; linter `--strict` must pass.
- Name consistency with entities.md; component boundaries own UC groups.

### 1.4 Anti-Patterns (relevant excerpts)
- No god objects (delegation via coordinators).
- No inlining across boundaries (ref in SQ, but C4 equivalent is proper boundary/relationship modeling).
- Self-documenting: structure + names speak; minimize prose.

### 1.5 Additional (project + global)
- RDM/00: 3 deployable units only (CLI, Server, Core Library). Single responsibility per group. No God Objects. MCP first-class. C4 fidelity.
- p1 corrective: reduced containers, introduced Safety/Subagent/Persona/Error coordinators, MCP group, full component inventory in overview, no orphan components.
- CSR/ROD: influences how Server + CLI controllers delegate to agent services (C4 models the services correctly).
- 2026 agentic best practices synthesized from references + modern patterns:
  - LLM as external System_Ext (multi-provider).
  - OS sandbox, plugin dir, git, lsp, memory, web as first-class externals.
  - Event-driven core with typed events (no I/O in agent).
  - Subagent isolation + nesting limits.
  - Emit-only structured logging + pull metrics (no agent push).
  - Context as graph + compaction + token budget + memory/repo injection (advanced RAG).
  - Wire log for replay/fork (determinism + debugging).
  - Edit strategy polymorphism + sandboxed diff staging.
  - Evaluation loop (LLM reviewer + success checks + repetition detection).
  - Safety as composed pipeline (permission + scanners).
  - MCP client/server/adapter/discovery first-class.
  - Multi-role/persona + plan mode.
  - Observability, memory, VCS, repo-intel as cross-cutting groups (not hidden).
  - Abstraction discipline: C4 components = architectural building blocks (coarse); fine strategies live in CL.

---

## 2. C4 Layer Audit by Level

### 2.1 Context Layer (`c4_nasim_context.puml`)

**Compliance:** Excellent. 0 linter violations.

**Actors (2):**
- Developer (Person)
- HTTP Client (Person)

**nasim System:** Correct single `System(nasim, ...)` with multi-interface description.

**External Systems (12+):**
- LLM Backend (multi-provider via litellm) — correct.
- Host Filesystem, Host Shell, Web, MCP Server, MCP Client, Git Repository, Sandbox Runtime, LSP Server, Plugin Directory.
- Observability Platform (with future_rel for emit path) — tenas pattern correct.

**Relationships:** Labeled with protocols ("terminal", "HTTP/JSON", "path operations", "stdio/SSE", "git CLI", "OS primitives", "LSP protocol").

**Findings vs Rules:**
- Header present but abbreviated (no full Milestone/Review in all fields).
- Uses `LAYOUT_LEFT_RIGHT()` + `LAYOUT_WITH_LEGEND()` + future tags — good.
- Include unpinned (`master`).
- No `SystemDb_Ext` misuse.
- All externals registered in ENTITIES.md.
- Descriptions concise (2-3 lines target met).
- Observability correctly external/platform-owned.

**CAR items later.**

### 2.2 Container Layer (`c4_nasim_container.puml`)

**Compliance:** Strong. 1 medium violation (OWN-002 on log agent edge).

**Containers (3 — correct per policy):**
- CLI (click + rich)
- HTTP API Server (FastAPI)
- Core Library (Python) — contains all groups

**Technology choices:** Visible and appropriate. Core owns agent/provider/tools/.../mcp/sandbox/obs/memory/git.

**Observability Platform boundary (outside nasim):** Log Agent, Loki, Prometheus, Grafana — correct tenas emit-only model. Relationships: stdout emit, pull /metrics, queries.

**Externals:** 12 modeled consistently with Context.

**Findings:**
- LAYOUT_LEFT_RIGHT + WITH_LEGEND good.
- Include unpinned.
- Medium: "LogAgent declared but no evidence of tailing" — relationship wording.
- Core Library correctly shown as the single place containing all component groups.
- No non-deployable "containers" (previous p1 violation fixed).

### 2.3 Component Layer

#### 2.3.1 Dedicated Per-Group Diagrams (18 files)

**Compliance:** 100% linter clean (0 violations each).

Groups (from overview + dedicated files + ENTITIES):
- Agent, Provider, Tools, MCP, Config, Session, Hooks, Plugins, Sandbox, Observability, Memory, Git, Repo Intelligence, Edit Strategy, Evaluation, Wire Log, Context Graph, CLI, Server, Subagent (some are collapsed or referenced via Container_Ext in siblings).

**Strengths (strict adherence):**
- Each uses `Container_Boundary("... Group" or "Process")` correctly inside C3 diagram.
- Components use Pascal names matching ENTITIES.md and UC owners.
- Relationships use clear labels; delegation visible (AgentOrchestrator → coordinators; ToolRegistry → *Tool; etc.).
- Cross-boundary shown via `Container_Ext` / `System_Ext`.
- Headers mostly complete (Title/Boundary/Purpose/Milestone/Version/Source/Review).
- Tech annotations in descriptions (pydantic, FastAPI, structlog) are acceptable at this level for key decisions.
- Advanced 2026 concerns modeled as first-class: subagent nesting limit, sandbox policy, wire log replay/fork, context graph pipeline stages, evaluation retry/repetition/turn budget, edit strategy polymorphism + diff sandbox, memory adapters (episodic/semantic/working), repo intel (AST + symbol graph + ranking + embeddings + repo-map), observability full pipeline (redactor, propagator, dual output, otel bridge).

**Issues (minor to moderate):**
- Include always `master` (policy violation).
- Version skew (5.0.0 vs 6.0.0).
- Some descriptions lean impl ("structlog + JSON").
- One diagram (server) has duplicate `@enduml`.
- Some groups (CLI/Server) appear primarily in dedicated files; overview does not use Container_Boundary for them.

#### 2.3.2 Cross-Container Component Overview (`c4_nasim_component.puml`)

**Compliance:** Critical failure. 212 HIGH violations (C4-C2-001 + C4-C3-001).

**Root cause:** Treats the overview as a C2/C3 hybrid:
- Uses `System_Boundary(group, "X Group")` (C2 containers live inside System_Boundary; C3 uses Components inside Container_Boundary).
- Places `Component(...)` directly inside those System_Boundary blocks.
- Linter expects either:
  - A pure documentation map (not validated as strict C4), or
  - Proper C3 structure (Container_Boundary inside the Core Library view).

**Other problems:**
- @startuml id `c4_nasim_component_overview` vs filename.
- Enormous file (many groups) — hard to maintain; duplicates all per-group content.
- Some data-ish elements (AgentEvent, HookResult, Config) modeled as Components with behavior notes.
- Many fine-grained strategies/processors (SearchReplaceCoder, DistillationProcessor, etc.) arguably belong only in CL or as internal notes.
- Despite violations, the *logical grouping and relationships* accurately reflect the target architecture and prior p1 fixes.

**Verdict on overview:** Valuable as architecture map, invalid as strict C4 diagram. Should be either removed from C4 validation path, converted to non-C4 PlantUML (or Markdown table + simple diagram), or rebuilt as a "Core Library Component Overview" using correct Container_Boundary nesting under a single Core container boundary.

#### 2.3.3 Name / Inventory Consistency

- ENTITIES.md is canonical and comprehensive. C4 component names match across dedicated diagrams.
- C4/README.md inventory is outdated (does not list Repo Intelligence, Edit Strategy, Evaluation, Wire Log, Context Graph, full sandbox sub-components).
- UC groups (CLI/AGT/PRV/CFG/SSN/SAF/CTX/SRV/HK/PLG/RTG/OBS/MEM/VCS/SBX/RIM/EDT/EVL/WRL) all have corresponding C4 component owners.
- No orphans reported in per-group files.
- Prior p1 "no orphan components" fix is intact in the model.

---

## 3. Principle-by-Principle Compliance Matrix (Strict)

| Principle (source) | Context | Container | Component (dedicated) | Overview | Status |
|--------------------|---------|-----------|-----------------------|----------|--------|
| 3 levels, correct macros | Pass | Pass | Pass | Fail (System_Boundary misuse) | Partial |
| Pinned include + theme + layout rules | Fail (master) | Fail | Fail | Fail | Fail |
| Structured header block | Partial | Partial | Mostly | Partial | Partial |
| Minimal comments / self-describing | Good | Good | Good | Overcrowded | Good |
| All names in entities.md first | Pass | Pass | Pass | Pass (but polluted) | Pass |
| Manager/Adapter (or equiv) per concern; no direct store | N/A | N/A | Pass (coordinators, registry, adapters) | N/A | Pass |
| One Manager per concern / no God | N/A | N/A | Pass (Safety/Subagent/Persona/Error split) | N/A | Pass |
| Dedicated component diag per group/layer | N/A | Good | Excellent (18) | N/A | Good |
| 3 deployables only | N/A | Pass (CLI/Server/Core) | N/A | N/A | Pass |
| Event-driven, UI-agnostic core | N/A | Pass | Pass (AgentEvent) | Pass | Pass |
| MCP first-class group | N/A | Pass | Pass | Pass | Pass |
| Emit-only observability (tenas) | Pass | Pass | Pass | Pass | Pass |
| Subagent limit + coordinator | N/A | Pass | Pass | Pass | Pass |
| Safety as coordinator/pipeline | N/A | Pass | Pass | Pass | Pass |
| Context graph + compaction + budget | N/A | Pass | Pass | Pass | Pass |
| Wire log / replay / fork | N/A | Pass | Pass | Pass | Pass |
| Edit strategy + sandbox diff | N/A | Pass | Pass | Pass | Pass |
| Evaluation (checks, LLM review, retry, repetition) | N/A | Pass | Pass | Pass | Pass |
| Repo intelligence full stack | N/A | Pass | Pass | Pass | Pass |
| Memory (3 scopes + adapters + RAG) | N/A | Pass | Pass | Pass | Pass |
| Multi-interface (CLI/Server/MCP) | Pass | Pass | Pass | Pass | Pass |
| No impl paths / file leakage | Pass | Pass | Pass | Pass | Pass |
| SQ/UC count invariants (via C4 owners) | N/A | N/A | N/A | N/A | Chain level (not C4) |
| Linter --strict gate | Pass | 1 med | Pass (all) | Fail | Fail (overview blocks) |

---

## 4. CAR Items (Condition / Action / Result)

### C4-OVERVIEW-01 — Overview diagram violates C4 level and boundary rules
**Condition:** `c4_nasim_component.puml` places Components inside System_Boundary blocks (212 high violations per linter). It is neither a valid C2 nor C3 diagram. It duplicates content of dedicated diagrams while breaking the model.
**Action:** 
1. Remove from strict C4 validation (move to `docs/architecture/` or rename to `logical-architecture-overview.puml` using plain PlantUML or Markdown).
2. Or rebuild as true C3 "Core Library Component Overview" using a top `Container_Boundary("Core Library")` containing the group `Container_Boundary`s (or collapse to high-level only).
3. Delete or deprecate the invalid file from docs/C4 if it will not be fixed; update C4/README and linter invocations.
**Result:** Linter passes on C4 dir. Design intent preserved in a non-C4 artifact. Maintainability improves.

### C4-STYLE-01 — Unpinned C4-PlantUML include across all diagrams
**Condition:** Every .puml uses `.../master/C4_...puml`. Policy requires a stable tag (e.g. v2.10.0) to prevent silent breakage.
**Action:** Replace in all 23 files (or use c4_fix.py extension if added). Add a one-line policy comment. Re-render key diagrams.
**Result:** Reproducible diagrams. Future-proof.

### C4-STYLE-02 — Version and milestone skew
**Condition:** Headers mix 5.0.0 / 6.0.0. Some lack full Review field.
**Action:** Standardize to current target (6.0.0 or 1.0.0 per RDM). Use consistent "Source" and "Review" paths. Run global replace + manual spot check.
**Result:** Traceable single source of truth.

### C4-SYNTAX-01 — Double @enduml in server diagram
**Condition:** `c4_nasim_component_server.puml` ends with two `@enduml`.
**Action:** Delete the duplicate line.
**Result:** Parsable file.

### C4-README-01 — C4 inventory stale
**Condition:** `docs/C4/README.md` lists fewer diagrams/groups than actually authored (missing RIM, EDT, EVL, WRL, CTX, full sandbox/edit/context-graph subcomponents). Per-group table incomplete.
**Action:** Regenerate inventory from ENTITIES.md + directory listing + dedicated diagram headers. Add row for the overview status (or mark it documentation-only).
**Result:** Accurate component inventory. New readers see the full 2026-scope design.

### C4-ABSTRACTION-01 — Potential over-decomposition at Component level
**Condition:** Many fine-grained items (SearchReplaceCoder, WholeFileCoder, DistillationProcessor, TokenBudgetTracker, etc.) are promoted to top-level Components. In pure C4 these may be implementation choices inside a parent component (e.g. EditStrategyManager or ContextGraph).
**Action:** Review each in dedicated diagrams. Move pure strategy/processor impl classes to CL only. Keep only the owning manager/adapter or the public "strategy selector" surface in C4 Component. Update ENTITIES.md + diagrams + downstream UC/SQ if names removed.
**Result:** C4 stays at architectural building-block granularity. CL captures polymorphism details.

### C4-CONTEXT-01 — Header and description polish
**Condition:** Context descriptions good but some externals (e.g. "Memory Backend") could be more precise; header not fully canonical format.
**Action:** Align header to the exact block template in c4.md. Tighten 1-2 descriptions.
**Result:** Uniform style.

### C4-CONTAINER-01 — Minor observability relationship wording
**Condition:** One medium linter note on LogAgent edge.
**Action:** Ensure explicit "tails stdout/stderr from Core/CLI/Server" relationship or accept as documentation artifact.
**Result:** Clean linter on container.

### C4-CONSISTENCY-01 — Cross-layer name drift risk (ongoing)
**Condition:** ENTITIES.md is excellent but some module paths listed may not yet exist (POC stage). C4 components (e.g. `DiffSandboxManager`, many *Adapter) must exactly match future code.
**Action:** On any C4 change: (a) update ENTITIES, (b) run `/design chain` or equivalent, (c) ensure SQ lifelines and CL use identical names.
**Result:** Zero drift when implementation begins.

### C4-FUTURE-01 — Future/phase visibility
**Condition:** Some future concerns use `$tags="future_rel"`. Observability platform is correctly marked. No [INACTIVE] stubs inside nasim boundaries (per policy preference for full target).
**Action:** Keep current approach. Add a short note in docs/C4/README or architecture decision log if any element is intentionally omitted from current milestone.
**Result:** Clean target architecture visible; phasing expressed outside diagrams.

---

## 5. 2026 Best Practices Coverage (Agentic Systems)

nasim C4 explicitly models or exceeds practices seen in top references (aider, claude-code, codex, gemini-cli, opencode, goose, plandex, etc.):

- Multi-provider + router + fallback + capabilities: covered.
- Event-sourced / event-driven agent core (no I/O in core): covered.
- Rich tool surface with ABC + dynamic registry (MCP): covered.
- OS-level sandbox + policy + monitor: covered (SBX).
- Subagent orchestration with limits + dedicated coordinator: covered.
- Structured memory (episodic/semantic/working) + retrieval: covered.
- Graph + symbol + embedding + repo-map context intelligence: covered (advanced).
- Multiple edit strategies + sandboxed staging + review: covered.
- Wire log (append-only, replay, fork): covered (rare, high value for determinism).
- Evaluation loop (checks + LLM-as-judge + retry + anti-repetition + budget): covered.
- Full observability as group + emit-only + correlation + redaction + dual output: covered (tenas).
- Hooks + plugins as first-class: covered.
- Safety pipeline (permission + scanners): covered.
- Multi-interface from one core (CLI + HTTP ROD + MCP): covered (unique strength).
- Git as first-class: covered.

Gaps vs ideal 2026 (mostly already in design, some execution risk):
- Explicit cost/token attribution on every external call (minor — can be added to OBS/Agent rels).
- Plugin/MCP security sandbox boundary (policy can be strengthened in SBX + PLG).
- Multi-tenant isolation if server mode grows (future).

No major architectural omissions.

---

## 6. Cross-Layer Cascade Notes (for when fixes land)

Any C4 change triggers (per cicd + design-chain):
- Update ENTITIES.md
- UC group ownership / new UCs if behavior added
- SQ lifelines (must reference exact component names)
- Downstream ERD/CL/CT only if new stores or entities introduced
- C4 README + audit docs
- Re-run linter + `/design chain`

Current state: C4 (except overview) is ready for downstream fidelity.

---

## 7. Recommendations & Phasing

**Immediate (before any code claiming C4 fidelity):**
1. Fix overview (C4-OVERVIEW-01) — highest impact.
2. Pin includes + fix double end + version normalize (STYLE-01/02, SYNTAX-01).
3. Regenerate C4 README inventory.
4. Re-run linter --strict until 0 violations on docs/C4.

**High (pre-implementation):**
5. Abstraction review (ABSTRACTION-01) — decide strategy granularity.
6. Confirm every C4 component has at least one owning UC ID in ENTITIES/UC README.

**Medium (during early code):**
7. Add any missing trace/cost relationships.
8. Ensure module paths in ENTITIES match final package layout.

**Result after above:** C4 layer passes all gates at 10/10. Design chain integrity from C4 root is sound.

---

## 8. Appendix: Linter Summary (2026-06-20)

```
Files: 23
Total violations: 213 (0 critical, 212 high from overview, 1 medium in container)
Passing strict (per-file): 22/23
Failing file: docs/C4/c4_nasim_component.puml (212)
```

Full per-file details captured in session logs + prior runs.

---

**End of C4 Deep Audit CAR.**

This document + the fixed diagrams + updated README + passing `--strict` linter = C4 layer complete and auditable at the highest standard.
