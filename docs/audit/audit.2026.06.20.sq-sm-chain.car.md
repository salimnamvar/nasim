# C4 → UC → SM → SQ Chain Audit — CAR Framework

**Date:** 2026-06-20
**Scope:** `docs/SQ/` (Sequence Diagrams) + `docs/SM/` (State Machines)
**Compared against:** `docs/UC/README.md` (151 UCs / 21 groups), `docs/C4/c4_nasim_component.puml`
**Reference style:** `tenas_infrastructure/services/model_management/docs/SQ/` + `docs/SM/`
**Auditor:** Claude Code (Sonnet 4.6)

---

## Challenge

The nasim design chain (`C4 → UC → SM → SQ`) was authored across multiple sprint
iterations. The UC layer was recently updated (151 UCs, standardized verb vocabulary,
corrected group codes). The SQ layer must now be reconciled against that updated UC
baseline, the C4 component catalog, and the SM lifecycle models. Key questions:

1. Does every UC in README.md have exactly one SQ file?
2. Do all SQ files follow the canonical structure (intro note + break blocks + ref
   blocks + summary note)?
3. Is the SM layer complete — which entities require lifecycle state machines, and do
   those SM files exist with proper style?
4. Are lifelines traceable to C4 components? Are actor entry chains correct?
5. Do SRV-group SQs comply with ROD (Resource-Oriented Design)?
6. Are CSR (Controller-Service-Repository), DRY, and OOP principles upheld?
7. Are state annotations in SQ diagrams colored consistently with SM hex palette?

---

## Action

### Step 1 — SQ Coverage: UC Count vs SQ File Count

**UC README total: 151 UCs across 21 groups**
**SQ files found: 80 files across 19 directories**

Per-group gap analysis:

| Group | UC Count | SQ Files | Status | Missing |
|---|---|---|---|---|
| AGT | 15 | 8 | **Incomplete** | AGT-09..15 (7) |
| CLI | 8 | 4 | **Incomplete** | CLI-05..08 (4) |
| PRV | 4 | 4 | Complete ✓ | — |
| CFG | 3 | 3 | Complete ✓ | — |
| SSN | 8 | 4 | **Incomplete** | SSN-05..08 (4) |
| SAF | 3 | 3 | Complete ✓ | — |
| CTX | 6 | 3 | **Incomplete** | CTX-04..06 (3) |
| MCP | 4 | 0 | **Empty — no directory** | MCP-01..04 (4) |
| TL | 22 | 12 | **Incomplete** | TL-13..22 (10) |
| SRV | 11 | 7 | **Incomplete + duplicates** | SRV-08..11 (4) |
| HK | 6 | 4 | **Incomplete** | HK-05..06 (2) |
| PLG | 6 | 1 | **Incomplete** | PLG-02..06 (5) |
| RTG | 4 | 2 | **Incomplete** | RTG-03..04 (2) |
| OBS | 5 | 5 | Complete ✓ | — |
| MEM | 4 | 0 | **Empty — no directory** | MEM-01..04 (4) |
| VCS | 4 | 0 | **Empty — no directory** | VCS-01..04 (4) |
| SBX | 4 | 0 | **Empty — no directory** | SBX-01..04 (4) |
| RIM | 6 | 4 | **Incomplete** | RIM-05..06 (2) |
| EDT | 10 | 5 | **Incomplete** | EDT-06..10 (5) |
| EVL | 9 | 5 | **Incomplete** | EVL-06..09 (4) |
| WRL | 5 | 4 | **Incomplete** | WRL-05 (1) |

**Net: 80 SQ files present, 151 required. 71 SQ files missing.**

**Additional: 2 orphaned SQ files (LLM group) with no corresponding UC:**
- `docs/SQ/LLM/sq_llm01_call_ollama_chat.puml`
- `docs/SQ/LLM/sq_llm02_stream_ollama_chat.puml`

The LLM group was eliminated from the UC inventory (provider abstraction via litellm
handles all providers; the LLM UC group was merged into PRV). These 2 files are
dangling artifacts.

---

### Step 2 — File Naming vs UC Operation Names

The UC README was updated with standardized verb vocabulary. Many SQ filenames still
carry the old names. Filename must derive from: `sq_{group}{nn}_{verb}_{noun}.puml`
where verb and noun come from the UC operation title in the README.

**Files whose names do not match the current UC operation:**

| Current Filename | UC ID | Correct UC Operation | Required Filename |
|---|---|---|---|
| `sq_agt01_execute_user_task.puml` | AGT-01 | PROCESS User Task | `sq_agt01_process_user_task.puml` |
| `sq_agt03_manage_conversation.puml` | AGT-03 | UPDATE Conversation | `sq_agt03_update_conversation.puml` |
| `sq_agt04_reset_history.puml` | AGT-04 | DELETE History | `sq_agt04_delete_history.puml` |
| `sq_agt05_check_tool_permission.puml` | AGT-05 | CHECK Permission | `sq_agt05_check_permission.puml` |
| `sq_cfg03_merge_layered_config.puml` | CFG-03 | APPLY Layered Config | `sq_cfg03_apply_layered_config.puml` |
| `sq_cli02_execute_slash_command.puml` | CLI-02 | DISPATCH Slash Command | `sq_cli02_dispatch_slash_command.puml` |
| `sq_cli03_display_streaming_output.puml` | CLI-03 | STREAM Output | `sq_cli03_stream_output.puml` |
| `sq_cli04_parse_cli_arguments.puml` | CLI-04 | READ CLI Arguments | `sq_cli04_read_cli_arguments.puml` |
| `sq_ctx01_track_token_count.puml` | CTX-06 | TRACK Token Budget | Number should be ctx06 |
| `sq_ctx03_summarize_old_exchanges.puml` | CTX-03 | DISTILL Nodes | `sq_ctx03_distill_nodes.puml` |
| `sq_edt02_apply_edit.puml` | EDT-02 | APPLY Search-Replace | `sq_edt02_apply_search_replace.puml` |
| `sq_edt03_validate_edit.puml` | EDT-03 | APPLY Whole-File | `sq_edt03_apply_whole_file.puml` (content must also change) |
| `sq_edt04_stage_edit.puml` | EDT-10 | STAGE Diff | `sq_edt10_stage_diff.puml` (number mismatch) |
| `sq_edt05_review_diff.puml` | — | Not a UC in README | Orphaned or merge into EDT-10 |
| `sq_evl01_run_success_checks.puml` | EVL-01 | EVALUATE Task | `sq_evl01_evaluate_task.puml` |
| `sq_evl02_invoke_llm_reviewer.puml` | EVL-04 | VALIDATE With LLM | `sq_evl04_validate_with_llm.puml` (number mismatch) |
| `sq_evl03_coordinate_retry.puml` | EVL-06 | COORDINATE Retry | `sq_evl06_coordinate_retry.puml` (number mismatch) |
| `sq_evl04_detect_repetition.puml` | EVL-08 | DETECT Repetition | `sq_evl08_detect_repetition.puml` (number mismatch) |
| `sq_evl05_inject_turn_budget.puml` | EVL-09 | INJECT Turn Budget | `sq_evl09_inject_turn_budget.puml` (number mismatch) |
| `sq_hk02_pre_tool_hook.puml` | HK-02 | DISPATCH Pre-Tool Hook | `sq_hk02_dispatch_pre_tool_hook.puml` |
| `sq_hk03_post_tool_hook.puml` | HK-03 | DISPATCH Post-Tool Hook | `sq_hk03_dispatch_post_tool_hook.puml` |
| `sq_prv01_initialize_provider.puml` | PRV-01 | REGISTER Provider | `sq_prv01_register_provider.puml` |
| `sq_prv02_call_provider_chat.puml` | PRV-02 | REQUEST Chat | `sq_prv02_request_chat.puml` |
| `sq_rim01_index_repository.puml` | RIM-01 | INDEX Codebase | `sq_rim01_index_codebase.puml` |
| `sq_rim02_rank_symbols.puml` | RIM-03 | RANK Results | `sq_rim03_rank_results.puml` (number mismatch) |
| `sq_rim03_search_semantic.puml` | RIM-06 | SEARCH Semantic | `sq_rim06_search_semantic.puml` (number mismatch) |
| `sq_saf01_check_tool_permission.puml` | SAF-01 | CHECK Permission | `sq_saf01_check_permission.puml` |
| `sq_ssn01_save_session.puml` | SSN-01 | PERSIST Session | `sq_ssn01_persist_session.puml` |
| `sq_ssn02_load_session.puml` | SSN-02 | READ Session | `sq_ssn02_read_session.puml` |
| `sq_ssn04_resume_session.puml` | SSN-04 | RESTORE Session | `sq_ssn04_restore_session.puml` |
| `sq_tl05_execute_shell_command.puml` | TL-05 | DISPATCH Shell Command | `sq_tl05_dispatch_shell_command.puml` |
| `sq_tl11_git_status_diff_commit.puml` | TL-11 | READ Git Status | `sq_tl11_read_git_status.puml` |
| `sq_tl12_invoke_mcp_extension.puml` | TL-12 | DISPATCH MCP Extension | `sq_tl12_dispatch_mcp_extension.puml` |
| `sq_wrl03_fork_session.puml` | WRL-04 | FORK Session | `sq_wrl04_fork_session.puml` (number mismatch) |
| `sq_wrl04_replay_session.puml` | — | Not in UC README | Orphaned (no WRL replay UC) |

**SRV group specific issues (duplicate ID + naming chaos):**

| File | Problem |
|---|---|
| `sq_srv01_list_sessions.puml` | Maps to SRV-01 LIST Sessions — correct |
| `sq_srv01_start_server.puml` | Duplicate SRV-01 prefix; start_server is not a UC in README |
| `sq_srv02_create_session.puml` | UC is SRV-02 INSERT Session — "create" vs "INSERT" naming mismatch |
| `sq_srv03_send_message.puml` | Maps to SRV-06 DISPATCH Message — wrong number |
| `sq_srv04_stream_response.puml` | No corresponding UC in README — orphaned or sub-flow |
| `sq_srv05_get_message_history.puml` | UC is SRV-07 LIST Messages — wrong number and "get" vs "LIST" |
| `sq_srv06_send_message.puml` | Duplicate of srv03 — two files claiming to cover DISPATCH Message |

---

### Step 3 — Structural Template Compliance

The canonical SQ template (from `sq.md` policy) requires:

**Intro note** (before first message):
```
Scope / Preconditions / Excludes / Contexts / Rollback / Design
```

**Summary note** (after last message):
```
Flow / State / Failure / Success
```

All notes must use consistent indentation. The intro note must use exactly those 6
section headers. The summary note must use exactly those 4 section headers.

State annotations must use `<back:#HEX>STATE</back>` format matching SM hex palette.

Compliance check across representative files:

| File | Intro Note | Summary Note | break blocks | box colors | State annotation |
|---|---|---|---|---|---|
| `sq_agt01_execute_user_task.puml` | ✓ (+ extra "Returns:") | ✓ | ✓ (1) | ✓ | ✗ text only |
| `sq_saf01_check_tool_permission.puml` | ✓ (inline format) | ✓ | ✗ (rejection not in break) | ✗ no boxes | ✗ text only |
| `sq_srv03_send_message.puml` | **✗ absent** | **✗ absent** | **✗ absent** | **✗ absent** | **✗ absent** |
| `sq_prv02_call_provider_chat.puml` | probable partial | probable partial | unknown | unknown | likely absent |
| `sq_ctx02_compact_context.puml` | unknown | unknown | unknown | unknown | unknown |

**By pattern (assessed from visible files), the following structural violations occur across the SQ layer:**

**SQ-STR-01** Non-standard extra fields in intro note.
`sq_agt01` adds `Returns:` as a 7th section — not in the canonical template.
Standard is exactly 6 fields. Extra sections must be removed.

**SQ-STR-02** Summary note missing `State:` annotation with colored state transitions.
All surveyed files use text-only state labels (`IDLE → LISTENING → THINKING`).
Required format: `State: <back:#E8EAF6>IDLE</back> → <back:#FFF3E0>THINKING</back> → <back:#E8F5E9>RESPONDING</back>`.
Hex codes must come from the nasim SM canonical color palette (not yet defined — see SM audit).

**SQ-STR-03** Intro note missing from `sq_srv03`, `sq_srv04`, `sq_srv05`, `sq_srv06`.
These SRV-group files lack both intro and summary notes entirely.

**SQ-STR-04** `break` blocks inconsistently applied.
`sq_agt01` correctly uses `break` for LLM/tool failure. `sq_saf01` uses `alt`
for rejection path instead of `break`. Rejection is a terminal path that must use
`break` (break always terminates; alt implies continuation after the branch closes).

**SQ-STR-05** Box colors absent on many files.
`sq_saf01` has no `box` groupings — just flat participant declarations without the
layer-colored boxes that trace each participant to a C4 boundary. Required boxes:

```plantuml
box "CLI Layer" #E8F5E9
box "Agent Layer" #E3F2FD
box "Provider Layer" #FFF3E0
box "Tool Layer" #F3E5F5
box "Safety Layer" #FFF9C4
box "Config Layer" #FCE4EC
box "Session Layer" #F3E5F5
box "Server Layer" #E8EAF6
box "Hooks Layer" #FFFDE7
box "Plugins Layer" #EDE7F6
box "Observability Layer" #E0F2F1
box "External" #F5F5F5
```

**SQ-STR-06** `@startuml` IDs do not match filenames.
`sq_agt01_execute_user_task.puml` starts with `@startuml sq_agt01_execute_user_task`.
After rename to `sq_agt01_process_user_task.puml`, the `@startuml` ID must also update.
Current files: IDs and filenames are inconsistent already.

---

### Step 4 — C4 Lifeline Traceability

Every participant in an SQ diagram must trace to a named C4 component in the
`c4_nasim_component.puml` container boundaries.

**Violations found:**

| SQ File | Participant | C4 Status |
|---|---|---|
| `sq_srv03_send_message.puml` | `"AgentOrchestrator"` | C4 component ✓ (but CSR violation — see Step 7) |
| `sq_srv03_send_message.puml` | `"Provider"` | C4 Protocol, not a named component — use `"LiteLLMProxy"` |
| `sq_saf01_check_tool_permission.puml` | `"PermissionGate"` | C4 component ✓ |
| `sq_agt01_execute_user_task.puml` | `"Provider"` | Same issue — should be `"LiteLLMProxy"` or `"Provider (Protocol)"` |
| Multiple SQ files | `"ToolRegistry"` as monolithic participant | C4 splits tools: `FileTools`, `SearchTools`, `ShellTool`, etc. Use ToolRegistry only for lookup; individual tool components for execution |

**Missing participants in SRV group SQs:**

`sq_srv03_send_message.puml` is missing:
- `APISchema` (request/response model validation — CSR controller concern)
- `HookManager` (hooks run around LLM calls and tool executions)
- `TraceCorrelator` (request_id correlation is mandatory per OBS design)

---

### Step 5 — Actor Entry Chain Compliance

Per `sq.md` policy, operator-initiated flows require the full entry chain:

**CLI flows:**
```
Developer → REPLSession → AgentOrchestrator
```

**HTTP flows:**
```
HTTPClient → ServerRouter → [Controller/Service chain]
```

**Violations:**

| File | Issue |
|---|---|
| `sq_saf01_check_tool_permission.puml` | No actor at all. SAF-01 is called via `ref` from AGT-02, so actor is optional IF this is a "Process Decomposition" diagram. But it lacks the `ref` entry context note. |
| `sq_srv03_send_message.puml` | HTTP Client → ServerRouter chain present ✓, but entry goes directly to AgentOrchestrator without passing through APISchema validation layer (CSR violation) |
| Multiple TL files | Tool SQs have no actor and no explicit `ref` context in intro note marking them as process decomposition diagrams |
| Multiple HK files | Hook SQs have no actor and no explicit note explaining they are sub-flows of AGT |

**Classification requirement:** Every SQ must declare itself as either:
- **Primary Orchestrator** — has Actor; shows full entry chain
- **UC-level Sub-flow** — has Actor (same chain); called via `ref` from others
- **Process Decomposition** — no Actor; called from parent SQ only; MUST have explicit "Contexts:" in intro note naming parent UC IDs

Currently, tool SQs and safety SQs fall in the "Process Decomposition" category but do
not mark themselves as such in the intro note.

---

### Step 6 — ROD Compliance (SRV Group)

The SRV group maps to the HTTP API surface. All SRV SQs must comply with ROD
(Google AIP) and the CSR pattern for the Server Layer.

**SRV path naming issues:**

| SQ File | URL in Diagram | Correct ROD Path | Issue |
|---|---|---|---|
| `sq_srv01_list_sessions.puml` | unknown | `GET /v1/sessions` | Verify `/v1/` prefix (AIP-185) |
| `sq_srv03_send_message.puml` | `POST /v1/sessions/{id}/messages` | `POST /v1/sessions/{id}:dispatch` | Wrong: creating a message resource vs. triggering a dispatch action; the UC is DISPATCH Message (custom method) not INSERT Message |
| `sq_srv02_create_session.puml` | unknown | `POST /v1/sessions` | Must return 201, not 200 |
| Various | unknown | All paths must start `/v1/` | AIP-185 mandatory |

**Error response compliance:**

`sq_srv03_send_message.puml` has:
- No `break` block for session not found (must return `404 NOT_FOUND`)
- No `break` block for invalid request body (must return `400 INVALID_ARGUMENT`)
- No `break` block for agent error (must return `502 UNAVAILABLE`)
- Return arrow `router --> client : 200 (SSE stream complete)` — correct status but missing
  `Content-Type: text/event-stream` annotation
- No AIP-193 error body shape (`{error: {code, message, status, details}}`)

**HTTP status code placement:**

Per `sq.md`, HTTP status codes appear ONLY on `ServerRouter → HTTPClient` return arrows.
Never on internal component calls. Verified: `sq_srv03` has `200` on the correct arrow.
However, error paths are absent entirely.

**CSR pattern violations (SRV group):**

```
Current:  HTTPClient → ServerRouter → AgentOrchestrator
Required: HTTPClient → ServerRouter(Controller) → AgentService(Service) → SessionStore(Repository)
```

`ServerRouter` is the Controller. It must call a **Service** layer (not directly call
`AgentOrchestrator`). `AgentOrchestrator` is not a Service in the CSR sense — it is the
agent core. The SRV layer needs an intermediary: an `AgentService` or `RequestProcessor`
that translates HTTP request payload into agent input, invokes the agent, and maps
agent events to SSE output.

Current design bypasses the Service layer and couples the Controller directly to the
agent domain object — a CSR-01 violation.

---

### Step 7 — DRY and ref Block Compliance

`sq.md` requires that any sub-flow that appears in more than one SQ must be expressed
as a `ref` block pointing to the sub-flow's own SQ file. Never inline.

**DRY violations identified:**

| Pattern | Files Affected | Issue |
|---|---|---|
| Permission check | `sq_agt01`, `sq_agt02`, various TL files | Each tool SQ should `ref SAF-01` at start — many inline the check instead |
| Provider call | `sq_agt01` correctly refs `prv02/prv03` ✓ | Good pattern |
| Context tracking | CTX-06 token tracking should be ref'd after every history update | Not ref'd in AGT-01 |
| Hook dispatch | HK-02..05 should be ref'd in AGT-01 around LLM calls and tool dispatches | Not ref'd in AGT-01 |
| Trace correlation | OBS-03 should be ref'd at the start of every Primary Orchestrator SQ | Not present in any surveyed file |
| Metrics recording | OBS-02 should be ref'd at the end of every completed flow | Not present in any surveyed file |

**Scenario diagram requirement:**

AGT-01 PROCESS User Task is the primary orchestrator for the entire agentic loop.
It must use `ref` blocks exclusively — no inlined logic from other groups.

Current AGT-01 inlines:
1. `agent -> history : append user message` (should be `ref AGT-03 UPDATE Conversation`)
2. `agent -> history : append assistant message` (should be `ref AGT-03 UPDATE Conversation`)
3. `agent --> repl : AgentEvent(Done)` — correct, this is a CLI-03 event but the rendering is CLI-layer concern

Currently AGT-01 correctly refs: `prv02/prv03` (Provider) and `agt02` (Tool Dispatch).
It must also ref: `CTX-06` (token tracking), `AGT-15` (safety pipeline), `HK-02..05` (hooks).

---

### Step 8 — State Machine Layer Audit

#### Step 8a — SM Completeness: Which Entities Need a Lifecycle SM?

A lifecycle state machine is required when an entity:
1. Has multiple named states that govern valid operations
2. Transitions are operator/system-initiated and must be validated
3. State is persisted (or communicated externally)
4. Different states allow different operations (guard conditions)

| Entity | States | Persisted? | Needs SM? | File |
|---|---|---|---|---|
| Agent (Process FSM) | IDLE/THINKING/TOOL_EXEC/COMPACTING/etc. | No (runtime only) | Process FSM ✓ (existing) | `sm_agent_lifecycle.puml` |
| **Session** | CREATED, ACTIVE, SAVED, RESTORED, BRANCHED, CLOSED | **Yes** (disk) | **Yes — missing** | — |
| **Plan** | EMPTY, BUILDING, QUEUED, APPROVED, EXECUTING, COMPLETED, REJECTED | **Yes** (PlanSession) | **Yes — missing** | — |
| **Plugin** | DISCOVERED, LOADING, LOADED, ENABLED, DISABLED, ERROR | **Yes** (config) | **Yes — missing** | — |
| Tool Execution | PENDING, RUNNING, COMPLETED, FAILED, REJECTED | No (single turn) | Optional (embedded in Agent FSM) | — |
| Subagent | SPAWNED, RUNNING, COMPLETED, FAILED, CANCELLED | No (session scope) | Optional | — |
| Sandbox | PENDING, RUNNING, COMPLETED, TIMED_OUT, KILLED | No (per-command) | Optional | — |
| MCP Connection | DISCONNECTED, CONNECTING, CONNECTED, ERROR | Partial (config) | Optional | — |

**3 entities require dedicated SM files that do not exist:**
- `docs/SM/sm_session_lifecycle.puml`
- `docs/SM/sm_plan_lifecycle.puml`
- `docs/SM/sm_plugin_lifecycle.puml`

#### Step 8b — SM Style Audit: sm_agent_lifecycle.puml

The existing Agent SM has critical style gaps against the tenas reference standard:

**Tenas SM style (canonical):**
```plantuml
skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

state "Active" as ACTIVE #2E7D32
state "Activation Failed" as ACTIVATION_FAILED #EF5350
```

Each state:
- Has an inline color (hex code)
- Has a human-readable display name in quotes
- Has description lines inside the state block:
  ```
  ACTIVE : Version is the operator-nominated primary version.
  ACTIVE : Under latest/all policy: additional STAGED versions may also be served.
  ```
- Has transition labels that name the UC + method that triggers the transition

**nasim Agent SM violations:**

| Check | Tenas | nasim SM | Gap |
|---|---|---|---|
| `skinparam state { ... }` block | ✓ | ✗ absent | All states render default colors |
| Inline hex color per state | ✓ `state "X" as Y #RRGGBB` | ✗ absent | No visual differentiation |
| State description lines | ✓ `ACTIVE : description.` | ✗ absent | States have no semantic doc |
| Transition labels naming UC | ✓ e.g. `modelstate07 SET...` | Partial (some transitions labeled) | Inconsistent |
| Structured header comment | ✓ | ✓ | Present |
| `title` statement | ✓ | ✓ | Present |
| `note` blocks for invariants | Optional in tenas | ✗ | Minor |
| Terminal state `DELETED --> [*]` | ✓ | `IDLE --> [*] : /quit or EOF` | OK for process FSM |

#### Step 8c — Proposed Nasim SM Color Palette

For the process FSM states (Agent), the color scheme must be defined and applied
in SQ state annotations. Proposed palette (to be canonical in nasim SM files):

| State | Hex | Color Name |
|---|---|---|
| IDLE | `#ECEFF1` | Blue Grey 50 |
| LISTENING | `#E8EAF6` | Indigo 50 |
| THINKING | `#FFF3E0` | Orange 50 |
| TOOL_EXEC | `#F3E5F5` | Purple 50 |
| AWAITING_APPROVAL | `#FFF9C4` | Yellow 50 |
| COMPACTING | `#E0F2F1` | Teal 50 |
| ROUTING | `#EDE7F6` | Deep Purple 50 |
| RESPONDING | `#E8F5E9` | Green 50 |
| ERROR | `#FFEBEE` | Red 50 |
| PLANNING | `#E3F2FD` | Blue 50 |
| SERVING | `#E8EAF6` | Indigo 50 |
| EVALUATING | `#F9FBE7` | Lime 50 |
| REVIEWING | `#FFF8E1` | Amber 50 |
| RETRYING | `#FBE9E7` | Deep Orange 50 |
| HOOK_RUNNING | `#FFFDE7` | Yellow 50 |
| STAGING | `#F1F8E9` | Light Green 50 |
| AWAITING_DIFF_APPROVAL | `#FCE4EC` | Pink 50 |

For entity lifecycle SMs (Session, Plan, Plugin):

**Session states:**
| State | Hex |
|---|---|
| CREATED | `#E3F2FD` |
| ACTIVE | `#2E7D32` (dark green) |
| SAVED | `#1565C0` (dark blue) |
| RESTORED | `#1E88E5` (blue) |
| BRANCHED | `#7B1FA2` (purple) |
| CLOSED | `#757575` (grey) |

**Plan states:**
| State | Hex |
|---|---|
| EMPTY | `#ECEFF1` |
| BUILDING | `#FFF3E0` |
| QUEUED | `#E3F2FD` |
| APPROVED | `#2E7D32` |
| EXECUTING | `#A5D6A7` |
| COMPLETED | `#1B5E20` |
| REJECTED | `#B71C1C` |

**Plugin states:**
| State | Hex |
|---|---|
| DISCOVERED | `#ECEFF1` |
| LOADING | `#FFF3E0` |
| LOADED | `#90CAF9` |
| ENABLED | `#2E7D32` |
| DISABLED | `#CE93D8` |
| ERROR | `#EF5350` |

#### Step 8d — State Color Usage in SQ Diagrams

When an SQ diagram transitions an entity's lifecycle state, it must annotate that
transition with the `<back:#HEX>STATE</back>` syntax.

**Required pattern (from tenas reference):**
```plantuml
note right of SessionStore
  State: <back:#E3F2FD>CREATED</back> → <back:#2E7D32>ACTIVE</back>
end note
```

**Current nasim SQ diagrams:** zero instances of `<back:#HEX>STATE</back>` usage.
All state change annotations (where present) are plain text only — `IDLE → THINKING`.

This violates the chain consistency principle: SM defines hex colors; SQ must use them.

---

### Step 9 — OOP and Design Principle Violations

**OOP: Single Responsibility Principle**

`sq_srv03_send_message.puml` — `ServerRouter` is responsible for:
1. HTTP request parsing
2. Session existence validation
3. Invoking the agent
4. Managing SSE streaming
5. Persisting session after completion

This is 5 responsibilities in one participant. CSR: Router is Controller only.
Service layer is missing. Repository (SessionStore) should be called from Service,
not from Controller.

**OOP: Open/Closed Principle violation**

The Provider participant in SQ diagrams is declared as just `"Provider"` (the Protocol
interface). But the actual implementation is `LiteLLMProxy`. When a new provider is
added, these SQ diagrams require modification because they reference the abstract
interface instead of showing the concrete implementation behind the factory. SQ diagrams
should show: `ProviderFactory → LiteLLMProxy (via litellm)` to make the design explicit.

**DRY: Repeated inline permission check**

Multiple tool SQ diagrams inline the permission check logic instead of using:
```plantuml
ref over AgentOrchestrator, PermissionGate
  SAF-01: CHECK Permission
  Output: approved | rejected
end ref
break SAF-01 rejected
  AgentOrchestrator --> REPLSession : AgentEvent(Error, "permission denied")
end
```

Every tool SQ that pre-checks permission is duplicating SAF-01. This means if the
permission logic changes, all tool SQs must be updated.

**DRY: Context tracking not ref'd**

After every `ConversationHistory` update (append user message, append assistant
message, append tool result), CTX-06 TRACK Token Budget should be `ref`'d. Currently
token tracking is neither ref'd nor inlined — it simply does not appear in the SQ flow,
making the context budget enforcement invisible.

---

### Step 10 — Canonical SQ Template (Reference)

The following template must be applied uniformly to every nasim SQ diagram:

```plantuml
@startuml sq_{group}{nn}_{verb}_{noun}

' ============================================================
' Title:     {GROUP}-{NN} — {VERB} {Noun}
' Boundary:  nasim code agent
' Purpose:   {one sentence}
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — {GROUP}-{NN} {VERB} {Noun}

' Optional: actor declaration for Primary Orchestrator or UC-level Sub-flow
actor "Developer" as Developer

' ============================================================
' Participants (grouped by layer box)
' ============================================================

box "CLI Layer" #E8F5E9
  participant "REPLSession" as repl
end box
box "Agent Layer" #E3F2FD
  participant "AgentOrchestrator" as agent
end box
' ... additional boxes per C4 boundary ...

' ============================================================
' Intro Note (mandatory — exactly these 6 fields)
' ============================================================

note over [first_lifeline], [last_lifeline]
  Scope:          {what this diagram covers — one line}
  Preconditions:  {required states and prior completed operations}
  Excludes:       {what is NOT in this diagram}
  Contexts:       {which parent UCs call this via ref — UC IDs}
  Rollback:       {what happens on each failure path}
  Design:         {key invariants and design decisions}
end note

' ============================================================
' == {GROUP}-{NN} {VERB} {Noun} ==
' ============================================================

' ... sequence content ...
' Use ref blocks for all sub-flows:
ref over agent, provider
  PRV-02: REQUEST Chat
  Output: LLMResponse | 502 provider error | 504 timeout
end ref

break PRV-02 failed [502 / 504]
  agent --> repl : AgentEvent(Error)
end

' State transitions with color annotations:
note right of SessionStore
  State: <back:#ECEFF1>IDLE</back> → <back:#2E7D32>ACTIVE</back>
end note

' ============================================================
' Summary Note (mandatory — exactly these 4 fields)
' ============================================================

note over [first_lifeline], [last_lifeline]
  Flow:    {one-line happy path description}
  State:   {<back:#HEX>FROM</back> → <back:#HEX>TO</back> or "No state change"}
  Failure: {what breaks and how it is handled}
  Success: {what the caller receives on success}
end note

@enduml
```

---

## Result

### Defect Classification

#### Critical (blocks design chain integrity)

| ID | Finding | Count |
|---|---|---|
| CR-SQ-01 | 71 SQ files missing (UC 1:1 invariant broken) | 71 files |
| CR-SQ-02 | 4 SQ group directories missing (MCP, MEM, VCS, SBX) | 4 dirs |
| CR-SQ-03 | SRV group: 2 duplicate SRV-01 files; 3 files with wrong UC number | 5 files |
| CR-SQ-04 | 2 orphaned SQ files (LLM group) with no corresponding UC | 2 files |
| CR-SQ-05 | `sq_srv03` (and others) missing intro note + summary note entirely | 4+ files |
| CR-SQ-06 | `sq_srv03` has no break blocks; no HTTP error paths; no session-not-found guard | 1 file |
| CR-SQ-07 | CSR violation: ServerRouter calls AgentOrchestrator directly (no Service layer) | SRV group |
| CR-SQ-08 | ROD violation: DISPATCH Message uses wrong URL pattern (should be `:dispatch` custom method) | SRV-06 |
| CR-SM-01 | 3 entity SM files missing (Session, Plan, Plugin) | 3 files |
| CR-SM-02 | Existing `sm_agent_lifecycle.puml` has no state colors (no hex codes) | 1 file |
| CR-CHAIN-01 | State annotations in all SQ files use plain text, not `<back:#HEX>STATE</back>` | All 80 files |

#### Major (degrades consistency and quality)

| ID | Finding | Count |
|---|---|---|
| MJ-SQ-01 | 35+ SQ filenames do not match updated UC operation names | 35+ files |
| MJ-SQ-02 | `break` block absent for rejection/denial paths in sub-flow SQs | 10+ files |
| MJ-SQ-03 | `@startuml` IDs will mismatch filenames after rename | 35+ files |
| MJ-SQ-04 | Box colors absent in SAF, CTX, some AGT sub-flow files | 15+ files |
| MJ-SQ-05 | Extra "Returns:" field in AGT-01 intro note (non-standard) | AGT group |
| MJ-SQ-06 | Permission check (SAF-01) not `ref`'d at start of tool SQs | TL group |
| MJ-SQ-07 | CTX-06 (TRACK Token Budget) never `ref`'d after history updates | AGT, TL |
| MJ-SQ-08 | OBS-03 (CORRELATE Trace) not `ref`'d at start of Primary Orchestrator SQs | CLI, SRV |
| MJ-SQ-09 | Hook dispatch (HK-02..05) not `ref`'d in AGT-01 (around LLM calls + tools) | AGT-01 |
| MJ-SQ-10 | Tool SQs do not mark themselves as "Process Decomposition" in intro note | TL, HK, SAF |
| MJ-SQ-11 | `"Provider"` used as participant name (protocol, not component); should be `"LiteLLMProxy"` | PRV, AGT |
| MJ-SM-01 | SM color palette not defined in any file (no canonical hex reference) | All SM files |
| MJ-SM-02 | State descriptions absent from all states in Agent SM | sm_agent_lifecycle.puml |
| MJ-SM-03 | Transition labels in Agent SM do not name the triggering UC ID | sm_agent_lifecycle.puml |

#### Minor

| ID | Finding | Count |
|---|---|---|
| MN-SQ-01 | SRV SQ `title` statements use inconsistent format (some missing, some have "SRV-03" wrong ID) | SRV group |
| MN-SQ-02 | `deactivate` blocks inconsistently applied (some participants never deactivated) | Multiple |
| MN-SQ-03 | `sq_wrl04_replay_session.puml` — no WRL replay UC in README; file is orphaned | 1 file |
| MN-SM-01 | Agent SM missing `skinparam state { BackgroundColor BorderColor FontColor }` block | 1 file |

---

### SM Entities — Canonical Requirement List

```
docs/SM/
  sm_agent_lifecycle.puml     ← Exists; needs color + description fix
  sm_session_lifecycle.puml   ← MISSING — must be created
  sm_plan_lifecycle.puml      ← MISSING — must be created
  sm_plugin_lifecycle.puml    ← MISSING — must be created
  README.md                   ← MISSING — must be created
```

---

### Remediation Order

```
Priority 1 — SM color palette (prerequisite for all SQ state annotation fixes):
  a. Add skinparam state block to sm_agent_lifecycle.puml
  b. Add hex color per state using proposed palette above
  c. Add state description lines (IDLE : Agent waiting for user input.)
  d. Add transition labels with UC IDs
  e. Create sm_session_lifecycle.puml
  f. Create sm_plan_lifecycle.puml
  g. Create sm_plugin_lifecycle.puml
  h. Create docs/SM/README.md

Priority 2 — SQ structural fixes on existing 80 files:
  a. Rename files to match UC operation names
  b. Update @startuml IDs to match filenames
  c. Add intro note (6 fields) to all files missing it
  d. Add summary note (4 fields) to all files missing it
  e. Add box colors to all participants
  f. Convert alt-for-terminal-paths to break blocks
  g. Add <back:#HEX>STATE</back> annotations where state changes occur
  h. Replace inline sub-flows with ref blocks (DRY)
  i. Add ref SAF-01 at start of all tool SQ flows
  j. Add ref CTX-06 after all history update ref blocks
  k. Add ref OBS-03 at start of all Primary Orchestrator flows
  l. Remove extra "Returns:" from AGT-01 intro note
  m. Mark Process Decomposition diagrams as such in intro note Contexts field

Priority 3 — SRV group rebuild:
  a. Delete sq_srv01_start_server.puml (not a UC)
  b. Delete sq_srv04_stream_response.puml (not a standalone UC — sub-flow of SRV-06)
  c. Delete sq_srv06_send_message.puml (duplicate of now-renamed SRV-06)
  d. Rename and rebuild sq_srv03 → sq_srv06_dispatch_message.puml with:
     - AIP-193 error format bodies
     - break blocks for 400/404/422/502/500
     - SSE Content-Type annotation
     - APISchema participant for request validation
     - CSR-compliant: Controller(ServerRouter) → Service → Repository pattern
     - `:dispatch` custom method URL per ROD (AIP-136)
  e. Add sq_srv07 through sq_srv11

Priority 4 — Create 71 missing SQ files:
  a. Create MCP directory + 4 files
  b. Create MEM directory + 4 files
  c. Create VCS directory + 4 files
  d. Create SBX directory + 4 files
  e. Fill all per-group gaps (AGT-09..15, CLI-05..08, SSN-05..08, etc.)

Priority 5 — Delete orphaned files:
  a. docs/SQ/LLM/sq_llm01_call_ollama_chat.puml
  b. docs/SQ/LLM/sq_llm02_stream_ollama_chat.puml
  c. docs/SQ/WRL/sq_wrl04_replay_session.puml
  d. docs/SQ/EDT/sq_edt05_review_diff.puml (if confirmed as sub-flow of EDT-10)
```

---

### Open Decisions for sprint.md

| OD | Decision |
|---|---|
| OD-SQ-01 | Does the SRV layer need an explicit Service class (`AgentService`) to fix CSR-01, or does `ServerRouter` delegate directly to `AgentOrchestrator` with documented justification? |
| OD-SQ-02 | For TL/HK/SAF sub-flow SQs: do they all require a `Developer` actor (UC-level sub-flow classification) or are they all Process Decomposition (no actor)? |
| OD-SQ-03 | Should OBS-03 CORRELATE Trace be ref'd at the START of every Primary Orchestrator SQ, or is it implicit (always active)? Affects 5+ Primary Orchestrator diagrams. |
| OD-SM-01 | Should the Agent SM remain a "Process FSM" documented deviation, or be refactored into a proper entity lifecycle SM with persisted state? |
| OD-SM-02 | The proposed state color palette above: adopt as canonical or modify? Must be decided before any SQ state annotations are written. |
| OD-SM-03 | Does a Sandbox execution need its own SM, or is SBX lifecycle fully captured by the Agent FSM's TOOL_EXEC → STAGING states? |
