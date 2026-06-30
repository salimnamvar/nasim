# 03 — Milestone 1: Provider & Tools

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [02-milestone-0-bootstrap.md](02-milestone-0-bootstrap.md)

Implement the provider abstraction and all tool implementations. These are the external-facing capabilities the agent orchestrates.

---

## Scope

- Provider Protocol + LLMRepository + OllamaProvider
- Tool ABC + ToolService + all tool implementations
- MCPRepository for extension tools

## Deliverables

| # | Deliverable | UC Trace | SQ Trace |
| - | --- | --- | --- |
| 1 | `Provider` Protocol + `LLMRepository` + `LLMResponse` + `ToolCall` | PROVIDER-01, PROVIDER-04 | sq_prv01, sq_prv04 |
| 2 | `OllamaProvider` (chat + stream) | LLM-01, LLM-02 | sq_llm01, sq_llm02 |
| 3 | `Tool` ABC + `ToolService` + `ToolResult` | TOOL-01..12 | sq_tl01..12 |
| 4 | `FileTools` (Read, Write, Edit) | TOOL-01, TOOL-02, TOOL-03 | sq_tl01, sq_tl02, sq_tl03 |
| 5 | `SearchTools` (Grep, Glob, Find) + `DirTool` | TOOL-04, TOOL-06, TOOL-07, TOOL-08 | sq_tl04, sq_tl06, sq_tl07, sq_tl08 |
| 6 | `ShellTool` + `GitTool` | TOOL-05, TOOL-11 | sq_tl05, sq_tl11 |
| 7 | `WebTools` (Fetch, Search) | TOOL-09, TOOL-10 | sq_tl09, sq_tl10 |
| 8 | `MCPRepository` | TOOL-12 | sq_tl12 |

## Acceptance Criteria

- Provider chat/stream return `LLMResponse` with text and/or tool_calls
- All tools return structured `ToolResult` (success, content, error)
- ToolService supports dynamic registration (for MCP)
- MCPRepository wraps MCP server tools into nasim Tool format
- No agentcli imports in provider or tool code
- Tests for each provider and tool
