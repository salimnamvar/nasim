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

## Transitions

| Source | Target | Trigger |
|--------|--------|---------|
| [*] | IDLE | Startup |
| IDLE | LISTENING | User input received |
| LISTENING | THINKING | Input parsed, messages built |
| THINKING | RESPONDING | LLM returns text (no tool calls) |
| THINKING | TOOL_EXEC | LLM returns tool calls |
| THINKING | COMPACTING | token_count > context_budget |
| TOOL_EXEC | THINKING | Tool result appended to messages |
| TOOL_EXEC | AWAITING_APPROVAL | safety_mode=ask AND tool.unsafe |
| AWAITING_APPROVAL | TOOL_EXEC | User approves (y) |
| AWAITING_APPROVAL | IDLE | User rejects (N) |
| COMPACTING | THINKING | Compaction complete, messages shortened |
| RESPONDING | IDLE | Response complete |
| THINKING | ERROR | LLM call fails |
| TOOL_EXEC | ERROR | Tool execution fails |
| ERROR | IDLE | Error displayed |
| IDLE | [*] | /quit or EOF |

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
