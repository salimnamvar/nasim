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

## Transitions

| Source | Target | Trigger |
|--------|--------|---------|
| [*] | IDLE | Startup |
| IDLE | LISTENING | User input received |
| LISTENING | THINKING | Input parsed, messages built |
| THINKING | RESPONDING | LLM returns text (no tool calls) |
| THINKING | TOOL_EXEC | LLM returns tool calls |
| TOOL_EXEC | THINKING | Tool result appended to messages |
| RESPONDING | IDLE | Response complete |
| THINKING | ERROR | LLM call fails |
| TOOL_EXEC | ERROR | Tool execution fails |
| ERROR | IDLE | Error displayed |
| IDLE | [*] | /quit or EOF |
