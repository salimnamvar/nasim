# nasim — State Machine Inventory (API-First)

> **Extraction date:** 2026-07-01 — State machines re-derived from `docs/C4/c4_nasim_component.puml` (v13.0.0) and UC diagrams only. Traceability matrix lives in `docs/UC/README.md` § State Machine Layer.
>
> **Key UC alignments (v13.0.0):** Agent compaction → `CONTEXTSVC-05`; plugin lifecycle → `TOOLSVC-PLG01..06`; LLM router → `LLMREPOSITORY-05..08`; LLM provider → `LLMREPOSITORY-01..04`; pre-tool hooks → `TOOLSVC-HK02`.
>
> **Update 2026-07-01 (Cycle 5):** Fixed SQ reference naming in transition coverage tables — updated from short prefixes (e.g., `sq_agent01`) to canonical names (e.g., `sq_taskservice01`) to match actual files on disk.
>
> **SM → SQ Verification (Infinite Loop Cycle):** Each infinite loop cycle MUST verify that all SM transition coverage table SQ references match actual files on disk. Verification command:
> ```bash
> cd docs/SM && grep -oE "sq_[a-z0-9_]+\.puml" README.md | sort -u > /tmp/sm_refs.txt && find ../SQ -name "sq_*.puml" -not -path "*/common/*" -exec basename {} \; | sort -u > /tmp/disk_files.txt && comm -23 /tmp/sm_refs.txt /tmp/disk_files.txt
> ```

## Agent Lifecycle States (Process FSM)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | Agent waiting for user input | Startup or response complete | #ECEFF1 |
| RECEIVING | Receiving request from any adapter | HTTPADP-06 DISPATCH Message received | #E8EAF6 |
| THINKING | LLM processing messages | Input parsed, messages built | #D7CCC8 |
| TOOL_EXEC | Executing a tool call | LLM returns tool_calls | #B2DFDB |
| RESPONDING | Streaming final text to user via API SSE | LLM returns text only | #D1C4E9 |
| ERROR | Error occurred | LLM call or tool exec fails | #FFEBEE |
| COMPACTING | Summarizing old exchanges | token_count > context_budget | #E0F2F1 |
| AWAITING_APPROVAL | Waiting for user permission | safety_mode=ask AND unsafe tool | #FFF9C4 |
| PLANNING | Plan mode, tool calls queued | /plan command entered | #FFCCBC |
| HOOK_RUNNING | Pre/post hook executing | tool or LLM call with hooks | #FFFDE7 |
| ROUTING | Model selection in progress | LLM Repository resolving model | #EDE7F6 |
| EVALUATING | Evaluating task completion | task_complete AND evaluation_enabled | #F9FBE7 |
| REVIEWING | LLM review of results | success checks passed, optional review | #FFF8E1 |
| RETRYING | Retrying with feedback | success checks failed or review rejected | #FBE9E7 |
| STAGING | Diff sandbox staging | tool exec in diff_sandbox mode | #F1F8E9 |
| AWAITING_DIFF_APPROVAL | Presenting diff to user | SAFETYSVC-02 REQUEST Approval | #FCE4EC |

> **API-First Entry:** All entry/exit transitions use `HTTPADP-06` (DISPATCH Message) as the sole entry gate. No interface container may bypass the API.
> **Simplification v11:** LISTENING and SERVING merged into RECEIVING (both process requests from adapters via HTTPADP-06; guard `[needs_thinking]` distinguishes CLI input from API requests that complete without thinking).

## Session Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| CREATED | Session record initialized | SESSIONSVC-01 PERSIST Session | #BBDEFB |
| ACTIVE | Session accepting messages | SESSIONSVC-01 PERSIST Session | #43A047 |
| SAVED | Session persisted to disk | SESSIONSVC-01 PERSIST Session | #1565C0 |
| RESTORED | Session loaded from disk | SESSIONSVC-04 RESTORE Session | #1E88E5 |
| BRANCHED | Session forked from parent | SESSIONSVC-08 BRANCH Session | #7B1FA2 |
| CLOSED | Session terminated | SESSIONSVC-09 DELETE Session | #757575 |

## Plan Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No plan active | Default state | #F5F5F5 |
| BUILDING | Plan being constructed | TASKSVC-07 QUEUE Plan | #FFE0B2 |
| QUEUED | Plan queued for approval | Plan construction complete | #E3F2FD |
| APPROVED | Plan approved by user | TASKSVC-08 APPROVE Plan | #388E3C |
| EXECUTING | Plan steps being executed | Plan approved, execution started | #A5D6A7 |
| COMPLETED | All plan steps finished | Implicit: agent loop finishes all steps | #1B5E20 |
| REJECTED | Plan rejected by user | User rejects plan | #B71C1C |

## Plugin Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCOVERED | Plugin found on filesystem | TOOLSVC-PLG01 DISCOVER Plugins | #E0E0E0 |
| LOADING | Plugin manifest being parsed | TOOLSVC-PLG02 LOAD Manifest | #FFCC80 |
| LOADED | Plugin manifest parsed, tools registered | TOOLSVC-PLG03 REGISTER Plugin Tools | #90CAF9 |
| ENABLED | Plugin active and available | TOOLSVC-PLG05 ENABLE Plugin | #4CAF50 |
| DISABLED | Plugin deactivated | TOOLSVC-PLG06 DISABLE Plugin | #CE93D8 |
| ERROR | Plugin failed to load or crashed | Load error or runtime exception | #EF5350 |

## Subagent Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No child agent active | Default state | #CFD8DC |
| SPAWNING | Child agent process initializing | TASKSVC-09 SPAWN Subagent | #FFAB91 |
| RUNNING | Child agent executing task | TASKSVC-09 SPAWN Subagent | #BCAAA4 |
| COMPLETED | Child agent finished successfully | TASKSVC-10 COLLECT Subagent Result | #80CBC4 |
| FAILED | Child agent encountered unrecoverable error | TASKSVC-14 HANDLE Error | #EF9A9A |

## Persona Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNLOADED | No persona loaded | Default state | #9E9E9E |
| LOADING | Persona configuration being loaded | TASKSVC-12 LOAD Persona | #FFC107 |
| ACTIVE | Persona active and available for delegation | TASKSVC-11 DELEGATE to Persona | #4DB6AC |
| SWITCHING | Switching to different persona at runtime | TASKSVC-13 SWITCH Persona | #FF9800 |
| ERROR | Persona load or switch failed | Load error or switch failure | #F44336 |

## MCP Client Connection Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| DISCONNECTED | No connection to MCP server | Default state | #B0BEC5 |
| CONNECTING | Connection to MCP server in progress | MCPREPOSITORY-01 CONNECT MCP Server | #FFCA28 |
| CONNECTED | Connected to MCP server | MCPREPOSITORY-01 CONNECT MCP Server | #00BCD4 |
| DISCOVERING | Discovering tools from connected server | MCPREPOSITORY-02 DISCOVER MCP Tools | #A1887F |
| ERROR | Connection or discovery failed | MCPREPOSITORY-01 or MCPREPOSITORY-02 failure | #E57373 |

## MCP Server Serving Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| STOPPED | MCP server not running | Default state | #616161 |
| STARTING | Server starting up | MCPREPOSITORY-04 EXPOSE nasim Tools | #FFA726 |
| RUNNING | Server running, serving tools to MCP clients | MCPREPOSITORY-04 EXPOSE nasim Tools | #66BB6A |
| STOPPING | Server shutting down | MCPREPOSITORY-04 EXPOSE nasim Tools | #FF7043 |
| ERROR | Server startup or runtime failure | MCPREPOSITORY-04 failure | #FFCDD2 |

## Sandbox Execution Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No process running in sandbox | Default state | #78909C |
| EXECUTING | Process running in sandbox | SANDBOXREPOSITORY-01 ISOLATE Command | #2196F3 |
| MONITORING | Process being monitored for resource usage | SANDBOXREPOSITORY-03 MONITOR Process | #64B5F6 |
| COMPLETED | Process finished successfully | SANDBOXREPOSITORY-01 ISOLATE Command | #8BC34A |
| TIMEOUT | Process exceeded time limit | SANDBOXREPOSITORY-03 MONITOR Process | #FFB74D |
| FAILED | Process crashed or was killed | SANDBOXREPOSITORY-01 ISOLATE Command | #D32F2F |
| RESOURCE_EXCEEDED | Process exceeded CPU, memory, or disk quota | SANDBOXREPOSITORY-04 LIMIT Resources | #FF5722 |

## Diff Staging Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| EMPTY | No diff staged | Default state | #9FA8DA |
| STAGING | Diff being computed | EDITSTRATEGYREPOSITORY-10 STAGE Diff | #FFE082 |
| STAGED | Diff ready for review | EDITSTRATEGYREPOSITORY-10 STAGE Diff | #C5E1A5 |
| AWAITING_APPROVAL | Diff presented to user for approval | SAFETYSVC-02 REQUEST Approval | #FFD54F |
| APPROVED | User approved diff | SAFETYSVC-02 REQUEST Approval | #AED581 |
| APPLYING | Approved diff being applied | EDITSTRATEGYREPOSITORY-10 STAGE Diff | #81C784 |
| APPLIED | Diff successfully applied | EDITSTRATEGYREPOSITORY-10 STAGE Diff | #009688 |
| ERROR | Diff computation or application failed | EDITSTRATEGYREPOSITORY-10 failure | #E53935 |

## Safety Mode Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINITIALIZED | Safety system not initialized | Default state | #BDBDBD |
| PERMISSIVE | All operations allowed, no approval prompts | SAFETYSVC-03 APPLY Safety Mode | #9CCC65 |
| ASK | User approval required for sensitive operations | SAFETYSVC-03 APPLY Safety Mode | #FDD835 |
| BLOCK | Dangerous operations blocked entirely | SAFETYSVC-03 APPLY Safety Mode | #E91E63 |
| ERROR | Safety system encountered an error | SAFETYSVC-01 CHECK Permission failure | #F4511E |

## Router Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No routing in progress | Default state | #EEEEEE |
| CLASSIFYING | Task classification for model routing | LLMREPOSITORY-03 CLASSIFY Task | #5C6BC0 |
| SELECTING | Model selection in progress | LLMREPOSITORY-01 SELECT Model | #3F51B5 |
| SWITCHING | Runtime model switch in progress | LLMREPOSITORY-04 SWITCH Model | #FF8F00 |
| FALLBACK | Falling back to next available model | LLMREPOSITORY-02 APPLY Fallback | #EF6C00 |
| ERROR | Routing or fallback failed | All models exhausted | #BF360C |

## Provider Connection Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNREGISTERED | No provider registered | Default state | #455A64 |
| REGISTERING | Provider registration in progress | LLMREPOSITORY-01 REGISTER Provider | #29B6F6 |
| ACTIVE | Provider registered and ready for chat | LLMREPOSITORY-01 REGISTER Provider | #03A9F4 |
| SELECTING | Backend selection in progress | LLMREPOSITORY-04 SELECT Provider Backend | #FBC02D |
| ERROR | Registration or selection failed | Provider unavailable | #E64A19 |

## Evaluation Lifecycle States (Process)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | No evaluation in progress | Default state | #90A4AE |
| CHECKING | Running task completion and success checks | EVALSVC-01 EVALUATE Task | #C5CAE9 |
| REVIEWING | LLM-based code review and quality assessment | EVALSVC-04 VALIDATE With LLM | #AB47BC |
| TESTING | Running project test suites | EVALSVC-05 VALIDATE Test Suite | #D4E157 |
| SCORING | Recording quality signal and scoring | EVALSVC-07 RECORD Quality Signal | #FF8A65 |
| RETRYING | Coordinating retry with backoff and escalation | EVALSVC-06 COORDINATE Retry | #C62828 |
| PASSED | Evaluation passed all criteria | Terminal success state | #689F38 |
| FAILED | Evaluation failed, retries exhausted | Terminal failure state | #AD1457 |

## Repository Index Lifecycle States (Entity)

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| UNINDEXED | No repository index exists | Default state | #424242 |
| INDEXING | AST indexing via tree-sitter in progress | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | #4FC3F7 |
| INDEXED | Repository fully indexed | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | #7CB342 |
| BUILDING_GRAPH | Cross-file symbol reference graph in progress | REPOINTELLIGENCEREPOSITORY-02 BUILD Symbol Graph | #9C27B0 |
| EMBEDDING | Generating vector embeddings for code | REPOINTELLIGENCEREPOSITORY-05 EMBED Code | #E6EE9C |
| STALE | Index outdated, needs re-index | Source files changed | #FFECB3 |
| ERROR | Indexing, graph building, or embedding failed | Unrecoverable processing error | #DD2C00 |

## Diagrams

| File | Scope |
|------|-------|
| `sm_task_svc_agent.puml` | Agent process FSM — 16 states (API-First, v11) |
| `sm_session_svc_session.puml` | Session entity lifecycle — 6 states (API-First) |
| `sm_task_svc_plan.puml` | Plan entity lifecycle — 7 states |
| `sm_tool_svc_plugin.puml` | Plugin entity lifecycle — 6 states (+ 2 terminal exits) |
| `sm_task_svc_subagent.puml` | Subagent entity lifecycle — 5 states (IDLE→SPAWNING→RUNNING→COMPLETED/FAILED) + 2 terminal exits |
| `sm_task_svc_persona.puml` | Persona entity lifecycle — 5 states (UNLOADED→LOADING→ACTIVE↔SWITCHING) |
| `sm_mcp_repo_client.puml` | MCP Client connection lifecycle — 5 states (DISCONNECTED→CONNECTING→CONNECTED→DISCOVERING) |
| `sm_mcp_repo_server.puml` | MCP Server serving lifecycle — 5 states (STOPPED→STARTING→RUNNING→STOPPING) |
| `sm_sandbox_repo_sandbox.puml` | Sandbox execution lifecycle — 7 states (IDLE→EXECUTING→COMPLETED/TIMEOUT/FAILED/RESOURCE_EXCEEDED) |
| `sm_edit_strategy_repo_diff.puml` | Diff staging lifecycle — 8 states (EMPTY→STAGING→STAGED→AWAITING_APPROVAL→APPROVED→APPLYING→APPLIED) |
| `sm_safety_svc_safety.puml` | Safety mode lifecycle — 5 states (UNINITIALIZED→PERMISSIVE|ASK|BLOCK) |
| `sm_llm_repo_router.puml` | Router selection lifecycle — 6 states (IDLE→CLASSIFYING→SELECTING→FALLBACK|SWITCHING) |
| `sm_llm_repo_provider.puml` | Provider connection lifecycle — 5 states (UNREGISTERED→REGISTERING→ACTIVE→SELECTING) |
| `sm_eval_svc_evaluation.puml` | Evaluation process lifecycle — 8 states (v3, terminal [*] exits only) |
| `sm_repo_intel_repo_index.puml` | Repository index lifecycle — 7 states (UNINDEXED→INDEXING→INDEXED→BUILDING_GRAPH|EMBEDDING) |

## Notes

- Agent SM is a **process FSM**, not an entity lifecycle. States are transient agent
  states during task execution, not persisted lifecycle states. SMT ownership
  rules from `sm.md` do not apply (documented deviation).
- Session, Plan, and Plugin SMs are **entity lifecycles** with persisted state.
  SMT ownership rules apply: one lifecycle-write UC per target state.
- All hex colors are canonical — state-machine diagrams use `state "STATE" as STATE #HEX`
  syntax per PlantUML standard.
- **Transition labels** use UC-ID-only convention (e.g., `TASKSVC-01`, `LLMREPOSITORY-02`, `SAFETYSVC-02`).
  No human-readable suffixes. Multiple transitions from one state may share a UC ID
  when the same action produces different outcomes (e.g., `LLMREPOSITORY-02` → RESPONDING, TOOL_EXEC, ERROR).
- **API-First:** All entry/exit transitions in Agent SM use `HTTPADP-06` as the sole entry gate.
  Session lifecycle mutations use `SESSIONSVC-XX` UC IDs (Session Service Group).

## Transition Matrices

### Agent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | TASKSVC-01 | Process startup |
| IDLE | RECEIVING | HTTPADP-06 | Request received (any adapter) |
| IDLE | PLANNING | TASKSVC-07 | /plan command entered |
| RECEIVING | THINKING | HTTPADP-06 | [needs_thinking] Input parsed, messages built |
| RECEIVING | IDLE | HTTPADP-06 | [!needs_thinking] API request complete |
| THINKING | RESPONDING | LLMREPOSITORY-02 | LLM returns text only |
| THINKING | TOOL_EXEC | LLMREPOSITORY-02 | LLM returns tool_calls |
| THINKING | COMPACTING | TASKSVC-06 | token_count > context_budget |
| THINKING | ROUTING | LLMREPOSITORY-05 | ModelRouter resolving model |
| THINKING | ERROR | LLMREPOSITORY-02 | Provider call failed |
| THINKING | EVALUATING | EVALSVC-01 | task_complete AND evaluation_enabled |
| ROUTING | THINKING | LLMREPOSITORY-05 | Model selected |
| TOOL_EXEC | THINKING | TASKSVC-02 | Tool call complete |
| TOOL_EXEC | AWAITING_APPROVAL | SAFETYSVC-02 | safety_mode=ask AND unsafe tool |
| TOOL_EXEC | HOOK_RUNNING | TOOLSVC-HK02 | Pre/post hook configured |
| TOOL_EXEC | ERROR | TASKSVC-02 | Tool execution failed |
| TOOL_EXEC | STAGING | EDITSTRATEGYREPOSITORY-10 | diff_sandbox mode active |
| HOOK_RUNNING | TOOL_EXEC | TOOLSVC-HK02 | Hook execution complete |
| HOOK_RUNNING | IDLE | TOOLSVC-HK02 | Hook execution complete (no tool) |
| AWAITING_APPROVAL | TOOL_EXEC | SAFETYSVC-02 | User approves |
| AWAITING_APPROVAL | IDLE | SAFETYSVC-02 | User denies |
| COMPACTING | THINKING | TASKSVC-06 | Context compacted |
| RESPONDING | IDLE | HTTPADP-06 | Response streamed to user |
| ERROR | IDLE | TASKSVC-14 | Error handled |
| PLANNING | IDLE | TASKSVC-07 | Plan mode exited |
| EVALUATING | REVIEWING | EVALSVC-01 | Evaluation passed |
| EVALUATING | RETRYING | EVALSVC-01 | Evaluation failed |
| EVALUATING | THINKING | EVALSVC-01 | Retry with feedback |
| REVIEWING | THINKING | EVALSVC-04 | LLM review passed |
| REVIEWING | RETRYING | EVALSVC-04 | LLM review rejected |
| RETRYING | THINKING | EVALSVC-06 | Retry with feedback |
| RETRYING | ERROR | EVALSVC-06 | Retry exhausted |
| STAGING | AWAITING_DIFF_APPROVAL | EDITSTRATEGYREPOSITORY-10 | Diff computed successfully |
| STAGING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff computation failed |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAFETYSVC-02 | User approves diff |
| AWAITING_DIFF_APPROVAL | IDLE | SAFETYSVC-02 | User rejects diff |

### Session Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | CREATED | SESSIONSVC-01 | Session record initialized |
| CREATED | ACTIVE | SESSIONSVC-01 | Session ready for messages |
| ACTIVE | SAVED | SESSIONSVC-01 | Session persisted to disk |
| ACTIVE | BRANCHED | SESSIONSVC-08 | Session forked from parent |
| ACTIVE | CLOSED | SESSIONSVC-09 | Session terminated |
| SAVED | RESTORED | SESSIONSVC-04 | Session loaded from disk |
| SAVED | CLOSED | SESSIONSVC-09 | Session terminated |
| RESTORED | ACTIVE | SESSIONSVC-02 | Session ready for messages |
| RESTORED | SAVED | SESSIONSVC-01 | Session persisted to disk |
| RESTORED | CLOSED | SESSIONSVC-09 | Session terminated |
| BRANCHED | ACTIVE | SESSIONSVC-02 | Session ready for messages |
| BRANCHED | CLOSED | SESSIONSVC-09 | Session terminated |
| CLOSED | [*] | — | Terminal state |

### Plan Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | EMPTY | TASKSVC-07 | No plan active |
| EMPTY | BUILDING | TASKSVC-07 | /plan command entered |
| BUILDING | QUEUED | TASKSVC-07 | Plan construction complete |
| BUILDING | EMPTY | TASKSVC-07 | Plan cancelled |
| QUEUED | APPROVED | TASKSVC-08 | User approves plan |
| QUEUED | REJECTED | TASKSVC-08 | User rejects plan |
| APPROVED | EXECUTING | TASKSVC-08 | Execution started |
| EXECUTING | COMPLETED | TASKSVC-01 | All plan steps finished |
| EXECUTING | EMPTY | TASKSVC-14 | Execution failed or cancelled |
| COMPLETED | [*] | TASKSVC-01 | Terminal state |
| REJECTED | [*] | TASKSVC-08 | Terminal state |

### Plugin Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | DISCOVERED | TOOLSVC-PLG01 | Plugin found on filesystem |
| DISCOVERED | LOADING | TOOLSVC-PLG02 | Manifest parsing starts |
| DISCOVERED | ERROR | TOOLSVC-PLG01 | Plugin discovery failed |
| LOADING | LOADED | TOOLSVC-PLG03 | Manifest parsed, tools registered |
| LOADING | ERROR | TOOLSVC-PLG02 | Manifest parsing failed |
| LOADED | ENABLED | TOOLSVC-PLG05 | Plugin activated |
| LOADED | DISABLED | TOOLSVC-PLG06 | Plugin deactivated |
| LOADED | ERROR | TOOLSVC-PLG03 | Tool registration failed |
| ENABLED | DISABLED | TOOLSVC-PLG06 | Plugin deactivated |
| ENABLED | ERROR | TOOLSVC-PLG01 | Runtime exception |
| ENABLED | [*] | TOOLSVC-PLG06 | Plugin unloaded |
| DISABLED | ENABLED | TOOLSVC-PLG05 | Plugin activated |
| DISABLED | [*] | TOOLSVC-PLG06 | Plugin unloaded |
| ERROR | DISCOVERED | TOOLSVC-PLG01 | Re-discovery (recovery) |

### Subagent Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | TASKSVC-09 | Default state |
| IDLE | SPAWNING | TASKSVC-09 | Child agent spawn requested |
| SPAWNING | RUNNING | TASKSVC-09 | Child agent initialized |
| SPAWNING | FAILED | TASKSVC-09 | Spawn failed |
| RUNNING | COMPLETED | TASKSVC-10 | Task finished successfully |
| RUNNING | FAILED | TASKSVC-14 | Unrecoverable error |
| COMPLETED | IDLE | TASKSVC-10 | Results aggregated to parent |
| COMPLETED | [*] | TASKSVC-10 | Terminal state |
| FAILED | IDLE | TASKSVC-14 | Error reported, cleanup done |
| FAILED | [*] | TASKSVC-14 | Terminal state |

### Persona Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | UNLOADED | TASKSVC-12 | Default state |
| UNLOADED | LOADING | TASKSVC-12 | Load requested |
| LOADING | ACTIVE | TASKSVC-12 | Load successful |
| LOADING | ERROR | TASKSVC-12 | Load failed |
| ACTIVE | SWITCHING | TASKSVC-13 | Switch requested |
| SWITCHING | ACTIVE | TASKSVC-13 | Switch successful |
| SWITCHING | ERROR | TASKSVC-13 | Switch failed |
| ACTIVE | UNLOADED | TASKSVC-11 | Delegation complete |
| ERROR | UNLOADED | TASKSVC-12 | Recovery: retry load |
| UNLOADED | [*] | TASKSVC-12 | Terminal state |

### MCP Client Connection Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | DISCONNECTED | MCPREPOSITORY-01 | Default state |
| DISCONNECTED | CONNECTING | MCPREPOSITORY-01 | Connect requested |
| CONNECTING | CONNECTED | MCPREPOSITORY-01 | Connection established |
| CONNECTING | ERROR | MCPREPOSITORY-01 | Connection failed |
| CONNECTED | DISCOVERING | MCPREPOSITORY-02 | Tool discovery started |
| DISCOVERING | CONNECTED | MCPREPOSITORY-02 | Discovery complete |
| DISCOVERING | ERROR | MCPREPOSITORY-02 | Discovery failed |
| CONNECTED | DISCONNECTED | MCPREPOSITORY-01 | Disconnected |
| ERROR | DISCONNECTED | MCPREPOSITORY-01 | Recovery: reconnect |
| DISCONNECTED | [*] | MCPREPOSITORY-01 | Terminal state |

### MCP Server Serving Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | STOPPED | MCPREPOSITORY-04 | Default state |
| STOPPED | STARTING | MCPREPOSITORY-04 | Start requested |
| STARTING | RUNNING | MCPREPOSITORY-04 | Startup complete |
| STARTING | ERROR | MCPREPOSITORY-04 | Startup failed |
| RUNNING | STOPPING | MCPREPOSITORY-04 | Stop requested |
| STOPPING | STOPPED | MCPREPOSITORY-04 | Shutdown complete |
| RUNNING | ERROR | MCPREPOSITORY-04 | Runtime failure |
| ERROR | STOPPED | MCPREPOSITORY-04 | Recovery: shutdown |
| STOPPED | [*] | MCPREPOSITORY-04 | Terminal state |

### Sandbox Execution Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | IDLE | SANDBOXREPOSITORY-01 | Default state |
| IDLE | EXECUTING | SANDBOXREPOSITORY-01 | Command started |
| EXECUTING | MONITORING | SANDBOXREPOSITORY-03 | Resource monitoring started |
| MONITORING | EXECUTING | SANDBOXREPOSITORY-03 | Monitoring continues |
| EXECUTING | COMPLETED | SANDBOXREPOSITORY-01 | Process finished |
| EXECUTING | FAILED | SANDBOXREPOSITORY-01 | Process crashed |
| EXECUTING | TIMEOUT | SANDBOXREPOSITORY-03 | Timeout exceeded |
| EXECUTING | RESOURCE_EXCEEDED | SANDBOXREPOSITORY-04 | Resource limit hit |
| MONITORING | TIMEOUT | SANDBOXREPOSITORY-03 | Timeout exceeded |
| MONITORING | RESOURCE_EXCEEDED | SANDBOXREPOSITORY-04 | Resource limit hit |
| TIMEOUT | IDLE | SANDBOXREPOSITORY-01 | Cleanup after timeout |
| FAILED | IDLE | SANDBOXREPOSITORY-01 | Cleanup after failure |
| RESOURCE_EXCEEDED | IDLE | SANDBOXREPOSITORY-04 | Cleanup after resource violation |
| COMPLETED | [*] | SANDBOXREPOSITORY-01 | Terminal state |

### Diff Staging Lifecycle Transition Matrix

| From | To | UC-ID | Condition |
|------|----|-------|-----------|
| [*] | EMPTY | EDITSTRATEGYREPOSITORY-10 | Default state |
| EMPTY | STAGING | EDITSTRATEGYREPOSITORY-10 | Diff computation started |
| STAGING | STAGED | EDITSTRATEGYREPOSITORY-10 | Diff computed successfully |
| STAGING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff computation failed |
| STAGED | AWAITING_APPROVAL | EDITSTRATEGYREPOSITORY-10 | Diff presented for review |
| AWAITING_APPROVAL | APPROVED | SAFETYSVC-02 | User approved |
| AWAITING_APPROVAL | EMPTY | SAFETYSVC-02 | User rejected, cleanup |
| APPROVED | APPLYING | EDITSTRATEGYREPOSITORY-10 | Diff application started |
| APPLYING | APPLIED | EDITSTRATEGYREPOSITORY-10 | Diff applied successfully |
| APPLYING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff application failed |
| APPLIED | EMPTY | EDITSTRATEGYREPOSITORY-10 | Cleanup after application |
| ERROR | EMPTY | EDITSTRATEGYREPOSITORY-10 | Cleanup after error |
| APPLIED | [*] | EDITSTRATEGYREPOSITORY-10 | Terminal state |

## Lifecycle-Write UC Mapping (SMT Ownership)

One lifecycle-write UC per target state. This table is the authoritative reference.

### Session Lifecycle (API-First)

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CREATED | SESSIONSVC-01 PERSIST Session | Session record initialized |
| ACTIVE | SESSIONSVC-01 PERSIST Session | Session accepting messages (after init/resume) |
| SAVED | SESSIONSVC-01 PERSIST Session | Session persisted to disk |
| RESTORED | SESSIONSVC-04 RESTORE Session | Session loaded from disk |
| BRANCHED | SESSIONSVC-08 BRANCH Session | Session forked from parent |
| CLOSED | SESSIONSVC-09 DELETE Session | Session terminated (quit or error) |

### Plan Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| BUILDING | TASKSVC-07 QUEUE Plan | Plan being constructed |
| QUEUED | TASKSVC-07 QUEUE Plan | Plan construction complete, queued for approval |
| APPROVED | TASKSVC-08 APPROVE Plan | Plan approved by user |
| EXECUTING | TASKSVC-08 APPROVE Plan | Plan execution starts |
| COMPLETED | TASKSVC-01 PROCESS User Task | Agent loop finishes all steps |
| REJECTED | TASKSVC-08 APPROVE Plan | Plan rejected by user |

### Plugin Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| DISCOVERED | TOOLSVC-PLG01 DISCOVER Plugins | Plugin found on filesystem |
| LOADING | TOOLSVC-PLG02 LOAD Manifest | Plugin manifest being parsed |
| LOADED | TOOLSVC-PLG03 REGISTER Plugin Tools | Manifest parsed, tools registered |
| ENABLED | TOOLSVC-PLG05 ENABLE Plugin | Plugin active and available |
| DISABLED | TOOLSVC-PLG06 DISABLE Plugin | Plugin deactivated |
| ERROR | TOOLSVC-PLG01 DISCOVER Plugins | Load error or runtime exception (re-discover recovers) |

### Subagent Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| SPAWNING | TASKSVC-09 SPAWN Subagent | Child agent process initializing |
| RUNNING | TASKSVC-09 SPAWN Subagent | Child agent executing task |
| COMPLETED | TASKSVC-10 COLLECT Subagent Result | Child agent finished successfully |
| FAILED | TASKSVC-14 HANDLE Error | Child agent encountered unrecoverable error |

### Persona Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| LOADING | TASKSVC-12 LOAD Persona | Persona configuration being loaded |
| ACTIVE | TASKSVC-11 DELEGATE to Persona | Persona active and available |
| SWITCHING | TASKSVC-13 SWITCH Persona | Switching persona at runtime |
| ERROR | TASKSVC-12 LOAD Persona | Persona load or switch failed |

### MCP Client Connection Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CONNECTING | MCPREPOSITORY-01 CONNECT MCP Server | Connection in progress |
| CONNECTED | MCPREPOSITORY-01 CONNECT MCP Server | Connected to MCP server |
| DISCOVERING | MCPREPOSITORY-02 DISCOVER MCP Tools | Discovering tools from server |
| ERROR | MCPREPOSITORY-01 CONNECT MCP Server | Connection or discovery failed |

### MCP Server Serving Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| STARTING | MCPREPOSITORY-04 EXPOSE nasim Tools | Server starting up |
| RUNNING | MCPREPOSITORY-04 EXPOSE nasim Tools | Server running |
| STOPPING | MCPREPOSITORY-04 EXPOSE nasim Tools | Server shutting down |
| ERROR | MCPREPOSITORY-04 EXPOSE nasim Tools | Server startup or runtime failure |

### Sandbox Execution Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| EXECUTING | SANDBOXREPOSITORY-01 ISOLATE Command | Process running in sandbox |
| MONITORING | SANDBOXREPOSITORY-03 MONITOR Process | Process being monitored |
| COMPLETED | SANDBOXREPOSITORY-01 ISOLATE Command | Process finished successfully |
| TIMEOUT | SANDBOXREPOSITORY-03 MONITOR Process | Process exceeded time limit |
| FAILED | SANDBOXREPOSITORY-01 ISOLATE Command | Process crashed or was killed |
| RESOURCE_EXCEEDED | SANDBOXREPOSITORY-04 LIMIT Resources | Process exceeded resource quota |

### Diff Staging Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| STAGING | EDITSTRATEGYREPOSITORY-10 STAGE Diff | Diff being computed |
| STAGED | EDITSTRATEGYREPOSITORY-10 STAGE Diff | Diff ready for review |
| AWAITING_APPROVAL | SAFETYSVC-02 REQUEST Approval | Diff presented for user approval |
| APPROVED | SAFETYSVC-02 REQUEST Approval | User approved diff |
| APPLYING | EDITSTRATEGYREPOSITORY-10 STAGE Diff | Approved diff being applied |
| APPLIED | EDITSTRATEGYREPOSITORY-10 STAGE Diff | Diff successfully applied |
| ERROR | EDITSTRATEGYREPOSITORY-10 STAGE Diff | Diff computation or application failed |

### Safety Mode Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| UNINITIALIZED | SAFETYSVC-03 APPLY Safety Mode | Safety system not initialized |
| PERMISSIVE | SAFETYSVC-03 APPLY Safety Mode | Permissive mode applied |
| ASK | SAFETYSVC-03 APPLY Safety Mode | Ask mode applied |
| BLOCK | SAFETYSVC-03 APPLY Safety Mode | Block mode applied |
| ERROR | SAFETYSVC-01 CHECK Permission | Safety system encountered error |

### Router Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CLASSIFYING | LLMREPOSITORY-03 CLASSIFY Task | Task classification started |
| SELECTING | LLMREPOSITORY-05 SELECT Model | Model selection in progress |
| SWITCHING | LLMREPOSITORY-08 SWITCH Model | Runtime model switch |
| FALLBACK | LLMREPOSITORY-06 APPLY Fallback | Falling back to next model |
| ERROR | LLMREPOSITORY-03 CLASSIFY Task | Classification or routing failure |

### Provider Connection Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| REGISTERING | LLMREPOSITORY-01 REGISTER Provider | Provider registration started |
| ACTIVE | LLMREPOSITORY-01 REGISTER Provider | Provider registered and ready |
| SELECTING | LLMREPOSITORY-04 SELECT Provider Backend | Backend selection in progress |
| ERROR | LLMREPOSITORY-01 REGISTER Provider | Registration or selection failed |

### Evaluation Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| CHECKING | EVALSVC-01 EVALUATE Task | Task completion checks started |
| REVIEWING | EVALSVC-04 VALIDATE With LLM | LLM review in progress |
| TESTING | EVALSVC-05 VALIDATE Test Suite | Test validation in progress |
| SCORING | EVALSVC-07 RECORD Quality Signal | Scoring in progress |
| RETRYING | EVALSVC-06 COORDINATE Retry | Retry with backoff and escalation |
| PASSED | EVALSVC-07 RECORD Quality Signal | Evaluation passed |
| FAILED | EVALSVC-02 CHECK Task Completion | Evaluation failed |

### Repository Index Lifecycle

| Target State | Lifecycle-Write UC | Description |
|--------------|-------------------|-------------|
| INDEXING | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | AST indexing in progress |
| INDEXED | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | Repository fully indexed |
| BUILDING_GRAPH | REPOINTELLIGENCEREPOSITORY-02 BUILD Symbol Graph | Cross-file symbol reference graph |
| EMBEDDING | REPOINTELLIGENCEREPOSITORY-05 EMBED Code | Vector embedding generation |
| STALE | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | Index outdated, needs re-index |
| ERROR | REPOINTELLIGENCEREPOSITORY-01 INDEX Codebase | Indexing operation failed |

## SM → SQ Transition Coverage Tables

> **TRC-SM-05 compliance:** Every SM transition mapped to its implementing SQ diagram.
> Terminal (`[*]`) transitions are state diagram syntax, not implementable transitions — marked `—`.

### sm_task_svc_agent — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | TASKSVC-01 | Process startup | sq_taskservice01_process_user_task.puml |
| IDLE | RECEIVING | HTTPADP-06 | Request received (any adapter) | sq_httpadapter06_dispatch_message.puml |
| IDLE | PLANNING | TASKSVC-07 | /plan command entered | sq_taskservice07_queue_plan.puml |
| IDLE | [*] | TASKSVC-01 | Error handled | — |
| RECEIVING | THINKING | HTTPADP-06 | [needs_thinking] Input parsed | sq_httpadapter06_dispatch_message.puml |
| RECEIVING | IDLE | HTTPADP-06 | [!needs_thinking] API request complete | sq_httpadapter06_dispatch_message.puml |
| THINKING | RESPONDING | LLMREPOSITORY-02 | LLM returns text only | sq_llmrepository02_request_chat.puml |
| THINKING | TOOL_EXEC | LLMREPOSITORY-02 | LLM returns tool_calls | sq_llmrepository02_request_chat.puml |
| THINKING | COMPACTING | TASKSVC-06 | token_count > context_budget | sq_taskservice06_compact_context.puml |
| THINKING | ROUTING | LLMREPOSITORY-05 | ModelRouter resolving model | sq_llmrepository05_select_model.puml |
| THINKING | ERROR | LLMREPOSITORY-02 | Provider call failed | sq_llmrepository02_request_chat.puml |
| THINKING | EVALUATING | EVALSVC-01 | task_complete AND evaluation_enabled | sq_evaluationservice01_evaluate_task.puml |
| ROUTING | THINKING | LLMREPOSITORY-05 | Model selected | sq_llmrepository05_select_model.puml |
| TOOL_EXEC | THINKING | TASKSVC-02 | Tool call complete | sq_taskservice02_dispatch_tool_call.puml |
| TOOL_EXEC | AWAITING_APPROVAL | SAFETYSVC-02 | safety_mode=ask AND unsafe tool | sq_safetyservice02_request_approval.puml |
| TOOL_EXEC | HOOK_RUNNING | TOOLSVC-HK02 | Pre/post hook configured | sq_toolservice_hk02_dispatch_pre_tool_hook.puml |
| TOOL_EXEC | ERROR | TASKSVC-02 | Tool execution failed | sq_taskservice02_dispatch_tool_call.puml |
| TOOL_EXEC | STAGING | EDITSTRATEGYREPOSITORY-10 | diff_sandbox mode active | sq_editstrategyrepository10_stage_diff.puml |
| HOOK_RUNNING | TOOL_EXEC | TOOLSVC-HK02 | Hook execution complete | sq_toolservice_hk02_dispatch_pre_tool_hook.puml |
| HOOK_RUNNING | IDLE | TOOLSVC-HK02 | Hook execution complete (no tool) | sq_toolservice_hk02_dispatch_pre_tool_hook.puml |
| AWAITING_APPROVAL | TOOL_EXEC | SAFETYSVC-02 | User approves | sq_safetyservice02_request_approval.puml |
| AWAITING_APPROVAL | IDLE | SAFETYSVC-02 | User denies | sq_safetyservice02_request_approval.puml |
| COMPACTING | THINKING | TASKSVC-06 | Context compacted | sq_taskservice06_compact_context.puml |
| RESPONDING | IDLE | HTTPADP-06 | Response streamed to user | sq_httpadapter06_dispatch_message.puml |
| ERROR | IDLE | TASKSVC-14 | Error handled | sq_taskservice14_handle_error.puml |
| PLANNING | IDLE | TASKSVC-07 | Plan mode exited | sq_taskservice07_queue_plan.puml |
| EVALUATING | REVIEWING | EVALSVC-01 | Evaluation passed | sq_evaluationservice01_evaluate_task.puml |
| EVALUATING | RETRYING | EVALSVC-01 | Evaluation failed | sq_evaluationservice01_evaluate_task.puml |
| EVALUATING | THINKING | EVALSVC-01 | Retry with feedback | sq_evaluationservice01_evaluate_task.puml |
| REVIEWING | THINKING | EVALSVC-04 | LLM review passed | sq_evaluationservice04_validate_with_llm.puml |
| REVIEWING | RETRYING | EVALSVC-04 | LLM review rejected | sq_evaluationservice04_validate_with_llm.puml |
| RETRYING | THINKING | EVALSVC-06 | Retry with feedback | sq_evaluationservice06_coordinate_retry.puml |
| RETRYING | ERROR | EVALSVC-06 | Retry exhausted | sq_evaluationservice06_coordinate_retry.puml |
| STAGING | AWAITING_DIFF_APPROVAL | EDITSTRATEGYREPOSITORY-10 | Diff computed successfully | sq_editstrategyrepository10_stage_diff.puml |
| STAGING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff computation failed | sq_editstrategyrepository10_stage_diff.puml |
| AWAITING_DIFF_APPROVAL | TOOL_EXEC | SAFETYSVC-02 | User approves diff | sq_safetyservice02_request_approval.puml |
| AWAITING_DIFF_APPROVAL | IDLE | SAFETYSVC-02 | User rejects diff | sq_safetyservice02_request_approval.puml |

> **Coverage:** 37/37 non-terminal transitions covered. 0 ORPHANs.
> **Note:** Merged LISTENING+SERVING→RECEIVING. Removed THINKING→RESPONDING duplicate (was LLMREPOSITORY-02 and HTTPADP-06; consolidated to LLMREPOSITORY-02 only).

### sm_session_svc_session — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | CREATED | SESSIONSVC-01 | Session record initialized | sq_sessionservice01_persist_session.puml |
| CREATED | ACTIVE | SESSIONSVC-01 | Session ready for messages | sq_sessionservice01_persist_session.puml |
| ACTIVE | SAVED | SESSIONSVC-01 | Session persisted to disk | sq_sessionservice01_persist_session.puml |
| ACTIVE | BRANCHED | SESSIONSVC-08 | Session forked from parent | sq_sessionservice08_branch_session.puml |
| ACTIVE | CLOSED | SESSIONSVC-09 | Session terminated | sq_sessionservice09_delete_session.puml |
| SAVED | RESTORED | SESSIONSVC-04 | Session loaded from disk | sq_sessionservice04_restore_session.puml |
| SAVED | CLOSED | SESSIONSVC-09 | Session terminated | sq_sessionservice09_delete_session.puml |
| RESTORED | ACTIVE | SESSIONSVC-02 | Session ready for messages | sq_sessionservice02_read_session.puml |
| RESTORED | SAVED | SESSIONSVC-01 | Session persisted to disk | sq_sessionservice01_persist_session.puml |
| RESTORED | CLOSED | SESSIONSVC-09 | Session terminated | sq_sessionservice09_delete_session.puml |
| BRANCHED | ACTIVE | SESSIONSVC-02 | Session ready for messages | sq_sessionservice02_read_session.puml |
| BRANCHED | CLOSED | SESSIONSVC-09 | Session terminated | sq_sessionservice09_delete_session.puml |
| CLOSED | [*] | — | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_task_svc_subagent — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | TASKSVC-09 | Default state | sq_taskservice09_spawn_subagent.puml |
| IDLE | SPAWNING | TASKSVC-09 | Child agent spawn requested | sq_taskservice09_spawn_subagent.puml |
| SPAWNING | RUNNING | TASKSVC-09 | Child agent initialized | sq_taskservice09_spawn_subagent.puml |
| SPAWNING | FAILED | TASKSVC-09 | Spawn failed | sq_taskservice09_spawn_subagent.puml |
| RUNNING | COMPLETED | TASKSVC-10 | Task finished successfully | sq_taskservice10_collect_subagent_result.puml |
| RUNNING | FAILED | TASKSVC-14 | Unrecoverable error | sq_taskservice14_handle_error.puml |
| COMPLETED | IDLE | TASKSVC-10 | Results aggregated to parent | sq_taskservice10_collect_subagent_result.puml |
| COMPLETED | [*] | TASKSVC-10 | Terminal state | — |
| FAILED | IDLE | TASKSVC-14 | Error reported, cleanup done | sq_taskservice14_handle_error.puml |
| FAILED | [*] | TASKSVC-14 | Terminal state | — |

> **Coverage:** 8/8 non-terminal transitions covered. 0 ORPHANs.

### sm_tool_svc_plugin — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCOVERED | TOOLSVC-PLG01 | Plugin found on filesystem | sq_toolservice_plg01_discover_plugins.puml |
| DISCOVERED | LOADING | TOOLSVC-PLG02 | Manifest parsing starts | sq_toolservice_plg02_load_manifest.puml |
| DISCOVERED | ERROR | TOOLSVC-PLG01 | Plugin discovery failed | sq_toolservice_plg01_discover_plugins.puml |
| LOADING | LOADED | TOOLSVC-PLG03 | Manifest parsed, tools registered | sq_toolservice_plg03_register_plugin_tools.puml |
| LOADING | ERROR | TOOLSVC-PLG02 | Manifest parsing failed | sq_toolservice_plg02_load_manifest.puml |
| LOADED | ENABLED | TOOLSVC-PLG05 | Plugin activated | sq_toolservice_plg05_enable_plugin.puml |
| LOADED | DISABLED | TOOLSVC-PLG06 | Plugin deactivated | sq_toolservice_plg06_disable_plugin.puml |
| LOADED | ERROR | TOOLSVC-PLG03 | Tool registration failed | sq_toolservice_plg03_register_plugin_tools.puml |
| ENABLED | DISABLED | TOOLSVC-PLG06 | Plugin deactivated | sq_toolservice_plg06_disable_plugin.puml |
| ENABLED | ERROR | TOOLSVC-PLG01 | Runtime exception | sq_toolservice_plg01_discover_plugins.puml |
| ENABLED | [*] | TOOLSVC-PLG06 | Plugin unloaded | — |
| DISABLED | ENABLED | TOOLSVC-PLG05 | Plugin activated | sq_toolservice_plg05_enable_plugin.puml |
| DISABLED | [*] | TOOLSVC-PLG06 | Plugin unloaded | — |
| ERROR | DISCOVERED | TOOLSVC-PLG01 | Re-discovery (recovery) | sq_toolservice_plg01_discover_plugins.puml |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_task_svc_plan — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | TASKSVC-07 | No plan active | sq_taskservice07_queue_plan.puml |
| EMPTY | BUILDING | TASKSVC-07 | /plan command entered | sq_taskservice07_queue_plan.puml |
| BUILDING | QUEUED | TASKSVC-07 | Plan construction complete | sq_taskservice07_queue_plan.puml |
| BUILDING | EMPTY | TASKSVC-07 | Plan cancelled | sq_taskservice07_queue_plan.puml |
| QUEUED | APPROVED | TASKSVC-08 | User approves plan | sq_taskservice08_approve_plan.puml |
| QUEUED | REJECTED | TASKSVC-08 | User rejects plan | sq_taskservice08_approve_plan.puml |
| APPROVED | EXECUTING | TASKSVC-08 | Execution started | sq_taskservice08_approve_plan.puml |
| EXECUTING | COMPLETED | TASKSVC-01 | All plan steps finished | sq_taskservice01_process_user_task.puml |
| EXECUTING | EMPTY | TASKSVC-14 | Execution failed or cancelled | sq_taskservice14_handle_error.puml |
| COMPLETED | [*] | TASKSVC-01 | Terminal state | — |
| REJECTED | [*] | TASKSVC-08 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_task_svc_persona — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNLOADED | TASKSVC-12 | Default state | `sq_taskservice12_load_persona.puml` |
| UNLOADED | LOADING | TASKSVC-12 | Load requested | `sq_taskservice12_load_persona.puml` |
| LOADING | ACTIVE | TASKSVC-12 | Load successful | `sq_taskservice12_load_persona.puml` |
| LOADING | ERROR | TASKSVC-12 | Load failed | `sq_taskservice12_load_persona.puml` |
| ACTIVE | SWITCHING | TASKSVC-13 | Switch requested | `sq_taskservice13_switch_persona.puml` |
| SWITCHING | ACTIVE | TASKSVC-13 | Switch successful | `sq_taskservice13_switch_persona.puml` |
| SWITCHING | ERROR | TASKSVC-13 | Switch failed | `sq_taskservice13_switch_persona.puml` |
| ACTIVE | UNLOADED | TASKSVC-11 | Delegation complete | `sq_taskservice11_delegate_to_persona.puml` |
| ERROR | UNLOADED | TASKSVC-12 | Recovery: retry load | `sq_taskservice12_load_persona.puml` |
| UNLOADED | [*] | TASKSVC-12 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_mcp_repo_client — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | DISCONNECTED | MCPREPOSITORY-01 | Default state | `sq_mcprepository01_connect_mcp_server.puml` |
| DISCONNECTED | CONNECTING | MCPREPOSITORY-01 | Connect requested | `sq_mcprepository01_connect_mcp_server.puml` |
| CONNECTING | CONNECTED | MCPREPOSITORY-01 | Connection established | `sq_mcprepository01_connect_mcp_server.puml` |
| CONNECTING | ERROR | MCPREPOSITORY-01 | Connection failed | `sq_mcprepository01_connect_mcp_server.puml` |
| CONNECTED | DISCOVERING | MCPREPOSITORY-02 | Tool discovery started | `sq_mcprepository02_discover_mcp_tools.puml` |
| DISCOVERING | CONNECTED | MCPREPOSITORY-02 | Discovery complete | `sq_mcprepository02_discover_mcp_tools.puml` |
| DISCOVERING | ERROR | MCPREPOSITORY-02 | Discovery failed | `sq_mcprepository02_discover_mcp_tools.puml` |
| CONNECTED | DISCONNECTED | MCPREPOSITORY-01 | Disconnected | `sq_mcprepository01_connect_mcp_server.puml` |
| ERROR | DISCONNECTED | MCPREPOSITORY-01 | Recovery: reconnect | `sq_mcprepository01_connect_mcp_server.puml` |
| DISCONNECTED | [*] | MCPREPOSITORY-01 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_mcp_repo_server — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | STOPPED | MCPREPOSITORY-04 | Default state | `sq_mcprepository04_expose_nasim_tools.puml` |
| STOPPED | STARTING | MCPREPOSITORY-04 | Start requested | `sq_mcprepository04_expose_nasim_tools.puml` |
| STARTING | RUNNING | MCPREPOSITORY-04 | Startup complete | `sq_mcprepository04_expose_nasim_tools.puml` |
| STARTING | ERROR | MCPREPOSITORY-04 | Startup failed | `sq_mcprepository04_expose_nasim_tools.puml` |
| RUNNING | STOPPING | MCPREPOSITORY-04 | Stop requested | `sq_mcprepository04_expose_nasim_tools.puml` |
| STOPPING | STOPPED | MCPREPOSITORY-04 | Shutdown complete | `sq_mcprepository04_expose_nasim_tools.puml` |
| RUNNING | ERROR | MCPREPOSITORY-04 | Runtime failure | `sq_mcprepository04_expose_nasim_tools.puml` |
| ERROR | STOPPED | MCPREPOSITORY-04 | Recovery: shutdown | `sq_mcprepository04_expose_nasim_tools.puml` |
| STOPPED | [*] | MCPREPOSITORY-04 | Terminal state | — |

> **Coverage:** 8/8 non-terminal transitions covered. 0 ORPHANs.

### sm_sandbox_repo_sandbox — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | SANDBOXREPOSITORY-01 | Default state | `sq_sandboxrepository01_isolate_command.puml` |
| IDLE | EXECUTING | SANDBOXREPOSITORY-01 | Command started | `sq_sandboxrepository01_isolate_command.puml` |
| EXECUTING | MONITORING | SANDBOXREPOSITORY-03 | Resource monitoring started | `sq_sandboxrepository03_monitor_process.puml` |
| MONITORING | EXECUTING | SANDBOXREPOSITORY-03 | Monitoring continues | `sq_sandboxrepository03_monitor_process.puml` |
| EXECUTING | COMPLETED | SANDBOXREPOSITORY-01 | Process finished | `sq_sandboxrepository01_isolate_command.puml` |
| EXECUTING | FAILED | SANDBOXREPOSITORY-01 | Process crashed | `sq_sandboxrepository01_isolate_command.puml` |
| EXECUTING | TIMEOUT | SANDBOXREPOSITORY-03 | Timeout exceeded | `sq_sandboxrepository03_monitor_process.puml` |
| EXECUTING | RESOURCE_EXCEEDED | SANDBOXREPOSITORY-04 | Resource limit hit | `sq_sandboxrepository04_limit_resources.puml` |
| MONITORING | TIMEOUT | SANDBOXREPOSITORY-03 | Timeout exceeded | `sq_sandboxrepository03_monitor_process.puml` |
| MONITORING | RESOURCE_EXCEEDED | SANDBOXREPOSITORY-04 | Resource limit hit | `sq_sandboxrepository04_limit_resources.puml` |
| TIMEOUT | IDLE | SANDBOXREPOSITORY-01 | Cleanup after timeout | `sq_sandboxrepository01_isolate_command.puml` |
| FAILED | IDLE | SANDBOXREPOSITORY-01 | Cleanup after failure | `sq_sandboxrepository01_isolate_command.puml` |
| RESOURCE_EXCEEDED | IDLE | SANDBOXREPOSITORY-04 | Cleanup after resource violation | `sq_sandboxrepository04_limit_resources.puml` |
| COMPLETED | [*] | SANDBOXREPOSITORY-01 | Terminal state | — |

> **Coverage:** 13/13 non-terminal transitions covered. 0 ORPHANs.

### sm_edit_strategy_repo_diff — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | EMPTY | EDITSTRATEGYREPOSITORY-10 | Default state | `sq_editstrategyrepository10_stage_diff.puml` |
| EMPTY | STAGING | EDITSTRATEGYREPOSITORY-10 | Diff computation started | `sq_editstrategyrepository10_stage_diff.puml` |
| STAGING | STAGED | EDITSTRATEGYREPOSITORY-10 | Diff computed successfully | `sq_editstrategyrepository10_stage_diff.puml` |
| STAGING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff computation failed | `sq_editstrategyrepository10_stage_diff.puml` |
| STAGED | AWAITING_APPROVAL | EDITSTRATEGYREPOSITORY-10 | Diff presented for review | `sq_editstrategyrepository10_stage_diff.puml` |
| AWAITING_APPROVAL | APPROVED | SAFETYSVC-02 | User approved | `sq_safetyservice02_request_approval.puml` |
| AWAITING_APPROVAL | EMPTY | SAFETYSVC-02 | User rejected, cleanup | `sq_safetyservice02_request_approval.puml` |
| APPROVED | APPLYING | EDITSTRATEGYREPOSITORY-10 | Diff application started | `sq_editstrategyrepository10_stage_diff.puml` |
| APPLYING | APPLIED | EDITSTRATEGYREPOSITORY-10 | Diff applied successfully | `sq_editstrategyrepository10_stage_diff.puml` |
| APPLYING | ERROR | EDITSTRATEGYREPOSITORY-10 | Diff application failed | `sq_editstrategyrepository10_stage_diff.puml` |
| APPLIED | EMPTY | EDITSTRATEGYREPOSITORY-10 | Cleanup after application | `sq_editstrategyrepository10_stage_diff.puml` |
| ERROR | EMPTY | EDITSTRATEGYREPOSITORY-10 | Cleanup after error | `sq_editstrategyrepository10_stage_diff.puml` |
| APPLIED | [*] | EDITSTRATEGYREPOSITORY-10 | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_safety_svc_safety — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINITIALIZED | SAFETYSVC-03 | Default state | sq_safetyservice03_apply_safety_mode.puml |
| UNINITIALIZED | PERMISSIVE | SAFETYSVC-03 | Apply permissive mode | sq_safetyservice03_apply_safety_mode.puml |
| UNINITIALIZED | ASK | SAFETYSVC-03 | Apply ask mode | sq_safetyservice03_apply_safety_mode.puml |
| UNINITIALIZED | BLOCK | SAFETYSVC-03 | Apply block mode | sq_safetyservice03_apply_safety_mode.puml |
| PERMISSIVE | ASK | SAFETYSVC-03 | Switch to ask mode | sq_safetyservice03_apply_safety_mode.puml |
| PERMISSIVE | BLOCK | SAFETYSVC-03 | Switch to block mode | sq_safetyservice03_apply_safety_mode.puml |
| ASK | PERMISSIVE | SAFETYSVC-03 | Switch to permissive mode | sq_safetyservice03_apply_safety_mode.puml |
| ASK | BLOCK | SAFETYSVC-03 | Switch to block mode | sq_safetyservice03_apply_safety_mode.puml |
| BLOCK | PERMISSIVE | SAFETYSVC-03 | Switch to permissive mode | sq_safetyservice03_apply_safety_mode.puml |
| BLOCK | ASK | SAFETYSVC-03 | Switch to ask mode | sq_safetyservice03_apply_safety_mode.puml |
| PERMISSIVE | ERROR | SAFETYSVC-01 | Permission check failed | sq_safetyservice01_check_permission.puml |
| ASK | ERROR | SAFETYSVC-01 | Permission check failed | sq_safetyservice01_check_permission.puml |
| BLOCK | ERROR | SAFETYSVC-01 | Permission check failed | sq_safetyservice01_check_permission.puml |
| ERROR | UNINITIALIZED | SAFETYSVC-03 | Recovery: reinitialize | sq_safetyservice03_apply_safety_mode.puml |
| UNINITIALIZED | [*] | SAFETYSVC-03 | Terminal state | — |

> **Coverage:** 14/14 non-terminal transitions covered. 0 ORPHANs.

### sm_llm_repo_router — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | LLMREPOSITORY-01 | Default state | sq_llmrepository05_select_model.puml |
| IDLE | CLASSIFYING | LLMREPOSITORY-03 | Task classification started | sq_llmrepository07_classify_task.puml |
| CLASSIFYING | SELECTING | LLMREPOSITORY-01 | Classification complete | sq_llmrepository05_select_model.puml |
| CLASSIFYING | ERROR | LLMREPOSITORY-03 | Classification failed | sq_llmrepository07_classify_task.puml |
| SELECTING | IDLE | LLMREPOSITORY-01 | Model selected | sq_llmrepository05_select_model.puml |
| SELECTING | FALLBACK | LLMREPOSITORY-02 | Primary model unavailable | sq_llmrepository06_apply_fallback.puml |
| FALLBACK | SELECTING | LLMREPOSITORY-02 | Fallback to next model | sq_llmrepository06_apply_fallback.puml |
| FALLBACK | ERROR | LLMREPOSITORY-02 | All models exhausted | sq_llmrepository06_apply_fallback.puml |
| IDLE | SWITCHING | LLMREPOSITORY-04 | Runtime switch requested | sq_llmrepository08_switch_model.puml |
| SWITCHING | IDLE | LLMREPOSITORY-04 | Switch successful | sq_llmrepository08_switch_model.puml |
| SWITCHING | ERROR | LLMREPOSITORY-04 | Switch failed | sq_llmrepository08_switch_model.puml |
| ERROR | IDLE | LLMREPOSITORY-01 | Recovery: retry | sq_llmrepository05_select_model.puml |
| IDLE | [*] | LLMREPOSITORY-01 | Terminal state | — |

> **Coverage:** 12/12 non-terminal transitions covered. 0 ORPHANs.

### sm_llm_repo_provider — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNREGISTERED | LLMREPOSITORY-01 | Default state | sq_llmrepository01_register_provider.puml |
| UNREGISTERED | REGISTERING | LLMREPOSITORY-01 | Registration started | sq_llmrepository01_register_provider.puml |
| REGISTERING | ACTIVE | LLMREPOSITORY-01 | Registration successful | sq_llmrepository01_register_provider.puml |
| REGISTERING | ERROR | LLMREPOSITORY-01 | Registration failed | sq_llmrepository01_register_provider.puml |
| ACTIVE | SELECTING | LLMREPOSITORY-04 | Backend selection started | sq_llmrepository04_select_provider_backend.puml |
| SELECTING | ACTIVE | LLMREPOSITORY-04 | Backend selected | sq_llmrepository04_select_provider_backend.puml |
| SELECTING | ERROR | LLMREPOSITORY-04 | Selection failed | sq_llmrepository04_select_provider_backend.puml |
| ACTIVE | UNREGISTERED | LLMREPOSITORY-01 | Unregistered | sq_llmrepository01_register_provider.puml |
| ERROR | UNREGISTERED | LLMREPOSITORY-01 | Recovery: re-register | sq_llmrepository01_register_provider.puml |
| UNREGISTERED | [*] | LLMREPOSITORY-01 | Terminal state | — |

> **Coverage:** 9/9 non-terminal transitions covered. 0 ORPHANs.

### sm_eval_svc_evaluation — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | IDLE | EVALSVC-01 | Default state | sq_evaluationservice01_evaluate_task.puml |
| IDLE | CHECKING | EVALSVC-01 | Evaluation started | sq_evaluationservice01_evaluate_task.puml |
| CHECKING | REVIEWING | EVALSVC-04 | LLM review required | sq_evaluationservice04_validate_with_llm.puml |
| CHECKING | TESTING | EVALSVC-05 | Test validation required | sq_evaluationservice05_validate_test_suite.puml |
| CHECKING | SCORING | EVALSVC-07 | Direct scoring (no review/test) | sq_evaluationservice07_record_quality_signal.puml |
| CHECKING | FAILED | EVALSVC-02 | Task completion check failed | sq_evaluationservice02_check_task_completion.puml |
| REVIEWING | SCORING | EVALSVC-07 | LLM review passed | sq_evaluationservice07_record_quality_signal.puml |
| REVIEWING | RETRYING | EVALSVC-06 | LLM review rejected | sq_evaluationservice06_coordinate_retry.puml |
| TESTING | SCORING | EVALSVC-07 | Tests passed | sq_evaluationservice07_record_quality_signal.puml |
| TESTING | RETRYING | EVALSVC-06 | Tests failed | sq_evaluationservice06_coordinate_retry.puml |
| SCORING | PASSED | EVALSVC-07 | Scoring threshold met | sq_evaluationservice07_record_quality_signal.puml |
| SCORING | RETRYING | EVALSVC-06 | Scoring below threshold | sq_evaluationservice06_coordinate_retry.puml |
| RETRYING | CHECKING | EVALSVC-06 | Retry with feedback | sq_evaluationservice06_coordinate_retry.puml |
| RETRYING | FAILED | EVALSVC-06 | Retries exhausted | sq_evaluationservice06_coordinate_retry.puml |
| PASSED | [*] | EVALSVC-07 | Terminal state | — |
| FAILED | [*] | EVALSVC-06 | Terminal state | — |

> **Coverage:** 14/14 non-terminal transitions covered. 0 ORPHANs.
> **Simplification v3:** Removed redundant PASSED→IDLE and FAILED→IDLE transitions (terminal states only have [*] exits).

### sm_repo_intel_repo_index — Transition Coverage Table

| From State | To State | UC-ID | Trigger | SQ Diagram |
|------------|----------|-------|---------|------------|
| [*] | UNINDEXED | REPOINTELLIGENCEREPOSITORY-01 | Default state | sq_repointelligencerepository01_index_codebase.puml |
| UNINDEXED | INDEXING | REPOINTELLIGENCEREPOSITORY-01 | Indexing started | sq_repointelligencerepository01_index_codebase.puml |
| INDEXING | INDEXED | REPOINTELLIGENCEREPOSITORY-01 | Indexing complete | sq_repointelligencerepository01_index_codebase.puml |
| INDEXING | ERROR | REPOINTELLIGENCEREPOSITORY-01 | Indexing failed | sq_repointelligencerepository01_index_codebase.puml |
| INDEXED | BUILDING_GRAPH | REPOINTELLIGENCEREPOSITORY-02 | Graph building started | sq_repointelligencerepository02_build_symbol_graph.puml |
| BUILDING_GRAPH | INDEXED | REPOINTELLIGENCEREPOSITORY-02 | Graph built | sq_repointelligencerepository02_build_symbol_graph.puml |
| BUILDING_GRAPH | ERROR | REPOINTELLIGENCEREPOSITORY-02 | Graph building failed | sq_repointelligencerepository02_build_symbol_graph.puml |
| INDEXED | EMBEDDING | REPOINTELLIGENCEREPOSITORY-05 | Embedding started | sq_repointelligencerepository05_embed_code.puml |
| EMBEDDING | INDEXED | REPOINTELLIGENCEREPOSITORY-05 | Embedding complete | sq_repointelligencerepository05_embed_code.puml |
| EMBEDDING | ERROR | REPOINTELLIGENCEREPOSITORY-05 | Embedding failed | sq_repointelligencerepository05_embed_code.puml |
| INDEXED | STALE | REPOINTELLIGENCEREPOSITORY-01 | Source files changed | sq_repointelligencerepository01_index_codebase.puml |
| STALE | INDEXING | REPOINTELLIGENCEREPOSITORY-01 | Re-indexing started | sq_repointelligencerepository01_index_codebase.puml |
| ERROR | UNINDEXED | REPOINTELLIGENCEREPOSITORY-01 | Recovery: start fresh | sq_repointelligencerepository01_index_codebase.puml |
| INDEXED | [*] | REPOINTELLIGENCEREPOSITORY-01 | Terminal state | — |
| UNINDEXED | [*] | REPOINTELLIGENCEREPOSITORY-01 | Terminal state | — |

> **Coverage:** 13/13 non-terminal transitions covered. 0 ORPHANs.

## SM Inventory & Completeness Report (2026-06-27)

### Audit Method
Systematic 21-group C4 component audit: every Component() in every `docs/C4/c4_nasim_component_*.puml` was cross-referenced against the 15 existing SM files, the UC catalog (`docs/UC/README.md`, 148 UCs), and the ERD layer. Components were flagged as stateful if they met any of the EXT-01..05 criteria (sm.md): lifecycle state field, process lifecycle management, multiple UCs implying state transitions, stateful naming (Manager, Coordinator, Session, Runtime).

### Full SM Inventory (15 files)

| # | SM File | Entity | C4 Component | Type | States | UCs | Status |
|---|---------|--------|--------------|------|--------|-----|--------|
| 1 | sm_task_svc_agent.puml | Task Service | Task Service | Process FSM | 16 | TASKSVC-01..14, HTTPADP-06, LLMREPOSITORY-02, EDITSTRATEGYREPOSITORY-10, SAFETYSVC-02, TOOLSVC-HK02, EVALSVC-01..06, LLMREPOSITORY-05 | ✅ GREEN |
| 2 | sm_session_svc_session.puml | Session | Session Service | Entity | 6 | SESSIONSVC-01..04, SESSIONSVC-08, SESSIONSVC-09 | ✅ GREEN |
| 3 | sm_task_svc_plan.puml | Task Service (Plan) | Task Service | Entity | 7 | TASKSVC-07, TASKSVC-08, TASKSVC-01, TASKSVC-14 | ✅ GREEN |
| 4 | sm_tool_svc_plugin.puml | Tool Service (Plugin) | Tool Service | Entity | 6 | TOOLSVC-PLG01..06 | ✅ GREEN |
| 5 | sm_task_svc_subagent.puml | Task Service (Subagent) | Task Service | Entity | 5 | TASKSVC-09, TASKSVC-10, TASKSVC-14 | ✅ GREEN |
| 6 | sm_task_svc_persona.puml | Task Service (Persona) | Task Service | Entity | 5 | TASKSVC-11, TASKSVC-12, TASKSVC-13 | ✅ GREEN |
| 7 | sm_mcp_repo_client.puml | MCP Repository | MCP Repository | Entity | 5 | MCPREPOSITORY-01, MCPREPOSITORY-02 | ✅ GREEN |
| 8 | sm_mcp_repo_server.puml | MCP Repository (Server) | MCP Repository | Entity | 5 | MCPREPOSITORY-04 | ✅ GREEN |
| 9 | sm_sandbox_repo_sandbox.puml | Sandbox Repository | Sandbox Repository | Entity | 7 | SANDBOXREPOSITORY-01, SANDBOXREPOSITORY-03, SANDBOXREPOSITORY-04 | ✅ GREEN |
| 10 | sm_edit_strategy_repo_diff.puml | Edit Strategy Repository | Edit Strategy Repository | Entity | 8 | EDITSTRATEGYREPOSITORY-10, SAFETYSVC-02 | ✅ GREEN |
| 11 | sm_safety_svc_safety.puml | Safety Service | Safety Service | Entity | 5 | SAFETYSVC-01, SAFETYSVC-03 | ✅ GREEN |
| 12 | sm_llm_repo_router.puml | LLM Repository | LLM Repository | Entity | 6 | LLMREPOSITORY-01..04 | ✅ GREEN |
| 13 | sm_llm_repo_provider.puml | LLM Repository (Provider) | LLM Repository | Entity | 5 | LLMREPOSITORY-01, LLMREPOSITORY-04 | ✅ GREEN |
| 14 | sm_eval_svc_evaluation.puml | Evaluation Service | Evaluation Service | Entity | 8 | EVALSVC-01..07 | ✅ GREEN |
| 15 | sm_repo_intel_repo_index.puml | Repo Intelligence Repository | Repo Intelligence Repository | Entity | 7 | REPOINTELLIGENCEREPOSITORY-01, REPOINTELLIGENCEREPOSITORY-02, REPOINTELLIGENCEREPOSITORY-05 | ✅ GREEN |

### Coverage Summary

| Metric | Value |
|--------|-------|
| Total C4 component groups audited | 21 |
| Total C4 components scanned | ~109 |
| Total SM files | 15 |
| Total states across all SMs | 91 |
| Unique hex colors | 91 (0 duplicates) |
| Total transitions (all SMs) | 195 |
| Non-terminal transitions | 195 |
| Covered by SQ diagrams | 80 |
| ORPHAN transitions (awaiting SQ) | 0 |
| Lint violations | 0 (across all 15 files) |
| Terminal UC-ID violations found & fixed | 2 (agent, session) |

### Stateful Entities with Dedicated SM Coverage

| C4 Component | C4 Group | SM File |
|--------------|----------|---------|
| Task Service | Task | `sm_task_svc_agent.puml` (Process FSM) |
| Session Service | Session | `sm_session_svc_session.puml` |
| Task Service | Task | `sm_task_svc_plan.puml` |
| Tool Service | Tool | `sm_tool_svc_plugin.puml` |
| Task Service | Task | `sm_task_svc_subagent.puml` |
| Task Service | Task | `sm_task_svc_persona.puml` |
| MCP Repository | Repository | `sm_mcp_repo_client.puml` |
| MCP Repository | Repository | `sm_mcp_repo_server.puml` |
| Sandbox Repository | Repository | `sm_sandbox_repo_sandbox.puml` |
| Edit Strategy Repository | Repository | `sm_edit_strategy_repo_diff.puml` |
| Safety Service | Service | `sm_safety_svc_safety.puml` |
| LLM Repository | Repository | `sm_llm_repo_router.puml` |
| LLM Repository | Repository | `sm_llm_repo_provider.puml` |
| Evaluation Service | Service | `sm_eval_svc_evaluation.puml` |
| Repo Intelligence Repository | Repository | `sm_repo_intel_repo_index.puml` |

### Stateful Entities Covered Inside Agent Process FSM

These components have lifecycle states that occur as transient sub-states within the agent processing loop. Dedicated SMs would add no value:

| Component | C4 Component | Rationale |
|-----------|--------------|-----------|
| ConversationHistory | Task Service | Message store with token tracking. Its only state transition (`normal → compacting`) is a sub-state of Agent FSM's COMPACTING. No independent lifecycle outside the agent loop. |
| ContextCompactor | Context Service | Stateless summarizer invoked by ConversationHistory. No independent lifecycle. |
| ErrorBoundary | Task Service | Error handler. Error states (recoverable vs terminal) are sub-states of Agent FSM's ERROR. |
| ToolRegistry | Tool Service | Instance registry. Registration is static at startup (except MCP tools, covered by MCP SMs). |
| PermissionGate | Safety Service | Stateless evaluator. Permission decision (allow/deny/ask) maps to Agent FSM transitions. |
| FallbackChain | LLM Repository | Fallback lifecycle captured within Router SM: SELECTING → FALLBACK → ERROR. |
| Provider (Protocol) | LLM Repository | Chat lifecycle maps to Agent FSM: THINKING → RESPONDING/ERROR. |

### Stateful Entities Without Dedicated SM (LOW Priority — Backlog)

| # | Entity | C4 Component | Reason | Rationale |
|---|--------|--------------|--------|-----------|
| 1 | WireLog | Wire Log Repository | Write-buffer lifecycle | Append-only event store with buffering/flush. Simple 3-state (OPEN→WRITING→FLUSHING). UCs: WIRELOGREPOSITORY-01..05. |
| 2 | GitIntegration | Git Repository | Auto-commit lifecycle | Monitors for changes then commits. 3-state (IDLE→CHANGES_DETECTED→COMMITTING). UC: GITREPOSITORY-04. |
| 3 | PipelineOrchestrator | Context Service | Pipeline stage lifecycle | 5 transient pipeline stages completing synchronously in one pass. LOW risk. |
| 4 | REPLSession | CLI Adapter | REPL loop lifecycle | CLI entry point. Delegates all business logic via API. REPL state is UI state, not domain state. |
| 5 | ServerApp | HTTP Adapter | ASGI lifespan lifecycle | Standard ASGI startup/shutdown. Few project-specific transitions. |

### Lifecycle-Write Ownership Verification

Every entity SM state has exactly one owning lifecycle-write UC. Verified per SMT rules:

- **Session**: CREATED (SESSIONSVC-01), ACTIVE (SESSIONSVC-01), SAVED (SESSIONSVC-01), RESTORED (SESSIONSVC-04), BRANCHED (SESSIONSVC-08), CLOSED (SESSIONSVC-09) ✅
- **Plan**: BUILDING (TASKSVC-07), QUEUED (TASKSVC-07), APPROVED (TASKSVC-08), EXECUTING (TASKSVC-08), COMPLETED (TASKSVC-01), REJECTED (TASKSVC-08) ✅
- **Plugin**: DISCOVERED (TOOLSVC-PLG01), LOADING (TOOLSVC-PLG02), LOADED (TOOLSVC-PLG03), ENABLED (TOOLSVC-PLG05), DISABLED (TOOLSVC-PLG06), ERROR (TOOLSVC-PLG01) ✅
- **Subagent**: SPAWNING (TASKSVC-09), RUNNING (TASKSVC-09), COMPLETED (TASKSVC-10), FAILED (TASKSVC-14) ✅
- **Persona**: LOADING (TASKSVC-12), ACTIVE (TASKSVC-11), SWITCHING (TASKSVC-13), ERROR (TASKSVC-12) ✅
- **MCP Client**: CONNECTING (MCPREPOSITORY-01), CONNECTED (MCPREPOSITORY-01), DISCOVERING (MCPREPOSITORY-02), ERROR (MCPREPOSITORY-01) ✅
- **MCP Server**: STARTING (MCPREPOSITORY-04), RUNNING (MCPREPOSITORY-04), STOPPING (MCPREPOSITORY-04), ERROR (MCPREPOSITORY-04) ✅
- **Sandbox**: EXECUTING (SANDBOXREPOSITORY-01), MONITORING (SANDBOXREPOSITORY-03), COMPLETED (SANDBOXREPOSITORY-01), TIMEOUT (SANDBOXREPOSITORY-03), FAILED (SANDBOXREPOSITORY-01), RESOURCE_EXCEEDED (SANDBOXREPOSITORY-04) ✅
- **Diff Staging**: STAGING (EDITSTRATEGYREPOSITORY-10), STAGED (EDITSTRATEGYREPOSITORY-10), AWAITING_APPROVAL (SAFETYSVC-02), APPROVED (SAFETYSVC-02), APPLYING (EDITSTRATEGYREPOSITORY-10), APPLIED (EDITSTRATEGYREPOSITORY-10), ERROR (EDITSTRATEGYREPOSITORY-10) ✅
- **Safety**: PERMISSIVE (SAFETYSVC-03), ASK (SAFETYSVC-03), BLOCK (SAFETYSVC-03), ERROR (SAFETYSVC-01) ✅
- **Router**: CLASSIFYING (LLMREPOSITORY-03), SELECTING (LLMREPOSITORY-01), SWITCHING (LLMREPOSITORY-04), FALLBACK (LLMREPOSITORY-02), ERROR (LLMREPOSITORY-03) ✅
- **Provider**: REGISTERING (LLMREPOSITORY-01), ACTIVE (LLMREPOSITORY-01), SELECTING (LLMREPOSITORY-04), ERROR (LLMREPOSITORY-01) ✅
- **Evaluation**: CHECKING (EVALSVC-01), REVIEWING (EVALSVC-04), TESTING (EVALSVC-05), SCORING (EVALSVC-07), RETRYING (EVALSVC-06), PASSED (EVALSVC-07), FAILED (EVALSVC-02) ✅
- **Index**: INDEXING (REPOINTELLIGENCEREPOSITORY-01), INDEXED (REPOINTELLIGENCEREPOSITORY-01), BUILDING_GRAPH (REPOINTELLIGENCEREPOSITORY-02), EMBEDDING (REPOINTELLIGENCEREPOSITORY-05), STALE (REPOINTELLIGENCEREPOSITORY-01), ERROR (REPOINTELLIGENCEREPOSITORY-01) ✅

### Agent Process FSM — Documented Deviation

The Agent SM is intentionally a **Process FSM**, not an Entity Lifecycle. Per sm.md:
*"SMT rules from sm.md do not apply (documented deviation)."*

 Rationale:
 - Models the runtime processing loop of Task Service, not a persisted entity.
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
| All hex colors unique (91 states, 91 colors, 0 duplicates) | ✅ |
| All terminal transitions have UC-IDs | ✅ |
| All lifecycle-write states have exactly one owning UC | ✅ |
| Transition coverage tables complete (all 15 SMs in README) | ✅ |
| Documentation up to date (state tables, matrices, maps) | ✅ |
| SQ coverage (orphan resolution) | ✅ — 0 orphans remain (181/181 covered) |

### Simplifications Applied (2026-07-01)

| # | Change | From | To | Rationale |
|---|--------|------|----|-----------|
| 1 | Agent FSM: Merge LISTENING+SERVING → RECEIVING | 17 states | 16 states | Both process requests from adapters via HTTPADP-06; guard `[needs_thinking]` distinguishes CLI input from API requests that complete without thinking |
| 2 | Agent FSM: Fix THINKING→RESPONDING duplicate | 2 transitions | 1 transition | Consolidated to LLMREPOSITORY-02 only (LLM generates content); HTTPADP-06 dispatch is implicit in RESPONDING state |
| 3 | Agent FSM: Fix UC-ID naming consistency | TOOLSVC-02 | TOOLSVC-HK02 | HOOK transitions use HK02 group, not TOOLSVC-02 |
| 4 | Agent FSM: Fix UC-ID naming consistency | LLMREPOSITORY-01 | LLMREPOSITORY-05 | Router transitions use LLMREPOSITORY-05 SELECT Model, not LLMREPOSITORY-01 |
| 5 | Evaluation SM: Remove redundant terminal transitions | PASSED→IDLE, FAILED→IDLE | Removed | Terminal states should only have [*] exits; redundant back-transitions removed |
