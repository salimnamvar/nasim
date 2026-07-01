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
├── CLI/                        # CLI LAYER — user interaction
│   ├── __init__.py
│   ├── args.py                 # ArgParser (C4: CLI)
│   ├── repl.py                 # REPLSession (C4: CLI)
│   ├── renderer.py             # Renderer (C4: CLI) — all terminal output
│   └── commands.py             # SlashCommandHandler (C4: CLI)
├── agent/                      # AGENT LAYER — core orchestration
│   ├── __init__.py
│   ├── orchestrator.py         # Task Service (C4: Task Service) — drives LLM/tool loop
│   ├── history.py              # ConversationHistory (C4: Task Service) — messages + token tracking
│   ├── compactor.py            # Context Service (C4: Task Service) — summarization
│   ├── permission.py           # Safety Service (C4: Task Service) — safety checks
│   ├── plan.py                 # Task Service (C4: Task Service) — plan mode queue
│   └── events.py               # AgentEvent hierarchy — TextChunk, ToolStart, ToolResult, Error, Done
├── provider/                   # PROVIDER LAYER — LLM abstraction
│   ├── __init__.py
│   ├── base.py                 # Provider (Protocol), LLM Repository, LLMResponse, ToolCall
│   ├── ollama.py               # OllamaProvider
│   ├── openai.py               # OpenAIProvider 
│   └── anthropic.py            # AnthropicProvider
├── tools/                      # TOOL LAYER — all tool implementations
│   ├── __init__.py
│   ├── base.py                 # Tool (ABC), Tool Service, ToolResult
│   ├── file.py                 # ReadFileTool, WriteFileTool, EditFileTool
│   ├── search.py               # GrepTool, GlobTool, FindFileTool
│   ├── shell.py                # ShellTool
│   ├── directory.py            # DirTool
│   ├── web.py                  # WebFetchTool, WebSearchTool
│   ├── git.py                  # GitTool
│   └── mcp.py                  # MCP Repository
├── config/                     # CONFIG LAYER — cross-cutting
│   ├── __init__.py
│   ├── schema.py               # Config (dataclass) — typed configuration
│   └── loader.py               # Config Repository — layered YAML + env + CLI
├── session/                    # SESSION LAYER — cross-cutting
│   ├── __init__.py
│   ├── model.py                # Session (dataclass) — session data
│   └── store.py                # Session Repository — JSON Lines persistence
└── domain/                     # DOMAIN — shared types
    ├── __init__.py
    └── exceptions.py           # Domain exceptions (raised in agent/tools, caught in CLI)

tests/
├── unit/
│   ├── agent/                  # Task Service, ConversationHistory, etc.
│   ├── provider/               # Provider mock tests
│   ├── tools/                  # Individual tool tests
│   ├── config/                 # Config loading tests
│   └── session/                # Session persistence tests
├── integration/                # Cross-layer integration tests
│   ├── agent_provider/         # Agent + provider interaction
│   └── session_persistence/    # Full save/load cycle
└── CLI/                        # CLI integration tests
```

---

## Layer Contract (do / don't)

| Layer | Do | Don't |
| --- | --- | --- |
| `CLI/` | Parse input → delegate to Task Service → render AgentEvents | Business logic, direct tool calls, provider calls |
| `agent/` | Orchestrate LLM/tool loop, emit AgentEvents, manage permissions | Import CLI/rendering, print(), sys.exit(), direct file I/O |
| `provider/` | Implement Provider Protocol, handle HTTP/JSON, return LLMResponse | Import agent or CLI, manage state beyond single call |
| `tools/` | Implement Tool ABC, return ToolResult, declare safe/unsafe | Import agent or CLI, manage cross-tool state |
| `config/` | Load/merge/validate config, return typed Config | Import agent, CLI, or tools |
| `session/` | Persist/load sessions, return Session objects | Import agent, CLI, or config |
| `domain/` | Shared types and exceptions | Framework imports, persistence logic |

**Dependency direction:** `CLI/ → agent/ → {provider/, tools/, config/, session/}`. No circular.
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

# Layer boundary check (no agent→CLI imports)
grep -r "from nasim.CLI" src/nasim/agent/ && echo "FAIL: agent imports CLI" || echo "OK"
grep -r "from nasim.agent" src/nasimcli/ && echo "FAIL: CLI imports agent internals" || echo "OK"
```
