from pathlib import Path

from .registry import register_tool


INTERFACER_TOOLS_PATH = Path(__file__).with_name("interfacer_tools.py")


@register_tool("coder", "read_interfacer_tools")
def read_interfacer_tools() -> str:
    """Return the text currently stored in interfacer_tools.py."""
    return INTERFACER_TOOLS_PATH.read_text(encoding="utf-8")


@register_tool("coder", "write_interfacer_tools")
def write_interfacer_tools(content: str) -> None:
    """Overwrite interfacer_tools.py with new content."""
    INTERFACER_TOOLS_PATH.write_text(content, encoding="utf-8")


@register_tool("coder", "replace_in_interfacer_tools")
def replace_in_interfacer_tools(target: str, replacement: str) -> str:
    """Replace the first occurrence of <target> with <replacement> and persist the change."""
    current = read_interfacer_tools()
    if target not in current:
        raise ValueError("target text not found in interfacer_tools.py")
    updated = current.replace(target, replacement, 1)
    write_interfacer_tools(updated)
    return updated


@register_tool("coder", "append_to_interfacer_tools")
def append_to_interfacer_tools(appendix: str) -> str:
    """Append <appendix> to the end of the file and return the new content."""
    current = read_interfacer_tools()
    updated = current + appendix
    write_interfacer_tools(updated)
    return updated
