import ollama
from typing import Any
from .agent import Agent
from .prompt_templates.coder_prompt import PROMPT as CODER_PROMPT
from .tools.registry import get_tools_for_agent, get_tool
from .utils.message_utils import prepare_messages
from .utils.tool_parser import parse

class Coder(Agent):
    def __init__(self):
        super().__init__(model_name="qwen2.5:1.5b", agent_name="coder", agent_prompt=CODER_PROMPT)
    # def generate(self, messages: list[dict]):
    #     payload = prepare_messages(messages, self.role)
    #     response = ollama.chat(
    #         model=self.model_name,
    #         messages=payload,
    #         tools=self.tool_specs,
    #     )
    #     tools_calls = ""
    #     reasoning = "Reasoning: "
    #     message_data = response.get("message") or {}
    #     for tool_call in (message_data.get("tool_calls") or []):
    #         fn_data = tool_call.get("function") or {}
    #         tool_name = fn_data.get("name")
    #         tool_args = fn_data.get("arguments", {})
    #         if not tool_name:
    #             continue
    #         tool_func = get_tool("coder", tool_name)
    #         if not tool_func:
    #             raise ValueError(f"Tool {tool_name} not found for coder agent.")
    #         result = tool_func(**tool_args)
    #         tools_calls += f"\n[Tool call: {tool_name} with args {tool_args} returned {result}]\n"
    #     def _extract_chunk_content(chunk: Any) -> str:
    #         if chunk is None:
    #             return ""
    #         if isinstance(chunk, dict):
    #             message = chunk.get("message")
    #             if isinstance(message, dict):
    #                 return message.get("content", "")
    #             return chunk.get("content", chunk.get("text", ""))
    #         return str(chunk)

    #     content_payload = message_data.get("content")
    #     if isinstance(content_payload, list):
    #         reasoning += " ".join(
    #             part
    #             for part in (_extract_chunk_content(chunk) for chunk in content_payload)
    #             if part
    #         ).strip()
    #     else:
    #         reasoning += _extract_chunk_content(content_payload)
    
    #     print("Tool calls : " + tools_calls)
    #     return reasoning + tools_calls