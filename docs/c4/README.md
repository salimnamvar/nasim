# nasim — Component Inventory

| Component | Layer | File | Responsibility |
|-----------|-------|------|----------------|
| REPL | CLI | `nasim/cli.py` | Interactive input loop, slash commands, streaming display |
| ArgParser | CLI | `nasim/cli.py` | CLI argument parsing (--model, --server, -c, --no-stream) |
| AgentLoop | Agent Core | `nasim/agent.py` | Orchestrates LLM + tool calls, enforces max_iterations |
| ContextManager | Agent Core | `nasim/agent.py` | Message list management, system prompt, history reset |
| OllamaClient | LLM | `nasim/llm.py` | HTTP client for Ollama /api/chat (sync + streaming) |
| ResponseParser | LLM | `nasim/llm.py` | Parses JSON response into LLMResponse / ToolCall |
| ToolRegistry | Tool | `nasim/tools.py` | Decorator registration, OpenAI-compatible definitions |
| ToolExecutor | Tool | `nasim/tools.py` | Dispatch, error handling, result formatting |
| FileTools | Tool | `nasim/tools.py` | read_file, write_file, edit_file |
| ShellTool | Tool | `nasim/tools.py` | shell_exec with timeout |
| DirTool | Tool | `nasim/tools.py` | list_dir |

## Actors

| Actor | Description |
|-------|-------------|
| Developer | Terminal user interacting with nasim |

## External Systems

| System | Protocol | Purpose |
|--------|----------|---------|
| Ollama Server | HTTP/JSON | LLM inference (qwen2.5-coder:14b on black) |
| Host Filesystem | path I/O | Read/write project files |
| Host Shell | subprocess | Execute shell commands |
