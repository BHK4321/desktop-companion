import ollama
from .tools.registry import get_tools_for_agent

class Coder:
    def __init__(self):
        self.model_name = "qwen2.5-coder:1.5b"
        self.tools = get_tools_for_agent("coder")
        self.tool_specs = [
            {
                "name": name,
                "description": tool.__doc__ or "agent helper",
                "callable": tool,
            }
            for name, tool in self.tools.items()
        ]
    def generate(self, messages: list[dict]):
        return ollama.chat(
            model=self.model_name,
            messages=messages,
            tools=self.tool_specs,
        )