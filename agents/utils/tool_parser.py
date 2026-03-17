from __future__ import annotations

from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any, get_args, get_origin


def _json_type_for_annotation(annotation: Any) -> str:
    origin = get_origin(annotation)
    if origin is not None:
        if origin in (list, tuple, set):
            return "array"
        if origin is dict:
            return "object"

        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        if args:
            return _json_type_for_annotation(args[0])

    if annotation is int:
        return "integer"
    if annotation is float:
        return "number"
    if annotation is bool:
        return "boolean"
    if annotation in (list, tuple, set):
        return "array"
    if annotation is dict:
        return "object"
    return "string"


def _build_parameters_schema(tool: Callable[..., Any]) -> dict[str, Any]:
    sig = signature(tool)
    properties: dict[str, dict[str, str]] = {}
    required: list[str] = []

    for param in sig.parameters.values():
        if param.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
            continue

        properties[param.name] = {"type": _json_type_for_annotation(param.annotation)}
        if param.default is Parameter.empty:
            required.append(param.name)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required

    return schema


def parse(tool_item: tuple[str, Callable[..., Any]]) -> dict[str, Any]:
    """Parse a single registered tool entry into Ollama's tool definition."""
    name, tool = tool_item
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": tool.__doc__ or "agent helper",
            "parameters": _build_parameters_schema(tool),
        },
    }
