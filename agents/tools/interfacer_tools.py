from ..coder import Coder
from .registry import register_tool

@register_tool("interfacer", "assign-to-coder")
def assign(messages: list[dict]):
    """Forward the chat history to the coder agent."""
    coder = Coder()
    return coder.generate(messages)
