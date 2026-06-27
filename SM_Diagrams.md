

--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/README.md ---

# nasim — State Machine Inventory (API-First)

## Agent Lifecycle States (Process FSM)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | Agent waiting for user input | Startup or response complete | #ECEFF1 |
| LISTENING | Receiving and parsing user input | API-06 DISPATCH Message received | #E8EAF6 |
| THINKING | LLM processing messages | Input parsed, messages built | #FFF3E0 |
| TOOL_EXEC | Executing a tool call | LLM returns tool_calls | #F3E5F5 |
| RESPONDING | Streaming final text to user via API SSE | LLM returns text only | #E8F5E9 |
| ERROR | Error occurred | LLM call or tool exec fails | #FFEBEE |
| COMPACTING | Summarizing old exchanges | token_count > context_budget | #E0F2F1 |
| AWAITING_APPROVAL | Waiting for user permission | safety_mode=ask AND unsafe tool | #FFF9C4 |
| PLANNING | Plan mode, tool calls queued | /plan command entered | #E3F2FD |
| HOOK_RUNNING | Pre/post hook executing | tool or LLM call with hooks | #FFFDE7 |
| ROUTING | Model selection in progress | ModelRouter resolving model | #EDE7F6 |
| SERVING | API processing request from any interface | API-06 DISPATCH Message | #E0F7FA |
| EVALUATING | Evaluating task completion | task_complete AND evaluation_enabled | #F9FBE7 |
| REVIEWING | LLM review of results | success checks passed, optional review | #FFF8E1 |
| RETRYING | Retrying with feedback | success checks failed or review rejected | #FBE9E7 |
| STAGING | Diff sandbox staging | tool exec in diff_sandbox mode | #F1F8E9 |

> **API-First Entry:** All entry/exit transitions use `API-06` (DISPATCH Message) as the sole entry gate. No interface container may bypass the API.

### Transitions from STAGING

| From | To | UC ID | Condition |
|------|----|-------|-----------|
| STAGING | AWAITING_DIFF_APPROVAL | EDT-10 | Diff computed successfully |
| STAGING | ERROR | EDT-10 | Diff computation failed (file deleted, conflict, algorithm error) |
| AWAITING_DIFF_APPROVAL | Presenting diff to user | diff staged, awaiting user approval | #FCE4EC |

## Session Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| CREATED | Session record initialized | API-02 CREATE Session | #E3F2FD |
| ACTIVE | Session accepting messages | Session created or restored | #2E7D32 |
| SAVED | Session persisted to disk | API-04 UPDATE Session | #1565C0 |
| RESTORED | Session loaded from disk | API-03 GET Session | #1E88E5 |
| BRANCHED | Session forked from parent | WRL-04 FORK Session | #7B1FA2 |
| CLOSED | Session terminated | API-05 DELETE Session | #757575 |

## Plan Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No plan active | Default state | #ECEFF1 |
| BUILDING | Plan being constructed | AGT-07 QUEUE Plan | #FFF3E0 |
| QUEUED | Plan queued for approval | Plan construction complete | #E3F2FD |
| APPROVED | Plan approved by user | AGT-08 APPROVE Plan | #2E7D32 |
| EXECUTING | Plan steps being executed | Plan approved, execution started | #A5D6A7 |
| COMPLETED | All plan steps finished | Implicit: agent loop finishes all steps | #1B5E20 |
| REJECTED | Plan rejected by user | User rejects plan | #B71C1C |

## Plugin Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCOVERED | Plugin found on filesystem | PLG-01 DISCOVER Plugins | #ECEFF1 |
| LOADING | Plugin manifest being parsed | PLG-02 LOAD Manifest | #FFF3E0 |
| LOADED | Plugin manifest parsed, tools registered | PLG-03 REGISTER Plugin Tools | #90CAF9 |
| ENABLED | Plugin active and available | PLG-05 ENABLE Plugin | #2E7D32 |
| DISABLED | Plugin deactivated | PLG-06 DISABLE Plugin | #CE93D8 |
| ERROR | Plugin failed to load or crashed | Load error or runtime exception | #EF5350 |

## Diagrams

| File | Scope |
|------|-------|
| `sm_agent_lifecycle.puml` | Agent process FSM — 17 states (API-First) |
| `sm_session_lifecycle.puml` | Session entity lifecycle — 6 states (API-First) |
| `sm_plan_lifecycle.puml` | Plan entity lifecycle — 7 states |
| `sm_plugin_lifecycle.puml` | Plugin entity lifecycle — 6 states |
| `sm_subagent_lifecycle.puml` | Subagent entity lifecycle — 5 states (IDLE→SPAWNING→RUNNING→COMPLETED/FAILED) |

## Notes

- Agent SM is a **process FSM**, not an entity lifecycle. States are transient agent
  states during task execution, not persisted lifecycle states. SMT ownership
  rules from `sm.md` do not apply (documented deviation).
- Session, Plan, and Plugin SMs are **entity lifecycles** with persisted state.
  SMT ownership rules apply: one lifecycle-write UC per target state.
- All hex colors are canonical — state-machine diagrams use `state "STATE" as STATE #HEX`
  syntax per PlantUML standard.
- **Transition labels** use UC-ID-only convention (e.g., `AGT-01`, `PRV-02`, `SAF-02`).
  No human-readable suffixes. Multiple transitions from one state may share a UC ID
  when the same action produces different outcomes (e.g., `PRV-02` → RESPONDING, TOOL_EXEC, ERROR).
- **API-First:** All entry/exit transitions in Agent SM use `API-06` as the sole entry gate.
  Session lifecycle mutations use API UCs (API-02 through API-05).

## Lifecycle-Write UC Mapping (SMT Ownership)

One lifecycle-write UC per target state. This table is the authoritative reference.

### Session Lifecycle (API-First)

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CREATED | API-02 CREATE Session | Session record initialized |
| ACTIVE | API-02 CREATE Session | Session accepting messages (after init/resume) |
| SAVED | API-04 UPDATE Session | Session persisted to disk |
| RESTORED | API-03 GET Session | Session loaded from disk |
| BRANCHED | WRL-04 FORK Session | Session forked from parent |
| CLOSED | API-05 DELETE Session | Session terminated (quit or error) |

### Plan Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| BUILDING | AGT-07 QUEUE Plan | Plan being constructed |
| QUEUED | AGT-07 QUEUE Plan | Plan construction complete, queued for approval |
| APPROVED | AGT-08 APPROVE Plan | Plan approved by user |
| EXECUTING | AGT-08 APPROVE Plan | Plan execution starts |
| COMPLETED | AGT-01 PROCESS User Task | Agent loop finishes all steps |
| REJECTED | AGT-08 APPROVE Plan | Plan rejected by user |

### Plugin Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| DISCOVERED | PLG-01 DISCOVER Plugins | Plugin found on filesystem |
| LOADING | PLG-02 LOAD Manifest | Plugin manifest being parsed |
| LOADED | PLG-03 REGISTER Plugin Tools | Manifest parsed, tools registered |
| ENABLED | PLG-05 ENABLE Plugin | Plugin active and available |
| DISABLED | PLG-06 DISABLE Plugin | Plugin deactivated |
| ERROR | PLG-01 DISCOVER Plugins | Load error or runtime exception (re-discover recovers) |



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_session_lifecycle.puml ---

@startuml sm_session_lifecycle
' ============================================================
' Title:     nasim — Session Lifecycle State Machine (API-First)
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Session (persisted to disk).
'            All mutations routed through API Group (Entry Gate).
' Milestone: v1.0
' Version:   8.0.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' ============================================================

title nasim — Session Lifecycle (API-First)

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> CREATED : API-02

state "CREATED" as CREATED #E3F2FD
CREATED : Session record initialized.
CREATED : API-02 CREATE Session.

state "ACTIVE" as ACTIVE #2E7D32
ACTIVE : Session accepting messages.
ACTIVE : API-03 GET Session, API-06 DISPATCH Message.

state "SAVED" as SAVED #1565C0
SAVED : Session persisted to disk.
SAVED : API-01 LIST Sessions, API-04 UPDATE Session.

state "RESTORED" as RESTORED #1E88E5
RESTORED : Session loaded from disk.
RESTORED : API-03 GET Session.

state "BRANCHED" as BRANCHED #7B1FA2
BRANCHED : Session forked from parent.
BRANCHED : WRL-04 FORK Session.

state "CLOSED" as CLOSED #757575
CLOSED : Session terminated.
CLOSED : Terminal state.

CREATED --> ACTIVE : API-02
ACTIVE --> SAVED : API-04
ACTIVE --> BRANCHED : WRL-04
ACTIVE --> CLOSED : API-05
SAVED --> RESTORED : API-03
RESTORED --> ACTIVE : API-02
RESTORED --> SAVED : API-04
RESTORED --> CLOSED : API-05
BRANCHED --> ACTIVE : API-02
BRANCHED --> CLOSED : API-05
SAVED --> CLOSED : API-05

CLOSED --> [*]

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_subagent_lifecycle.puml ---

@startuml sm_subagent_lifecycle
' ============================================================
' Title:     nasim — Subagent Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for SubagentCoordinator child agent processes.
'            States: IDLE → SPAWNING → RUNNING → COMPLETED | FAILED
' Milestone: v1.0
' Version:   9.1.0
' Source:    docs/SM/README.md
' Review:    CAR audit 2026-06-26
' Convention: All transitions are triggered by the corresponding UC ID
'             as listed in docs/UC/README.md.
' ============================================================

title nasim — Subagent Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> IDLE

state "IDLE" as IDLE #ECEFF1
IDLE : No child agent active.
IDLE : Default state.

state "SPAWNING" as SPAWNING #E3F2FD
SPAWNING : Child agent process initializing.
SPAWNING : Session created, orchestrator assigned.

state "RUNNING" as RUNNING #FFF3E0
RUNNING : Child agent executing task.
RUNNING : Provider calls, tool dispatches in progress.

state "COMPLETED" as COMPLETED #E8F5E9
COMPLETED : Child agent finished successfully.
COMPLETED : Results aggregated to parent.

state "FAILED" as FAILED #FFEBEE
FAILED : Child agent encountered unrecoverable error.
FAILED : Error reported to parent, child cleaned up.

IDLE --> SPAWNING : AGT-09
SPAWNING --> RUNNING : AGT-09
SPAWNING --> FAILED : AGT-09
RUNNING --> COMPLETED : AGT-10
RUNNING --> FAILED : AGT-14
COMPLETED --> IDLE : AGT-10
FAILED --> IDLE : AGT-14

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_agent_lifecycle.puml ---

@startuml sm_agent_lifecycle
' ============================================================
' Title:     nasim — Agent Lifecycle State Machine (API-First)
' Boundary:  nasim code agent
' Purpose:   Process FSM showing all agent states and transitions.
'            All entry points route through the API (API-06).
' Milestone: v1.0
' Version:   8.0.0
' Source:    CAR refinement loop — API-First transformation
' Review:    —
' Note:      Process FSM, not entity lifecycle. SMT rules from sm.md
'            do not apply (documented deviation).
' Convention: All transitions are triggered by the corresponding UC ID
'            (e.g., EVL-01, EDT-10, AGT-07) as listed in docs/UC/README.md.
'            Entry/exit transitions use API-06 (DISPATCH Message) as the
'            sole entry gate for all interface containers.
' ============================================================

title nasim — Agent Lifecycle (API-First)

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> IDLE : AGT-01

state "IDLE" as IDLE #ECEFF1
IDLE : Agent waiting for user input.
IDLE : No active provider call.

state "LISTENING" as LISTENING #E8EAF6
LISTENING : Receiving and parsing user input.
LISTENING : API-06 DISPATCH Message (via any interface).

state "THINKING" as THINKING #FFF3E0
THINKING : LLM processing messages.
THINKING : PRV-02 REQUEST Chat or PRV-03 STREAM Chat.

state "TOOL_EXEC" as TOOL_EXEC #F3E5F5
TOOL_EXEC : Executing a tool call.
TOOL_EXEC : AGT-02 DISPATCH Tool Call.

state "RESPONDING" as RESPONDING #E8F5E9
RESPONDING : Streaming final text to user via API SSE.
RESPONDING : API-06 DISPATCH Message (SSE response).

state "ERROR" as ERROR #FFEBEE
ERROR : Error occurred.
ERROR : AGT-14 HANDLE Error.

state "COMPACTING" as COMPACTING #E0F2F1
COMPACTING : Summarizing old exchanges.
COMPACTING : AGT-06 COMPACT Context.

state "AWAITING_APPROVAL" as AWAITING_APPROVAL #FFF9C4
AWAITING_APPROVAL : Waiting for user permission.
AWAITING_APPROVAL : SAF-02 REQUEST Approval.

state "PLANNING" as PLANNING #E3F2FD
PLANNING : Plan mode, tool calls queued.
PLANNING : AGT-07 QUEUE Plan.

state "HOOK_RUNNING" as HOOK_RUNNING #FFFDE7
HOOK_RUNNING : Pre/post hook executing.
HOOK_RUNNING : HK-02..05 DISPATCH Hook.

state "ROUTING" as ROUTING #EDE7F6
ROUTING : Model selection in progress.
ROUTING : RTG-01 SELECT Model.

state "SERVING" as SERVING #E0F7FA
SERVING : API processing request from any interface.
SERVING : API-06 DISPATCH Message.

state "EVALUATING" as EVALUATING #F9FBE7
EVALUATING : Evaluating task completion.
EVALUATING : EVL-01 EVALUATE Task.

state "REVIEWING" as REVIEWING #FFF8E1
REVIEWING : LLM review of results.
REVIEWING : EVL-04 VALIDATE With LLM.

state "RETRYING" as RETRYING #FBE9E7
RETRYING : Retrying with feedback.
RETRYING : EVL-06 COORDINATE Retry.

state "STAGING" as STAGING #F1F8E9
STAGING : Diff sandbox staging.
STAGING : EDT-10 STAGE Diff.

state "AWAITING_DIFF_APPROVAL" as AWAITING_DIFF_APPROVAL #FCE4EC
AWAITING_DIFF_APPROVAL : Presenting diff to user.
AWAITING_DIFF_APPROVAL : SAF-02 REQUEST Approval.

' ============================================================
' Entry transitions: ALL go through API-06 (sole entry gate)
' ============================================================

IDLE --> LISTENING : API-06
IDLE --> SERVING : API-06
IDLE --> [*] : API-06

LISTENING --> THINKING : API-06

THINKING --> RESPONDING : PRV-02
THINKING --> TOOL_EXEC : PRV-02
THINKING --> COMPACTING : AGT-06
THINKING --> ROUTING : RTG-01
THINKING --> ERROR : PRV-02
THINKING --> RESPONDING : API-06
THINKING --> EVALUATING : EVL-01

ROUTING --> THINKING : RTG-01

TOOL_EXEC --> THINKING : AGT-02
TOOL_EXEC --> AWAITING_APPROVAL : SAF-02
TOOL_EXEC --> HOOK_RUNNING : HK-02
TOOL_EXEC --> ERROR : AGT-02
TOOL_EXEC --> STAGING : EDT-10

HOOK_RUNNING --> TOOL_EXEC : HK-02
HOOK_RUNNING --> IDLE : HK-02

AWAITING_APPROVAL --> TOOL_EXEC : SAF-02
AWAITING_APPROVAL --> IDLE : SAF-02

COMPACTING --> THINKING : AGT-06

' ============================================================
' Exit transitions: response flows back through API-06
' ============================================================

RESPONDING --> IDLE : API-06

ERROR --> IDLE : AGT-14

SERVING --> THINKING : API-06
SERVING --> IDLE : API-06

IDLE --> PLANNING : AGT-07
PLANNING --> IDLE : AGT-07

EVALUATING --> REVIEWING : EVL-01
EVALUATING --> RETRYING : EVL-01
EVALUATING --> THINKING : EVL-01

REVIEWING --> THINKING : EVL-04
REVIEWING --> RETRYING : EVL-04

RETRYING --> THINKING : EVL-06
RETRYING --> ERROR : EVL-06

STAGING --> AWAITING_DIFF_APPROVAL : EDT-10
STAGING --> ERROR : EDT-10

AWAITING_DIFF_APPROVAL --> TOOL_EXEC : SAF-02
AWAITING_DIFF_APPROVAL --> IDLE : SAF-02

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_plugin_lifecycle.puml ---

@startuml sm_plugin_lifecycle
' ============================================================
' Title:     nasim — Plugin Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Plugin (persisted in config)
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Plugin Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> DISCOVERED : PLG-01

state "DISCOVERED" as DISCOVERED #ECEFF1
DISCOVERED : Plugin found on filesystem.
DISCOVERED : PLG-01 DISCOVER Plugins.

state "LOADING" as LOADING #FFF3E0
LOADING : Plugin manifest being parsed.
LOADING : PLG-02 LOAD Manifest.

state "LOADED" as LOADED #90CAF9
LOADED : Plugin manifest parsed, tools registered.
LOADED : PLG-03 REGISTER Plugin Tools.

state "ENABLED" as ENABLED #2E7D32
ENABLED : Plugin active and available.
ENABLED : PLG-05 ENABLE Plugin.

state "DISABLED" as DISABLED #CE93D8
DISABLED : Plugin deactivated.
DISABLED : PLG-06 DISABLE Plugin.

state "ERROR" as ERROR #EF5350
ERROR : Plugin failed to load or crashed.
ERROR : Load error or runtime exception.

DISCOVERED --> LOADING : PLG-02
DISCOVERED --> ERROR : PLG-01
LOADING --> LOADED : PLG-03
LOADING --> ERROR : PLG-02
LOADED --> ENABLED : PLG-05
LOADED --> DISABLED : PLG-06
ENABLED --> DISABLED : PLG-06
DISABLED --> ENABLED : PLG-05
ENABLED --> ERROR : PLG-01
LOADED --> ERROR : PLG-03

ERROR --> DISCOVERED : PLG-01

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_plan_lifecycle.puml ---

@startuml sm_plan_lifecycle
' ============================================================
' Title:     nasim — Plan Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Plan (persisted in PlanSession)
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Plan Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> EMPTY : AGT-07

state "EMPTY" as EMPTY #ECEFF1
EMPTY : No plan active.
EMPTY : Default state.

state "BUILDING" as BUILDING #FFF3E0
BUILDING : Plan being constructed.
BUILDING : AGT-07 QUEUE Plan.

state "QUEUED" as QUEUED #E3F2FD
QUEUED : Plan queued for approval.
QUEUED : Plan construction complete.

state "APPROVED" as APPROVED #2E7D32
APPROVED : Plan approved by user.
APPROVED : AGT-08 APPROVE Plan.

state "EXECUTING" as EXECUTING #A5D6A7
EXECUTING : Plan steps being executed.
EXECUTING : Approved plan, tool calls dispatched.

state "COMPLETED" as COMPLETED #1B5E20
COMPLETED : All plan steps finished.
COMPLETED : Terminal state.

state "REJECTED" as REJECTED #B71C1C
REJECTED : Plan rejected by user.
REJECTED : Terminal state.

EMPTY --> BUILDING : AGT-07
BUILDING --> QUEUED : AGT-07
BUILDING --> EMPTY : AGT-07
QUEUED --> APPROVED : AGT-08
QUEUED --> REJECTED : AGT-08
APPROVED --> EXECUTING : AGT-08
EXECUTING --> COMPLETED : AGT-01
EXECUTING --> EMPTY : AGT-14
COMPLETED --> [*] : AGT-01
REJECTED --> [*] : AGT-08

@enduml

