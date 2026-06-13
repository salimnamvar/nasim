"""Translator — pure Anthropic Messages API <-> Ollama chat API.

Every function here is dict-in / dict-out with **no I/O** (no sockets, no files,
no environment reads), so the hard part of the bridge is exhaustively
unit-testable without a network or a model. The server (:mod:`nasim.bridge.server`)
is the only place that performs I/O; it wires these functions to HTTP.

- Anthropic Messages API: https://docs.anthropic.com/en/api/messages
- Ollama chat API: https://github.com/ollama/ollama/blob/main/docs/api.md

Public API:
    anthropic_to_ollama: Request translation.
    ollama_to_anthropic: Non-streaming response translation.
    stream_ollama_to_anthropic: Streaming (SSE) response translation.
    estimate_tokens: Heuristic token estimate for count_tokens.
    map_model: Resolve a requested model name to an Ollama tag.
    coerce_arguments: Coerce a tool call's arguments to its schema.
    salvage_tool_calls: Recover text-encoded tool calls.
    sse: Format a single server-sent event.
"""

from nasim.bridge.translator.model_map import map_model
from nasim.bridge.translator.request import anthropic_to_ollama
from nasim.bridge.translator.response import ollama_to_anthropic
from nasim.bridge.translator.schema_coerce import coerce_arguments
from nasim.bridge.translator.sse import sse
from nasim.bridge.translator.streaming import stream_ollama_to_anthropic
from nasim.bridge.translator.tokens import estimate_tokens
from nasim.bridge.translator.tool_salvage import salvage_tool_calls

__all__ = [
    "anthropic_to_ollama",
    "ollama_to_anthropic",
    "stream_ollama_to_anthropic",
    "estimate_tokens",
    "map_model",
    "coerce_arguments",
    "salvage_tool_calls",
    "sse",
]
