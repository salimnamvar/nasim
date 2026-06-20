# nasim — State Machine Inventory

## Agent Lifecycle States

| State | Description | Entry Condition | Hex Color |
|-------|-------------|-----------------|-----------|
| IDLE | Waiting for user input | Startup or response complete | #E8F5E9 |
| LISTENING | Receiving and parsing user input | User types input | #E3F2FD |
| THINKING | LLM processing messages | Input parsed, messages built | #FFF3E0 |
| TOOL_EXEC | Executing a tool call | LLM returns tool_calls | #F3E5F5 |
| RESPONDING | Streaming final text to user | LLM returns text only | #FCE4EC |
| ERROR | Error occurred | LLM call or tool exec fails | #FFEBEE |
| COMPACTING | Summarizing old exchanges | token_count > context_budget | #E0F7FA |
| AWAITING_APPROVAL | Waiting for user permission | safety_mode=ask AND unsafe tool | #FFF9C4 |
| PLANNING | Plan mode, tool calls queued | /plan command entered | #F1F8E9 |
| HOOK_RUNNING | Pre/post hook executing | tool or LLM call with hooks | #E8EAF6 |
| ROUTING | Model selection in progress | ModelRouter resolving model | #FBE9E7 |
| SERVING | HTTP server handling request | HTTP client sends request | #E0F2F1 |
| SUBAGENT_SPAWNED | Child agent created | SubagentTool dispatched | #DCEDC8 |
| SUBAGENT_RUNNING | Child agent executing | Child agent started | #C8E6C9 |
| SUBAGENT_COLLECTED | Child agent result gathered | Child agent completed | #A5D6A7 |
| SANDBOXED | Command running in sandbox | ShellTool via SandboxExecutor | #B3E5FC |
| SANDBOX_BLOCKED | Command blocked by policy | SandboxPolicy deny | #FFCDD2 |
| MEMORY_READ | Retrieving knowledge | MemoryTool RECALL invoked | #D1C4E9 |
| MEMORY_WRITE | Storing knowledge | MemoryTool PERSIST invoked | #B39DDB |
| GIT_OP | Git operation in progress | GitTool invoked | #FFE0B2 |

## Diagram

See `sm_agent_lifecycle.puml` for the PlantUML state machine diagram.

## Notes

- This is a **process FSM**, not an entity lifecycle. States are transient agent
  states during task execution, not persisted lifecycle states. SMT ownership
  rules from `sm.md` do not apply (documented deviation).
- PLANNING state is Phase 2 (CAP-09). When active, tool calls are queued and
  displayed as a plan; `/approve` drains the queue.
- COMPACTING is triggered by ContextCompactor (CAP-05) when token count exceeds
  the configured context budget.
- AWAITING_APPROVAL is triggered by PermissionGate (CAP-07) when safety_mode
  is `ask` and the tool is marked unsafe.
- HOOK_RUNNING is triggered when hooks are registered for a tool or LLM call.
  Hooks can allow, deny, or modify the execution.
- ROUTING is triggered when ModelRouter resolves which model/provider to use.
- SERVING is triggered in HTTP server mode when a client request is processed.
