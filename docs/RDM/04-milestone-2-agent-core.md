# 04 — Milestone 2: Agent Core

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [03-milestone-1-provider-tools.md](03-milestone-1-provider-tools.md)

Implement the agent orchestrator, conversation history, context compaction, permission gate, and plan session. This is the core agentic loop.

---

## Scope

- TaskService (core loop: LLM call → tool dispatch → repeat)
- ConversationHistory (messages + token tracking)
- ContextService (summarize old exchanges when budget exceeded)
- SafetyService (per-tool safety: ask/auto/off)
- TaskService (queue tool calls in plan mode)
- AgentEvent hierarchy (TextChunk, ToolStart, ToolResult, Error, Done)

## Deliverables

| # | Deliverable | UC Trace | SQ Trace |
| - | --- | --- | --- |
| 1 | `TaskService` core loop | TASKSERVICE-01 | sq_agt01 |
| 2 | Tool dispatch with permission gate | TASKSERVICE-02, TASKSERVICE-05 | sq_agt02, sq_agt05 |
| 3 | `ConversationHistory` + token tracking | TASKSERVICE-03, TASKSERVICE-04, CONTEXTSERVICE-01 | sq_agt03, sq_agt04, sq_ctx01 |
| 4 | `ContextService` | TASKSERVICE-06, CONTEXTSERVICE-02, CONTEXTSERVICE-03 | sq_agt06, sq_ctx02, sq_ctx03 |
| 5 | `SafetyService` | SAFETYSERVICE-01, SAFETYSERVICE-02, SAFETYSERVICE-03 | sq_saf01, sq_saf02, sq_saf03 |
| 6 | `TaskService` | TASKSERVICE-07, TASKSERVICE-08 | sq_agt07, sq_agt08 |
| 7 | `AgentEvent` hierarchy | — | — |

## Acceptance Criteria

- TaskService yields `AgentEvent` objects (no print())
- LLM returns text → Done event; LLM returns tool_calls → dispatch loop → recurse
- SafetyService blocks unsafe tools in `ask` mode, prompts user
- ContextService triggers when token_count > budget, summarizes oldest exchanges
- TaskService queues tool calls, drains on /approve
- State machine: IDLE → LISTENING → THINKING → [TOOL_EXEC]* → RESPONDING → IDLE
- Tests for orchestrator loop, permission gate, compaction, plan mode
