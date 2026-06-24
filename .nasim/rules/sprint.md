# nasim Sprint / Decisions

## Current Sprint: Design Chain Audit + Remediation

**Status:** C4 ✓, UC audit ✓, SM+SQ chain audit written (2026-06-20). Next: apply SQ/SM remediation.

**Target branch:** `feature/next`

---

## Design Layer Status

| Layer | Location | Status | Notes |
|-------|----------|--------|-------|
| C4 | `docs/C4/` | Complete | Context → Component; 5 diagrams |
| UC | `docs/UC/` | Audit complete | 151 UCs, 21 groups; 6.0.0 style applied |
| SM | `docs/SM/` | **Incomplete** | 1 of 4 required files; no state colors; 3 missing |
| SQ | `docs/SQ/` | **Incomplete** | 80 of 151 files; 71 missing; 35+ misnaming; structural violations |
| ERD | `docs/ER/` | Not Started | — |
| Class Diagram | `docs/CL/` | Complete (runtime) | `cl_runtime.puml` |
| DATA Contracts | `docs/CT/DATA/` | Not Started | — |
| API Spec | `docs/CT/API/` | Not Started | — |
| Implementation | `nasim/` | v0.1 PoC | Hardcoded Ollama, minimal tools |

---

## Open Decisions

| ID | Decision | Status |
|----|----------|--------|
| OD-SQ-01 | Does SRV layer need an explicit AgentService class to fix CSR-01, or does ServerRouter delegate directly to AgentOrchestrator with documented justification? | Open |
| OD-SQ-02 | TL/HK/SAF sub-flow SQs: UC-level sub-flow (with actor) or Process Decomposition (no actor)? | Open |
| OD-SQ-03 | Should OBS-03 CORRELATE Trace be ref'd at the start of every Primary Orchestrator SQ, or is it always implicit? | Open |
| OD-SM-01 | Should Agent SM remain a Process FSM (documented deviation) or be refactored to entity lifecycle SM? | Open |
| OD-SM-02 | Adopt proposed state color palette from sq-sm-chain audit doc as canonical? | Open |
| OD-SM-03 | Does Sandbox execution need its own SM, or captured by Agent FSM TOOL_EXEC → STAGING states? | Open |

---

## Resolved Decisions

| ID | Decision | Resolution |
|----|----------|------------|
| OD-01 | UC verb vocabulary | CAPS-only verbs from allowed list; no banned verbs |
| OD-02 | UC actor vocabulary | Developer + HTTPClient only; no internal components as actors |
| OD-03 | UC diagram style | tenas 6.0.0 skinparam; IDs embedded in labels |
| OD-04 | SQ note policy | Only intro (6 fields: Scope/Preconditions/Excludes/Contexts/Rollback/Design) + summary (4 fields: Flow/State/Failure/Success); no other notes |
| OD-05 | SQ break block policy | All terminal failure paths use break blocks |
| OD-06 | State annotation format | `<back:#HEX>STATE</back>` in summary note; hex codes from SM palette |

---

## SQ/SM Remediation Order (from audit.2026.06.20.sq-sm-chain.car.md)

**Priority 1 — SM color palette (prerequisite for all SQ state annotations):**
- Add skinparam state block + hex color per state to `sm_agent_lifecycle.puml`
- Add state description lines to every state
- Add transition labels with UC IDs
- Create `sm_session_lifecycle.puml`
- Create `sm_plan_lifecycle.puml`
- Create `sm_plugin_lifecycle.puml`
- Create `docs/SM/README.md`

**Priority 2 — SQ structural fixes on existing 80 files:**
- Rename 35+ SQ files to match UC operation names; update @startuml IDs
- Add intro note (6 fields) to all files missing it
- Add summary note (4 fields) to all files missing it
- Add box colors to all participants missing layer groupings
- Convert alt-for-terminal-paths to break blocks
- Add `<back:#HEX>STATE</back>` annotations where state changes occur
- Replace inline sub-flows with ref blocks (DRY)
- Add `ref SAF-01` at start of all tool SQ flows
- Add `ref CTX-06` after all history update ref blocks
- Add `ref OBS-03` at start of all Primary Orchestrator flows
- Remove extra "Returns:" from AGT-01 intro note (non-standard field)
- Mark Process Decomposition diagrams as such in intro note Contexts field

**Priority 3 — SRV group rebuild:**
- Delete `sq_srv01_start_server.puml` (not a UC)
- Delete `sq_srv04_stream_response.puml` (sub-flow, not standalone UC)
- Delete `sq_srv06_send_message.puml` (duplicate)
- Rebuild `sq_srv06_dispatch_message.puml` with AIP-193 errors, break blocks, CSR compliance
- Create `sq_srv07` through `sq_srv11`

**Priority 4 — Create 71 missing SQ files:**
- Create `docs/SQ/MCP/` + 4 files
- Create `docs/SQ/MEM/` + 4 files
- Create `docs/SQ/VCS/` + 4 files
- Create `docs/SQ/SBX/` + 4 files
- Fill per-group gaps (AGT-09..15, CLI-05..08, SSN-05..08, CTX-04..06, etc.)

**Priority 5 — Delete orphaned files:**
- `docs/SQ/LLM/sq_llm01_call_ollama_chat.puml`
- `docs/SQ/LLM/sq_llm02_stream_ollama_chat.puml`
- `docs/SQ/WRL/sq_wrl04_replay_session.puml`
- `docs/SQ/EDT/sq_edt05_review_diff.puml`

---

## Required SM Files

```
docs/SM/sm_agent_lifecycle.puml   ← Exists; needs skinparam colors + state descriptions
docs/SM/sm_session_lifecycle.puml ← MISSING
docs/SM/sm_plan_lifecycle.puml    ← MISSING
docs/SM/sm_plugin_lifecycle.puml  ← MISSING
docs/SM/README.md                 ← MISSING
```

---

## Next Focus Areas (implementation, post design-chain fix)

1. Provider abstraction (litellm)
2. Search/grep/glob tools
3. Web tools
4. Safety gates
5. Session persistence + resume
6. Config system
7. Context compaction

Record material decisions here immediately.
