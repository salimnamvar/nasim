# nasim Design Chain — Team Rulebook

## Mandatory Validation (All Gates)

Before claiming any gate is ready, the following **must** pass:

1. **PlantUML Rendering Test** — All modified diagrams render with exit code 0.
2. **No Notes in SQ** — SQ diagrams contain no `note over` blocks.
3. **Proper CSR + ROD Flow** — SQ diagrams show full Actor → API → Controller → Service → Repository path with ROD method names.
4. **SM Initial/Terminal States** — All SM diagrams have correct `[*] -->` and `--> [*]`.
5. **Linter + Cross-Reference** — All relevant linters pass on `--strict`.

## Team Composition

- Tech Lead (Orchestrator)
- C4 Architect
- SM Modeller
- SQ Diagrammer
- UC Modeller
- **Evolutionizer** (runs after major batches to generalize rules)

**Current Priority:** SQ flow/ROD compliance + final SM rendering verification.