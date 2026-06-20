

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
| COMPLETED | All plan steps finished | Last step executed | #1B5E20 |
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
| COMPLETED | AGT-08 APPROVE Plan | Implicit: agent loop finishes all steps |
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
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Session Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> CREATED : SSN-01 PERSIST Session

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

CREATED --> ACTIVE : SSN-01 session initialized
ACTIVE --> SAVED : SSN-01 explicit save
ACTIVE --> BRANCHED : WRL-04 fork session
ACTIVE --> CLOSED : SSN-01 /quit or explicit close
SAVED --> RESTORED : SSN-04 restore session
RESTORED --> ACTIVE : SSN-04 session resumed
RESTORED --> SAVED : SSN-01 save after restore
BRANCHED --> ACTIVE : SSN-01 child session starts
BRANCHED --> CLOSED : SSN-01 child session closed
SAVED --> CLOSED : SSN-01 explicit close after save

CLOSED --> [*]

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_agent_lifecycle.puml ---

@startuml sm_agent_lifecycle
' ============================================================
' Title:     nasim — Agent Lifecycle State Machine
' Boundary:  nasim code agent CLI + HTTP API
' Purpose:   Process FSM showing all agent states and transitions
' Milestone: v1.0
' Version:   5.0.0
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

[*] --> IDLE : Startup / AGT-01 init

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
TOOL_EXEC : Executing a tool call.
TOOL_EXEC : AGT-02 DISPATCH Tool Call.

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

IDLE --> LISTENING : CLI-01 PROCESS User Input
IDLE --> SERVING : SRV-06 HTTP request received
IDLE --> [*] : /quit or EOF

LISTENING --> THINKING : CLI-01 input parsed

THINKING --> RESPONDING : PRV-02 LLM returns text
THINKING --> TOOL_EXEC : PRV-02 LLM returns tool_calls
THINKING --> COMPACTING : token_count > budget
THINKING --> ROUTING : RTG-01 ModelRouter resolving
THINKING --> ERROR : PRV-02 LLM call fails
THINKING --> SERVING : Response to HTTP client
THINKING --> EVALUATING : task_complete AND evaluation_enabled

ROUTING --> THINKING : RTG-01 Model selected

TOOL_EXEC --> THINKING : AGT-02 Tool result appended
TOOL_EXEC --> AWAITING_APPROVAL : SAF-03 safety_mode=ask AND unsafe
TOOL_EXEC --> HOOK_RUNNING : HK-02 pre-tool hook registered
TOOL_EXEC --> ERROR : AGT-02 Tool execution fails
TOOL_EXEC --> STAGING : EDT-10 diff_sandbox mode

HOOK_RUNNING --> TOOL_EXEC : HK-02 Hook allows
HOOK_RUNNING --> IDLE : HK-02 Hook denies

AWAITING_APPROVAL --> TOOL_EXEC : User approves (y)
AWAITING_APPROVAL --> IDLE : User rejects (N)

COMPACTING --> THINKING : AGT-06 Compaction complete

RESPONDING --> IDLE : CLI-03 Response complete

ERROR --> IDLE : AGT-14 Error displayed

SERVING --> THINKING : SRV-06 Request processed
SERVING --> IDLE : SRV-06 Response complete

IDLE --> PLANNING : AGT-07 /plan command
PLANNING --> IDLE : AGT-07 /plan off

EVALUATING --> REVIEWING : EVL-01 success checks passed
EVALUATING --> RETRYING : EVL-01 success checks failed
EVALUATING --> THINKING : EVL-01 evaluation passed

REVIEWING --> THINKING : EVL-04 review approved
REVIEWING --> RETRYING : EVL-04 review rejected

RETRYING --> THINKING : EVL-06 retry with feedback
RETRYING --> ERROR : EVL-06 max retries exceeded

STAGING --> AWAITING_DIFF_APPROVAL : EDT-10 present diff

AWAITING_DIFF_APPROVAL --> TOOL_EXEC : User approves diff
AWAITING_DIFF_APPROVAL --> IDLE : User rejects diff

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_plugin_lifecycle.puml ---

@startuml sm_plugin_lifecycle
' ============================================================
' Title:     nasim — Plugin Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Plugin (persisted in config)
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Plugin Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> DISCOVERED : PLG-01 scan

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

DISCOVERED --> LOADING : PLG-02 load manifest
DISCOVERED --> ERROR : PLG-01 manifest not found
LOADING --> LOADED : PLG-03 tools registered
LOADING --> ERROR : PLG-02 parse error
LOADED --> ENABLED : PLG-05 enable
LOADED --> DISABLED : PLG-06 disable
ENABLED --> DISABLED : PLG-06 disable
DISABLED --> ENABLED : PLG-05 re-enable
ENABLED --> ERROR : PLG-01 runtime error
LOADED --> ERROR : PLG-03 registration error

ERROR --> DISCOVERED : PLG-01 re-discover

@enduml



--- SOURCE: /home/salim/prj/salim/nasim/code/nasim/docs/SM/sm_plan_lifecycle.puml ---

@startuml sm_plan_lifecycle
' ============================================================
' Title:     nasim — Plan Lifecycle State Machine
' Boundary:  nasim code agent
' Purpose:   Entity lifecycle for Plan (persisted in PlanSession)
' Milestone: v1.0
' Version:   1.0.0
' Source:    docs/UC/README.md
' Review:    docs/audit/audit.2026.06.20.sq-sm-chain.car.md
' ============================================================

title nasim — Plan Lifecycle

skinparam state {
  BackgroundColor #FFFFFF
  BorderColor #424242
  FontColor #000000
}

[*] --> EMPTY : Startup

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

EMPTY --> BUILDING : AGT-07 /plan command
BUILDING --> QUEUED : AGT-07 plan queued
BUILDING --> EMPTY : AGT-07 /plan off
QUEUED --> APPROVED : AGT-08 /approve
QUEUED --> REJECTED : AGT-08 user rejects
APPROVED --> EXECUTING : AGT-08 execution starts
EXECUTING --> COMPLETED : AGT-08 all steps done
EXECUTING --> EMPTY : Execution error, plan discarded
COMPLETED --> [*]
REJECTED --> [*]

@enduml

