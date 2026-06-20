# nasim — CL Inventory

| Diagram | Scope | Description |
|---------|-------|-------------|
| cl_domain_model | Runtime | Core runtime classes: OllamaClient, LLMResponse, ToolCall, Agent, ToolRegistry |

## Class List

| Class | Module | Type | Description |
|-------|--------|------|-------------|
| OllamaClient | `nasim/llm.py` | dataclass-like | Ollama API client |
| LLMResponse | `nasim/llm.py` | dataclass | Parsed LLM response |
| ToolCall | `nasim/llm.py` | dataclass | Parsed tool call |
| Agent | `nasim/agent.py` | class | Core agentic orchestrator |
| TOOL_REGISTRY | `nasim/tools.py` | dict | Tool registration store |

Note: nasim is a small CLI tool. The CL diagram covers runtime structure
rather than a pure domain model (no business entities). This is a deliberate
deviation from the OVMS-style domain CL — documented in entities.md.
