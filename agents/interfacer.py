import ollama
from .tools import (
    coder_tools as _coder_tools,
    interfacer_tools as _interfacer_tools,
)
from .tools.registry import get_tools_for_agent

class Interfacer:
    def __init__(self):
        self.model_name = "gemma3:1b"
        self.tools = get_tools_for_agent("interfacer")
        self.tool_specs = [
            {
                "name": name,
                "description": tool.__doc__ or "agent helper",
                "callable": tool,
            }
            for name, tool in self.tools.items()
        ]
    def chat(self, messages: list[dict], stream: bool = False):
        if stream:
            return ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=self.tool_specs,
                stream=True,
            )
        else:
            return ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=self.tool_specs,
            )

