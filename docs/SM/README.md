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
| ROUTING | Model selection in progress | LLMRepository resolving model | #EDE7F6 |
| SERVING | API processing request from any interface | API-06 DISPATCH Message | #E0F7FA |
| EVALUATING | Evaluating task completion | task_complete AND evaluation_enabled | #F9FBE7 |
| REVIEWING | LLM review of results | success checks passed, optional review | #FFF8E1 |
| RETRYING | Retrying with feedback | success checks failed or review rejected | #FBE9E7 |
| STAGING | Diff sandbox staging | tool exec in diff_sandbox mode | #F1F8E9 |
| AWAITING_DIFF_APPROVAL | Presenting diff to user | SAFETY-02 REQUEST Approval | #FCE4EC |

> **API-First Entry:** All entry/exit transitions use `API-06` (DISPATCH Message) as the sole entry gate. No interface container may bypass the API.

### Transitions from STAGING

| From | To | UC ID | Condition |
|------|----|-------|-----------|
| STAGING | AWAITING_DIFF_APPROVAL | EDITSTRATEGY-10 | Diff computed successfully |
| STAGING | ERROR | EDITSTRATEGY-10 | Diff computation failed (file deleted, conflict, algorithm error) |

## Session Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| CREATED | Session record initialized | API-02 CREATE Session | #BBDEFB |
| ACTIVE | Session accepting messages | Session created or restored | #43A047 |
| SAVED | Session persisted to disk | API-04 UPDATE Session | #1565C0 |
| RESTORED | Session loaded from disk | API-03 GET Session | #1E88E5 |
| BRANCHED | Session forked from parent | WIRELOG-04 FORK Session | #7B1FA2 |
| CLOSED | Session terminated | API-05 DELETE Session | #757575 |

## Plan Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No plan active | Default state | #F5F5F5 |
| BUILDING | Plan being constructed | AGENT-07 QUEUE Plan | #FFE0B2 |
| QUEUED | Plan queued for approval | Plan construction complete | #E3F2FD |
| APPROVED | Plan approved by user | AGENT-08 APPROVE Plan | #388E3C |
| EXECUTING | Plan steps being executed | Plan approved, execution started | #A5D6A7 |
| COMPLETED | All plan steps finished | Implicit: agent loop finishes all steps | #1B5E20 |
| REJECTED | Plan rejected by user | User rejects plan | #B71C1C |

## Plugin Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCOVERED | Plugin found on filesystem | PLUGINS-01 DISCOVER Plugins | #E0E0E0 |
| LOADING | Plugin manifest being parsed | PLUGINS-02 LOAD Manifest | #FFCC80 |
| LOADED | Plugin manifest parsed, tools registered | PLUGINS-03 REGISTER Plugin Tools | #90CAF9 |
| ENABLED | Plugin active and available | PLUGINS-05 ENABLE Plugin | #4CAF50 |
| DISABLED | Plugin deactivated | PLUGINS-06 DISABLE Plugin | #CE93D8 |
| ERROR | Plugin failed to load or crashed | Load error or runtime exception | #EF5350 |

## Subagent Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No child agent active | Default state | #CFD8DC |
| SPAWNING | Child agent process initializing | AGENT-09 SPAWN Subagent | #FFAB91 |
| RUNNING | Child agent executing task | AGENT-09 SPAWN Subagent | #BCAAA4 |
| COMPLETED | Child agent finished successfully | AGENT-10 COLLECT Subagent Result | #80CBC4 |
| FAILED | Child agent encountered unrecoverable error | AGENT-14 HANDLE Error | #EF9A9A |

## Persona Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNLOADED | No persona loaded | Default state | #9E9E9E |
| LOADING | Persona configuration being loaded | AGENT-12 LOAD Persona | #FFC107 |
| ACTIVE | Persona active and available for delegation | AGENT-11 DELEGATE to Persona | #4DB6AC |
| SWITCHING | Switching to different persona at runtime | AGENT-13 SWITCH Persona | #FF9800 |
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
| EXECUTING | Process running in sandbox | SANDBOX-01 ISOLATE Command | #2196F3 |
| MONITORING | Process being monitored for resource usage | SANDBOX-03 MONITOR Process | #64B5F6 |
| COMPLETED | Process finished successfully | SANDBOX-01 ISOLATE Command | #8BC34A |
| TIMEOUT | Process exceeded time limit | SANDBOX-03 MONITOR Process | #FFB74D |
| FAILED | Process crashed or was killed | SANDBOX-01 ISOLATE Command | #D32F2F |
| RESOURCE_EXCEEDED | Process exceeded CPU, memory, or disk quota | SANDBOX-04 LIMIT Resources | #FF5722 |

## Diff Staging Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No diff staged | Default state | #9FA8DA |
| STAGING | Diff being computed | EDITSTRATEGY-10 STAGE Diff | #FFE082 |
| STAGED | Diff ready for review | EDITSTRATEGY-10 STAGE Diff | #C5E1A5 |
| AWAITING_APPROVAL | Diff presented to user for approval | SAFETY-02 REQUEST Approval | #FFD54F |
| APPROVED | User approved diff | SAFETY-02 REQUEST Approval | #AED581 |
| APPLYING | Approved diff being applied | EDITSTRATEGY-10 STAGE Diff | #81C784 |
| APPLIED | Diff successfully applied | EDITSTRATEGY-10 STAGE Diff | #009688 |
| ERROR | Diff computation or application failed | EDITSTRATEGY-10 failure | #E53935 |

## Safety Mode Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINITIALIZED | Safety system not initialized | Default state | #BDBDBD |
| PERMISSIVE | All operations allowed, no approval prompts | SAFETY-03 APPLY Safety Mode | #9CCC65 |
| ASK | User approval required for sensitive operations | SAFETY-03 APPLY Safety Mode | #FDD835 |
| BLOCK | Dangerous operations blocked entirely | SAFETY-03 APPLY Safety Mode | #E91E63 |
| ERROR | Safety system encountered an error | SAFETY-01 CHECK Permission failure | #F4511E |

## Router Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No routing in progress | Default state | #EEEEEE |
| CLASSIFYING | Task classification for model routing | ROUTER-03 CLASSIFY Task | #5C6BC0 |
| SELECTING | Model selection in progress | ROUTER-01 SELECT Model | #3F51B5 |
| SWITCHING | Runtime model switch in progress | ROUTER-04 SWITCH Model | #FF8F00 |
| FALLBACK | Falling back to next available model | ROUTER-02 APPLY Fallback | #EF6C00 |
| ERROR | Routing or fallback failed | All models exhausted | #BF360C |

## Provider Connection Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNREGISTERED | No provider registered | Default state | #455A64 |
| REGISTERING | Provider registration in progress | PROVIDER-01 REGISTER Provider | #29B6F6 |
| ACTIVE | Provider registered and ready for chat | PROVIDER-01 REGISTER Provider | #03A9F4 |
| SELECTING | Backend selection in progress | PROVIDER-04 SELECT Provider Backend | #FBC02D |
| ERROR | Registration or selection failed | Provider unavailable | #E64A19 |

## Evaluation Lifecycle States (Process)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No evaluation in progress | Default state | #90A4AE |
| CHECKING | Running task completion and success checks | EVALUATION-01 EVALUATE Task | #C5CAE9 |
| REVIEWING | LLM-based code review and quality assessment | EVALUATION-04 VALIDATE With LLM | #AB47BC |
| TESTING | Running project test suites | EVALUATION-05 VALIDATE Test Suite | #D4E157 |
| SCORING | Recording quality signal and scoring | EVALUATION-07 RECORD Quality Signal | #FF8A65 |
| RETRYING | Coordinating retry with backoff and escalation | EVALUATION-06 COORDINATE Retry | #C62828 |
| PASSED | Evaluation passed all criteria | Terminal success state | #689F38 |
| FAILED | Evaluation failed, retries exhausted | Terminal failure state | #AD1457 |

## Repository Index Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINDEXED | No repository index exists | Default state | #424242 |
| INDEXING | AST indexing via tree-sitter in progress | REPOINTELLIGENCE-01 INDEX Codebase | #4FC3F7 |
| INDEXED | Repository fully indexed | REPOINTELLIGENCE-01 INDEX Codebase | #7CB342 |
| BUILDING_GRAPH | Cross-file symbol reference graph in progress | REPOINTELLIGENCE-02 BUILD Symbol Graph | #9C27B0 |
| EMBEDDING | Generating vector embeddings for code | REPOINTELLIGENCE-05 EMBED Code | #E6EE9C |
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
- **Transition labels** use UC-ID-only convention (e.g., `AGENT-01`, `PROVIDER-02`, `SAFETY-02`).
  No human-readable suffixes. Multiple transitions from one state may share a UC ID
  when the same action produces different outcomes (e.g., `PROVIDER-02` → RESPONDING, TOOL_EXEC, ERROR).
- **API-First:** All entry/exit transitions in Agent SM use `API-06` as the sole entry gate.
  Session lifecycle mutations use API UCs (API-02 through API-05).

## Transition Matrices

### Agent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | AGENT-01 | Process startup |
| IDLE | LISTENING | API-06 | DISPATCH Message received |
| IDLE | SERVING | API-06 | API request received |
| IDLE | PLANNING | AGENT-07 | /plan command entered |
| LISTENING | THINKING | API-06 | Input parsed, messages built |
| SERVING | THINKING | API-06 | API request processed |
| SERVING | IDLE | API-06 | API request complete |
| THINKING | RESPONDING | PROVIDER-02 | LLM returns text only |
| THINKING | TOOL_EXEC | PROVIDER-02 | LLM returns tool_calls |
| THINKING | COMPACTING | AGENT-06 | token_count > context_budget |
| THINKING | ROUTING | ROUTER-01 | ModelRouter resolving model |
| THINKING | ERROR | PROVIDER-02 | Provider call failed |
| THINKING | EVALUATING | EVALUATION-01 | task_complete AND evaluation_enabled |
| ROUTING | THINKING | ROUTER-01 | Model selected |
| TOOL_EXEC | THINKING | AGENT-02 | Tool call complete |
| TOOL_EXEC | AWAITING_APPROVAL | SAFETY-02 | safety_mode=ask AND unsafe tool |
| TOOL_EXEC | HOOK_RUNNING | HOOKS-02 | Pre/post hook configured |
| TOOL_EXEC | ERROR | AGENT-02 | Tool execution failed |
| TOOL_EXEC | STAGING | EDITSTRATEGY-10 | diff_sandbox mode active |
| HOOK_RUNNING | TOOL_EXEC | HOOKS-02 | Hook execution complete |
| HOOK_RUNNING | IDLE | HOOKS-02 | Hook execution complete (no tool) |
| AWAITING_APPROVAL | TOOL_EXEC | SAFETY-02 | User approves |
| AWAITING_APPROVAL | IDLE | SAFETY-02 | User denies |
| COMPACTING | THINKING | AGENT-06 | Context compacted |
| RESPONDING | IDLE | API-06 | Response streamed to user |
| ERROR | IDLE | AGENT-14 | Error handled |
| PLANNING | IDLE | AGENT-07 | Plan mode exited |
| EVALUATING | REVIEWING | EVALUATION-01 | Evaluation passed |
| EVALUATING | RETRYING | EVALUATION-01 | Evaluation failed |
| EVALUATING | THINKING | EVALUATION-01 | Retry with feedback |
| REVIEWING | THINKING | EVALUATION-04 | LLM review passed |
| REVIEWING | RETRYING | EVALUATION-04 | LLM review rejected |
| RETRYING | THINKING | EVALUATION-06 | Retry with feedback |
| RETRYING | ERROR | EVALUATION-06 | Retry exhausted |
| STAGING | AWAITING_DIFF_APPROVAL | EDITSTRATEGY-10 | Diff computed successfully |
| STAGING | ERROR | EDITSTRATEGY-10 | Diff computation failed |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAFETY-02 | User approves diff |
| AWAITING_DIFF_APPROVAL | IDLE | SAFETY-02 | User rejects diff |

### Session Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | CREATED | API-02 | Session record initialized |
| CREATED | ACTIVE | API-02 | Session ready for messages |
| ACTIVE | SAVED | API-04 | Session persisted to disk |
| ACTIVE | BRANCHED | WIRELOG-04 | Session forked from parent |
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
| [*] | EMPTY | AGENT-07 | No plan active |
| EMPTY | BUILDING | AGENT-07 | /plan command entered |
| BUILDING | QUEUED | AGENT-07 | Plan construction complete |
| BUILDING | EMPTY | AGENT-07 | Plan cancelled |
| QUEUED | APPROVED | AGENT-08 | User approves plan |
| QUEUED | REJECTED | AGENT-08 | User rejects plan |
| APPROVED | EXECUTING | AGENT-08 | Execution started |
| EXECUTING | COMPLETED | AGENT-01 | All plan steps finished |
| EXECUTING | EMPTY | AGENT-14 | Execution failed or cancelled |
| COMPLETED | [*] | AGENT-01 | Terminal state |
| REJECTED | [*] | AGENT-08 | Terminal state |

### Plugin Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | DISCOVERED | PLUGINS-01 | Plugin found on filesystem |
| DISCOVERED | LOADING | PLUGINS-02 | Manifest parsing starts |
| DISCOVERED | ERROR | PLUGINS-01 | Plugin discovery failed |
| LOADING | LOADED | PLUGINS-03 | Manifest parsed, tools registered |
| LOADING | ERROR | PLUGINS-02 | Manifest parsing failed |
| LOADED | ENABLED | PLUGINS-05 | Plugin activated |
| LOADED | DISABLED | PLUGINS-06 | Plugin deactivated |
| LOADED | ERROR | PLUGINS-03 | Tool registration failed |
| ENABLED | DISABLED | PLUGINS-06 | Plugin deactivated |
| ENABLED | ERROR | PLUGINS-01 | Runtime exception |
| ENABLED | [*] | PLUGINS-06 | Plugin unloaded |
| DISABLED | ENABLED | PLUGINS-05 | Plugin activated |
| DISABLED | [*] | PLUGINS-06 | Plugin unloaded |
| ERROR | DISCOVERED | PLUGINS-01 | Re-discovery (recovery) |

### Subagent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | AGENT-09 | Default state |
| IDLE | SPAWNING | AGENT-09 | Child agent spawn requested |
| SPAWNING | RUNNING | AGENT-09 | Child agent initialized |
| SPAWNING | FAILED | AGENT-09 | Spawn failed |
| RUNNING | COMPLETED | AGENT-10 | Task finished successfully |
| RUNNING | FAILED | AGENT-14 | Unrecoverable error |
| COMPLETED | IDLE | AGENT-10 | Results aggregated to parent |
| COMPLETED | [*] | AGENT-10 | Terminal state |
| FAILED | IDLE | AGENT-14 | Error reported, cleanup done |
| FAILED | [*] | AGENT-14 | Terminal state |

### Persona Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNLOADED | AGENT-12 | Default state |
| UNLOADED | LOADING | AGENT-12 | Load requested |
| LOADING | ACTIVE | AGENT-12 | Load successful |
| LOADING | ERROR | AGENT-12 | Load failed |
| ACTIVE | SWITCHING | AGENT-13 | Switch requested |
| SWITCHING | ACTIVE | AGENT-13 | Switch successful |
| SWITCHING | ERROR | AGENT-13 | Switch failed |
| ACTIVE | UNLOADED | AGENT-11 | Delegation complete |
| ERROR | UNLOADED | AGENT-12 | Recovery: retry load |
| UNLOADED | [*] | AGENT-12 | Terminal state |

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
| [*] | IDLE | SANDBOX-01 | Default state |
| IDLE | EXECUTING | SANDBOX-01 | Command started |
| EXECUTING | MONITORING | SANDBOX-03 | Resource monitoring started |
| MONITORING | EXECUTING | SANDBOX-03 | Monitoring continues |
| EXECUTING | COMPLETED | SANDBOX-01 | Process finished |
| EXECUTING | FAILED | SANDBOX-01 | Process crashed |
| EXECUTING | TIMEOUT | SANDBOX-03 | Timeout exceeded |
| EXECUTING | RESOURCE_EXCEEDED | SANDBOX-04 | Resource limit hit |
| MONITORING | TIMEOUT | SANDBOX-03 | Timeout exceeded |
| MONITORING | RESOURCE_EXCEEDED | SANDBOX-04 | Resource limit hit |
| TIMEOUT | IDLE | SANDBOX-01 | Cleanup after timeout |
| FAILED | IDLE | SANDBOX-01 | Cleanup after failure |
| RESOURCE_EXCEEDED | IDLE | SANDBOX-04 | Cleanup after resource violation |
| COMPLETED | [*] | SANDBOX-01 | Terminal state |

### Diff Staging Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | EMPTY | EDITSTRATEGY-10 | Default state |
| EMPTY | STAGING | EDITSTRATEGY-10 | Diff computation started |
| STAGING | STAGED | EDITSTRATEGY-10 | Diff computed successfully |
| STAGING | ERROR | EDITSTRATEGY-10 | Diff computation failed |
| STAGED | AWAITING_APPROVAL | EDITSTRATEGY-10 | Diff presented for review |
| AWAITING_APPROVAL | APPROVED | SAFETY-02 | User approved |
| AWAITING_APPROVAL | EMPTY | SAFETY-02 | User rejected, cleanup |
| APPROVED | APPLYING | EDITSTRATEGY-10 | Diff application started |
| APPLYING | APPLIED | EDITSTRATEGY-10 | Diff applied successfully |
| APPLYING | ERROR | EDITSTRATEGY-10 | Diff application failed |
| APPLIED | EMPTY | EDITSTRATEGY-10 | Cleanup after application |
| ERROR | EMPTY | EDITSTRATEGY-10 | Cleanup after error |
| APPLIED | [*] | EDITSTRATEGY-10 | Terminal state |

## Lifecycle-Write UC Mapping (SMT Ownership)

One lifecycle-write UC per target state. This table is the authoritative reference.

### Session Lifecycle (API-First)

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CREATED | API-02 CREATE Session | Session record initialized |
| ACTIVE | API-02 CREATE Session | Session accepting messages (after init/resume) |
| SAVED | API-04 UPDATE Session | Session persisted to disk |
| RESTORED | API-03 GET Session | Session loaded from disk |
| BRANCHED | WIRELOG-04 FORK Session | Session forked from parent |
| CLOSED | API-05 DELETE Session | Session terminated (quit or error) |

### Plan Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| BUILDING | AGENT-07 QUEUE Plan | Plan being constructed |
| QUEUED | AGENT-07 QUEUE Plan | Plan construction complete, queued for approval |
| APPROVED | AGENT-08 APPROVE Plan | Plan approved by user |
| EXECUTING | AGENT-08 APPROVE Plan | Plan execution starts |
| COMPLETED | AGENT-01 PROCESS User Task | Agent loop finishes all steps |
| REJECTED | AGENT-08 APPROVE Plan | Plan rejected by user |

### Plugin Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| DISCOVERED | PLUGINS-01 DISCOVER Plugins | Plugin found on filesystem |
| LOADING | PLUGINS-02 LOAD Manifest | Plugin manifest being parsed |
| LOADED | PLUGINS-03 REGISTER Plugin Tools | Manifest parsed, tools registered |
| ENABLED | PLUGINS-05 ENABLE Plugin | Plugin active and available |
| DISABLED | PLUGINS-06 DISABLE Plugin | Plugin deactivated |
| ERROR | PLUGINS-01 DISCOVER Plugins | Load error or runtime exception (re-discover recovers) |

### Subagent Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| SPAWNING | AGENT-09 SPAWN Subagent | Child agent process initializing |
| RUNNING | AGENT-09 SPAWN Subagent | Child agent executing task |
| COMPLETED | AGENT-10 COLLECT Subagent Result | Child agent finished successfully |
| FAILED | AGENT-14 HANDLE Error | Child agent encountered unrecoverable error |

### Persona Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| LOADING | AGENT-12 LOAD Persona | Persona configuration being loaded |
| ACTIVE | AGENT-11 DELEGATE to Persona | Persona active and available |
| SWITCHING | AGENT-13 SWITCH Persona | Switching persona at runtime |
| ERROR | AGENT-12 LOAD Persona | Persona load or switch failed |

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
| EXECUTING | SANDBOX-01 ISOLATE Command | Process running in sandbox |
| MONITORING | SANDBOX-03 MONITOR Process | Process being monitored |
| COMPLETED | SANDBOX-01 ISOLATE Command | Process finished successfully |
| TIMEOUT | SANDBOX-03 MONITOR Process | Process exceeded time limit |
| FAILED | SANDBOX-01 ISOLATE Command | Process crashed or was killed |
| RESOURCE_EXCEEDED | SANDBOX-04 LIMIT Resources | Process exceeded resource quota |

### Diff Staging Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| STAGING | EDITSTRATEGY-10 STAGE Diff | Diff being computed |
| STAGED | EDITSTRATEGY-10 STAGE Diff | Diff ready for review |
| AWAITING_APPROVAL | SAFETY-02 REQUEST Approval | Diff presented for user approval |
| APPROVED | SAFETY-02 REQUEST Approval | User approved diff |
| APPLYING | EDITSTRATEGY-10 STAGE Diff | Approved diff being applied |
| APPLIED | EDITSTRATEGY-10 STAGE Diff | Diff successfully applied |
| ERROR | EDITSTRATEGY-10 STAGE Diff | Diff computation or application failed |

### Safety Mode Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| UNINITIALIZED | SAFETY-03 APPLY Safety Mode | Safety system not initialized |
| PERMISSIVE | SAFETY-03 APPLY Safety Mode | Permissive mode applied |
| ASK | SAFETY-03 APPLY Safety Mode | Ask mode applied |
| BLOCK | SAFETY-03 APPLY Safety Mode | Block mode applied |
| ERROR | SAFETY-01 CHECK Permission | Safety system encountered error |

### Router Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CLASSIFYING | ROUTER-03 CLASSIFY Task | Task classification started |
| SELECTING | ROUTER-01 SELECT Model | Model selection in progress |
| SWITCHING | ROUTER-04 SWITCH Model | Runtime model switch |
| FALLBACK | ROUTER-02 APPLY Fallback | Falling back to next model |
| ERROR | ROUTER-03 CLASSIFY Task | Classification or routing failure |

### Provider Connection Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| REGISTERING | PROVIDER-01 REGISTER Provider | Provider registration started |
| ACTIVE | PROVIDER-01 REGISTER Provider | Provider registered and ready |
| SELECTING | PROVIDER-04 SELECT Provider Backend | Backend selection in progress |
| ERROR | PROVIDER-01 REGISTER Provider | Registration or selection failed |

### Evaluation Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CHECKING | EVALUATION-01 EVALUATE Task | Task completion checks started |
| REVIEWING | EVALUATION-04 VALIDATE With LLM | LLM review in progress |
| TESTING | EVALUATION-05 VALIDATE Test Suite | Test validation in progress |
| SCORING | EVALUATION-07 RECORD Quality Signal | Scoring in progress |
| RETRYING | EVALUATION-06 COORDINATE Retry | Retry with backoff and escalation |
| PASSED | EVALUATION-07 RECORD Quality Signal | Evaluation passed |
| FAILED | EVALUATION-02 CHECK Task Completion | Evaluation failed |

### Repository Index Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| INDEXING | REPOINTELLIGENCE-01 INDEX Codebase | AST indexing in progress |
| INDEXED | REPOINTELLIGENCE-01 INDEX Codebase | Repository fully indexed |
| BUILDING_GRAPH | REPOINTELLIGENCE-02 BUILD Symbol Graph | Cross-file symbol reference graph |
| EMBEDDING | REPOINTELLIGENCE-05 EMBED Code | Vector embedding generation |
| STALE | REPOINTELLIGENCE-01 INDEX Codebase | Index outdated, needs re-index |
| ERROR | REPOINTELLIGENCE-01 INDEX Codebase | Indexing operation failed |

## SM → SQ Transition Coverage Tables

> **TRC-SM-05 compliance:** Every SM transition mapped to its implementing SQ diagram.
> Terminal (`[*]`) transitions are state diagram syntax, not implementable transitions — marked `—`.

### sm_agent_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | AGENT-01 | Process startup | sq_agent01_process_user_task.puml |
| IDLE | LISTENING | API-06 | DISPATCH Message received | sq_api06_dispatch_message.puml |
| IDLE | SERVING | API-06 | API request received | sq_api06_dispatch_message.puml |
| IDLE | PLANNING | AGENT-07 | /plan command entered | sq_agent07_queue_plan.puml |
| IDLE | [*] | AGENT-01 | Error handled | — |
| LISTENING | THINKING | API-06 | Input parsed, messages built | sq_api06_dispatch_message.puml |
| SERVING | THINKING | API-06 | API request processed | sq_api06_dispatch_message.puml |
| SERVING | IDLE | API-06 | API request complete | sq_api06_dispatch_message.puml |
| THINKING | RESPONDING | PROVIDER-02 | LLM returns text only | sq_provider02_request_chat.puml |
| THINKING | TOOL_EXEC | PROVIDER-02 | LLM returns tool_calls | sq_provider02_request_chat.puml |
| THINKING | COMPACTING | AGENT-06 | token_count > context_budget | sq_agent06_compact_context.puml |
| THINKING | ROUTING | ROUTER-01 | ModelRouter resolving model | sq_router01_select_model.puml |
| THINKING | ERROR | PROVIDER-02 | Provider call failed | sq_provider02_request_chat.puml |
| THINKING | RESPONDING | API-06 | Response dispatched | sq_api06_dispatch_message.puml |
| THINKING | EVALUATING | EVALUATION-01 | task_complete AND evaluation_enabled | sq_evaluation01_evaluate_task.puml |
| ROUTING | THINKING | ROUTER-01 | Model selected | sq_router01_select_model.puml |
| TOOL_EXEC | THINKING | AGENT-02 | Tool call complete | sq_agent02_dispatch_tool_call.puml |
| TOOL_EXEC | AWAITING_APPROVAL | SAFETY-02 | safety_mode=ask AND unsafe tool | sq_safety02_request_approval.puml |
| TOOL_EXEC | HOOK_RUNNING | HOOKS-02 | Pre/post hook configured | sq_hooks02_dispatch_pre_tool_hook.puml |
| TOOL_EXEC | ERROR | AGENT-02 | Tool execution failed | sq_agent02_dispatch_tool_call.puml |
| TOOL_EXEC | STAGING | EDITSTRATEGY-10 | diff_sandbox mode active | sq_editstrategy10_stage_diff.puml |
| HOOK_RUNNING | TOOL_EXEC | HOOKS-02 | Hook execution complete | sq_hooks02_dispatch_pre_tool_hook.puml |
| HOOK_RUNNING | IDLE | HOOKS-02 | Hook execution complete (no tool) | sq_hooks02_dispatch_pre_tool_hook.puml |
| AWAITING_APPROVAL | TOOL_EXEC | SAFETY-02 | User approves | sq_safety02_request_approval.puml |
| AWAITING_APPROVAL | IDLE | SAFETY-02 | User denies | sq_safety02_request_approval.puml |
| COMPACTING | THINKING | AGENT-06 | Context compacted | sq_agent06_compact_context.puml |
| RESPONDING | IDLE | API-06 | Response streamed to user | sq_api06_dispatch_message.puml |
| ERROR | IDLE | AGENT-14 | Error handled | sq_agent14_handle_error.puml |
| PLANNING | IDLE | AGENT-07 | Plan mode exited | sq_agent07_queue_plan.puml |
| EVALUATING | REVIEWING | EVALUATION-01 | Evaluation passed | sq_evaluation01_evaluate_task.puml |
| EVALUATING | RETRYING | EVALUATION-01 | Evaluation failed | sq_evaluation01_evaluate_task.puml |
| EVALUATING | THINKING | EVALUATION-01 | Retry with feedback | sq_evaluation01_evaluate_task.puml |
| REVIEWING | THINKING | EVALUATION-04 | LLM review passed | sq_evaluation04_validate_with_llm.puml |
| REVIEWING | RETRYING | EVALUATION-04 | LLM review rejected | sq_evaluation04_validate_with_llm.puml |
| RETRYING | THINKING | EVALUATION-06 | Retry with feedback | sq_evaluation06_coordinate_retry.puml |
| RETRYING | ERROR | EVALUATION-06 | Retry exhausted | sq_evaluation06_coordinate_retry.puml |
| STAGING | AWAITING_DIFF_APPROVAL | EDITSTRATEGY-10 | Diff computed successfully | sq_editstrategy10_stage_diff.puml |
| STAGING | ERROR | EDITSTRATEGY-10 | Diff computation failed | sq_editstrategy10_stage_diff.puml |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAFETY-02 | User approves diff | sq_safety02_request_approval.puml |
| AWAITING_DIFF_APPROVAL | IDLE | SAFETY-02 | User rejects diff | sq_safety02_request_approval.puml |

> **Coverage:** 39/39 non-terminal transitions covered. 0 ORPHANs.
> **Note:** `THINKING→RESPONDING` appears twice with different UC-IDs — `PROVIDER-02` (provider generates content) and `API-06` (API dispatches to network) — reflecting two semantically distinct transitions between the same states.

### sm_session_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | CREATED | API-02 | Session record initialized | sq_api02_create_session.puml |
| CREATED | ACTIVE | API-02 | Session ready for messages | sq_api02_create_session.puml |
| ACTIVE | SAVED | API-04 | Session persisted to disk | sq_api04_update_session.puml |
| ACTIVE | BRANCHED | WIRELOG-04 | Session forked from parent | sq_wirelog04_fork_session.puml |
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
| [*] | IDLE | AGENT-09 | Default state | sq_agent09_spawn_subagent.puml |
| IDLE | SPAWNING | AGENT-09 | Child agent spawn requested | sq_agent09_spawn_subagent.puml |
| SPAWNING | RUNNING | AGENT-09 | Child agent initialized | sq_agent09_spawn_subagent.puml |
| SPAWNING | FAILED | AGENT-09 | Spawn failed | sq_agent09_spawn_subagent.puml |
| RUNNING | COMPLETED | AGENT-10 | Task finished successfully | sq_agent10_collect_subagent_result.puml |
| RUNNING | FAILED | AGENT-14 | Unrecoverable error | sq_agent14_handle_error.puml |
| COMPLETED | IDLE | AGENT-10 | Results aggregated to parent | sq_agent10_collect_subagent_result.puml |
| COMPLETED | [*] | AGENT-10 | Terminal state | — |
| FAILED | IDLE | AGENT-14 | Error reported, cleanup done | sq_agent14_handle_error.puml |
| FAILED | [*] | AGENT-14 | Terminal state | — |

> **Coverage:** 8/8 non-terminal transitions covered. 0 ORPHANs.

### sm_plugin_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCOVERED | PLUGINS-01 | Plugin found on filesystem | sq_plugins01_discover_plugins.puml |
| DISCOVERED | LOADING | PLUGINS-02 | Manifest parsing starts | sq_plugins02_load_manifest.puml |
| DISCOVERED | ERROR | PLUGINS-01 | Plugin discovery failed | sq_plugins01_discover_plugins.puml |
| LOADING | LOADED | PLUGINS-03 | Manifest parsed, tools registered | sq_plugins03_register_plugin_tools.puml |
| LOADING | ERROR | PLUGINS-02 | Manifest parsing failed | sq_plugins02_load_manifest.puml |
| LOADED | ENABLED | PLUGINS-05 | Plugin activated | sq_plugins05_enable_plugin.puml |
| LOADED | DISABLED | PLUGINS-06 | Plugin deactivated | sq_plugins06_disable_plugin.puml |
| LOADED | ERROR | PLUGINS-03 | Tool registration failed | sq_plugins03_register_plugin_tools.puml |
| ENABLED | DISABLED | PLUGINS-06 | Plugin deactivated | sq_plugins06_disable_plugin.puml |
| ENABLED | ERROR | PLUGINS-01 | Runtime exception | sq_plugins01_discover_plugins.puml |
| ENABLED | [*] | PLUGINS-06 | Plugin unloaded | — |
| DISABLED | ENABLED | PLUGINS-05 | Plugin activated | sq_plugins05_enable_plugin.puml |
| DISABLED | [*] | PLUGINS-06 | Plugin unloaded | — |
| ERROR | DISCOVERED | PLUGINS-01 | Re-discovery (recovery) | sq_plugins01_discover_plugins.puml |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_plan_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | AGENT-07 | No plan active | sq_agent07_queue_plan.puml |
| EMPTY | BUILDING | AGENT-07 | /plan command entered | sq_agent07_queue_plan.puml |
| BUILDING | QUEUED | AGENT-07 | Plan construction complete | sq_agent07_queue_plan.puml |
| BUILDING | EMPTY | AGENT-07 | Plan cancelled | sq_agent07_queue_plan.puml |
| QUEUED | APPROVED | AGENT-08 | User approves plan | sq_agent08_approve_plan.puml |
| QUEUED | REJECTED | AGENT-08 | User rejects plan | sq_agent08_approve_plan.puml |
| APPROVED | EXECUTING | AGENT-08 | Execution started | sq_agent08_approve_plan.puml |
| EXECUTING | COMPLETED | AGENT-01 | All plan steps finished | sq_agent01_process_user_task.puml |
| EXECUTING | EMPTY | AGENT-14 | Execution failed or cancelled | sq_agent14_handle_error.puml |
| COMPLETED | [*] | AGENT-01 | Terminal state | — |
| REJECTED | [*] | AGENT-08 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_persona_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNLOADED | AGENT-12 | Default state | `sq_agent12_load_persona.puml` |
| UNLOADED | LOADING | AGENT-12 | Load requested | `sq_agent12_load_persona.puml` |
| LOADING | ACTIVE | AGENT-12 | Load successful | `sq_agent12_load_persona.puml` |
| LOADING | ERROR | AGENT-12 | Load failed | `sq_agent12_load_persona.puml` |
| ACTIVE | SWITCHING | AGENT-13 | Switch requested | `sq_agent13_switch_persona.puml` |
| SWITCHING | ACTIVE | AGENT-13 | Switch successful | `sq_agent13_switch_persona.puml` |
| SWITCHING | ERROR | AGENT-13 | Switch failed | `sq_agent13_switch_persona.puml` |
| ACTIVE | UNLOADED | AGENT-11 | Delegation complete | `sq_agent11_delegate_to_persona.puml` |
| ERROR | UNLOADED | AGENT-12 | Recovery: retry load | `sq_agent12_load_persona.puml` |
| UNLOADED | [*] | AGENT-12 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_mcp_client_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCONNECTED | MCP-01 | Default state | `sq_mcp01_connect_mcp_server.puml` |
| DISCONNECTED | CONNECTING | MCP-01 | Connect requested | `sq_mcp01_connect_mcp_server.puml` |
| CONNECTING | CONNECTED | MCP-01 | Connection established | `sq_mcp01_connect_mcp_server.puml` |
| CONNECTING | ERROR | MCP-01 | Connection failed | `sq_mcp01_connect_mcp_server.puml` |
| CONNECTED | DISCOVERING | MCP-02 | Tool discovery started | `sq_mcp02_discover_mcp_tools.puml` |
| DISCOVERING | CONNECTED | MCP-02 | Discovery complete | `sq_mcp02_discover_mcp_tools.puml` |
| DISCOVERING | ERROR | MCP-02 | Discovery failed | `sq_mcp02_discover_mcp_tools.puml` |
| CONNECTED | DISCONNECTED | MCP-01 | Disconnected | `sq_mcp01_connect_mcp_server.puml` |
| ERROR | DISCONNECTED | MCP-01 | Recovery: reconnect | `sq_mcp01_connect_mcp_server.puml` |
| DISCONNECTED | [*] | MCP-01 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_mcp_server_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | STOPPED | MCP-04 | Default state | `sq_mcp04_expose_nasim_tools.puml` |
| STOPPED | STARTING | MCP-04 | Start requested | `sq_mcp04_expose_nasim_tools.puml` |
| STARTING | RUNNING | MCP-04 | Startup complete | `sq_mcp04_expose_nasim_tools.puml` |
| STARTING | ERROR | MCP-04 | Startup failed | `sq_mcp04_expose_nasim_tools.puml` |
| RUNNING | STOPPING | MCP-04 | Stop requested | `sq_mcp04_expose_nasim_tools.puml` |
| STOPPING | STOPPED | MCP-04 | Shutdown complete | `sq_mcp04_expose_nasim_tools.puml` |
| RUNNING | ERROR | MCP-04 | Runtime failure | `sq_mcp04_expose_nasim_tools.puml` |
| ERROR | STOPPED | MCP-04 | Recovery: shutdown | `sq_mcp04_expose_nasim_tools.puml` |
| STOPPED | [*] | MCP-04 | Terminal state | — |

> **Coverage:** 8/8 non-terminal transitions covered. 0 ORPHANs.

### sm_sandbox_execution_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | SANDBOX-01 | Default state | `sq_sandbox01_isolate_command.puml` |
| IDLE | EXECUTING | SANDBOX-01 | Command started | `sq_sandbox01_isolate_command.puml` |
| EXECUTING | MONITORING | SANDBOX-03 | Resource monitoring started | `sq_sandbox03_monitor_process.puml` |
| MONITORING | EXECUTING | SANDBOX-03 | Monitoring continues | `sq_sandbox03_monitor_process.puml` |
| EXECUTING | COMPLETED | SANDBOX-01 | Process finished | `sq_sandbox01_isolate_command.puml` |
| EXECUTING | FAILED | SANDBOX-01 | Process crashed | `sq_sandbox01_isolate_command.puml` |
| EXECUTING | TIMEOUT | SANDBOX-03 | Timeout exceeded | `sq_sandbox03_monitor_process.puml` |
| EXECUTING | RESOURCE_EXCEEDED | SANDBOX-04 | Resource limit hit | `sq_sandbox04_limit_resources.puml` |
| MONITORING | TIMEOUT | SANDBOX-03 | Timeout exceeded | `sq_sandbox03_monitor_process.puml` |
| MONITORING | RESOURCE_EXCEEDED | SANDBOX-04 | Resource limit hit | `sq_sandbox04_limit_resources.puml` |
| TIMEOUT | IDLE | SANDBOX-01 | Cleanup after timeout | `sq_sandbox01_isolate_command.puml` |
| FAILED | IDLE | SANDBOX-01 | Cleanup after failure | `sq_sandbox01_isolate_command.puml` |
| RESOURCE_EXCEEDED | IDLE | SANDBOX-04 | Cleanup after resource violation | `sq_sandbox04_limit_resources.puml` |
| COMPLETED | [*] | SANDBOX-01 | Terminal state | — |

> **Coverage:** 13/13 non-terminal transitions covered. 0 ORPHANs.

### sm_diff_staging_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | EDITSTRATEGY-10 | Default state | `sq_editstrategy10_stage_diff.puml` |
| EMPTY | STAGING | EDITSTRATEGY-10 | Diff computation started | `sq_editstrategy10_stage_diff.puml` |
| STAGING | STAGED | EDITSTRATEGY-10 | Diff computed successfully | `sq_editstrategy10_stage_diff.puml` |
| STAGING | ERROR | EDITSTRATEGY-10 | Diff computation failed | `sq_editstrategy10_stage_diff.puml` |
| STAGED | AWAITING_APPROVAL | EDITSTRATEGY-10 | Diff presented for review | `sq_editstrategy10_stage_diff.puml` |
| AWAITING_APPROVAL | APPROVED | SAFETY-02 | User approved | `sq_safety02_request_approval.puml` |
| AWAITING_APPROVAL | EMPTY | SAFETY-02 | User rejected, cleanup | `sq_safety02_request_approval.puml` |
| APPROVED | APPLYING | EDITSTRATEGY-10 | Diff application started | `sq_editstrategy10_stage_diff.puml` |
| APPLYING | APPLIED | EDITSTRATEGY-10 | Diff applied successfully | `sq_editstrategy10_stage_diff.puml` |
| APPLYING | ERROR | EDITSTRATEGY-10 | Diff application failed | `sq_editstrategy10_stage_diff.puml` |
| APPLIED | EMPTY | EDITSTRATEGY-10 | Cleanup after application | `sq_editstrategy10_stage_diff.puml` |
| ERROR | EMPTY | EDITSTRATEGY-10 | Cleanup after error | `sq_editstrategy10_stage_diff.puml` |
| APPLIED | [*] | EDITSTRATEGY-10 | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_safety_mode_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINITIALIZED | SAFETY-03 | Default state | sq_safety03_apply_safety_mode.puml |
| UNINITIALIZED | PERMISSIVE | SAFETY-03 | Apply permissive mode | sq_safety03_apply_safety_mode.puml |
| UNINITIALIZED | ASK | SAFETY-03 | Apply ask mode | sq_safety03_apply_safety_mode.puml |
| UNINITIALIZED | BLOCK | SAFETY-03 | Apply block mode | sq_safety03_apply_safety_mode.puml |
| PERMISSIVE | ASK | SAFETY-03 | Switch to ask mode | sq_safety03_apply_safety_mode.puml |
| PERMISSIVE | BLOCK | SAFETY-03 | Switch to block mode | sq_safety03_apply_safety_mode.puml |
| ASK | PERMISSIVE | SAFETY-03 | Switch to permissive mode | sq_safety03_apply_safety_mode.puml |
| ASK | BLOCK | SAFETY-03 | Switch to block mode | sq_safety03_apply_safety_mode.puml |
| BLOCK | PERMISSIVE | SAFETY-03 | Switch to permissive mode | sq_safety03_apply_safety_mode.puml |
| BLOCK | ASK | SAFETY-03 | Switch to ask mode | sq_safety03_apply_safety_mode.puml |
| PERMISSIVE | ERROR | SAFETY-01 | Permission check failed | sq_safety01_check_permission.puml |
| ASK | ERROR | SAFETY-01 | Permission check failed | sq_safety01_check_permission.puml |
| BLOCK | ERROR | SAFETY-01 | Permission check failed | sq_safety01_check_permission.puml |
| ERROR | UNINITIALIZED | SAFETY-03 | Recovery: reinitialize | sq_safety03_apply_safety_mode.puml |
| UNINITIALIZED | [*] | SAFETY-03 | Terminal state | — |

> **Coverage:** 14/14 non-terminal transitions covered. 0 ORPHANs.

### sm_router_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | ROUTER-01 | Default state | sq_router01_select_model.puml |
| IDLE | CLASSIFYING | ROUTER-03 | Task classification started | sq_router03_classify_task.puml |
| CLASSIFYING | SELECTING | ROUTER-01 | Classification complete | sq_router01_select_model.puml |
| CLASSIFYING | ERROR | ROUTER-03 | Classification failed | sq_router03_classify_task.puml |
| SELECTING | IDLE | ROUTER-01 | Model selected | sq_router01_select_model.puml |
| SELECTING | FALLBACK | ROUTER-02 | Primary model unavailable | sq_router02_apply_fallback.puml |
| FALLBACK | SELECTING | ROUTER-02 | Fallback to next model | sq_router02_apply_fallback.puml |
| FALLBACK | ERROR | ROUTER-02 | All models exhausted | sq_router02_apply_fallback.puml |
| IDLE | SWITCHING | ROUTER-04 | Runtime switch requested | sq_router04_switch_model.puml |
| SWITCHING | IDLE | ROUTER-04 | Switch successful | sq_router04_switch_model.puml |
| SWITCHING | ERROR | ROUTER-04 | Switch failed | sq_router04_switch_model.puml |
| ERROR | IDLE | ROUTER-01 | Recovery: retry | sq_router01_select_model.puml |
| IDLE | [*] | ROUTER-01 | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_provider_connection_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNREGISTERED | PROVIDER-01 | Default state | sq_provider01_register_provider.puml |
| UNREGISTERED | REGISTERING | PROVIDER-01 | Registration started | sq_provider01_register_provider.puml |
| REGISTERING | ACTIVE | PROVIDER-01 | Registration successful | sq_provider01_register_provider.puml |
| REGISTERING | ERROR | PROVIDER-01 | Registration failed | sq_provider01_register_provider.puml |
| ACTIVE | SELECTING | PROVIDER-04 | Backend selection started | sq_provider04_select_provider_backend.puml |
| SELECTING | ACTIVE | PROVIDER-04 | Backend selected | sq_provider04_select_provider_backend.puml |
| SELECTING | ERROR | PROVIDER-04 | Selection failed | sq_provider04_select_provider_backend.puml |
| ACTIVE | UNREGISTERED | PROVIDER-01 | Unregistered | sq_provider01_register_provider.puml |
| ERROR | UNREGISTERED | PROVIDER-01 | Recovery: re-register | sq_provider01_register_provider.puml |
| UNREGISTERED | [*] | PROVIDER-01 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_evaluation_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | EVALUATION-01 | Default state | sq_evaluation01_evaluate_task.puml |
| IDLE | CHECKING | EVALUATION-01 | Evaluation started | sq_evaluation01_evaluate_task.puml |
| CHECKING | REVIEWING | EVALUATION-04 | LLM review required | sq_evaluation04_validate_with_llm.puml |
| CHECKING | TESTING | EVALUATION-05 | Test validation required | sq_evaluation05_validate_test_suite.puml |
| CHECKING | SCORING | EVALUATION-07 | Direct scoring (no review/test) | sq_evaluation07_record_quality_signal.puml |
| CHECKING | FAILED | EVALUATION-02 | Task completion check failed | sq_evaluation02_check_task_completion.puml |
| REVIEWING | SCORING | EVALUATION-07 | LLM review passed | sq_evaluation07_record_quality_signal.puml |
| REVIEWING | RETRYING | EVALUATION-06 | LLM review rejected | sq_evaluation06_coordinate_retry.puml |
| TESTING | SCORING | EVALUATION-07 | Tests passed | sq_evaluation07_record_quality_signal.puml |
| TESTING | RETRYING | EVALUATION-06 | Tests failed | sq_evaluation06_coordinate_retry.puml |
| SCORING | PASSED | EVALUATION-07 | Scoring threshold met | sq_evaluation07_record_quality_signal.puml |
| SCORING | RETRYING | EVALUATION-06 | Scoring below threshold | sq_evaluation06_coordinate_retry.puml |
| RETRYING | CHECKING | EVALUATION-06 | Retry with feedback | sq_evaluation06_coordinate_retry.puml |
| RETRYING | FAILED | EVALUATION-06 | Retries exhausted | sq_evaluation06_coordinate_retry.puml |
| PASSED | IDLE | EVALUATION-01 | Reset for next evaluation | sq_evaluation01_evaluate_task.puml |
| FAILED | IDLE | EVALUATION-01 | Reset for next evaluation | sq_evaluation01_evaluate_task.puml |
| PASSED | [*] | EVALUATION-01 | Terminal state | — |
| FAILED | [*] | EVALUATION-01 | Terminal state | — |

> **Coverage:** 16/16 non-terminal transitions covered. 0 ORPHANs.

### sm_index_lifecycle — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINDEXED | REPOINTELLIGENCE-01 | Default state | sq_repointelligence01_index_codebase.puml |
| UNINDEXED | INDEXING | REPOINTELLIGENCE-01 | Indexing started | sq_repointelligence01_index_codebase.puml |
| INDEXING | INDEXED | REPOINTELLIGENCE-01 | Indexing complete | sq_repointelligence01_index_codebase.puml |
| INDEXING | ERROR | REPOINTELLIGENCE-01 | Indexing failed | sq_repointelligence01_index_codebase.puml |
| INDEXED | BUILDING_GRAPH | REPOINTELLIGENCE-02 | Graph building started | sq_repointelligence02_build_symbol_graph.puml |
| BUILDING_GRAPH | INDEXED | REPOINTELLIGENCE-02 | Graph built | sq_repointelligence02_build_symbol_graph.puml |
| BUILDING_GRAPH | ERROR | REPOINTELLIGENCE-02 | Graph building failed | sq_repointelligence02_build_symbol_graph.puml |
| INDEXED | EMBEDDING | REPOINTELLIGENCE-05 | Embedding started | sq_repointelligence05_embed_code.puml |
| EMBEDDING | INDEXED | REPOINTELLIGENCE-05 | Embedding complete | sq_repointelligence05_embed_code.puml |
| EMBEDDING | ERROR | REPOINTELLIGENCE-05 | Embedding failed | sq_repointelligence05_embed_code.puml |
| INDEXED | STALE | REPOINTELLIGENCE-01 | Source files changed | sq_repointelligence01_index_codebase.puml |
| STALE | INDEXING | REPOINTELLIGENCE-01 | Re-indexing started | sq_repointelligence01_index_codebase.puml |
| ERROR | UNINDEXED | REPOINTELLIGENCE-01 | Recovery: start fresh | sq_repointelligence01_index_codebase.puml |
| INDEXED | [*] | REPOINTELLIGENCE-01 | Terminal state | — |
| UNINDEXED | [*] | REPOINTELLIGENCE-01 | Terminal state | — |

> **Coverage:** 13/13 non-terminal transitions covered. 0 ORPHANs.

## SM Inventory & Completeness Report (2026-06-27)

### Audit Method
Systematic 21-group C4 component audit: every Component() in every `docs/C4/c4_nasim_component_*.puml` was cross-referenced against the 15 existing SM files, the UC catalog (`docs/UC/README.md`, 148 UCs), and the ERD layer. Components were flagged as stateful if they met any of the EXT-01..05 criteria (sm.md): lifecycle state field, process lifecycle management, multiple UCs implying state transitions, stateful naming (Manager, Coordinator, Session, Runtime).

### Full SM Inventory (15 files)

| # | SM File | Entity | C4 Component | Type | States | UCs | Status |
|---|---------|--------|--------------|------|--------|-----|--------|
| 1 | sm_agent_lifecycle.puml | TaskService | TaskService | Process FSM | 17 | AGENT-01..14, API-06, PROVIDER-02, EDITSTRATEGY-10, SAFETY-02, HOOKS-02, EVALUATION-01..06, ROUTER-01 | ✅ GREEN |
| 2 | sm_session_lifecycle.puml | SessionRepository | SessionService | Entity | 6 | API-02..05, WIRELOG-04 | ✅ GREEN |
| 3 | sm_plan_lifecycle.puml | TaskService (Plan) | TaskService | Entity | 7 | AGENT-07, AGENT-08, AGENT-01, AGENT-14 | ✅ GREEN |
| 4 | sm_plugin_lifecycle.puml | ToolService (Plugin) | ToolService | Entity | 6 | PLUGINS-01..06 | ✅ GREEN |
| 5 | sm_subagent_lifecycle.puml | TaskService (Subagent) | TaskService | Entity | 5 | AGENT-09, AGENT-10, AGENT-14 | ✅ GREEN |
| 6 | sm_persona_lifecycle.puml | TaskService (Persona) | TaskService | Entity | 5 | AGENT-11, AGENT-12, AGENT-13 | ✅ GREEN |
| 7 | sm_mcp_client_lifecycle.puml | MCPRepository | MCPRepository | Entity | 5 | MCP-01, MCP-02 | ✅ GREEN |
| 8 | sm_mcp_server_lifecycle.puml | MCPRepository (Server) | MCPRepository | Entity | 5 | MCP-04 | ✅ GREEN |
| 9 | sm_sandbox_execution_lifecycle.puml | SandboxRepository | SandboxRepository | Entity | 7 | SANDBOX-01, SANDBOX-03, SANDBOX-04 | ✅ GREEN |
| 10 | sm_diff_staging_lifecycle.puml | EditStrategyRepository | EditStrategyRepository | Entity | 8 | EDITSTRATEGY-10, SAFETY-02 | ✅ GREEN |
| 11 | sm_safety_mode_lifecycle.puml | SafetyService | SafetyService | Entity | 5 | SAFETY-01, SAFETY-03 | ✅ GREEN |
| 12 | sm_router_lifecycle.puml | LLMRepository | LLMRepository | Entity | 6 | ROUTER-01..04 | ✅ GREEN |
| 13 | sm_provider_connection_lifecycle.puml | LLMRepository (Provider) | LLMRepository | Entity | 5 | PROVIDER-01, PROVIDER-04 | ✅ GREEN |
| 14 | sm_evaluation_lifecycle.puml | EvaluationService | EvaluationService | Entity | 8 | EVALUATION-01..07 | ✅ GREEN |
| 15 | sm_index_lifecycle.puml | RepoIntelligenceRepository | RepoIntelligenceRepository | Entity | 7 | REPOINTELLIGENCE-01, REPOINTELLIGENCE-02, REPOINTELLIGENCE-05 | ✅ GREEN |

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
| ORPHAN transitions (awaiting SQ) | 0 |
| Lint violations | 0 (across all 15 files) |
| Terminal UC-ID violations found & fixed | 2 (agent, session) |

### Stateful Entities with Dedicated SM Coverage

| C4 Component | C4 Group | SM File |
|--------------|----------|---------|
| TaskService | Task | `sm_agent_lifecycle.puml` (Process FSM) |
| SessionService | Session | sm_session_lifecycle.puml |
| TaskService | Task | sm_plan_lifecycle.puml |
| ToolService | Tool | sm_plugin_lifecycle.puml |
| TaskService | Task | sm_subagent_lifecycle.puml |
| TaskService | Task | sm_persona_lifecycle.puml |
| MCPRepository | Repository | sm_mcp_client_lifecycle.puml |
| MCPRepository | Repository | sm_mcp_server_lifecycle.puml |
| SandboxRepository | Repository | sm_sandbox_execution_lifecycle.puml |
| EditStrategyRepository | Repository | sm_diff_staging_lifecycle.puml |
| SafetyService | Service | sm_safety_mode_lifecycle.puml |
| LLMRepository | Repository | sm_router_lifecycle.puml |
| LLMRepository | Repository | sm_provider_connection_lifecycle.puml |
| EvaluationService | Service | sm_evaluation_lifecycle.puml |
| RepoIntelligenceRepository | Repository | sm_index_lifecycle.puml |

### Stateful Entities Covered Inside Agent Process FSM

These components have lifecycle states that occur as transient sub-states within the agent processing loop. Dedicated SMs would add no value:

| Component | C4 Component | Rationale |
|-----------|--------------|-----------|
| ConversationHistory | TaskService | Message store with token tracking. Its only state transition (`normal → compacting`) is a sub-state of Agent FSM's COMPACTING. No independent lifecycle outside the agent loop. |
| ContextCompactor | ContextService | Stateless summarizer invoked by ConversationHistory. No independent lifecycle. |
| ErrorBoundary | TaskService | Error handler. Error states (recoverable vs terminal) are sub-states of Agent FSM's ERROR. |
| ToolRegistry | ToolService | Instance registry. Registration is static at startup (except MCP tools, covered by MCP SMs). |
| PermissionGate | SafetyService | Stateless evaluator. Permission decision (allow/deny/ask) maps to Agent FSM transitions. |
| FallbackChain | LLMRepository | Fallback lifecycle captured within Router SM: SELECTING → FALLBACK → ERROR. |
| Provider (Protocol) | LLMRepository | Chat lifecycle maps to Agent FSM: THINKING → RESPONDING/ERROR. |

### Stateful Entities Without Dedicated SM (LOW Priority — Backlog)

| # | Entity | C4 Component | Reason | Rationale |
|---|--------|--------------|--------|-----------|
| 1 | WireLog | WireLogRepository | Write-buffer lifecycle | Append-only event store with buffering/flush. Simple 3-state (OPEN→WRITING→FLUSHING). UCs: WIRELOG-01..05. |
| 2 | GitIntegration | GitRepository | Auto-commit lifecycle | Monitors for changes then commits. 3-state (IDLE→CHANGES_DETECTED→COMMITTING). UC: GIT-04. |
| 3 | PipelineOrchestrator | ContextService | Pipeline stage lifecycle | 5 transient pipeline stages completing synchronously in one pass. LOW risk. |
| 4 | REPLSession | CLIAdapter | REPL loop lifecycle | CLI entry point. Delegates all business logic via API. REPL state is UI state, not domain state. |
| 5 | ServerApp | HTTPAdapter | ASGI lifespan lifecycle | Standard ASGI startup/shutdown. Few project-specific transitions. |

### Lifecycle-Write Ownership Verification

Every entity SM state has exactly one owning lifecycle-write UC. Verified per SMT rules:

- **Session**: CREATED (API-02), ACTIVE (API-02), SAVED (API-04), RESTORED (API-03), BRANCHED (WIRELOG-04), CLOSED (API-05) ✅
- **Plan**: BUILDING (AGENT-07), QUEUED (AGENT-07), APPROVED (AGENT-08), EXECUTING (AGENT-08), COMPLETED (AGENT-01), REJECTED (AGENT-08) ✅
- **Plugin**: DISCOVERED (PLUGINS-01), LOADING (PLUGINS-02), LOADED (PLUGINS-03), ENABLED (PLUGINS-05), DISABLED (PLUGINS-06), ERROR (PLUGINS-01) ✅
- **Subagent**: SPAWNING (AGENT-09), RUNNING (AGENT-09), COMPLETED (AGENT-10), FAILED (AGENT-14) ✅
- **Persona**: LOADING (AGENT-12), ACTIVE (AGENT-11), SWITCHING (AGENT-13), ERROR (AGENT-12) ✅
- **MCP Client**: CONNECTING (MCP-01), CONNECTED (MCP-01), DISCOVERING (MCP-02), ERROR (MCP-01) ✅
- **MCP Server**: STARTING (MCP-04), RUNNING (MCP-04), STOPPING (MCP-04), ERROR (MCP-04) ✅
- **Sandbox**: EXECUTING (SANDBOX-01), MONITORING (SANDBOX-03), COMPLETED (SANDBOX-01), TIMEOUT (SANDBOX-03), FAILED (SANDBOX-01), RESOURCE_EXCEEDED (SANDBOX-04) ✅
- **Diff Staging**: STAGING (EDITSTRATEGY-10), STAGED (EDITSTRATEGY-10), AWAITING_APPROVAL (SAFETY-02), APPROVED (SAFETY-02), APPLYING (EDITSTRATEGY-10), APPLIED (EDITSTRATEGY-10), ERROR (EDITSTRATEGY-10) ✅
- **Safety**: PERMISSIVE (SAFETY-03), ASK (SAFETY-03), BLOCK (SAFETY-03), ERROR (SAFETY-01) ✅
- **Router**: CLASSIFYING (ROUTER-03), SELECTING (ROUTER-01), SWITCHING (ROUTER-04), FALLBACK (ROUTER-02), ERROR (ROUTER-03) ✅
- **Provider**: REGISTERING (PROVIDER-01), ACTIVE (PROVIDER-01), SELECTING (PROVIDER-04), ERROR (PROVIDER-01) ✅
- **Evaluation**: CHECKING (EVALUATION-01), REVIEWING (EVALUATION-04), TESTING (EVALUATION-05), SCORING (EVALUATION-07), RETRYING (EVALUATION-06), PASSED (EVALUATION-07), FAILED (EVALUATION-02) ✅
- **Index**: INDEXING (REPOINTELLIGENCE-01), INDEXED (REPOINTELLIGENCE-01), BUILDING_GRAPH (REPOINTELLIGENCE-02), EMBEDDING (REPOINTELLIGENCE-05), STALE (REPOINTELLIGENCE-01), ERROR (REPOINTELLIGENCE-01) ✅

### Agent Process FSM — Documented Deviation

The Agent SM is intentionally a **Process FSM**, not an Entity Lifecycle. Per sm.md:
*"SMT rules from sm.md do not apply (documented deviation)."*

 Rationale:
 - Models the runtime processing loop of TaskService, not a persisted entity.
- States (THINKING, TOOL_EXEC, RESPONDING) are transient processing states.
- Transitions driven by UC events on the active processing context, not writes to a stored entity.
- No persisted `lifecycle_state` — the process state lives in the runtime stack.

### SQ Coverage Verification

All 195 non-terminal transitions across all 15 SMs have been verified against the existing 148 SQ diagrams in `docs/SQ/`. Every non-terminal transition now has a corresponding SQ diagram referenced in its coverage table. The previous "115 orphan" count was a documentation gap in the README — the SQ diagrams existed but the coverage tables had not been updated to reference them.

Of the 148 SQ diagrams, 49 are referenced in SM coverage tables (they implement lifecycle-write transitions). The remaining 99 SQ diagrams cover non-lifecycle-write UCs (queries, reads, utility operations, or intermediate steps) that don't trigger SM transitions. This is expected — not every UC has an associated state change.

| Metric | Value |
|--------|-------|
| Total transitions (all SMs) | 216 (195 non-terminal + 21 terminal) |
| Non-terminal transitions | 195 |
| Covered by SQ diagrams | 195 |
| ORPHAN transitions | **0** |
| SQ diagrams in `docs/SQ/` | 148 (49 lifecycle-write + 99 non-transition) |

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
| SQ coverage (orphan resolution) | ✅ — 0 orphans remain (195/195 covered) |
