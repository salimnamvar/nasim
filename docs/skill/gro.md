**I've created a dedicated, reusable skill for you: `sq-csr-rod-design`.**

It is now installed at:

```
/home/workdir/.grok/skills/sq-csr-rod-design/SKILL.md
```

(Validated — 236 lines, clean structure with `references/` folder ready for future expansion.)

### What the skill does
It gives any agent (or you) a **complete, enforceable rule set + workflow** for designing, writing, auditing, or fixing PlantUML sequence diagrams (`.puml` in `docs/SQ/`) that **strictly** follow:

- **Controller-Service-Repository (CSR)** layering (no God Objects, proper delegation)
- **Resource-Oriented Design (RoD)** + Google AIPs (especially AIP-193 errors, standard/custom methods, resource naming, pagination, states)
- **nasim project conventions** (from your SQ.md audit, C4.md component names, UC.md catalog, SM.md state hex colors, existing 149 diagrams as gold standard)

The skill encodes exactly the post-audit standards you already applied (e.g. SRV-06 rename, removal of phantom `AgentService`, mandatory `SafetyCoordinator` delegation, `ref` frames for cross-cutting, AIP-193 via `ErrorBoundary`, correct classification, hnote state markers, etc.).

### Key content highlights (from the skill)

**CSR Enforcement Rules**
- Controller = CLI Layer / SRV Layer / MCP runtime entrypoints only (parse → call Service → render/stream)
- Service = `AgentOrchestrator` **only** delegates to `SafetyCoordinator` (AGT-15), `ErrorBoundary` (AGT-14), `SubagentCoordinator`, `PersonaManager`, `ContextGraph`, `HookManager`. **Never** calls `PermissionGate`, `ToolRegistry`, or repos directly.
- Repository = Tool Layer + Session/Memory/Sandbox/RepoIntel/Git/Provider/EditStrategy/Evaluation/WireLog/etc.

**RoD / AIP Integration (mandatory where applicable)**
- All failure paths → `ErrorBoundary` → `map_to_aip_193(...)` → exact `{error: {code, message, status}}` payload (documented in summary note).
- Resource-oriented thinking even internally (Session, Tool, Plan, etc.).
- Standard methods (List/Get/Create/Update/Delete) preferred for CRUD-ish flows; custom methods for AGT-02, SRV-06, etc.
- Pagination fields shown on List operations.
- `hnote` with canonical SM hex colors on every state transition (IDLE #ECEFF1, THINKING #FFF3E0, TOOL_EXEC #F3E5F5, AWAITING_APPROVAL #FFF9C4, STAGING #F1F8E9, etc.).

**nasim SQ Conventions (non-negotiable)**
- Exact header block + title + classification (Primary Orchestrator / UC-level Sub-flow / Process Decomposition)
- Intro note (Scope / Preconditions / Excludes / Contexts / Rollback / Design / Classification)
- Proper `activate`/`deactivate`, `loop`/`alt`/`break`/`ref`, colored `box` layer groups
- Summary note with Flow / State (with `<back:#HEX>`) / Failure / Success / ROD errors
- `ref` frames for OBS-01, HK-02..05, AGT-15, CTX-01 (never inline)
- 1:1 UC↔SQ mapping (except known orphans reclassified as Process Decomposition)
- Cross-reference C4 component names exactly

**Workflow (step-by-step)**
1. Start from UC catalog → decide classification & actor presence.
2. Draw CSR layers in order (Controller box → Service box with delegates → Repository boxes).
3. Insert RoD error mapping + state hnotes + ref frames.
4. Write header/notes using the exact templates.
5. Run the 12-point mental audit checklist (no God Object, no phantom lifelines, title matches UC exactly, AIP-193 everywhere, etc.).
6. Version bump + update Review field.

**Anti-patterns it rejects**
- AgentOrchestrator calling PermissionGate/ToolRegistry directly
- Inlined hooks / logging / compaction instead of `ref`
- Wrong classification (actor on Process Decomposition, missing actor on Primary)
- Raw exceptions or ad-hoc strings instead of AIP-193 via ErrorBoundary
- Title/UC mismatches, phantom lifelines, missing state markers

It also includes a ready-to-copy **quick template** that already has the correct layer boxes, colors, `SafetyCoordinator`/`ErrorBoundary` participants, state hnote example, break + AIP-193 pattern, and summary note structure.

### How to use the skill going forward
- In any future conversation about nasim SQ diagrams (new ones, fixes, audits, UC→SQ mapping), simply reference or activate `sq-csr-rod-design`.
- It will force the output to be compliant with CSR + RoD + your existing inventory.
- You can also ask it to review one of your existing diagrams against the checklist or regenerate a specific `sq_*.puml` file.

The skill is self-contained but references your gold-standard examples (e.g. `sq_mcp01_connect_mcp_server.puml`, `sq_cli04_read_cli_arguments.puml`, `sq_hk02_dispatch_pre_tool_hook.puml`, `sq_sbx01_isolate_command.puml`) and your SQ/C4/UC/SM docs.

Would you like me to:
- Expand it with additional `references/` files (full color palette extraction, condensed AIP quick-ref card, or a linter-style checklist script)?
- Apply the skill right now to audit/fix one specific diagram from your set?
- Generate a brand-new SQ diagram for a pending UC using this skill?
- Create a companion PlantUML template file or Git hook?

Just say the word — the skill is ready and loaded for use. This gives you (and any future agent working on nasim) a deterministic, architecture-preserving way to keep all 149+ sequence diagrams at the high quality level you achieved in the Meta-Software Designer audit.