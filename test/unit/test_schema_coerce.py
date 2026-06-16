"""Unit tests for schema coercion (capability B15) — the 'Invalid tool parameters' fix.

Each test maps to a behaviour the strict client-side validator requires, and to
the conservatism guarantees in ``.claude/rules/anti-patterns.md`` (AP-02).
"""

from nasim.bridge.translator.schema_coerce import coerce_arguments


def test_b15_coerces_string_to_integer():
    """A stringified integer is coerced to int when the schema says integer."""
    schema = {"properties": {"limit": {"type": "integer"}}}
    assert coerce_arguments({"limit": "5"}, schema) == {"limit": 5}


def test_b15_coerces_string_to_boolean():
    """A stringified boolean is coerced to bool when the schema says boolean."""
    schema = {"properties": {"force": {"type": "boolean"}}}
    assert coerce_arguments({"force": "true"}, schema) == {"force": True}
    assert coerce_arguments({"force": "false"}, schema) == {"force": False}


def test_b15_coerces_int_to_string():
    """A number is stringified when the schema says string."""
    schema = {"properties": {"name": {"type": "string"}}}
    assert coerce_arguments({"name": 42}, schema) == {"name": "42"}


def test_b15_parses_json_string_arguments():
    """An ``arguments`` value that arrived as a JSON string is parsed first."""
    schema = {"properties": {"a": {"type": "integer"}}}
    assert coerce_arguments('{"a": "7"}', schema) == {"a": 7}


def test_b15_parses_json_string_into_array_field():
    """A JSON-string field is parsed into an array when the schema says array."""
    schema = {"properties": {"items": {"type": "array"}}}
    assert coerce_arguments({"items": "[1, 2, 3]"}, schema) == {"items": [1, 2, 3]}


def test_b15_drops_unknown_when_additional_properties_false():
    """Unknown properties are dropped only when additionalProperties is False."""
    schema = {"properties": {"a": {"type": "string"}}, "additionalProperties": False}
    assert coerce_arguments({"a": "x", "junk": 1}, schema) == {"a": "x"}


def test_b15_keeps_unknown_when_additional_properties_allowed():
    """Unknown properties are kept when the schema allows extras (default)."""
    schema = {"properties": {"a": {"type": "string"}}}
    assert coerce_arguments({"a": "x", "extra": 1}, schema) == {"a": "x", "extra": 1}


def test_b15_fills_missing_required_with_type_zero():
    """Missing required fields are filled with type-zero defaults (AP-02)."""
    schema = {
        "properties": {"path": {"type": "string"}, "count": {"type": "integer"}},
        "required": ["path", "count"],
    }
    assert coerce_arguments({}, schema) == {"path": "", "count": 0}


def test_b15_never_overrides_a_value_the_model_provided():
    """A provided required field is never replaced by a type-zero default (AP-02)."""
    schema = {"properties": {"path": {"type": "string"}}, "required": ["path"]}
    assert coerce_arguments({"path": "/real/file.py"}, schema) == {"path": "/real/file.py"}


def test_b15_handles_nullable_type_list():
    """A ``["string", "null"]`` type uses the first non-null type."""
    schema = {"properties": {"x": {"type": ["integer", "null"]}}}
    assert coerce_arguments({"x": "9"}, schema) == {"x": 9}


def test_b15_unparseable_json_string_preserved_as_raw():
    """Arguments that are an unparseable string are preserved under ``_raw``."""
    assert coerce_arguments("not json", {}) == {"_raw": "not json"}


def test_b15_fill_required_can_be_disabled():
    """Required-fill is skippable for callers that want it off."""
    schema = {"properties": {"a": {"type": "string"}}, "required": ["a"]}
    assert coerce_arguments({}, schema, a_fill_required=False) == {}


def test_b15_non_numeric_string_left_unchanged_for_integer():
    """A non-numeric string for an integer field is left as-is (no lossy guess)."""
    schema = {"properties": {"n": {"type": "integer"}}}
    assert coerce_arguments({"n": "abc"}, schema) == {"n": "abc"}
