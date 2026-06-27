# nasim Design Chain — Team Rulebook & Task Assignment (2026-06-27)

**Objective:** Achieve a clean, consistent, and renderable design chain (C4 → UC → SM → SQ) with zero architectural defects and zero PlantUML rendering errors.

## Team Roles & Responsibilities

### 1. Tech Lead (Orchestrator)
- Maintain Kanban and assign focused tasks.
- Personally gate every batch.
- Decide on architectural deviations.
- Stop the loop only when **all** criteria below are met.

### 2. SQ Diagrammer
**Current Tasks:**
- Verify that **all 148 SQ diagrams render without errors** in PlantUML.
- Ensure every diagram has:
  - Proper `actor "User"`
  - Full entry chain through `ServerRouter`
  - CSR-coloured boxes using `common/sq_styles.puml`
  - No large `note over` blocks (already done)
- Fix any broken `ref` or lifeline declarations introduced during notes removal.

### 3. SM Modeller (Highest Priority Right Now)
**Critical Tasks:**
- Fix **initial and terminal states** in all 5 SM diagrams:
  - Every diagram must clearly show:
    - `[*] --> FirstRealState : UC-ID` (initial)
    - `LastRealState --> [*] : UC-ID` (terminal) where appropriate
  - `sm_agent_lifecycle.puml`: Resolve the dual role of `IDLE` as both start and end state. Either introduce a proper `TERMINATED` state or clearly document why `IDLE --> [*]` is acceptable.
  - `sm_subagent_lifecycle.puml`: Ensure consistent initial + terminal pattern.
- Re-validate that all state transitions are labeled with UC-IDs only.
- Ensure `common/sm_styles.puml` is correctly included and does not break rendering.
- Update `SM/README.md` transition matrices if any state changes were made.

### 4. C4 Architect
**Tasks:**
- Verify all 24 C4 diagrams render cleanly.
- Confirm `Container_Boundary` is used correctly in all component diagrams.
- Ensure `entities.md` is properly referenced in all headers.
- Fix any PlantUML errors in C4 diagrams.

### 5. UC Modeller
**Tasks:**
- Re-run full cross-reference checks (UC-ID consistency + matrix vs disk).
- Confirm no new broken references were introduced during SQ renames.

## Mandatory Validation Before Claiming "Done"

Before any specialist says a gate is ready, the following **must** pass:

1. **PlantUML Rendering Test**
   - Every modified `.puml` file must render without syntax errors or missing elements.

2. **SM Specific Checks**
   - All 5 SM diagrams must have clear, consistent **initial** (`[*] --> State`) and **terminal** (`State --> [*]`) transitions.
   - No state should be used as both a normal state and a terminal without clear justification.

3. **Linter + Cross-Reference**
   - Run all layer linters with `--strict`.
   - Run Appendix-A cross-reference scripts.
   - `entities.md` must exist and be referenced.

4. **Visual & Consistency**
   - All SQ diagrams use `common/sq_styles.puml`.
   - All SM diagrams use `common/sm_styles.puml`.
   - CSR colours are consistent.
   - No large `note over` blocks remain in SQ.

## Loop Rule

- Run in **non-stop iterations**.
- After every batch of fixes, re-validate the above 4 points.
- Only move to the next priority when the current specialist confirms **rendering + linter + SM state correctness** are clean.
- Tech Lead makes the final "Gate Closed" decision.

## Starting Point (Now)

**Priority 1 (Immediate):**  
SM Modeller must fix initial/terminal states + verify rendering in all 5 SM diagrams.

**Priority 2:**  
SQ Diagrammer must verify all 148 SQ diagrams render cleanly after notes removal and style inclusion.

Begin the loop now. Start with SM Modeller on the initial/terminal state issue.