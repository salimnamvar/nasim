# UC Layer Audit — Controller Layer Refactoring

**Date:** 2026-07-01
**Scope:** Controller Layer (`cli_adp`, `http_adp`, `mcp_adp`, `agent_ctrl`)
**Baseline:** C4 v13.0.0, docs/C4/c4_nasim_component.puml

---

## Issues Found and Resolved

### 1. [HIGH] CLIADP-06 DIRECT ACTOR ON EXTEND UC

**File:** `uc_cli_adp.puml:45`

**Observation:** `CLIADP-06 REQUEST Approval` was stereotyped `<<extend>>` but had a direct `User --> CLI06` actor association. This violates UC-008 from `uc_styles.puml` (line 89): "`<<extend>>` UCs must NOT have direct actor associations."

**Root cause:** The approval prompt was modeled as an independently invocable operation. In reality, it is triggered by the system during CLIADP-01 (REPL loop) when a tool requires safety approval. The user does not independently "request approval."

**Fix:** Removed `User --> CLI06` association. The UC remains `<<extend>>` of CLIADP-01, inheriting actor through the extend chain.

**Impact:** 1 SQ diagram (`sq_cli06_request_approval.puml`) may need review — if it shows User as the initiating actor, update to show Task Service or Agent Controller as initiator.

---

### 2. [HIGH] HTTP DIAGRAM MISMATCH — AC01_ext vs AC04_ext

**File:** `uc_http_adp.puml`

**Observation:** All 11 HTTP UCs included `AGENTCTRL-01 PROCESS Request` via `AC01_ext`, but the README routing table documented `AGENTCTRL-04 DISPATCH to Services` as the entry point.

**Architectural rationale:** HTTP REST requests are well-structured (paths, JSON bodies) and do not need protocol adaptation (AGENTCTRL-03) or the same validation pipeline as unstructured CLI input. Bypassing AGENTCTRL-01..03 for AGENTCTRL-04 is intentional.

**Fix:** Replaced `AC01_ext` with `AC04_ext` in the HTTP diagram. All 11 `<<include>>` relationships now point to `AGENTCTRL-04`.

---

### 3. [HIGH] MCP DIAGRAM — MISSING AC04_ext ENTRIES

**File:** `uc_mcp_adp.puml`

**Observation:** The README documented `MCPADP-02` and `MCPADP-03` as including `AGENTCTRL-04`, but the diagram only had `AC01_ext` (AGENTCTRL-01).

**Fix:** Added `AGENTCTRL-04` extref to the MCP diagram:
- `MCPADP-02 LIST nasim Tools` → `AC04_ext` (direct dispatch to TOOLSVC-14 via AGENTCTRL-04)
- `MCPADP-03 INVOKE nasim Tool` → `AC01_ext` + `AC04_ext` (process request, then dispatch)
- `MCPADP-01 PROCESS MCP Request` remains → `AC01_ext only`

---

## Duplication Analysis

### Cross-Adapter Patterns

| Behavior | CLI | HTTP | MCP | Resolution |
|----------|-----|------|-----|------------|
| Process input → delegate | CLIADP-01 → AC01 | HTTPADP-06 → AC04 | MCPADP-01 → AC01 | **By design** — each adapter delegates to `agent_ctrl`. Common logic extracted to service layer. |
| Stream events to client | CLIADP-03 (include) | embedded in HTTPADP-06 | MCPADP-04 (include) | **Minor inconsistency** — HTTP does not model streaming as a separate UC. Acceptable as SSE is inherent to HTTPADP-06. |
| List/expose tools | CLIADP-02 (slash) | HTTPADP-08..09 | MCPADP-02 | **By design** — each protocol exposes tools differently. Common logic in TOOLSVC-14. |

### Extracted Common Logic

Already in `agent_ctrl` (service layer):
- `AGENTCTRL-01 PROCESS Request` — routing
- `AGENTCTRL-02 VALIDATE Request` — validation
- `AGENTCTRL-03 ADAPT Protocol` — protocol adaptation
- `AGENTCTRL-04 DISPATCH to Services` — dispatch

All three adapters now consistently reference the correct entry point per their protocol needs.

---

## Remaining Observations

| Severity | Issue | File | Recommendation |
|----------|-------|------|---------------|
| Minor | HTTP has no explicit STREAM UC | `uc_http_adp.puml` | Consider adding `HTTPADP-12 STREAM Events` as `<<include>>` of HTTPADP-06 for diagram consistency with CLI/MCP |
| Minor | CLIADP-06 sq_diagram may need initiator review | `sq_cli06_request_approval.puml` | Verify the SQ diagram does not show User as initiator of approval |
| Info | All 24 C4 components have 1:1 UC coverage | — | 164 UCs total, unchanged by this refactoring |

---

## Summary

| Metric | Before | After |
|--------|--------|-------|
| UC count | 164 | 164 (unchanged) |
| Rule violations (UC-008) | 1 (CLIADP-06) | 0 |
| Diagram/README mismatches | 2 (HTTP, MCP) | 0 |
| Actor associations | 23 | 22 (−1: CLIADP-06) |
