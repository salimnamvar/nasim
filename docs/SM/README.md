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
