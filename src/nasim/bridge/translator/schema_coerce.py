"""Schema coercion — make a tool call pass the client's strict validation.

Claude Code validates every ``tool_use.input`` against the tool's JSON schema
(``input_schema``) and rejects the call with "Invalid tool parameters" when a
field has the wrong type, an unexpected property is present (and the schema
forbids extras), or a required field is missing. Smaller models trip all three
under load. :func:`coerce_arguments` repairs these **conservatively**:

- it never changes a value the model supplied with the already-correct type;
- it never invents a value for a field the model actually provided;
- it only fills *missing* required fields, with type-zero defaults (models omit
  trivial annotation fields, not the semantically critical ones).

Functions:
    coerce_arguments: Coerce a tool call's arguments to its input schema.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

_ZERO: Dict[str, Any] = {
    "string": "",
    "integer": 0,
    "number": 0.0,
    "boolean": False,
    "array": [],
    "object": {},
}
_TRUE = {"true", "1", "yes", "y", "on"}
_FALSE = {"false", "0", "no", "n", "off"}


def _primary_type(a_prop: Any) -> Optional[str]:
    """Return the primary JSON type of a schema property.

    Handles a ``type`` that is a string or a list (e.g. ``["string","null"]``)
    by returning the first non-null type.

    Args:
        a_prop (Any): A JSON-schema property object.

    Returns:
        Optional[str]: The primary type name, or None if unspecified.
    """
    result: Optional[str] = None
    if isinstance(a_prop, dict):
        ptype = a_prop.get("type")
        if isinstance(ptype, str):
            result = ptype
        elif isinstance(ptype, list):
            non_null = [t for t in ptype if t != "null"]
            result = non_null[0] if non_null else None
    return result


def _coerce_value(a_value: Any, a_prop: Any) -> Any:
    """Coerce one value toward a schema property's type, conservatively.

    Only obvious, lossless conversions are applied (``"5"`` -> ``5``,
    ``"true"`` -> ``True``, a JSON string -> the parsed array/object). When no
    safe conversion exists the original value is returned unchanged.

    Args:
        a_value (Any): The value the model supplied.
        a_prop (Any): The JSON-schema property describing the field.

    Returns:
        Any: The coerced value, or the original when no safe coercion applies.
    """
    result = a_value
    target = _primary_type(a_prop)
    if a_value is None or target is None:
        result = a_value
    elif target == "string":
        if isinstance(a_value, bool):
            result = "true" if a_value else "false"
        elif isinstance(a_value, (int, float)):
            result = str(a_value)
        else:
            result = a_value
    elif target == "integer":
        if isinstance(a_value, bool):
            result = a_value
        elif isinstance(a_value, int):
            result = a_value
        elif isinstance(a_value, float) and a_value.is_integer():
            result = int(a_value)
        elif isinstance(a_value, str) and a_value.strip().lstrip("+-").isdigit():
            result = int(a_value.strip())
        else:
            result = a_value
    elif target == "number":
        if isinstance(a_value, bool):
            result = a_value
        elif isinstance(a_value, (int, float)):
            result = float(a_value)
        elif isinstance(a_value, str):
            try:
                result = float(a_value.strip())
            except ValueError:
                result = a_value
        else:
            result = a_value
    elif target == "boolean":
        if isinstance(a_value, bool):
            result = a_value
        elif isinstance(a_value, int):
            result = bool(a_value)
        elif isinstance(a_value, str) and a_value.strip().lower() in _TRUE:
            result = True
        elif isinstance(a_value, str) and a_value.strip().lower() in _FALSE:
            result = False
        else:
            result = a_value
    elif target in ("array", "object"):
        result = _coerce_json(a_value, target)
    return result


def _coerce_json(a_value: Any, a_target: str) -> Any:
    """Parse a JSON-string value into an array/object when it matches the target.

    Args:
        a_value (Any): The value (possibly a JSON string).
        a_target (str): ``"array"`` or ``"object"``.

    Returns:
        Any: Parsed list/dict when the string parses to the target kind; else
        the original value.
    """
    result = a_value
    want_list = a_target == "array"
    if isinstance(a_value, list) and want_list:
        result = a_value
    elif isinstance(a_value, dict) and not want_list:
        result = a_value
    elif isinstance(a_value, str):
        try:
            parsed = json.loads(a_value)
        except (json.JSONDecodeError, ValueError):
            parsed = None
        if (want_list and isinstance(parsed, list)) or (not want_list and isinstance(parsed, dict)):
            result = parsed
    return result


def coerce_arguments(a_arguments: Any, a_schema: Any, a_fill_required: bool = True) -> Dict[str, Any]:
    """Coerce a tool call's arguments to its JSON ``input_schema``.

    Pipeline: parse a JSON-string ``arguments``; coerce each present field to
    its schema type; drop unknown properties when ``additionalProperties`` is
    ``False``; optionally fill missing required fields with type-zero defaults.

    Args:
        a_arguments (Any): The raw arguments (dict, JSON string, or other).
        a_schema (Any): The tool's ``input_schema`` (a JSON-schema object).
        a_fill_required (bool, optional): Fill missing required fields with
            type-zero defaults so client validation passes. Defaults to True.

    Returns:
        Dict[str, Any]: The coerced argument object. A value that cannot be a
        dict is preserved under ``{"_raw": value}`` so nothing is silently lost.
    """
    result: Dict[str, Any] = {}
    args = a_arguments
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, ValueError):
            result = {"_raw": a_arguments}
            args = None

    if isinstance(args, dict):
        schema = a_schema if isinstance(a_schema, dict) else {}
        props: Dict[str, Any] = schema.get("properties", {}) or {}
        additional = schema.get("additionalProperties", True)
        required: List[str] = schema.get("required", []) or []
        for key, value in args.items():
            if key in props:
                result[key] = _coerce_value(value, props[key])
            elif additional is not False:
                result[key] = value
            # else: drop a property the schema explicitly forbids
        if a_fill_required:
            for field in required:
                if field not in result:
                    ptype = _primary_type(props.get(field, {})) or "string"
                    result[field] = _ZERO.get(ptype, "")
    elif args is not None:
        result = {"_raw": args}

    return result
