import ollama

from agents.tools.interfacer_tools import assign

from .state import State
from typing import List
from ..agent import Agent
class Tree:
    def __init__(self, root: State):
        self.root = root
        self.links = {root.idx: {}}
    def addChild(self, parent: State, child: State, link: str):
        if parent.idx not in self.links:
            self.links[parent.idx] = {}
        self.links[parent.idx][link] = child
        if child.idx not in self.links:
            self.links[child.idx] = {}
    def traverse(self, node: State, agent: Agent):
        if self.links[node.idx] == {}:
            assign(Agent=agent, request=node.goal)
            return
        prompt = "Answer in only ONE word." + "\n"
        prompt += "Question: " + node.goal + "\n"
        prompt += "Context: " + node.context + "\n"
        prompt += "Options: " + ", ".join(self.links.get(node.idx, {}).keys()) + "\n"
        response = agent.generate(prompt)
        self.traverse(self.links[node.idx][response], agent)
        