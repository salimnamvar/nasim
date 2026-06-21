

--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/README.md ---

# nasim — State Machine Inventory

## Agent Lifecycle States (Process FSM)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | Agent waiting for user input | Startup or response complete | #ECEFF1 |
| LISTENING | Receiving and parsing user input | User types input | #E8EAF6 |
| THINKING | LLM processing messages | Input parsed, messages built | #FFF3E0 |
| TOOL_EXEC | Executing a tool call | LLM returns tool_calls | #F3E5F5 |
| RESPONDING | Streaming final text to user | LLM returns text only | #E8F5E9 |
| ERROR | Error occurred | LLM call or tool exec fails | #FFEBEE |
| COMPACTING | Summarizing old exchanges | token_count > context_budget | #E0F2F1 |
| AWAITING_APPROVAL | Waiting for user permission | safety_mode=ask AND unsafe tool | #FFF9C4 |
| PLANNING | Plan mode, tool calls queued | /plan command entered | #E3F2FD |
| HOOK_RUNNING | Pre/post hook executing | tool or LLM call with hooks | #FFFDE7 |
| ROUTING | Model selection in progress | ModelRouter resolving model | #EDE7F6 |
| SERVING | HTTP server handling request | HTTP client sends request | #E0F7FA |
| EVALUATING | Evaluating task completion | task_complete AND evaluation_enabled | #F9FBE7 |
| REVIEWING | LLM review of results | success checks passed, optional review | #FFF8E1 |
| RETRYING | Retrying with feedback | success checks failed or review rejected | #FBE9E7 |
| STAGING | Diff sandbox staging | tool exec in diff_sandbox mode | #F1F8E9 |
| AWAITING_DIFF_APPROVAL | Presenting diff to user | diff staged, awaiting user approval | #FCE4EC |

## Session Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| CREATED | Session record initialized | POST /v1/sessions | #E3F2FD |
| ACTIVE | Session accepting messages | Session created or restored | #2E7D32 |
| SAVED | Session persisted to disk | SSN-01 PERSIST Session | #1565C0 |
| RESTORED | Session loaded from disk | SSN-04 RESTORE Session | #1E88E5 |
| BRANCHED | Session forked from parent | WRL-04 FORK Session | #7B1FA2 |
| CLOSED | Session terminated | /quit or explicit close | #757575 |

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
| `sm_agent_lifecycle.puml` | Agent process FSM — 17 states |
| `sm_session_lifecycle.puml` | Session entity lifecycle — 6 states |
| `sm_plan_lifecycle.puml` | Plan entity lifecycle — 7 states |
| `sm_plugin_lifecycle.puml` | Plugin entity lifecycle — 6 states |

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

## Lifecycle-Write UC Mapping (SMT Ownership)

One lifecycle-write UC per target state. This table is the authoritative reference.

### Session Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CREATED | SSN-01 PERSIST Session | Session record initialized |
| ACTIVE | SSN-01 PERSIST Session | Session accepting messages (after init/resume) |
| SAVED | SSN-01 PERSIST Session | Session persisted to disk |
| RESTORED | SSN-04 RESTORE Session | Session loaded from disk |
| BRANCHED | WRL-04 FORK Session | Session forked from parent |
| CLOSED | SSN-01 PERSIST Session | Session terminated (quit or error) |

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
' Title:     nasim — Session Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Session (persisted to disk)
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Session Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> CREATED : SSN-01

state "CREATED" as CREATED #E3F2FD
CREATED : Session record initialized.
CREATED : SSN-01 PERSIST Session owns all writes here.

state "ACTIVE" as ACTIVE #2E7D32
ACTIVE : Session accepting messages.
ACTIVE : SSN-02 READ Session, SRV-06 DISPATCH Message.

state "SAVED" as SAVED #1565C0
SAVED : Session persisted to disk.
SAVED : SSN-01 PERSIST Session.

state "RESTORED" as RESTORED #1E88E5
RESTORED : Session loaded from disk.
RESTORED : SSN-04 RESTORE Session.

state "BRANCHED" as BRANCHED #7B1FA2
BRANCHED : Session forked from parent.
BRANCHED : WRL-04 FORK Session.

state "CLOSED" as CLOSED #757575
CLOSED : Session terminated.
CLOSED : Terminal state.

CREATED --> ACTIVE : SSN-01
ACTIVE --> SAVED : SSN-01
ACTIVE --> BRANCHED : WRL-04
ACTIVE --> CLOSED : SSN-01
SAVED --> RESTORED : SSN-04
RESTORED --> ACTIVE : SSN-01
RESTORED --> SAVED : SSN-01
BRANCHED --> ACTIVE : SSN-01
BRANCHED --> CLOSED : SSN-01
SAVED --> CLOSED : SSN-01

CLOSED --> [*]

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_agent_lifecycle.puml ---

@startuml sm_agent_lifecycle
' ============================================================
' Title:     nasim — Agent Lifecycle State Machine
' Boundary:  nasim code agent CLI + HTTP API
' Purpose:   Process FSM showing all agent states and transitions
' Milestone: v1.0
' Version:   6.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' Note:      Process FSM, not entity lifecycle. SMT rules from sm.md
'            do not apply (documented deviation).
' Convention: All transitions are triggered by the corresponding UC ID
'            (e.g., EVL-01, EDT-10, AGT-07) as listed in docs/UC/README.md.
' ============================================================

title nasim — Agent Lifecycle

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
LISTENING : CLI-01 PROCESS User Input.

state "THINKING" as THINKING #FFF3E0
THINKING : LLM processing messages.
THINKING : PRV-02 REQUEST Chat or PRV-03 STREAM Chat.

state "TOOL_EXEC" as TOOL_EXEC #F3E5F5
TOOL_EXEC : ToolRegistry executing tool call.
TOOL_EXEC : AGT-02 DISPATCH Tool Call.
TOOL_EXEC : Delegated by AgentOrchestrator.

state "RESPONDING" as RESPONDING #E8F5E9
RESPONDING : Streaming final text to user.
RESPONDING : CLI-03 STREAM Output.

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
SERVING : HTTP server handling request.
SERVING : SRV-06 DISPATCH Message.

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

IDLE --> LISTENING : CLI-01
IDLE --> SERVING : SRV-06
IDLE --> [*] : CLI-02

LISTENING --> THINKING : CLI-01

THINKING --> RESPONDING : PRV-02
THINKING --> TOOL_EXEC : PRV-02
THINKING --> COMPACTING : AGT-06
THINKING --> ROUTING : RTG-01
THINKING --> ERROR : PRV-02
THINKING --> RESPONDING : SRV-06
THINKING --> EVALUATING : EVL-01

ROUTING --> THINKING : RTG-01

TOOL_EXEC --> THINKING : AGT-02
TOOL_EXEC --> AWAITING_APPROVAL : SAF-03
TOOL_EXEC --> HOOK_RUNNING : HK-02
TOOL_EXEC --> ERROR : AGT-02
TOOL_EXEC --> STAGING : EDT-10

HOOK_RUNNING --> TOOL_EXEC : HK-02
HOOK_RUNNING --> IDLE : HK-02

AWAITING_APPROVAL --> TOOL_EXEC : SAF-02
AWAITING_APPROVAL --> IDLE : SAF-02

COMPACTING --> THINKING : AGT-06

RESPONDING --> IDLE : CLI-03

ERROR --> IDLE : AGT-14

SERVING --> THINKING : SRV-06
SERVING --> IDLE : SRV-06

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

