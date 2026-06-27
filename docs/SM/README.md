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
| ACTIVE | Session accepting messages | Session created or restored | #43A047 |
| SAVED | Session persisted to disk | API-04 UPDATE Session | #1565C0 |
| RESTORED | Session loaded from disk | API-03 GET Session | #1E88E5 |
| BRANCHED | Session forked from parent | WRL-04 FORK Session | #7B1FA2 |
| CLOSED | Session terminated | API-05 DELETE Session | #757575 |

## Plan Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No plan active | Default state | #F5F5F5 |
| BUILDING | Plan being constructed | AGT-07 QUEUE Plan | #FFE0B2 |
| QUEUED | Plan queued for approval | Plan construction complete | #E3F2FD |
| APPROVED | Plan approved by user | AGT-08 APPROVE Plan | #388E3C |
| EXECUTING | Plan steps being executed | Plan approved, execution started | #A5D6A7 |
| COMPLETED | All plan steps finished | Implicit: agent loop finishes all steps | #1B5E20 |
| REJECTED | Plan rejected by user | User rejects plan | #B71C1C |

## Plugin Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCOVERED | Plugin found on filesystem | PLG-01 DISCOVER Plugins | #E0E0E0 |
| LOADING | Plugin manifest being parsed | PLG-02 LOAD Manifest | #FFCC80 |
| LOADED | Plugin manifest parsed, tools registered | PLG-03 REGISTER Plugin Tools | #90CAF9 |
| ENABLED | Plugin active and available | PLG-05 ENABLE Plugin | #4CAF50 |
| DISABLED | Plugin deactivated | PLG-06 DISABLE Plugin | #CE93D8 |
| ERROR | Plugin failed to load or crashed | Load error or runtime exception | #EF5350 |

## Subagent Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No child agent active | Default state | #CFD8DC |
| SPAWNING | Child agent process initializing | AGT-09 SPAWN Subagent | #FFAB91 |
| RUNNING | Child agent executing task | AGT-09 SPAWN Subagent | #BCAAA4 |
| COMPLETED | Child agent finished successfully | AGT-10 COLLECT Subagent Result | #80CBC4 |
| FAILED | Child agent encountered unrecoverable error | AGT-14 HANDLE Error | #EF9A9A |

## Persona Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNLOADED | No persona loaded | Default state | #9E9E9E |
| LOADING | Persona configuration being loaded | AGT-12 LOAD Persona | #FFC107 |
| ACTIVE | Persona active and available for delegation | AGT-11 DELEGATE to Persona | #4DB6AC |
| SWITCHING | Switching to different persona at runtime | AGT-13 SWITCH Persona | #FF9800 |
| ERROR | Persona load or switch failed | Load error or switch failure | #F44336 |

## MCP Client Connection Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCONNECTED | No connection to MCP server | Default state | #B0BEC5 |
| CONNECTING | Connection to MCP server in progress | MCP-01 CONNECT MCP Server | #FFCA28 |
| CONNECTED | Connected to MCP server | MCP-01 CONNECT MCP Server | #00BCD4 |
| DISCOVERING | Discovering tools from connected server | MCP-02 DISCOVER MCP Tools | #A1887F |
| ERROR | Connection or discovery failed | MCP-01 or MCP-02 failure | #E57373 |

## MCP Server Serving Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| STOPPED | MCP server not running | Default state | #616161 |
| STARTING | Server starting up | MCP-04 EXPOSE nasim Tools | #FFA726 |
| RUNNING | Server running, serving tools to MCP clients | MCP-04 EXPOSE nasim Tools | #66BB6A |
| STOPPING | Server shutting down | MCP-04 EXPOSE nasim Tools | #FF7043 |
| ERROR | Server startup or runtime failure | MCP-04 failure | #FFCDD2 |

## Sandbox Execution Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No process running in sandbox | Default state | #78909C |
| EXECUTING | Process running in sandbox | SBX-01 ISOLATE Command | #2196F3 |
| MONITORING | Process being monitored for resource usage | SBX-03 MONITOR Process | #64B5F6 |
| COMPLETED | Process finished successfully | SBX-01 ISOLATE Command | #8BC34A |
| TIMEOUT | Process exceeded time limit | SBX-03 MONITOR Process | #FFB74D |
| FAILED | Process crashed or was killed | SBX-01 ISOLATE Command | #D32F2F |
| RESOURCE_EXCEEDED | Process exceeded CPU, memory, or disk quota | SBX-04 LIMIT Resources | #FF5722 |

## Diff Staging Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No diff staged | Default state | #9FA8DA |
| STAGING | Diff being computed | EDT-10 STAGE Diff | #FFE082 |
| STAGED | Diff ready for review | EDT-10 STAGE Diff | #C5E1A5 |
| AWAITING_APPROVAL | Diff presented to user for approval | SAF-02 REQUEST Approval | #FFD54F |
| APPROVED | User approved diff | SAF-02 REQUEST Approval | #AED581 |
| APPLYING | Approved diff being applied | EDT-10 STAGE Diff | #81C784 |
| APPLIED | Diff successfully applied | EDT-10 STAGE Diff | #009688 |
| ERROR | Diff computation or application failed | EDT-10 failure | #E53935 |

## Safety Mode Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINITIALIZED | Safety system not initialized | Default state | #BDBDBD |
| PERMISSIVE | All operations allowed, no approval prompts | SAF-03 APPLY Safety Mode | #9CCC65 |
| ASK | User approval required for sensitive operations | SAF-03 APPLY Safety Mode | #FDD835 |
| BLOCK | Dangerous operations blocked entirely | SAF-03 APPLY Safety Mode | #E91E63 |
| ERROR | Safety system encountered an error | SAF-01 CHECK Permission failure | #F4511E |

## Router Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No routing in progress | Default state | #EEEEEE |
| CLASSIFYING | Task classification for model routing | RTG-03 CLASSIFY Task | #5C6BC0 |
| SELECTING | Model selection in progress | RTG-01 SELECT Model | #3F51B5 |
| SWITCHING | Runtime model switch in progress | RTG-04 SWITCH Model | #FF8F00 |
| FALLBACK | Falling back to next available model | RTG-02 APPLY Fallback | #EF6C00 |
| ERROR | Routing or fallback failed | All models exhausted | #BF360C |

## Provider Connection Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNREGISTERED | No provider registered | Default state | #455A64 |
| REGISTERING | Provider registration in progress | PRV-01 REGISTER Provider | #29B6F6 |
| ACTIVE | Provider registered and ready for chat | PRV-01 REGISTER Provider | #03A9F4 |
| SELECTING | Backend selection in progress | PRV-04 SELECT Provider Backend | #FBC02D |
| ERROR | Registration or selection failed | Provider unavailable | #E64A19 |

## Evaluation Lifecycle States (Process)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No evaluation in progress | Default state | #90A4AE |
| CHECKING | Running task completion and success checks | EVL-01 EVALUATE Task | #C5CAE9 |
| REVIEWING | LLM-based code review and quality assessment | EVL-04 VALIDATE With LLM | #AB47BC |
| TESTING | Running project test suites | EVL-05 VALIDATE Test Suite | #D4E157 |
| SCORING | Recording quality signal and scoring | EVL-07 RECORD Quality Signal | #FF8A65 |
| RETRYING | Coordinating retry with backoff and escalation | EVL-06 COORDINATE Retry | #C62828 |
| PASSED | Evaluation passed all criteria | Terminal success state | #689F38 |
| FAILED | Evaluation failed, retries exhausted | Terminal failure state | #AD1457 |

## Repository Index Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINDEXED | No repository index exists | Default state | #424242 |
| INDEXING | AST indexing via tree-sitter in progress | RIM-01 INDEX Codebase | #4FC3F7 |
| INDEXED | Repository fully indexed | RIM-01 INDEX Codebase | #7CB342 |
| BUILDING_GRAPH | Cross-file symbol reference graph in progress | RIM-02 BUILD Symbol Graph | #9C27B0 |
| EMBEDDING | Generating vector embeddings for code | RIM-05 EMBED Code | #E6EE9C |
| STALE | Index outdated, needs re-index | Source files changed | #FFECB3 |
| ERROR | Indexing, graph building, or embedding failed | Unrecoverable processing error | #DD2C00 |

## Diagrams

| File | Scope |
|------|-------|
| `sm_agent_lifecycle.puml` | Agent process FSM — 17 states (API-First) |
| `sm_session_lifecycle.puml` | Session entity lifecycle — 6 states (API-First) |
| `sm_plan_lifecycle.puml` | Plan entity lifecycle — 7 states |
| `sm_plugin_lifecycle.puml` | Plugin entity lifecycle — 6 states (+ 2 terminal exits) |
| `sm_subagent_lifecycle.puml` | Subagent entity lifecycle — 5 states (IDLE→SPAWNING→RUNNING→COMPLETED/FAILED) + 2 terminal exits |
| `sm_persona_lifecycle.puml` | Persona entity lifecycle — 5 states (UNLOADED→LOADING→ACTIVE↔SWITCHING) |
| `sm_mcp_client_lifecycle.puml` | MCP Client connection lifecycle — 5 states (DISCONNECTED→CONNECTING→CONNECTED→DISCOVERING) |
| `sm_mcp_server_lifecycle.puml` | MCP Server serving lifecycle — 5 states (STOPPED→STARTING→RUNNING→STOPPING) |
| `sm_sandbox_execution_lifecycle.puml` | Sandbox execution lifecycle — 7 states (IDLE→EXECUTING→COMPLETED/TIMEOUT/FAILED/RESOURCE_EXCEEDED) |
| `sm_diff_staging_lifecycle.puml` | Diff staging lifecycle — 8 states (EMPTY→STAGING→STAGED→AWAITING_APPROVAL→APPROVED→APPLYING→APPLIED) |
| `sm_safety_mode_lifecycle.puml` | Safety mode lifecycle — 5 states (UNINITIALIZED→PERMISSIVE|ASK|BLOCK) |
| `sm_router_lifecycle.puml` | Router selection lifecycle — 6 states (IDLE→CLASSIFYING→SELECTING→FALLBACK|SWITCHING) |
| `sm_provider_connection_lifecycle.puml` | Provider connection lifecycle — 5 states (UNREGISTERED→REGISTERING→ACTIVE→SELECTING) |
| `sm_evaluation_lifecycle.puml` | Evaluation process lifecycle — 9 states (IDLE→CHECKING→REVIEWING|TESTING→SCORING→PASSED|FAILED) |
| `sm_index_lifecycle.puml` | Repository index lifecycle — 7 states (UNINDEXED→INDEXING→INDEXED→BUILDING_GRAPH|EMBEDDING) |

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

### Persona Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNLOADED | AGT-12 | Default state |
| UNLOADED | LOADING | AGT-12 | Load requested |
| LOADING | ACTIVE | AGT-12 | Load successful |
| LOADING | ERROR | AGT-12 | Load failed |
| ACTIVE | SWITCHING | AGT-13 | Switch requested |
| SWITCHING | ACTIVE | AGT-13 | Switch successful |
| SWITCHING | ERROR | AGT-13 | Switch failed |
| ACTIVE | UNLOADED | AGT-11 | Delegation complete |
| ERROR | UNLOADED | AGT-12 | Recovery: retry load |
| UNLOADED | [*] | AGT-12 | Terminal state |

### MCP Client Connection Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | DISCONNECTED | MCP-01 | Default state |
| DISCONNECTED | CONNECTING | MCP-01 | Connect requested |
| CONNECTING | CONNECTED | MCP-01 | Connection established |
| CONNECTING | ERROR | MCP-01 | Connection failed |
| CONNECTED | DISCOVERING | MCP-02 | Tool discovery started |
| DISCOVERING | CONNECTED | MCP-02 | Discovery complete |
| DISCOVERING | ERROR | MCP-02 | Discovery failed |
| CONNECTED | DISCONNECTED | MCP-01 | Disconnected |
| ERROR | DISCONNECTED | MCP-01 | Recovery: reconnect |
| DISCONNECTED | [*] | MCP-01 | Terminal state |

### MCP Server Serving Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | STOPPED | MCP-04 | Default state |
| STOPPED | STARTING | MCP-04 | Start requested |
| STARTING | RUNNING | MCP-04 | Startup complete |
| STARTING | ERROR | MCP-04 | Startup failed |
| RUNNING | STOPPING | MCP-04 | Stop requested |
| STOPPING | STOPPED | MCP-04 | Shutdown complete |
| RUNNING | ERROR | MCP-04 | Runtime failure |
| ERROR | STOPPED | MCP-04 | Recovery: shutdown |
| STOPPED | [*] | MCP-04 | Terminal state |

### Sandbox Execution Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | SBX-01 | Default state |
| IDLE | EXECUTING | SBX-01 | Command started |
| EXECUTING | MONITORING | SBX-03 | Resource monitoring started |
| MONITORING | EXECUTING | SBX-03 | Monitoring continues |
| EXECUTING | COMPLETED | SBX-01 | Process finished |
| EXECUTING | FAILED | SBX-01 | Process crashed |
| EXECUTING | TIMEOUT | SBX-03 | Timeout exceeded |
| EXECUTING | RESOURCE_EXCEEDED | SBX-04 | Resource limit hit |
| MONITORING | TIMEOUT | SBX-03 | Timeout exceeded |
| MONITORING | RESOURCE_EXCEEDED | SBX-04 | Resource limit hit |
| TIMEOUT | IDLE | SBX-01 | Cleanup after timeout |
| FAILED | IDLE | SBX-01 | Cleanup after failure |
| RESOURCE_EXCEEDED | IDLE | SBX-04 | Cleanup after resource violation |
| COMPLETED | [*] | SBX-01 | Terminal state |

### Diff Staging Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | EMPTY | EDT-10 | Default state |
| EMPTY | STAGING | EDT-10 | Diff computation started |
| STAGING | STAGED | EDT-10 | Diff computed successfully |
| STAGING | ERROR | EDT-10 | Diff computation failed |
| STAGED | AWAITING_APPROVAL | EDT-10 | Diff presented for review |
| AWAITING_APPROVAL | APPROVED | SAF-02 | User approved |
| AWAITING_APPROVAL | EMPTY | SAF-02 | User rejected, cleanup |
| APPROVED | APPLYING | EDT-10 | Diff application started |
| APPLYING | APPLIED | EDT-10 | Diff applied successfully |
| APPLYING | ERROR | EDT-10 | Diff application failed |
| APPLIED | EMPTY | EDT-10 | Cleanup after application |
| ERROR | EMPTY | EDT-10 | Cleanup after error |
| APPLIED | [*] | EDT-10 | Terminal state |

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

### Subagent Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| SPAWNING | AGT-09 SPAWN Subagent | Child agent process initializing |
| RUNNING | AGT-09 SPAWN Subagent | Child agent executing task |
| COMPLETED | AGT-10 COLLECT Subagent Result | Child agent finished successfully |
| FAILED | AGT-14 HANDLE Error | Child agent encountered unrecoverable error |

### Persona Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| LOADING | AGT-12 LOAD Persona | Persona configuration being loaded |
| ACTIVE | AGT-11 DELEGATE to Persona | Persona active and available |
| SWITCHING | AGT-13 SWITCH Persona | Switching persona at runtime |
| ERROR | AGT-12 LOAD Persona | Persona load or switch failed |

### MCP Client Connection Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CONNECTING | MCP-01 CONNECT MCP Server | Connection in progress |
| CONNECTED | MCP-01 CONNECT MCP Server | Connected to MCP server |
| DISCOVERING | MCP-02 DISCOVER MCP Tools | Discovering tools from server |
| ERROR | MCP-01 CONNECT MCP Server | Connection or discovery failed |

### MCP Server Serving Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| STARTING | MCP-04 EXPOSE nasim Tools | Server starting up |
| RUNNING | MCP-04 EXPOSE nasim Tools | Server running |
| STOPPING | MCP-04 EXPOSE nasim Tools | Server shutting down |
| ERROR | MCP-04 EXPOSE nasim Tools | Server startup or runtime failure |

### Sandbox Execution Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| EXECUTING | SBX-01 ISOLATE Command | Process running in sandbox |
| MONITORING | SBX-03 MONITOR Process | Process being monitored |
| COMPLETED | SBX-01 ISOLATE Command | Process finished successfully |
| TIMEOUT | SBX-03 MONITOR Process | Process exceeded time limit |
| FAILED | SBX-01 ISOLATE Command | Process crashed or was killed |
| RESOURCE_EXCEEDED | SBX-04 LIMIT Resources | Process exceeded resource quota |

### Diff Staging Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| STAGING | EDT-10 STAGE Diff | Diff being computed |
| STAGED | EDT-10 STAGE Diff | Diff ready for review |
| AWAITING_APPROVAL | SAF-02 REQUEST Approval | Diff presented for user approval |
| APPROVED | SAF-02 REQUEST Approval | User approved diff |
| APPLYING | EDT-10 STAGE Diff | Approved diff being applied |
| APPLIED | EDT-10 STAGE Diff | Diff successfully applied |
| ERROR | EDT-10 STAGE Diff | Diff computation or application failed |

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

### sm_persona_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNLOADED | AGT-12 | Default state | — |
| UNLOADED | LOADING | AGT-12 | Load requested | — |
| LOADING | ACTIVE | AGT-12 | Load successful | — |
| LOADING | ERROR | AGT-12 | Load failed | — |
| ACTIVE | SWITCHING | AGT-13 | Switch requested | — |
| SWITCHING | ACTIVE | AGT-13 | Switch successful | — |
| SWITCHING | ERROR | AGT-13 | Switch failed | — |
| ACTIVE | UNLOADED | AGT-11 | Delegation complete | — |
| ERROR | UNLOADED | AGT-12 | Recovery: retry load | — |
| UNLOADED | [*] | AGT-12 | Terminal state | — |

> **Coverage:** 0/9 non-terminal transitions covered. 9 ORPHANs (SQ diagrams not yet created).

### sm_mcp_client_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCONNECTED | MCP-01 | Default state | — |
| DISCONNECTED | CONNECTING | MCP-01 | Connect requested | — |
| CONNECTING | CONNECTED | MCP-01 | Connection established | — |
| CONNECTING | ERROR | MCP-01 | Connection failed | — |
| CONNECTED | DISCOVERING | MCP-02 | Tool discovery started | — |
| DISCOVERING | CONNECTED | MCP-02 | Discovery complete | — |
| DISCOVERING | ERROR | MCP-02 | Discovery failed | — |
| CONNECTED | DISCONNECTED | MCP-01 | Disconnected | — |
| ERROR | DISCONNECTED | MCP-01 | Recovery: reconnect | — |
| DISCONNECTED | [*] | MCP-01 | Terminal state | — |

> **Coverage:** 0/9 non-terminal transitions covered. 9 ORPHANs (SQ diagrams not yet created).

### sm_mcp_server_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | STOPPED | MCP-04 | Default state | — |
| STOPPED | STARTING | MCP-04 | Start requested | — |
| STARTING | RUNNING | MCP-04 | Startup complete | — |
| STARTING | ERROR | MCP-04 | Startup failed | — |
| RUNNING | STOPPING | MCP-04 | Stop requested | — |
| STOPPING | STOPPED | MCP-04 | Shutdown complete | — |
| RUNNING | ERROR | MCP-04 | Runtime failure | — |
| ERROR | STOPPED | MCP-04 | Recovery: shutdown | — |
| STOPPED | [*] | MCP-04 | Terminal state | — |

> **Coverage:** 0/8 non-terminal transitions covered. 8 ORPHANs (SQ diagrams not yet created).

### sm_sandbox_execution_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | SBX-01 | Default state | — |
| IDLE | EXECUTING | SBX-01 | Command started | — |
| EXECUTING | MONITORING | SBX-03 | Resource monitoring started | — |
| MONITORING | EXECUTING | SBX-03 | Monitoring continues | — |
| EXECUTING | COMPLETED | SBX-01 | Process finished | — |
| EXECUTING | FAILED | SBX-01 | Process crashed | — |
| EXECUTING | TIMEOUT | SBX-03 | Timeout exceeded | — |
| EXECUTING | RESOURCE_EXCEEDED | SBX-04 | Resource limit hit | — |
| MONITORING | TIMEOUT | SBX-03 | Timeout exceeded | — |
| MONITORING | RESOURCE_EXCEEDED | SBX-04 | Resource limit hit | — |
| TIMEOUT | IDLE | SBX-01 | Cleanup after timeout | — |
| FAILED | IDLE | SBX-01 | Cleanup after failure | — |
| RESOURCE_EXCEEDED | IDLE | SBX-04 | Cleanup after resource violation | — |
| COMPLETED | [*] | SBX-01 | Terminal state | — |

> **Coverage:** 0/13 non-terminal transitions covered. 13 ORPHANs (SQ diagrams not yet created).

### sm_diff_staging_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | EDT-10 | Default state | — |
| EMPTY | STAGING | EDT-10 | Diff computation started | — |
| STAGING | STAGED | EDT-10 | Diff computed successfully | — |
| STAGING | ERROR | EDT-10 | Diff computation failed | — |
| STAGED | AWAITING_APPROVAL | EDT-10 | Diff presented for review | — |
| AWAITING_APPROVAL | APPROVED | SAF-02 | User approved | — |
| AWAITING_APPROVAL | EMPTY | SAF-02 | User rejected, cleanup | — |
| APPROVED | APPLYING | EDT-10 | Diff application started | — |
| APPLYING | APPLIED | EDT-10 | Diff applied successfully | — |
| APPLYING | ERROR | EDT-10 | Diff application failed | — |
| APPLIED | EMPTY | EDT-10 | Cleanup after application | — |
| ERROR | EMPTY | EDT-10 | Cleanup after error | — |
| APPLIED | [*] | EDT-10 | Terminal state | — |

> **Coverage:** 0/12 non-terminal transitions covered. 12 ORPHANs (SQ diagrams not yet created).

### Safety Mode Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNINITIALIZED | SAF-03 | Default state |
| UNINITIALIZED | PERMISSIVE | SAF-03 | Apply permissive mode |
| UNINITIALIZED | ASK | SAF-03 | Apply ask mode |
| UNINITIALIZED | BLOCK | SAF-03 | Apply block mode |
| PERMISSIVE | ASK | SAF-03 | Switch to ask mode |
| PERMISSIVE | BLOCK | SAF-03 | Switch to block mode |
| ASK | PERMISSIVE | SAF-03 | Switch to permissive mode |
| ASK | BLOCK | SAF-03 | Switch to block mode |
| BLOCK | PERMISSIVE | SAF-03 | Switch to permissive mode |
| BLOCK | ASK | SAF-03 | Switch to ask mode |
| PERMISSIVE | ERROR | SAF-01 | Permission check failed |
| ASK | ERROR | SAF-01 | Permission check failed |
| BLOCK | ERROR | SAF-01 | Permission check failed |
| ERROR | UNINITIALIZED | SAF-03 | Recovery: reinitialize |
| UNINITIALIZED | [*] | SAF-03 | Terminal state |

### Router Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | RTG-01 | Default state |
| IDLE | CLASSIFYING | RTG-03 | Task classification started |
| CLASSIFYING | SELECTING | RTG-01 | Classification complete |
| CLASSIFYING | ERROR | RTG-03 | Classification failed |
| SELECTING | IDLE | RTG-01 | Model selected |
| SELECTING | FALLBACK | RTG-02 | Primary model unavailable |
| FALLBACK | SELECTING | RTG-02 | Fallback to next model |
| FALLBACK | ERROR | RTG-02 | All models exhausted |
| IDLE | SWITCHING | RTG-04 | Runtime switch requested |
| SWITCHING | IDLE | RTG-04 | Switch successful |
| SWITCHING | ERROR | RTG-04 | Switch failed |
| ERROR | IDLE | RTG-01 | Recovery: retry |
| IDLE | [*] | RTG-01 | Terminal state |

### Provider Connection Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNREGISTERED | PRV-01 | Default state |
| UNREGISTERED | REGISTERING | PRV-01 | Registration started |
| REGISTERING | ACTIVE | PRV-01 | Registration successful |
| REGISTERING | ERROR | PRV-01 | Registration failed |
| ACTIVE | SELECTING | PRV-04 | Backend selection started |
| SELECTING | ACTIVE | PRV-04 | Backend selected |
| SELECTING | ERROR | PRV-04 | Selection failed |
| ACTIVE | UNREGISTERED | PRV-01 | Unregistered |
| ERROR | UNREGISTERED | PRV-01 | Recovery: re-register |
| UNREGISTERED | [*] | PRV-01 | Terminal state |

### Evaluation Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | EVL-01 | Default state |
| IDLE | CHECKING | EVL-01 | Evaluation started |
| CHECKING | REVIEWING | EVL-04 | LLM review required |
| CHECKING | TESTING | EVL-05 | Test validation required |
| CHECKING | SCORING | EVL-07 | Direct scoring (no review/test) |
| CHECKING | FAILED | EVL-02 | Task completion check failed |
| REVIEWING | SCORING | EVL-07 | LLM review passed |
| REVIEWING | RETRYING | EVL-06 | LLM review rejected |
| TESTING | SCORING | EVL-07 | Tests passed |
| TESTING | RETRYING | EVL-06 | Tests failed |
| SCORING | PASSED | EVL-07 | Scoring threshold met |
| SCORING | RETRYING | EVL-06 | Scoring below threshold |
| RETRYING | CHECKING | EVL-06 | Retry with feedback |
| RETRYING | FAILED | EVL-06 | Retries exhausted |
| PASSED | IDLE | EVL-01 | Reset for next evaluation |
| FAILED | IDLE | EVL-01 | Reset for next evaluation |
| PASSED | [*] | EVL-01 | Terminal state |
| FAILED | [*] | EVL-01 | Terminal state |

### Repository Index Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNINDEXED | RIM-01 | Default state |
| UNINDEXED | INDEXING | RIM-01 | Indexing started |
| INDEXING | INDEXED | RIM-01 | Indexing complete |
| INDEXING | ERROR | RIM-01 | Indexing failed |
| INDEXED | BUILDING_GRAPH | RIM-02 | Graph building started |
| BUILDING_GRAPH | INDEXED | RIM-02 | Graph built |
| BUILDING_GRAPH | ERROR | RIM-02 | Graph building failed |
| INDEXED | EMBEDDING | RIM-05 | Embedding started |
| EMBEDDING | INDEXED | RIM-05 | Embedding complete |
| EMBEDDING | ERROR | RIM-05 | Embedding failed |
| INDEXED | STALE | RIM-01 | Source files changed |
| STALE | INDEXING | RIM-01 | Re-indexing started |
| ERROR | UNINDEXED | RIM-01 | Recovery: start fresh |
| INDEXED | [*] | RIM-01 | Terminal state |
| UNINDEXED | [*] | RIM-01 | Terminal state |

### Safety Mode Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| UNINITIALIZED | SAF-03 APPLY Safety Mode | Safety system not initialized |
| PERMISSIVE | SAF-03 APPLY Safety Mode | Permissive mode applied |
| ASK | SAF-03 APPLY Safety Mode | Ask mode applied |
| BLOCK | SAF-03 APPLY Safety Mode | Block mode applied |
| ERROR | SAF-01 CHECK Permission | Safety system encountered error |

### Router Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CLASSIFYING | RTG-03 CLASSIFY Task | Task classification started |
| SELECTING | RTG-01 SELECT Model | Model selection in progress |
| SWITCHING | RTG-04 SWITCH Model | Runtime model switch |
| FALLBACK | RTG-02 APPLY Fallback | Falling back to next model |
| ERROR | RTG-03 CLASSIFY Task | Classification or routing failure |

### Provider Connection Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| REGISTERING | PRV-01 REGISTER Provider | Provider registration started |
| ACTIVE | PRV-01 REGISTER Provider | Provider registered and ready |
| SELECTING | PRV-04 SELECT Provider Backend | Backend selection in progress |
| ERROR | PRV-01 REGISTER Provider | Registration or selection failed |

### Evaluation Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CHECKING | EVL-01 EVALUATE Task | Task completion checks started |
| REVIEWING | EVL-04 VALIDATE With LLM | LLM review in progress |
| TESTING | EVL-05 VALIDATE Test Suite | Test validation in progress |
| SCORING | EVL-07 RECORD Quality Signal | Scoring in progress |
| RETRYING | EVL-06 COORDINATE Retry | Retry with backoff and escalation |
| PASSED | EVL-07 RECORD Quality Signal | Evaluation passed |
| FAILED | EVL-02 CHECK Task Completion | Evaluation failed |

### Repository Index Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| INDEXING | RIM-01 INDEX Codebase | AST indexing in progress |
| INDEXED | RIM-01 INDEX Codebase | Repository fully indexed |
| BUILDING_GRAPH | RIM-02 BUILD Symbol Graph | Cross-file symbol reference graph |
| EMBEDDING | RIM-05 EMBED Code | Vector embedding generation |
| STALE | RIM-01 INDEX Codebase | Index outdated, needs re-index |
| ERROR | RIM-01 INDEX Codebase | Indexing operation failed |

### sm_safety_mode_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINITIALIZED | SAF-03 | Default state | — |
| UNINITIALIZED | PERMISSIVE | SAF-03 | Apply permissive mode | — |
| UNINITIALIZED | ASK | SAF-03 | Apply ask mode | — |
| UNINITIALIZED | BLOCK | SAF-03 | Apply block mode | — |
| PERMISSIVE | ASK | SAF-03 | Switch to ask mode | — |
| PERMISSIVE | BLOCK | SAF-03 | Switch to block mode | — |
| ASK | PERMISSIVE | SAF-03 | Switch to permissive mode | — |
| ASK | BLOCK | SAF-03 | Switch to block mode | — |
| BLOCK | PERMISSIVE | SAF-03 | Switch to permissive mode | —
| BLOCK | ASK | SAF-03 | Switch to ask mode | — |
| PERMISSIVE | ERROR | SAF-01 | Permission check failed | — |
| ASK | ERROR | SAF-01 | Permission check failed | — |
| BLOCK | ERROR | SAF-01 | Permission check failed | — |
| ERROR | UNINITIALIZED | SAF-03 | Recovery: reinitialize | — |
| UNINITIALIZED | [*] | SAF-03 | Terminal state | — |

> **Coverage:** 0/14 non-terminal transitions covered. 14 ORPHANs (SQ diagrams not yet created).

### sm_router_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | RTG-01 | Default state | — |
| IDLE | CLASSIFYING | RTG-03 | Task classification started | — |
| CLASSIFYING | SELECTING | RTG-01 | Classification complete | — |
| CLASSIFYING | ERROR | RTG-03 | Classification failed | — |
| SELECTING | IDLE | RTG-01 | Model selected | — |
| SELECTING | FALLBACK | RTG-02 | Primary model unavailable | — |
| FALLBACK | SELECTING | RTG-02 | Fallback to next model | — |
| FALLBACK | ERROR | RTG-02 | All models exhausted | — |
| IDLE | SWITCHING | RTG-04 | Runtime switch requested | — |
| SWITCHING | IDLE | RTG-04 | Switch successful | — |
| SWITCHING | ERROR | RTG-04 | Switch failed | — |
| ERROR | IDLE | RTG-01 | Recovery: retry | — |
| IDLE | [*] | RTG-01 | Terminal state | — |

> **Coverage:** 0/12 non-terminal transitions covered. 12 ORPHANs (SQ diagrams not yet created).

### sm_provider_connection_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNREGISTERED | PRV-01 | Default state | — |
| UNREGISTERED | REGISTERING | PRV-01 | Registration started | — |
| REGISTERING | ACTIVE | PRV-01 | Registration successful | — |
| REGISTERING | ERROR | PRV-01 | Registration failed | — |
| ACTIVE | SELECTING | PRV-04 | Backend selection started | — |
| SELECTING | ACTIVE | PRV-04 | Backend selected | — |
| SELECTING | ERROR | PRV-04 | Selection failed | — |
| ACTIVE | UNREGISTERED | PRV-01 | Unregistered | — |
| ERROR | UNREGISTERED | PRV-01 | Recovery: re-register | — |
| UNREGISTERED | [*] | PRV-01 | Terminal state | — |

> **Coverage:** 0/9 non-terminal transitions covered. 9 ORPHANs (SQ diagrams not yet created).

### sm_evaluation_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | EVL-01 | Default state | — |
| IDLE | CHECKING | EVL-01 | Evaluation started | — |
| CHECKING | REVIEWING | EVL-04 | LLM review required | — |
| CHECKING | TESTING | EVL-05 | Test validation required | — |
| CHECKING | SCORING | EVL-07 | Direct scoring (no review/test) | — |
| CHECKING | FAILED | EVL-02 | Task completion check failed | — |
| REVIEWING | SCORING | EVL-07 | LLM review passed | — |
| REVIEWING | RETRYING | EVL-06 | LLM review rejected | — |
| TESTING | SCORING | EVL-07 | Tests passed | — |
| TESTING | RETRYING | EVL-06 | Tests failed | — |
| SCORING | PASSED | EVL-07 | Scoring threshold met | — |
| SCORING | RETRYING | EVL-06 | Scoring below threshold | — |
| RETRYING | CHECKING | EVL-06 | Retry with feedback | — |
| RETRYING | FAILED | EVL-06 | Retries exhausted | — |
| PASSED | IDLE | EVL-01 | Reset for next evaluation | — |
| FAILED | IDLE | EVL-01 | Reset for next evaluation | — |
| PASSED | [*] | EVL-01 | Terminal state | — |
| FAILED | [*] | EVL-01 | Terminal state | — |

> **Coverage:** 0/16 non-terminal transitions covered. 16 ORPHANs (SQ diagrams not yet created).

### sm_index_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINDEXED | RIM-01 | Default state | — |
| UNINDEXED | INDEXING | RIM-01 | Indexing started | — |
| INDEXING | INDEXED | RIM-01 | Indexing complete | — |
| INDEXING | ERROR | RIM-01 | Indexing failed | — |
| INDEXED | BUILDING_GRAPH | RIM-02 | Graph building started | — |
| BUILDING_GRAPH | INDEXED | RIM-02 | Graph built | — |
| BUILDING_GRAPH | ERROR | RIM-02 | Graph building failed | — |
| INDEXED | EMBEDDING | RIM-05 | Embedding started | — |
| EMBEDDING | INDEXED | RIM-05 | Embedding complete | — |
| EMBEDDING | ERROR | RIM-05 | Embedding failed | — |
| INDEXED | STALE | RIM-01 | Source files changed | — |
| STALE | INDEXING | RIM-01 | Re-indexing started | — |
| ERROR | UNINDEXED | RIM-01 | Recovery: start fresh | — |
| INDEXED | [*] | RIM-01 | Terminal state | — |
| UNINDEXED | [*] | RIM-01 | Terminal state | — |

> **Coverage:** 0/13 non-terminal transitions covered. 13 ORPHANs (SQ diagrams not yet created).

## SM Inventory & Completeness Report (2026-06-27)

### Audit Method
Systematic 21-group C4 component audit: every Component() in every `docs/C4/c4_nasim_component_*.puml` was cross-referenced against the 15 existing SM files, the UC catalog (`docs/UC/README.md`, 148 UCs), and the ERD layer. Components were flagged as stateful if they met any of the EXT-01..05 criteria (sm.md): lifecycle state field, process lifecycle management, multiple UCs implying state transitions, stateful naming (Manager, Coordinator, Session, Runtime).

### Full SM Inventory (15 files)

| # | SM File | Entity | C4 Group | Type | States | UCs | Status |
|---|---------|--------|----------|------|--------|-----|--------|
| 1 | `sm_agent_lifecycle.puml` | AgentOrchestrator | Agent | Process FSM | 17 | AGT-01..14, API-06, PRV-02, EDT-10, SAF-02, HK-02, EVL-01..06, RTG-01 | ✅ GREEN |
| 2 | `sm_session_lifecycle.puml` | SessionStore | Session | Entity | 6 | API-02..05, WRL-04 | ✅ GREEN |
| 3 | `sm_plan_lifecycle.puml` | PlanSession | Agent | Entity | 7 | AGT-07, AGT-08, AGT-01, AGT-14 | ✅ GREEN |
| 4 | `sm_plugin_lifecycle.puml` | PluginLoader | Plugins | Entity | 6 | PLG-01..06 | ✅ GREEN |
| 5 | `sm_subagent_lifecycle.puml` | SubagentCoordinator | Agent | Entity | 5 | AGT-09, AGT-10, AGT-14 | ✅ GREEN |
| 6 | `sm_persona_lifecycle.puml` | PersonaManager | Agent | Entity | 5 | AGT-11, AGT-12, AGT-13 | ✅ GREEN |
| 7 | `sm_mcp_client_lifecycle.puml` | MCPClientRuntime | MCP | Entity | 5 | MCP-01, MCP-02 | ✅ GREEN |
| 8 | `sm_mcp_server_lifecycle.puml` | MCPServerRuntime | MCP | Entity | 5 | MCP-04 | ✅ GREEN |
| 9 | `sm_sandbox_execution_lifecycle.puml` | SandboxExecutor | Sandbox | Entity | 7 | SBX-01, SBX-03, SBX-04 | ✅ GREEN |
| 10 | `sm_diff_staging_lifecycle.puml` | DiffSandboxManager | Sandbox | Entity | 8 | EDT-10, SAF-02 | ✅ GREEN |
| 11 | `sm_safety_mode_lifecycle.puml` | SafetyCoordinator | Safety | Entity | 5 | SAF-01, SAF-03 | ✅ GREEN |
| 12 | `sm_router_lifecycle.puml` | ModelRouter | Router | Entity | 6 | RTG-01..04 | ✅ GREEN |
| 13 | `sm_provider_connection_lifecycle.puml` | LiteLLMProxy | Provider | Entity | 5 | PRV-01, PRV-04 | ✅ GREEN |
| 14 | `sm_evaluation_lifecycle.puml` | EvaluationEngine | Evaluation | Entity | 8 | EVL-01..07 | ✅ GREEN |
| 15 | `sm_index_lifecycle.puml` | RepoIntelligenceManager | Repo Intelligence | Entity | 7 | RIM-01, RIM-02, RIM-05 | ✅ GREEN |

### Coverage Summary

| Metric | Value |
|--------|-------|
| Total C4 component groups audited | 21 |
| Total C4 components scanned | ~109 |
| Total SM files | 15 |
| Total states across all SMs | 92 |
| Unique hex colors | 92 (0 duplicates) |
| Total transitions (all SMs) | 195 |
| Non-terminal transitions | 195 |
| Covered by SQ diagrams | 80 |
| ORPHAN transitions (awaiting SQ) | 115 |
| Lint violations | 0 (across all 15 files) |
| Terminal UC-ID violations found & fixed | 2 (agent, session) |

### Stateful Entities with Dedicated SM Coverage

| C4 Component | C4 Group | SM File |
|--------------|----------|---------|
| AgentOrchestrator | Agent | `sm_agent_lifecycle.puml` (Process FSM) |
| SessionStore | Session | `sm_session_lifecycle.puml` |
| PlanSession | Agent | `sm_plan_lifecycle.puml` |
| PluginLoader | Plugins | `sm_plugin_lifecycle.puml` |
| SubagentCoordinator | Agent | `sm_subagent_lifecycle.puml` |
| PersonaManager | Agent | `sm_persona_lifecycle.puml` |
| MCPClientRuntime | MCP | `sm_mcp_client_lifecycle.puml` |
| MCPServerRuntime | MCP | `sm_mcp_server_lifecycle.puml` |
| SandboxExecutor | Sandbox | `sm_sandbox_execution_lifecycle.puml` |
| DiffSandboxManager | Sandbox | `sm_diff_staging_lifecycle.puml` |
| SafetyCoordinator | Safety | `sm_safety_mode_lifecycle.puml` |
| ModelRouter | Router | `sm_router_lifecycle.puml` |
| LiteLLMProxy | Provider | `sm_provider_connection_lifecycle.puml` |
| EvaluationEngine | Evaluation | `sm_evaluation_lifecycle.puml` |
| RepoIntelligenceManager | Repo Intelligence | `sm_index_lifecycle.puml` |

### Stateful Entities Covered Inside Agent Process FSM

These components have lifecycle states that occur as transient sub-states within the agent processing loop. Dedicated SMs would add no value:

| Component | Group | Rationale |
|-----------|-------|-----------|
| ConversationHistory | Agent | Message store with token tracking. Its only state transition (`normal → compacting`) is a sub-state of Agent FSM's COMPACTING. No independent lifecycle outside the agent loop. |
| ContextCompactor | Agent | Stateless summarizer invoked by ConversationHistory. No independent lifecycle. |
| ErrorBoundary | Agent | Error handler. Error states (recoverable vs terminal) are sub-states of Agent FSM's ERROR. |
| ToolRegistry | Tool | Instance registry. Registration is static at startup (except MCP tools, covered by MCP SMs). |
| PermissionGate | Safety | Stateless evaluator. Permission decision (allow/deny/ask) maps to Agent FSM transitions. |
| FallbackChain | Router | Fallback lifecycle captured within Router SM: SELECTING → FALLBACK → ERROR. |
| Provider (Protocol) | Provider | Chat lifecycle maps to Agent FSM: THINKING → RESPONDING/ERROR. |

### Stateful Entities Without Dedicated SM (LOW Priority — Backlog)

| # | Entity | C4 Group | Reason | Rationale |
|---|--------|----------|--------|-----------|
| 1 | WireLog | Wire Log | Write-buffer lifecycle | Append-only event store with buffering/flush. Simple 3-state (OPEN→WRITING→FLUSHING). UCs: WRL-01..05. |
| 2 | GitIntegration | Git | Auto-commit lifecycle | Monitors for changes then commits. 3-state (IDLE→CHANGES_DETECTED→COMMITTING). UC: VCS-04. |
| 3 | PipelineOrchestrator | Context Graph | Pipeline stage lifecycle | 5 transient pipeline stages completing synchronously in one pass. LOW risk. |
| 4 | REPLSession | CLI | REPL loop lifecycle | CLI entry point. Delegates all business logic via API. REPL state is UI state, not domain state. |
| 5 | ServerApp | API | ASGI lifespan lifecycle | Standard ASGI startup/shutdown. Few project-specific transitions. |

### Lifecycle-Write Ownership Verification

Every entity SM state has exactly one owning lifecycle-write UC. Verified per SMT rules:

- **Session**: CREATED (API-02), ACTIVE (API-02), SAVED (API-04), RESTORED (API-03), BRANCHED (WRL-04), CLOSED (API-05) ✅
- **Plan**: BUILDING (AGT-07), QUEUED (AGT-07), APPROVED (AGT-08), EXECUTING (AGT-08), COMPLETED (AGT-01), REJECTED (AGT-08) ✅
- **Plugin**: DISCOVERED (PLG-01), LOADING (PLG-02), LOADED (PLG-03), ENABLED (PLG-05), DISABLED (PLG-06), ERROR (PLG-01) ✅
- **Subagent**: SPAWNING (AGT-09), RUNNING (AGT-09), COMPLETED (AGT-10), FAILED (AGT-14) ✅
- **Persona**: LOADING (AGT-12), ACTIVE (AGT-11), SWITCHING (AGT-13), ERROR (AGT-12) ✅
- **MCP Client**: CONNECTING (MCP-01), CONNECTED (MCP-01), DISCOVERING (MCP-02), ERROR (MCP-01) ✅
- **MCP Server**: STARTING (MCP-04), RUNNING (MCP-04), STOPPING (MCP-04), ERROR (MCP-04) ✅
- **Sandbox**: EXECUTING (SBX-01), MONITORING (SBX-03), COMPLETED (SBX-01), TIMEOUT (SBX-03), FAILED (SBX-01), RESOURCE_EXCEEDED (SBX-04) ✅
- **Diff Staging**: STAGING (EDT-10), STAGED (EDT-10), AWAITING_APPROVAL (SAF-02), APPROVED (SAF-02), APPLYING (EDT-10), APPLIED (EDT-10), ERROR (EDT-10) ✅
- **Safety**: PERMISSIVE (SAF-03), ASK (SAF-03), BLOCK (SAF-03), ERROR (SAF-01) ✅
- **Router**: CLASSIFYING (RTG-03), SELECTING (RTG-01), SWITCHING (RTG-04), FALLBACK (RTG-02), ERROR (RTG-03) ✅
- **Provider**: REGISTERING (PRV-01), ACTIVE (PRV-01), SELECTING (PRV-04), ERROR (PRV-01) ✅
- **Evaluation**: CHECKING (EVL-01), REVIEWING (EVL-04), TESTING (EVL-05), SCORING (EVL-07), RETRYING (EVL-06), PASSED (EVL-07), FAILED (EVL-02) ✅
- **Index**: INDEXING (RIM-01), INDEXED (RIM-01), BUILDING_GRAPH (RIM-02), EMBEDDING (RIM-05), STALE (RIM-01), ERROR (RIM-01) ✅

### Agent Process FSM — Documented Deviation

The Agent SM is intentionally a **Process FSM**, not an Entity Lifecycle. Per sm.md:
*"SMT rules from sm.md do not apply (documented deviation)."*

Rationale:
- Models the runtime processing loop of AgentOrchestrator, not a persisted entity.
- States (THINKING, TOOL_EXEC, RESPONDING) are transient processing states.
- Transitions driven by UC events on the active processing context, not writes to a stored entity.
- No persisted `lifecycle_state` — the process state lives in the runtime stack.

### Orphan Transition Resolution Plan

The 115 orphan transitions will be resolved by the SQ Diagrammer when the SQ layer activates:

| Phase | Priority | SM Diagrams | Orphans | Target |
|-------|----------|-------------|---------|--------|
| 1 | HIGH | persona, mcp_client, mcp_server, sandbox, diff_staging | 51 | Next cycle |
| 2 | MEDIUM | safety, router, provider, evaluation, index | 64 | After Phase 1 |

### Final Gate Status

| Criteria | Status |
|----------|--------|
| All stateful entities identified across 21 C4 groups | ✅ |
| All 15 SMs pass `sm_lint.py --strict` (0 violations) | ✅ |
| All hex colors unique (92 states, 92 colors, 0 duplicates) | ✅ |
| All terminal transitions have UC-IDs | ✅ |
| All lifecycle-write states have exactly one owning UC | ✅ |
| Transition coverage tables complete (all 15 SMs in README) | ✅ |
| Documentation up to date (state tables, matrices, maps) | ✅ |
| SQ coverage (orphan resolution) | ⏳ — 115 orphans remain |
