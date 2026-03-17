import ast
import json
import ollama
from .agent import Agent
from .prompt_templates.interfacer_prompt import PROMPT as INTERFACER_PROMPT
from .utils.message_utils import prepare_messages
from .utils.tool_parser import parse


class Interfacer(Agent):
    def __init__(self):
        super().__init__(model_name="qwen2.5:1.5b", agent_name="interfacer", agent_prompt=INTERFACER_PROMPT)
        self.decision_tree = None 
