# nasim — Canonical Entity Registry

**Date:** 2026-06-20
**Purpose:** Single source of truth for all component names across C4, UC, SM, SQ, CL, CT, and Code layers.

## Provider Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| Provider | `nasim/provider/base.py` | Provider (Protocol) | Design |
| OllamaProvider | `nasim/provider/ollama.py` | OllamaProvider | Design |
| ProviderFactory | `nasim/provider/factory.py` | ProviderFactory | Design |
| ModelRouter | `nasim/provider/router.py` | ModelRouter | Phase 2 |
| LLMResponse | `nasim/provider/models.py` | LLMResponse | Design |
| ToolCall | `nasim/provider/models.py` | ToolCall | Design |

## Agent Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| AgentOrchestrator | `nasim/agent/orchestrator.py` | AgentOrchestrator | Design |
| ConversationHistory | `nasim/agent/history.py` | ConversationHistory | Design |
| ContextCompactor | `nasim/agent/compactor.py` | ContextCompactor | Design |
| PermissionGate | `nasim/agent/permission.py` | PermissionGate | Design |
| PlanSession | `nasim/agent/plan.py` | PlanSession | Phase 2 |
| AgentEvent | `nasim/agent/events.py` | AgentEvent (abstract) | Design |
| TextChunk | `nasim/agent/events.py` | TextChunk | Design |
| ToolStart | `nasim/agent/events.py` | ToolStart | Design |
| ToolResultEvent | `nasim/agent/events.py` | ToolResultEvent | Design |
| Error | `nasim/agent/events.py` | Error | Design |
| Done | `nasim/agent/events.py` | Done | Design |

## Tool Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| Tool | `nasim/tools/base.py` | Tool (abstract) | Design |
| ToolRegistry | `nasim/tools/registry.py` | ToolRegistry | Design |
| ToolResult | `nasim/tools/base.py` | ToolResult | Design |
| ReadFileTool | `nasim/tools/file.py` | ReadFileTool | Design |
| WriteFileTool | `nasim/tools/file.py` | WriteFileTool | Design |
| EditFileTool | `nasim/tools/file.py` | EditFileTool | Design |
| GrepTool | `nasim/tools/search.py` | GrepTool | Phase 2 |
| GlobTool | `nasim/tools/search.py` | GlobTool | Phase 2 |
| FindFileTool | `nasim/tools/search.py` | FindFileTool | Phase 2 |
| ShellTool | `nasim/tools/shell.py` | ShellTool | Design |
| DirTool | `nasim/tools/directory.py` | DirTool | Design |
| WebFetchTool | `nasim/tools/web.py` | WebFetchTool | Phase 2 |
| WebSearchTool | `nasim/tools/web.py` | WebSearchTool | Phase 2 |
| GitTool | `nasim/tools/git.py` | GitTool | Phase 3 |
| MCPToolAdapter | `nasim/tools/mcp.py` | MCPToolAdapter | Phase 3 |

## Config Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| Config | `nasim/config/schema.py` | Config | Design |
| ConfigLoader | `nasim/config/loader.py` | ConfigLoader | Design |

## Session Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| Session | `nasim/session/model.py` | Session | Design |
| SessionStore | `nasim/session/store.py` | SessionStore | Design |

## CLI Layer

| Entity | Python Module | CL Class | Status |
|--------|---------------|----------|--------|
| ArgParser | `nasim/cli/args.py` | ArgParser | Design |
| REPLSession | `nasim/cli/repl.py` | REPLSession | Design |
| Renderer | `nasim/cli/renderer.py` | Renderer | Design |
| SlashCommandHandler | `nasim/cli/commands.py` | SlashCommandHandler | Design |

## Server Layer (Phase 3)

| Entity | Python Module | CL Class | CT/API | Status |
|--------|---------------|----------|--------|--------|
| ServerApp | `nasim/server/app.py` | ServerApp | — | Phase 3 |
| ServerRouter | `nasim/server/router.py` | ServerRouter | Sessions, Messages, Tools, Config | Phase 3 |
| SSEHandler | `nasim/server/sse.py` | SSEHandler | — | Phase 3 |

## UC Group Codes

| Code | Group | Description |
|------|-------|-------------|
| AGT | Agent | Core agent orchestration |
| CLI | CLI | Command-line interface |
| CFG | Config | Configuration management |
| CTX | Context | Context window management |
| HK | Hooks | Pre/post tool/LLM hooks |
| LLM | LLM | LLM provider operations |
| PRV | Provider | Provider abstraction |
| SAF | Safety | Permission and safety checks |
| SRV | Server | HTTP API server |
| SSN | Session | Session persistence |
| TL | Tools | Tool operations |
