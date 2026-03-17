from agents.tools.registry import get_tools_for_agent
from agents.utils.message_utils import prepare_messages
from .utils.tool_parser import parse
import ollama
class Agent:
    def __init__(self, model_name, agent_name, agent_prompt):
        self.model_name = model_name
        self.agent_name = agent_name
        self.role = agent_prompt
        self.tools = get_tools_for_agent(self.agent_name)
        self.tool_specs = [parse(item) for item in self.tools.items()]
    def simpleChat(self, prompt: str):
        response = ollama.generate(
            model = self.model_name,
            prompt=prompt,
        )
        return response["response"]
    def chat(self, messages: list[dict], stream: bool = True):
        payload = prepare_messages(messages, self.role)
        return ollama.chat(
            model=self.model_name,
            messages=payload,
            stream=stream,
        )