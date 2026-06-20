# 01 — Project Skeleton & Layer Rules

Back to [docs/rdm/](./README.md).

**Status:** Active · **Prerequisite:** [00-principles-and-stack.md](00-principles-and-stack.md)

Enforces layered architecture + exact C4 class names. Package names mirror the design
chain layers. Every method/test cites UC+SQ. No orphan code.

---

## Directory Layout (src layout)

```
src/nasim/
├── __init__.py
├── __main__.py                 # python -m nasim entry
├── cli/                        # CLI LAYER — user interaction
│   ├── __init__.py
│   ├── args.py                 # ArgParser (C4: CLI)
│   ├── repl.py                 # REPLSession (C4: CLI)
│   ├── renderer.py             # Renderer (C4: CLI) — all terminal output
│   └── commands.py             # SlashCommandHandler (C4: CLI)
├── agent/                      # AGENT LAYER — core orchestration
│   ├── __init__.py
│   ├── orchestrator.py         # AgentOrchestrator (C4: Agent) — drives LLM/tool loop
│   ├── history.py              # ConversationHistory (C4: Agent) — messages + token tracking
│   ├── compactor.py            # ContextCompactor (C4: Agent) — summarization
│   ├── permission.py           # PermissionGate (C4: Agent) — safety checks
│   ├── plan.py                 # PlanSession (C4: Agent) — plan mode queue
│   └── events.py               # AgentEvent hierarchy — TextChunk, ToolStart, ToolResult, Error, Done
├── provider/                   # PROVIDER LAYER — LLM abstraction
│   ├── __init__.py
│   ├── base.py                 # Provider (Protocol), ProviderFactory, LLMResponse, ToolCall
│   ├── ollama.py               # OllamaProvider
│   ├── openai.py               # OpenAIProvider (Phase 2)
│   └── anthropic.py            # AnthropicProvider (Phase 2)
├── tools/                      # TOOL LAYER — all tool implementations
│   ├── __init__.py
│   ├── base.py                 # Tool (ABC), ToolRegistry, ToolResult
│   ├── file.py                 # ReadFileTool, WriteFileTool, EditFileTool
│   ├── search.py               # GrepTool, GlobTool, FindFileTool
│   ├── shell.py                # ShellTool
│   ├── directory.py            # DirTool
│   ├── web.py                  # WebFetchTool, WebSearchTool
│   ├── git.py                  # GitTool
│   └── mcp.py                  # MCPToolAdapter
├── config/                     # CONFIG LAYER — cross-cutting
│   ├── __init__.py
│   ├── schema.py               # Config (dataclass) — typed configuration
│   └── loader.py               # ConfigLoader — layered YAML + env + CLI
├── session/                    # SESSION LAYER — cross-cutting
│   ├── __init__.py
│   ├── model.py                # Session (dataclass) — session data
│   └── store.py                # SessionStore — JSON Lines persistence
└── domain/                     # DOMAIN — shared types
    ├── __init__.py
    └── exceptions.py           # Domain exceptions (raised in agent/tools, caught in CLI)

tests/
├── unit/
│   ├── agent/                  # AgentOrchestrator, ConversationHistory, etc.
│   ├── provider/               # Provider mock tests
│   ├── tools/                  # Individual tool tests
│   ├── config/                 # Config loading tests
│   └── session/                # Session persistence tests
├── integration/                # Cross-layer integration tests
│   ├── agent_provider/         # Agent + provider interaction
│   └── session_persistence/    # Full save/load cycle
└── cli/                        # CLI integration tests
```

---

## Layer Contract (do / don't)

| Layer | Do | Don't |
| --- | --- | --- |
| `cli/` | Parse input → delegate to AgentOrchestrator → render AgentEvents | Business logic, direct tool calls, provider calls |
| `agent/` | Orchestrate LLM/tool loop, emit AgentEvents, manage permissions | Import CLI/rendering, print(), sys.exit(), direct file I/O |
| `provider/` | Implement Provider Protocol, handle HTTP/JSON, return LLMResponse | Import agent or CLI, manage state beyond single call |
| `tools/` | Implement Tool ABC, return ToolResult, declare safe/unsafe | Import agent or CLI, manage cross-tool state |
| `config/` | Load/merge/validate config, return typed Config | Import agent, CLI, or tools |
| `session/` | Persist/load sessions, return Session objects | Import agent, CLI, or config |
| `domain/` | Shared types and exceptions | Framework imports, persistence logic |

**Dependency direction:** `cli/ → agent/ → {provider/, tools/, config/, session/}`. No circular.
Agent layer never imports from CLI. Tools never import from agent.

---

## CI Verification (before every PR)

```bash
# Type checking
mypy src/nasim/

# Linting
ruff check src/nasim/

# Formatting
black --check src/nasim/

# Tests
pytest tests/ -v

# Layer boundary check (no agent→cli imports)
grep -r "from nasim.cli" src/nasim/agent/ && echo "FAIL: agent imports CLI" || echo "OK"
grep -r "from nasim.agent" src/nasim/cli/ && echo "FAIL: CLI imports agent internals" || echo "OK"
```
