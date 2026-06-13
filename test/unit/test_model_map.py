"""Unit tests for model mapping (capability B14)."""

from nasim.bridge.translator.model_map import map_model

_DEFAULT = "qwen2.5-coder:14b"
_FAST = "qwen2.5-coder:7b"


def test_b14_opus_maps_to_default():
    """opus/sonnet/fable/unknown route to the default model."""
    assert map_model("opus", _DEFAULT, _FAST) == _DEFAULT
    assert map_model("claude-sonnet-4-6", _DEFAULT, _FAST) == _DEFAULT
    assert map_model("fable", _DEFAULT, _FAST) == _DEFAULT
    assert map_model("totally-unknown", _DEFAULT, _FAST) == _DEFAULT


def test_b14_haiku_maps_to_fast():
    """Any name containing 'haiku' routes to the fast model."""
    assert map_model("haiku", _DEFAULT, _FAST) == _FAST
    assert map_model("claude-haiku-4-5-20251001", _DEFAULT, _FAST) == _FAST
    assert map_model("HAIKU", _DEFAULT, _FAST) == _FAST


def test_b14_colon_tag_passthrough():
    """A name already carrying an Ollama tag (':') passes through unchanged."""
    assert map_model("qwen2.5-coder:7b", _DEFAULT, _FAST) == "qwen2.5-coder:7b"
    assert map_model("llama3.1:70b", _DEFAULT, _FAST) == "llama3.1:70b"


def test_b14_empty_falls_back_to_default():
    """An empty/missing model name falls back to the default."""
    assert map_model("", _DEFAULT, _FAST) == _DEFAULT
