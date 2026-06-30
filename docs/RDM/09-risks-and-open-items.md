# 09 — Risks & Open Items

Back to [docs/rdm/](./README.md).

**Status:** Active · **Scope:** Known risks and deferred decisions.

---

## Risks

| # | Risk | Impact | Mitigation |
| - | --- | --- | --- |
| R1 | LLM provider API changes | Provider layer breaks | Protocol abstraction isolates changes; pin versions |
| R2 | MCP protocol evolution | MCPRepository breaks | MCP SDK handles versioning; adapter pattern |
| R3 | Context compaction quality | Poor summaries degrade agent | Secondary LLM call with detailed prompt; fallback to truncation |
| R4 | Large session files | Performance degradation | Lazy loading, streaming read, max session size |
| R5 | Tool permission bypass | Security vulnerability | SafetyService tests with bypass attempts |

## Open Items

| # | Item | Status | Target |
| - | --- | --- | --- |
| O1 | OpenAI provider implementation | Deferred | Phase 2 |
| O2 | Anthropic provider implementation | Deferred | Phase 2 |
| O3 | Web server mode (async) | Deferred | Phase 2 |
| O4 | Session search/compaction UI | Deferred | Phase 2 |
| O5 | Tool usage analytics | Deferred | Phase 2 |
