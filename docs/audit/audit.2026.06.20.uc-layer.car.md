# UC Layer Audit — CAR Framework

**Date:** 2026-06-20
**Scope:** `docs/UC/` — Use Case diagrams vs C4 component layer vs tenas reference style
**Reference Style:** `tenas_infrastructure/services/model_management/docs/UC/`
**Auditor:** Claude Code (Sonnet 4.6)

---

## Challenge

The nasim UC layer (`docs/UC/`) was authored across multiple audit iterations and
improvement plans. It has accumulated 17 UC diagram files covering ~18 UC groups and
100+ UC entries in `README.md`. The C4 component layer defines 20+ container groups
with named components. The challenge is to establish whether the UC layer is:

1. **Complete** — every C4 component group has a corresponding UC diagram; every UC in
   `README.md` is represented in a diagram file
2. **Consistent** — UC naming, ID format, verb vocabulary, actor usage, and diagram
   structure are uniform across all files
3. **Visually coherent** — diagrams match the reference style (tenas) for actor
   styling, use case formatting, skinparam blocks, titles, and zero notes
4. **Architecturally sound** — actors are external entities only; groups do not
   duplicate each other's responsibility; overview diagram exists

---

## Action

### Step 1 — C4 Group Inventory vs UC Diagram Files

Extracted all Container_Boundary groups from `c4_nasim_component.puml` and mapped
against existing UC diagram files:

| C4 Group | Expected UC File | Status |
|---|---|---|
| Agent Group (AgentOrchestrator, etc.) | `uc_agent.puml` | Present |
| Provider Group (Provider, ModelRouter, etc.) | `uc_provider.puml` | Present |
| Tool Group (FileTools, SearchTools, etc.) | `uc_tools.puml` | Present |
| MCP Group (MCPClientRuntime, MCPServerRuntime) | — | **MISSING** |
| Config Group (ConfigLoader, Config) | `uc_config.puml` | Present |
| Session Group (SessionStore, SessionVersioning, etc.) | `uc_session.puml` | Present |
| Server Group (ServerApp, ServerRouter, SSEHandler) | `uc_server.puml` | Present |
| Hooks Group (HookManager, Hook) | `uc_hooks.puml` | Present |
| Plugins Group (PluginLoader, PluginManifest) | `uc_plugins.puml` | Present |
| Sandbox Group (SandboxExecutor, etc.) | — | **MISSING** |
| Observability Group (StructuredLogger, etc.) | `uc_observability.puml` | Present |
| Memory Group (MemoryStore, MemoryIndex, etc.) | — | **MISSING** |
| Git Group (GitIntegration, GitStatus, GitCommit) | — | **MISSING** |
| Repo Intelligence Group | `uc_repo_intelligence.puml` | Present |
| Edit Strategy Group | `uc_edit_strategy.puml` | Present |
| Evaluation Group | `uc_evaluation.puml` | Present |
| Wire Log Group | `uc_wire_log.puml` | Present |
| Context Graph Group | `uc_context.puml` | Present |
| LLM Group (OllamaProvider) | — | **MISSING** |
| Model Router Group | `uc_router.puml` | Present |
| Safety/Permission (PermissionGate) | `uc_safety.puml` | Present |
| **Overview** | — | **MISSING** |

**Summary: 5 missing diagram files + missing overview.**

---

### Step 2 — UC Naming Consistency Audit

Reviewed all 17 diagram files for verb adherence to the global rule (`uc.md`):
allowed verbs are `INSERT READ UPDATE DELETE VALIDATE ENABLE DISABLE ACTIVATE
RETIRE ROLLBACK APPLY SET RELOAD SEARCH FETCH STREAM PROCESS DISPATCH CHECK
COMPACT QUEUE APPROVE SPAWN COLLECT DELEGATE LOAD SWITCH LIST INDEX RANK INJECT
INVALIDATE EXTRACT SELECT APPLY VALIDATE STAGE REVIEW REVERT RUN RECORD
COORDINATE DETECT REGISTER DISCOVER APPEND SEEK FORK CHECKPOINT REPLAY BRANCH
SNAPSHOT RESTORE REDACT EXPOSE`.

Banned verbs: `CREATE GET EXECUTE INVOKE PERFORM TRIGGER RUN`.

Found violations:

| File | UC | Verb Used | Violation |
|---|---|---|---|
| `uc_agent.puml` | UC_AGT_03 | `Manage Conversation` | No verb prefix at all |
| `uc_agent.puml` | UC_AGT_04 | `Reset History` | `RESET` not in allowed list |
| `uc_agent.puml` | UC_AGT_07 | `Queue Plan` | `QUEUE` uncapitalized |
| `uc_agent.puml` | UC_AGT_08 | `Approve Plan` | `APPROVE` uncapitalized |
| `uc_cli.puml` | UC_CLI_02 | `Execute Slash Command` | `EXECUTE` is banned |
| `uc_cli.puml` | UC_CLI_04 | `Parse CLI Arguments` | `PARSE` not in allowed list |
| `uc_cli.puml` | UC_CLI_05 | `Toggle Plan Mode` | `TOGGLE` not in allowed list |
| `uc_cli.puml` | UC_CLI_06 | `Prompt Safety Approval` | `PROMPT` not in allowed list |
| `uc_cli.puml` | UC_CLI_07 | `Switch Model` | verb mixed-case, should be `SWITCH` |
| `uc_config.puml` | UC_CFG_02 | `Validate Config` | `VALIDATE` uncapitalized |
| `uc_config.puml` | UC_CFG_03 | `Merge Layered Config` | `MERGE` not in allowed list |
| `uc_hooks.puml` | UC_HK_01 | `Register Hook` | `REGISTER` uncapitalized |
| `uc_hooks.puml` | UC_HK_02 | `Execute Pre-Tool Hook` | `EXECUTE` is banned |
| `uc_hooks.puml` | UC_HK_03 | `Execute Post-Tool Hook` | `EXECUTE` is banned |
| `uc_hooks.puml` | UC_HK_04 | `Execute Pre-LLM Hook` | `EXECUTE` is banned |
| `uc_hooks.puml` | UC_HK_05 | `Execute Post-LLM Hook` | `EXECUTE` is banned |
| `uc_hooks.puml` | UC_HK_06 | `Evaluate Hook Result` | `EVALUATE` not in base list |
| `uc_plugins.puml` | UC_PLG_01 | `Discover Plugins` | `DISCOVER` uncapitalized |
| `uc_plugins.puml` | UC_PLG_02 | `Load Plugin Manifest` | `LOAD` uncapitalized |
| `uc_plugins.puml` | UC_PLG_03 | `Register Plugin Tools` | `REGISTER` uncapitalized |
| `uc_plugins.puml` | UC_PLG_04 | `Register Plugin Hooks` | `REGISTER` uncapitalized |
| `uc_plugins.puml` | UC_PLG_05 | `Enable/Disable Plugin` | Slash in name, mixed case |
| `uc_provider.puml` | UC_PRV_01 | `Initialize Provider` | `INITIALIZE` not in allowed list |
| `uc_provider.puml` | UC_PRV_02 | `Call Provider Chat` | `CALL` not in allowed list |
| `uc_provider.puml` | UC_PRV_04 | `Select Provider Backend` | `SELECT` uncapitalized |
| `uc_router.puml` | UC_RTG_02 | `Apply Fallback` | mixed-case |
| `uc_router.puml` | UC_RTG_03 | `Classify Task` | `CLASSIFY` uncapitalized |
| `uc_router.puml` | UC_RTG_04 | `Switch Model Mid-Session` | mid-session qualifier improper |
| `uc_safety.puml` | UC_SAF_02 | `Prompt User Approval` | `PROMPT` not in allowed list |
| `uc_safety.puml` | UC_SAF_03 | `Apply Safety Mode` | mixed-case |
| `uc_session.puml` | UC_SSN_01 | `Save Session` | `SAVE` not in allowed list |
| `uc_session.puml` | UC_SSN_02 | `Load Session` | `LOAD` uncapitalized |
| `uc_session.puml` | UC_SSN_05 | `FORK Session` | OK (caps) |
| `uc_session.puml` | UC_SSN_06 | `UNDO Turn` | `UNDO` not in allowed list |
| `uc_tools.puml` | UC_TL_01..04 | `Read File`, etc. | All uncapitalized |
| `uc_tools.puml` | UC_TL_05 | `Execute Shell Command` | `EXECUTE` is banned |
| `uc_tools.puml` | UC_TL_06..08 | `Grep Search`, `Glob Files`, `Find Files` | No CAPS verb prefix |
| `uc_tools.puml` | UC_TL_11 | `Git Status Diff Commit` | No verb, compound name |
| `uc_evaluation.puml` | UC_EVL_01 | `RUN Success Checks` | `RUN` is banned |
| `uc_evaluation.puml` | UC_EVL_03 | `RUN Test Suite` | `RUN` is banned |
| `uc_evaluation.puml` | UC_EVL_04 | `RECORD Result` | OK |
| `uc_evaluation.puml` | UC_EVL_05 | `COORDINATE Retry` | OK |
| `uc_evaluation.puml` | UC_EVL_08 | `RESET On Failure` | `RESET` not in allowed list |

---

### Step 3 — UC ID Format Audit

The `README.md` uses `CLI-01`, `AGT-01` format. The diagram variable names use
`UC_CLI_01`, `UC_AGT_01`. The tenas standard embeds the ID directly in the
use case label text: `**modelstore01 INSERT Model Version Files**\n--\ndescription`.

Nasim diagrams do not embed the ID in the label. The UC label text is just
`"PROCESS User Task"` — no ID embedded.

| File | Label Format | Expected Format |
|---|---|---|
| All nasim UC files | `"VERB Description"` | `"**GROUP-NN VERB Description**\n--\none-line description"` |
| `uc_server.puml` | `"UC-SRV-01: List Sessions"` | Inconsistent with all others |

---

### Step 4 — Actor Audit

**Canonical external actors from C4 context diagram:**
- `Person(dev, "Developer")` — human
- `Person(http_client, "HTTP Client")` — human/machine

**Actors used incorrectly in UC diagrams (internal components, not external actors):**

| File | Wrong Actor | Why Wrong |
|---|---|---|
| `uc_agent.puml` | `actor "HTTP Client" as client` | HTTP Client is correct, but AgentOrchestrator should not be calling APPROVE Plan and others directly |
| `uc_config.puml` | `actor "ArgParser" as parser` | ArgParser is a C4 Component, not an external actor |
| `uc_context.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_context.puml` | `actor "ContextGraph" as ctx` | Internal C4 Component used as actor |
| `uc_edit_strategy.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_evaluation.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_hooks.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_observability.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_observability.puml` | `actor "Provider" as provider` | Internal C4 Component |
| `uc_observability.puml` | `actor "ToolRegistry" as tools` | Internal C4 Component |
| `uc_observability.puml` | `actor "Instrumentation" as entry` | Internal C4 Component |
| `uc_observability.puml` | `actor "Developer / Platform" as ops` | Mixed actor type |
| `uc_plugins.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_provider.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_repo_intelligence.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_repo_intelligence.puml` | `actor "ContextGraph" as ctx` | Internal C4 Component |
| `uc_safety.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_session.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_tools.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |
| `uc_wire_log.puml` | `actor "AgentOrchestrator" as agent` | Internal C4 Component |

**Root cause:** nasim is a code agent. The agent's sub-systems call each other
internally, but in UC diagrams only external actors (Developer, HTTP Client, MCP Client)
initiate use cases. Internal component-to-component delegation is an SQ concern, not a
UC actor concern. UC diagrams must model what an external user/system *can do*, not how
the internals call each other.

Correct actor set for nasim:

| Actor Alias | Name | Type | Applies to |
|---|---|---|---|
| `Developer` | Developer | Human | CLI interaction UCs |
| `HTTPClient` | HTTP Client | System | Server UCs |
| `MCPClient` | MCP Client | System | MCP UCs |
| `Platform` | Observability Platform | System (ext) | OBS, WRL |

---

### Step 5 — Style Audit (vs tenas reference)

Tenas canonical style block (every diagram has this):

```plantuml
skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

skinparam actor<<future>> {
  BackgroundColor #F0F0F0
  BorderColor #999999
  BorderStyle dashed
  FontColor #666666
}
```

Nasim diagrams use only `skinparam packageStyle rectangle` — missing all of the above.

| Style Property | Tenas | Nasim | Gap |
|---|---|---|---|
| `actorStyle awesome` | Yes | No | All files |
| Actor skinparam colors (human) | Yes | No | All files |
| Actor skinparam colors (system) | Yes | No | All files |
| UC skinparam colors | Yes | No | All files |
| `<<system>>` stereotype on actors | Yes | No | All files |
| `<<future>>` stereotype on deferred | Yes | No | All files |
| ID embedded in UC label text | Yes | No | All files |
| `--\ndescription` in UC label | Yes | No | All files |
| `title` statement | Yes | Partial | Most files missing `title` |
| Structured header comment block | Yes | Yes | Present |

---

### Step 6 — Notes Violations

Notes are strictly prohibited in UC diagrams (policy: "no notes, design speaks").

| File | Violation |
|---|---|
| `uc_observability.puml` | Large multi-line `note over agent, runtime` block with 15+ lines |
| `uc_server.puml` | Four `note right of UCxx` blocks |

---

### Step 7 — Wrong Macro Set

| File | Violation |
|---|---|
| `uc_session.puml` | Uses `System_Ext()` macro (C4 context macro, not UC notation) |
| `uc_config.puml` | Uses `System_Ext()` macro (C4 context macro, not UC notation) |
| `uc_server.puml` | Includes `!include C4_Usecase.puml` — no such standard C4 macro; plain PlantUML UC notation is correct |

---

### Step 8 — Disconnected Use Cases (no actor→UC arrow)

Use cases with no actor connection are unreachable flows in the UC model:

| File | Disconnected UCs |
|---|---|
| `uc_agent.puml` | `UC_AGT_03` (Manage Conversation), `UC_AGT_04` (Reset History), `UC_AGT_07` (Queue Plan), `UC_AGT_08` (Approve Plan), `UC_AGT_09` (EVALUATE Task), `UC_AGT_10` (INJECT Turn Budget) |
| `uc_cli.puml` | `UC_CLI_03` (STREAM Output) — no direct actor, only called via include |
| `uc_context.puml` | `UC_CTX_03` (Summarize Old Exchanges) — no actor, only include target |
| `uc_hooks.puml` | `UC_HK_01` (Register Hook) — no actor connected |
| `uc_safety.puml` | `UC_SAF_03` (Apply Safety Mode), `UC_SAF_04` (CHECK Diff Sandbox) — SAF-04 connects to user but SAF-03 has no direct or include path from actor |
| `uc_router.puml` | `UC_RTG_02` (Apply Fallback), `UC_RTG_05..07` — no actor connections |
| `uc_wire_log.puml` | `UC_WRL_02` (READ Log), `UC_WRL_03` (SEEK Turn), `UC_WRL_05` (CHECKPOINT) — no actor connections |

---

### Step 9 — Responsibility Overlap / Duplicate UCs

| Duplicate | Files | Issue |
|---|---|---|
| CHECK Tool Permission | `uc_agent.puml` (UC_AGT_05) AND `uc_safety.puml` (UC_SAF_01) | Same UC defined twice across groups; AGT group should `<<include>>` SAF-01, not redeclare it |
| COMPACT Context | `uc_agent.puml` (UC_AGT_06) AND `uc_context.puml` (UC_CTX_02) | Same UC in two groups |
| Queue Plan / APPROVE Plan | Defined in `uc_agent.puml` as UC_AGT_07/08 AND referenced in `uc_cli.puml` | Should only be declared once (AGT group) |
| Repo Intelligence UCs | `uc_tools.puml` declares UC_TL_13/14 (INJECT RepoMap, SEARCH Semantic) AND `uc_repo_intelligence.puml` has UC_RIM_04/03 for the same operations | Double declaration |
| EVALUATE Task | `uc_agent.puml` (UC_AGT_09) AND `uc_evaluation.puml` has the full Evaluation group | Duplicate |

---

### Step 10 — README vs Diagram Coverage Gap

UC groups in README with no corresponding diagram file:

| README Group | UC Count | Diagram | Status |
|---|---|---|---|
| MEM | 4 (MEM-01..04) | None | **Missing** |
| VCS | 4 (VCS-01..04) | None | **Missing** |
| SBX | 3 (SBX-01..03) | None | **Missing** |
| LLM | 2 (LLM-01..02) | None | **Missing** |
| MCP | Implicit in components | None | **Missing** |

UC groups with diagrams but no matching README group:
- `uc_router.puml` references `RTG` group but README has `RTG-01..04` — present

UC IDs in README without any SQ diagram:
- RTG-03 (Classify Task), RTG-04 (Switch Model Mid-Session) — no SQ file
- Multiple MEM, VCS, SBX entries — no SQ diagrams

---

### Step 11 — Overview Diagram Analysis

The tenas `uc_overview.puml` provides:
- All actors (human + system + future/inactive)
- All UC groups as summary use cases with a multi-line description of their verbs
- Relationships between actors and groups
- `<<future>>` groups shown as inactive stubs

Nasim has **no `uc_overview.puml`**. This is the primary navigation artifact for the
UC layer and must be the first diagram created.

---

## Result

### Defect Classification

#### Critical (blocks design chain integrity)

| ID | Finding | Files Affected |
|---|---|---|
| CR-01 | No `uc_overview.puml` — primary navigation artifact missing | — (new file needed) |
| CR-02 | 5 UC diagram files missing for C4 component groups | LLM, MCP, MEM, VCS/GIT, SBX |
| CR-03 | Notes in diagrams violate "no notes" policy | `uc_observability.puml`, `uc_server.puml` |
| CR-04 | C4 macros (`System_Ext()`) used in UC diagrams — wrong notation | `uc_session.puml`, `uc_config.puml` |
| CR-05 | C4 PlantUML include in UC diagram — wrong macro set | `uc_server.puml` |
| CR-06 | Internal C4 components used as UC actors (20 violations) | 14 files |
| CR-07 | UC IDs not embedded in use case label text | All 17 files |
| CR-08 | Duplicate UC declarations across groups (5 pairs) | Multiple files |
| CR-09 | 6+ disconnected use cases with no actor→UC path | 6 files |

#### Major (degrades consistency and readability)

| ID | Finding | Files Affected |
|---|---|---|
| MJ-01 | Missing full actor/use case skinparam block | All 17 files |
| MJ-02 | `actorStyle awesome` absent | All 17 files |
| MJ-03 | `title` statement absent | 15 of 17 files |
| MJ-04 | Description line (`--\none-liner`) absent from UC labels | All 17 files |
| MJ-05 | Banned verbs used: `EXECUTE` (5x), `RUN` (2x) | 4 files |
| MJ-06 | Mixed verb capitalization: ~35 UCs use Title Case instead of CAPS | All 17 files |
| MJ-07 | Non-allowed verbs: `RESET`, `MERGE`, `TOGGLE`, `SAVE`, `UNDO`, `PROMPT`, `PARSE`, `INITIALIZE`, `CALL` | 8 files |
| MJ-08 | `<<system>>` stereotype absent on system actors | All files with system actors |
| MJ-09 | `<<future>>` stereotype not applied to deferred groups | All files |
| MJ-10 | README UC IDs not present in any SQ diagram for MEM/VCS/SBX groups | — |

#### Minor (polish)

| ID | Finding | Files Affected |
|---|---|---|
| MN-01 | `uc_agent.puml` header has Version 3.0.0 but `uc_provider.puml` has 2.0.0 — no coherent versioning policy | Multiple |
| MN-02 | `uc_tools.puml` mixes tool categories into separate `rectangle` blocks instead of one `package` | `uc_tools.puml` |
| MN-03 | `uc_router.puml` defines both old RTG-01..04 and new RTG-05..07 sets inconsistently | `uc_router.puml` |
| MN-04 | `uc_session.puml` and `uc_wire_log.puml` both have FORK Session as separate UCs | Cross-file |
| MN-05 | `uc_evaluation.puml` UC_EVL_07 (INJECT Turn Budget) duplicates CTX group INJECT responsibility | Cross-file |

---

### Remediation Plan (Priority Order)

```
Priority 1 — Create missing files (CR-01, CR-02):
  + docs/UC/uc_overview.puml
  + docs/UC/uc_llm.puml
  + docs/UC/uc_mcp.puml
  + docs/UC/uc_memory.puml
  + docs/UC/uc_git.puml
  + docs/UC/uc_sandbox.puml

Priority 2 — Fix all 17 existing files (CR-03..09, MJ-01..10):
  For each file:
    a. Replace skinparam with tenas canonical block
       (actorStyle awesome + actor colors + usecase colors)
    b. Add title statement
    c. Replace internal components with canonical external actors
       (Developer, HTTPClient, MCPClient, Platform)
    d. Embed UC ID + description in every usecase label:
       "**GROUP-NN VERB Entity**\n--\none-line description"
    e. Remove all notes (notes are banned from UC diagrams)
    f. Replace System_Ext() / C4 macros with plain rectangle+component
    g. Remove duplicate UC declarations; replace with <<extref>> stereotype
    h. Connect all orphaned UCs to actors
    i. Fix all banned verbs: EXECUTE→RUN_HOOK, RUN→CHECK
       (where possible use allowed verbs from vocabulary)

Priority 3 — Rebuild uc_overview.puml:
    - All groups as summary use cases
    - Developer + HTTP Client + MCP Client actors
    - Platform (Observability) actor
    - Future/deferred groups with <<future>> stereotype
    - SHOW_LEGEND() with AddElementTag for future

Priority 4 — Align README.md:
    - Remove MEM/VCS/SBX from README until diagram files exist
    - OR create the missing diagrams
    - Ensure README row count matches diagram file UC count
```

---

### Corrected Actor Vocabulary (nasim canonical)

| Alias | Display Name | Stereotype | Used In |
|---|---|---|---|
| `Developer` | Developer | (human — default) | CLI, Session, Wire Log, Plugins, Evaluation |
| `HTTPClient` | HTTP Client | `<<system>>` | Server, Observability |
| `MCPClient` | MCP Client | `<<system>>` | MCP |
| `Platform` | Observability Platform | `<<system>>` | Observability (scrape, log collection) |
| `LLMBackend` | LLM Backend | `<<system>>` (future) | LLM, Provider |

Internal components (AgentOrchestrator, ContextGraph, ArgParser, Provider,
ToolRegistry, Instrumentation) must **not** appear as actors in any UC diagram.
Their interaction is the subject of SQ diagrams.

---

### Corrected Verb Vocabulary (nasim extensions to global list)

| Banned / Wrong | Replacement |
|---|---|
| `Execute Hook` | `RUN Hook` → ban; use `DISPATCH Hook` |
| `Run Success Checks` | `CHECK Success` |
| `Run Test Suite` | `VALIDATE Test Suite` |
| `Save Session` | `PERSIST Session` |
| `Load Session` | `READ Session` |
| `Initialize Provider` | `REGISTER Provider` |
| `Call Provider Chat` | `CALL` → ban; use `INVOKE Chat` → also ban; use `REQUEST Chat` |
| `Prompt Safety Approval` | `REQUEST Approval` |
| `Toggle Plan Mode` | `ENABLE Plan Mode` / `DISABLE Plan Mode` |
| `Parse CLI Arguments` | `READ CLI Arguments` |
| `Merge Layered Config` | `APPLY Layered Config` |
| `Manage Conversation` | `UPDATE Conversation` |
| `Reset History` | `DELETE History` |
| `Undo Turn` | `REVERT Turn` |
| `Enable/Disable Plugin` | Two separate UCs: `ENABLE Plugin` / `DISABLE Plugin` |
| `Git Status Diff Commit` | Three separate UCs: `READ Git Status` / `READ Git Diff` / `INSERT Git Commit` |
| `Evaluate Hook Result` | `VALIDATE Hook Result` |
| `Select Provider Backend` | `SELECT Provider` |
| `Classify Task` | `CLASSIFY Task` (caps — allowed, add to extended list) |

---

### Reference Style Template (all nasim UC files must match)

```plantuml
@startuml uc_{group}

' ============================================================
' Title:     nasim — UC: {Group Name}
' Group:     {Group Code} ({GroupName})
' Boundary:  nasim code agent
' Purpose:   {One sentence purpose}
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/entities.md
' Review:    docs/audit/audit.2026.06.20.uc-layer.car.md
' ============================================================

left to right direction

title nasim — {Group Name} Use Cases

skinparam actorStyle awesome
skinparam packageStyle rectangle

skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
  ArrowColor #424242
  FontSize 12
}

skinparam actor {
  BackgroundColor #E8EAF6
  BorderColor #3949AB
  FontColor #1A237E
  FontSize 12
}

skinparam actor<<system>> {
  BackgroundColor #E3F2FD
  BorderColor #1565C0
  FontColor #0D47A1
}

skinparam actor<<future>> {
  BackgroundColor #F0F0F0
  BorderColor #999999
  BorderStyle dashed
  FontColor #666666
}

skinparam usecase<<extref>> {
  BackgroundColor #FFF9C4
  BorderColor #F9A825
  FontColor #5D4037
  BorderStyle dashed
}

' ============================================================
' Actors
' ============================================================

actor "Developer" as Developer
actor "HTTP Client" as HTTPClient <<system>>

' ============================================================
' System Boundary
' ============================================================

rectangle "nasim" {
  package "{Group Name} ({GroupCode})" {
    usecase "**{GroupCode}-01 VERB Entity**\n--\none-line description" as {groupcode}01
    ...
  }
}

' ============================================================
' Actor → Use Case Associations
' ============================================================

Developer --> {groupcode}01
...

' ============================================================
' Relationships
' ============================================================

{groupcode}01 .> {groupcode}02 : <<include>>
...

@enduml
```

---

### Disposition

This audit document is a **working paper**. Once remediation is applied:

1. Extract all resolved findings → apply fixes to each UC diagram file
2. Extract all open gaps → add as open decisions in `.claude/rules/sprint.md`
3. Delete or archive this audit file — the fixes live in the diagrams, not here

**Open decisions to add to sprint.md:**

| OD | Decision Needed |
|---|---|
| OD-UC-01 | Are MEM/VCS/SBX UC groups Phase 1 or Phase 2? If Phase 2, mark as `<<future>>` in overview |
| OD-UC-02 | Should `AgentOrchestrator` appear as a `<<system>>` actor in sub-group diagrams or be removed entirely? |
| OD-UC-03 | Should the LLM group merge into the Provider group UC diagram or stay separate? |
| OD-UC-04 | MCP group: does it merit its own UC diagram or is it covered as a system-extension of Tools? |
| OD-UC-05 | FORK Session is declared in both `uc_session.puml` (SSN) and `uc_wire_log.puml` (WRL) — which group owns it? |
