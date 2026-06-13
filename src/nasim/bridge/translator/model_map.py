"""Model mapping — resolve a requested model name to an Ollama tag.

Functions:
    map_model: Map a Claude/Naseem-style model name to an Ollama model tag.
"""


def map_model(a_model: str, a_default: str, a_fast: str) -> str:
    """Map a requested model name to an Ollama model tag.

    Rules, in order:
        1. A name containing ``:`` is already an Ollama tag — pass it through.
           This enables hot-swap: ``/model qwen2.5-coder:7b`` inside the CLI.
        2. A name containing ``haiku`` (any case) maps to the fast model.
        3. Everything else (sonnet/opus/fable/unknown) maps to the default model.

    Args:
        a_model (str): Model name as sent by the client.
        a_default (str): Default Ollama tag (opus/sonnet/fable/unknown route here).
        a_fast (str): Fast Ollama tag (haiku routes here).

    Returns:
        str: Resolved Ollama model tag.
    """
    result = a_default
    if a_model and ":" in a_model:
        result = a_model
    elif a_model and "haiku" in a_model.lower():
        result = a_fast
    return result
