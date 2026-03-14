from __future__ import annotations

from collections.abc import Callable
from typing import Any, Dict


Tool = Callable[..., Any]
ToolDecorator = Callable[[Tool], Tool]
AgentRegistry = Dict[str, Tool]


TOOL_REGISTRY: Dict[str, AgentRegistry] = {}


def register_tool(agent_name: str, tool_name: str) -> ToolDecorator:
    """Register a callable under an agent so it can be looked up later."""

    def decorator(func: Tool) -> Tool:
        agent_tools = TOOL_REGISTRY.setdefault(agent_name, {})
        if tool_name in agent_tools:
            raise ValueError(
                f"tool '{tool_name}' already registered for agent '{agent_name}'"
            )
        agent_tools[tool_name] = func
        return func

    return decorator


def get_tools_for_agent(agent_name: str) -> AgentRegistry:
    """Return a shallow copy of the tools available to <agent_name>."""
    return dict(TOOL_REGISTRY.get(agent_name, {}))


def get_tool(agent_name: str, tool_name: str) -> Tool:
    """Return a single tool registered under <agent_name>.<tool_name>."""
    tools = get_tools_for_agent(agent_name)
    if tool_name not in tools:
        raise KeyError(f"{tool_name} is not registered for {agent_name}")
    return tools[tool_name]
