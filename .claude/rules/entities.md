# nasim — Canonical Entity Registry

Every component, class, and actor name used in any design diagram must appear here
before it is added to any C4, UC, SM, SQ, or CL artifact.

---

## Actors

| Name | Type | Description |
|------|------|-------------|
| Developer | Person | Terminal user interacting with nasim |

## External Systems

| Name | Type | Description |
|------|------|-------------|
| OllamaServer | System_Ext | LLM inference API on remote host |
| HostFilesystem | System_Ext | Project files and directories |
| HostShell | System_Ext | Shell for executing commands |

## C4 Components

| Name | Python Module | File | Boundary | Layer |
|------|--------------|------|----------|-------|
| REPL | `nasim.cli:repl` | `cli.py` | CLI | CLI |
| ArgParser | `nasim.cli:parse_args` | `cli.py` | CLI | CLI |
| Agent | `nasim.agent:Agent` | `agent.py` | Agent Core | Agent |
| ContextManager | `nasim.agent:Agent` (messages attr) | `agent.py` | Agent Core | Agent |
| OllamaClient | `nasim.llm:OllamaClient` | `llm.py` | LLM | LLM |
| ToolRegistry | `nasim.tools:TOOL_REGISTRY` | `tools.py` | Tool | Tool |
| ToolExecutor | `nasim.tools:execute_tool` | `tools.py` | Tool | Tool |
| FileTools | `nasim.tools:read_file, write_file, edit_file` | `tools.py` | Tool | Tool |
| ShellTool | `nasim.tools:shell_exec` | `tools.py` | Tool | Tool |
| DirTool | `nasim.tools:list_dir` | `tools.py` | Tool | Tool |

## Domain Classes (CL)

| Name | Python Type | Description |
|------|-------------|-------------|
| LLMResponse | `nasim.llm:LLMResponse` (dataclass) | Parsed LLM response |
| ToolCall | `nasim.llm:ToolCall` (dataclass) | Parsed tool call from LLM |
| ToolDef | `nasim.tools:TOOL_REGISTRY entry` (dict) | Registered tool definition |

## UC Groups

| Group Code | Full Name | Scope |
|-----------|-----------|-------|
| CLI | CLI Interaction | User I/O, slash commands, streaming |
| AGT | Agent Core | Agentic loop, tool dispatch, conversation |
| LLM | LLM Layer | Ollama API communication |
| TL | Tool Layer | File, shell, directory tools |

## Verb Policy (Project Extension)

The global `uc.md` verb list targets registry/management domains. For nasim
(a CLI code agent), the following verbs are added to the allowed set:

| Verb | Use |
|------|-----|
| PROCESS | Receive and parse user input |
| DISPATCH | Forward a tool call to execution |
| STREAM | Deliver tokens incrementally |
| DISPLAY | Present output to terminal |
| INVOKE | Trigger a tool call from LLM |
| CALL | Make an LLM API request |
| MANAGE | Maintain conversation state |
| PARSE | Transform raw data into structured form |
| REGISTER | Add a tool to the registry |

Banned verbs (`EXECUTE`, `RUN`, `TRIGGER`) are retained for non-tool operations.
`EXECUTE` is reserved for shell command execution only (TL-05).
