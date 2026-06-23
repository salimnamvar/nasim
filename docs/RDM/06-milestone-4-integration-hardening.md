# 06 — Milestone 4: Integration & Hardening

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [05-milestone-3-CLI-session.md](05-milestone-3-CLI-session.md)

End-to-end integration testing, error handling hardening, edge cases, and performance.

---

## Scope

- Full integration test suite (user input → agent → provider → tools → response)
- Error handling: provider failures, tool timeouts, malformed LLM responses
- Edge cases: empty context, max iterations, concurrent tool calls
- Performance: context compaction efficiency, large session files
- Security: tool permission enforcement, path traversal prevention

## Deliverables

| # | Deliverable | Notes |
| - | --- | --- |
| 1 | Integration test suite | Full agent loop tests |
| 2 | Error handling hardening | Provider timeout, malformed response, tool failure |
| 3 | Edge case tests | Empty context, max iterations, large sessions |
| 4 | Security audit | Permission bypass attempts, path traversal |

## Acceptance Criteria

- All integration tests pass
- Provider timeout gracefully returns Error event
- Malformed LLM response handled without crash
- Tool timeout returns ToolResult with error
- Permission gate cannot be bypassed in ask mode
- Path traversal in file tools returns error
