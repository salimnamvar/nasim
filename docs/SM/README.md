# nasim — State Machine Inventory (API-First)

## Agent Lifecycle States (Process FSM)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | Agent waiting for user input | Startup or response complete | #ECEFF1 |
| LISTENING | Receiving and parsing user input | API-06 DISPATCH Message received | #E8EAF6 |
| THINKING | LLM processing messages | Input parsed, messages built | #D7CCC8 |
| TOOL_EXEC | Executing a tool call | LLM returns tool_calls | #B2DFDB |
| RESPONDING | Streaming final text to user via API SSE | LLM returns text only | #D1C4E9 |
| ERROR | Error occurred | LLM call or tool exec fails | #FFEBEE |
| COMPACTING | Summarizing old exchanges | token_count > context_budget | #E0F2F1 |
| AWAITING_APPROVAL | Waiting for user permission | safety_mode=ask AND unsafe tool | #FFF9C4 |
| PLANNING | Plan mode, tool calls queued | /plan command entered | #FFCCBC |
| HOOK_RUNNING | Pre/post hook executing | tool or LLM call with hooks | #FFFDE7 |
| ROUTING | Model selection in progress | ModelRouter resolving model | #EDE7F6 |
| SERVING | API processing request from any interface | API-06 DISPATCH Message | #E0F7FA |
| EVALUATING | Evaluating task completion | task_complete AND evaluation_enabled | #F9FBE7 |
| REVIEWING | LLM review of results | success checks passed, optional review | #FFF8E1 |
| RETRYING | Retrying with feedback | success checks failed or review rejected | #FBE9E7 |
| STAGING | Diff sandbox staging | tool exec in diff_sandbox mode | #F1F8E9 |
| AWAITING_DIFF_APPROVAL | Presenting diff to user | SAF-02 REQUEST Approval | #FCE4EC |

> **API-First Entry:** All entry/exit transitions use `API-06` (DISPATCH Message) as the sole entry gate. No interface container may bypass the API.

### Transitions from STAGING

| From | To | UC ID | Condition |
|------|----|-------|-----------|
| STAGING | AWAITING_DIFF_APPROVAL | EDT-10 | Diff computed successfully |
| STAGING | ERROR | EDT-10 | Diff computation failed (file deleted, conflict, algorithm error) |

## Session Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| CREATED | Session record initialized | API-02 CREATE Session | #BBDEFB |
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
| `sm_plugin_lifecycle.puml` | Plugin entity lifecycle — 6 states (+ 2 terminal exits) |
| `sm_subagent_lifecycle.puml` | Subagent entity lifecycle — 5 states (IDLE→SPAWNING→RUNNING→COMPLETED/FAILED) + 2 terminal exits |

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

## Transition Matrices

### Agent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | AGT-01 | Process startup |
| IDLE | LISTENING | API-06 | DISPATCH Message received |
| IDLE | SERVING | API-06 | API request received |
| IDLE | PLANNING | AGT-07 | /plan command entered |
| LISTENING | THINKING | API-06 | Input parsed, messages built |
| SERVING | THINKING | API-06 | API request processed |
| SERVING | IDLE | API-06 | API request complete |
| THINKING | RESPONDING | PRV-02 | LLM returns text only |
| THINKING | TOOL_EXEC | PRV-02 | LLM returns tool_calls |
| THINKING | COMPACTING | AGT-06 | token_count > context_budget |
| THINKING | ROUTING | RTG-01 | ModelRouter resolving model |
| THINKING | ERROR | PRV-02 | Provider call failed |
| THINKING | EVALUATING | EVL-01 | task_complete AND evaluation_enabled |
| ROUTING | THINKING | RTG-01 | Model selected |
| TOOL_EXEC | THINKING | AGT-02 | Tool call complete |
| TOOL_EXEC | AWAITING_APPROVAL | SAF-02 | safety_mode=ask AND unsafe tool |
| TOOL_EXEC | HOOK_RUNNING | HK-02 | Pre/post hook configured |
| TOOL_EXEC | ERROR | AGT-02 | Tool execution failed |
| TOOL_EXEC | STAGING | EDT-10 | diff_sandbox mode active |
| HOOK_RUNNING | TOOL_EXEC | HK-02 | Hook execution complete |
| HOOK_RUNNING | IDLE | HK-02 | Hook execution complete (no tool) |
| AWAITING_APPROVAL | TOOL_EXEC | SAF-02 | User approves |
| AWAITING_APPROVAL | IDLE | SAF-02 | User denies |
| COMPACTING | THINKING | AGT-06 | Context compacted |
| RESPONDING | IDLE | API-06 | Response streamed to user |
| ERROR | IDLE | AGT-14 | Error handled |
| PLANNING | IDLE | AGT-07 | Plan mode exited |
| EVALUATING | REVIEWING | EVL-01 | Evaluation passed |
| EVALUATING | RETRYING | EVL-01 | Evaluation failed |
| EVALUATING | THINKING | EVL-01 | Retry with feedback |
| REVIEWING | THINKING | EVL-04 | LLM review passed |
| REVIEWING | RETRYING | EVL-04 | LLM review rejected |
| RETRYING | THINKING | EVL-06 | Retry with feedback |
| RETRYING | ERROR | EVL-06 | Retry exhausted |
| STAGING | AWAITING_DIFF_APPROVAL | EDT-10 | Diff computed successfully |
| STAGING | ERROR | EDT-10 | Diff computation failed |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAF-02 | User approves diff |
| AWAITING_DIFF_APPROVAL | IDLE | SAF-02 | User rejects diff |

### Session Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | CREATED | API-02 | Session record initialized |
| CREATED | ACTIVE | API-02 | Session ready for messages |
| ACTIVE | SAVED | API-04 | Session persisted to disk |
| ACTIVE | BRANCHED | WRL-04 | Session forked from parent |
| ACTIVE | CLOSED | API-05 | Session terminated |
| SAVED | RESTORED | API-03 | Session loaded from disk |
| SAVED | CLOSED | API-05 | Session terminated |
| RESTORED | ACTIVE | API-02 | Session ready for messages |
| RESTORED | SAVED | API-04 | Session persisted to disk |
| RESTORED | CLOSED | API-05 | Session terminated |
| BRANCHED | ACTIVE | API-02 | Session ready for messages |
| BRANCHED | CLOSED | API-05 | Session terminated |
| CLOSED | [*] | — | Terminal state |

### Plan Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | EMPTY | AGT-07 | No plan active |
| EMPTY | BUILDING | AGT-07 | /plan command entered |
| BUILDING | QUEUED | AGT-07 | Plan construction complete |
| BUILDING | EMPTY | AGT-07 | Plan cancelled |
| QUEUED | APPROVED | AGT-08 | User approves plan |
| QUEUED | REJECTED | AGT-08 | User rejects plan |
| APPROVED | EXECUTING | AGT-08 | Execution started |
| EXECUTING | COMPLETED | AGT-01 | All plan steps finished |
| EXECUTING | EMPTY | AGT-14 | Execution failed or cancelled |
| COMPLETED | [*] | AGT-01 | Terminal state |
| REJECTED | [*] | AGT-08 | Terminal state |

### Plugin Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | DISCOVERED | PLG-01 | Plugin found on filesystem |
| DISCOVERED | LOADING | PLG-02 | Manifest parsing starts |
| DISCOVERED | ERROR | PLG-01 | Plugin discovery failed |
| LOADING | LOADED | PLG-03 | Manifest parsed, tools registered |
| LOADING | ERROR | PLG-02 | Manifest parsing failed |
| LOADED | ENABLED | PLG-05 | Plugin activated |
| LOADED | DISABLED | PLG-06 | Plugin deactivated |
| LOADED | ERROR | PLG-03 | Tool registration failed |
| ENABLED | DISABLED | PLG-06 | Plugin deactivated |
| ENABLED | ERROR | PLG-01 | Runtime exception |
| ENABLED | [*] | PLG-06 | Plugin unloaded |
| DISABLED | ENABLED | PLG-05 | Plugin activated |
| DISABLED | [*] | PLG-06 | Plugin unloaded |
| ERROR | DISCOVERED | PLG-01 | Re-discovery (recovery) |

### Subagent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | AGT-09 | Default state |
| IDLE | SPAWNING | AGT-09 | Child agent spawn requested |
| SPAWNING | RUNNING | AGT-09 | Child agent initialized |
| SPAWNING | FAILED | AGT-09 | Spawn failed |
| RUNNING | COMPLETED | AGT-10 | Task finished successfully |
| RUNNING | FAILED | AGT-14 | Unrecoverable error |
| COMPLETED | IDLE | AGT-10 | Results aggregated to parent |
| COMPLETED | [*] | AGT-10 | Terminal state |
| FAILED | IDLE | AGT-14 | Error reported, cleanup done |
| FAILED | [*] | AGT-14 | Terminal state |

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

## SM → SQ Transition Coverage Tables

> **TRC-SM-05 compliance:** Every SM transition mapped to its implementing SQ diagram.
> Terminal (`[*]`) transitions are state diagram syntax, not implementable transitions — marked `—`.

### sm_agent_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | AGT-01 | Process startup | sq_agent01_process_user_task.puml |
| IDLE | LISTENING | API-06 | DISPATCH Message received | sq_api06_dispatch_message.puml |
| IDLE | SERVING | API-06 | API request received | sq_api06_dispatch_message.puml |
| IDLE | PLANNING | AGT-07 | /plan command entered | sq_agent07_queue_plan.puml |
| IDLE | [*] | — | Shutdown | — |
| LISTENING | THINKING | API-06 | Input parsed, messages built | sq_api06_dispatch_message.puml |
| SERVING | THINKING | API-06 | API request processed | sq_api06_dispatch_message.puml |
| SERVING | IDLE | API-06 | API request complete | sq_api06_dispatch_message.puml |
| THINKING | RESPONDING | PRV-02 | LLM returns text only | sq_provider02_request_chat.puml |
| THINKING | TOOL_EXEC | PRV-02 | LLM returns tool_calls | sq_provider02_request_chat.puml |
| THINKING | COMPACTING | AGT-06 | token_count > context_budget | sq_agent06_compact_context.puml |
| THINKING | ROUTING | RTG-01 | ModelRouter resolving model | sq_router01_select_model.puml |
| THINKING | ERROR | PRV-02 | Provider call failed | sq_provider02_request_chat.puml |
| THINKING | RESPONDING | API-06 | Response dispatched | sq_api06_dispatch_message.puml |
| THINKING | EVALUATING | EVL-01 | task_complete AND evaluation_enabled | sq_evaluation01_evaluate_task.puml |
| ROUTING | THINKING | RTG-01 | Model selected | sq_router01_select_model.puml |
| TOOL_EXEC | THINKING | AGT-02 | Tool call complete | sq_agent02_dispatch_tool_call.puml |
| TOOL_EXEC | AWAITING_APPROVAL | SAF-02 | safety_mode=ask AND unsafe tool | sq_safety02_request_approval.puml |
| TOOL_EXEC | HOOK_RUNNING | HK-02 | Pre/post hook configured | sq_hooks02_dispatch_pre_tool_hook.puml |
| TOOL_EXEC | ERROR | AGT-02 | Tool execution failed | sq_agent02_dispatch_tool_call.puml |
| TOOL_EXEC | STAGING | EDT-10 | diff_sandbox mode active | sq_editstrategy10_stage_diff.puml |
| HOOK_RUNNING | TOOL_EXEC | HK-02 | Hook execution complete | sq_hooks02_dispatch_pre_tool_hook.puml |
| HOOK_RUNNING | IDLE | HK-02 | Hook execution complete (no tool) | sq_hooks02_dispatch_pre_tool_hook.puml |
| AWAITING_APPROVAL | TOOL_EXEC | SAF-02 | User approves | sq_safety02_request_approval.puml |
| AWAITING_APPROVAL | IDLE | SAF-02 | User denies | sq_safety02_request_approval.puml |
| COMPACTING | THINKING | AGT-06 | Context compacted | sq_agent06_compact_context.puml |
| RESPONDING | IDLE | API-06 | Response streamed to user | sq_api06_dispatch_message.puml |
| ERROR | IDLE | AGT-14 | Error handled | sq_agent14_handle_error.puml |
| PLANNING | IDLE | AGT-07 | Plan mode exited | sq_agent07_queue_plan.puml |
| EVALUATING | REVIEWING | EVL-01 | Evaluation passed | sq_evaluation01_evaluate_task.puml |
| EVALUATING | RETRYING | EVL-01 | Evaluation failed | sq_evaluation01_evaluate_task.puml |
| EVALUATING | THINKING | EVL-01 | Retry with feedback | sq_evaluation01_evaluate_task.puml |
| REVIEWING | THINKING | EVL-04 | LLM review passed | sq_evaluation04_validate_with_llm.puml |
| REVIEWING | RETRYING | EVL-04 | LLM review rejected | sq_evaluation04_validate_with_llm.puml |
| RETRYING | THINKING | EVL-06 | Retry with feedback | sq_evaluation06_coordinate_retry.puml |
| RETRYING | ERROR | EVL-06 | Retry exhausted | sq_evaluation06_coordinate_retry.puml |
| STAGING | AWAITING_DIFF_APPROVAL | EDT-10 | Diff computed successfully | sq_editstrategy10_stage_diff.puml |
| STAGING | ERROR | EDT-10 | Diff computation failed | sq_editstrategy10_stage_diff.puml |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAF-02 | User approves diff | sq_safety02_request_approval.puml |
| AWAITING_DIFF_APPROVAL | IDLE | SAF-02 | User rejects diff | sq_safety02_request_approval.puml |

> **Coverage:** 39/39 non-terminal transitions covered. 0 ORPHANs.

### sm_session_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | CREATED | API-02 | Session record initialized | sq_api02_create_session.puml |
| CREATED | ACTIVE | API-02 | Session ready for messages | sq_api02_create_session.puml |
| ACTIVE | SAVED | API-04 | Session persisted to disk | sq_api04_update_session.puml |
| ACTIVE | BRANCHED | WRL-04 | Session forked from parent | sq_wirelog04_fork_session.puml |
| ACTIVE | CLOSED | API-05 | Session terminated | sq_api05_delete_session.puml |
| SAVED | RESTORED | API-03 | Session loaded from disk | sq_api03_get_session.puml |
| SAVED | CLOSED | API-05 | Session terminated | sq_api05_delete_session.puml |
| RESTORED | ACTIVE | API-02 | Session ready for messages | sq_api02_create_session.puml |
| RESTORED | SAVED | API-04 | Session persisted to disk | sq_api04_update_session.puml |
| RESTORED | CLOSED | API-05 | Session terminated | sq_api05_delete_session.puml |
| BRANCHED | ACTIVE | API-02 | Session ready for messages | sq_api02_create_session.puml |
| BRANCHED | CLOSED | API-05 | Session terminated | sq_api05_delete_session.puml |
| CLOSED | [*] | — | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_subagent_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | AGT-09 | Default state | sq_agent09_spawn_subagent.puml |
| IDLE | SPAWNING | AGT-09 | Child agent spawn requested | sq_agent09_spawn_subagent.puml |
| SPAWNING | RUNNING | AGT-09 | Child agent initialized | sq_agent09_spawn_subagent.puml |
| SPAWNING | FAILED | AGT-09 | Spawn failed | sq_agent09_spawn_subagent.puml |
| RUNNING | COMPLETED | AGT-10 | Task finished successfully | sq_agent10_collect_subagent_result.puml |
| RUNNING | FAILED | AGT-14 | Unrecoverable error | sq_agent14_handle_error.puml |
| COMPLETED | IDLE | AGT-10 | Results aggregated to parent | sq_agent10_collect_subagent_result.puml |
| COMPLETED | [*] | AGT-10 | Terminal state | — |
| FAILED | IDLE | AGT-14 | Error reported, cleanup done | sq_agent14_handle_error.puml |
| FAILED | [*] | AGT-14 | Terminal state | — |

> **Coverage:** 8/8 non-terminal transitions covered. 0 ORPHANs.

### sm_plugin_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCOVERED | PLG-01 | Plugin found on filesystem | sq_plugins01_discover_plugins.puml |
| DISCOVERED | LOADING | PLG-02 | Manifest parsing starts | sq_plugins02_load_manifest.puml |
| DISCOVERED | ERROR | PLG-01 | Plugin discovery failed | sq_plugins01_discover_plugins.puml |
| LOADING | LOADED | PLG-03 | Manifest parsed, tools registered | sq_plugins03_register_plugin_tools.puml |
| LOADING | ERROR | PLG-02 | Manifest parsing failed | sq_plugins02_load_manifest.puml |
| LOADED | ENABLED | PLG-05 | Plugin activated | sq_plugins05_enable_plugin.puml |
| LOADED | DISABLED | PLG-06 | Plugin deactivated | sq_plugins06_disable_plugin.puml |
| LOADED | ERROR | PLG-03 | Tool registration failed | sq_plugins03_register_plugin_tools.puml |
| ENABLED | DISABLED | PLG-06 | Plugin deactivated | sq_plugins06_disable_plugin.puml |
| ENABLED | ERROR | PLG-01 | Runtime exception | sq_plugins01_discover_plugins.puml |
| ENABLED | [*] | PLG-06 | Plugin unloaded | — |
| DISABLED | ENABLED | PLG-05 | Plugin activated | sq_plugins05_enable_plugin.puml |
| DISABLED | [*] | PLG-06 | Plugin unloaded | — |
| ERROR | DISCOVERED | PLG-01 | Re-discovery (recovery) | sq_plugins01_discover_plugins.puml |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_plan_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | AGT-07 | No plan active | sq_agent07_queue_plan.puml |
| EMPTY | BUILDING | AGT-07 | /plan command entered | sq_agent07_queue_plan.puml |
| BUILDING | QUEUED | AGT-07 | Plan construction complete | sq_agent07_queue_plan.puml |
| BUILDING | EMPTY | AGT-07 | Plan cancelled | sq_agent07_queue_plan.puml |
| QUEUED | APPROVED | AGT-08 | User approves plan | sq_agent08_approve_plan.puml |
| QUEUED | REJECTED | AGT-08 | User rejects plan | sq_agent08_approve_plan.puml |
| APPROVED | EXECUTING | AGT-08 | Execution started | sq_agent08_approve_plan.puml |
| EXECUTING | COMPLETED | AGT-01 | All plan steps finished | sq_agent01_process_user_task.puml |
| EXECUTING | EMPTY | AGT-14 | Execution failed or cancelled | sq_agent14_handle_error.puml |
| COMPLETED | [*] | AGT-01 | Terminal state | — |
| REJECTED | [*] | AGT-08 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.
