# nasim Design Chain — Team Rulebook & Task Assignment (2026-06-27)

**Objective:** Achieve a clean, consistent, and renderable design chain (C4 → UC → SM → SQ) with zero architectural defects and zero PlantUML rendering errors.

## Team Roles

### Tech Lead (Orchestrator)
- Maintain Kanban and assign focused tasks.
- Personally gate every batch.
- Stop the loop only when **all** criteria below are met.

### SM Modeller (Current Highest Priority)
**Tasks:**
- Fix initial and terminal states in all 5 SM diagrams.
- Create full transition matrices in `SM/README.md`.
- Split SM palette from CSR colours.
- Extract common `sm_styles.puml`.
- Verify all SM diagrams render cleanly.

### SQ Diagrammer
**Tasks:**
- Verify all 148 SQ diagrams render without PlantUML errors.
- Normalise box colours to CSR palette.
- Ensure common `sq_styles.puml` is included in all files.

### C4 Architect
**Tasks:**
- Create missing `entities.md`.
- Move headers before `@startuml`.
- Fix legend mechanism.
- Verify all C4 diagrams render cleanly.

### UC Modeller
- Re-run cross-reference checks when requested by Tech Lead.

## Mandatory Validation Before Claiming "Done"

Before any specialist says a gate is ready, the following **must** pass:

1. **PlantUML Rendering Test** — Every modified `.puml` renders without errors.
2. **SM Specific Checks** — Clear initial (`[*] --> State`) and terminal (`State --> [*]`) transitions in all 5 SMs.
3. **Linter + Cross-Reference** — All layer linters pass + Appendix-A scripts return 0 errors.
4. **Common Styles** — All SQ and SM diagrams include their respective common style files.

## Loop Rule

Run in **non-stop iterations**. Only move to the next priority when the current specialist confirms **rendering + linter + correctness** are clean. Tech Lead makes the final decision.

**Starting Priority (Now):** SM Modeller on initial/terminal states + rendering.