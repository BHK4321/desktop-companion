from dataclasses import dataclass

@dataclass
class State:
    def __init__(
        self,
        idx: int,
        goal: str,
        context: str = "",
        current_step: str = "classify_intent",
    ):
        self.idx = idx
        self.goal = goal
        self.context = context
        self.current_step = current_step

    def to_dict(self):
        return {
            "idx": self.idx,
            "goal": self.goal,
            "context": self.context,
            "current_step": self.current_step,
        }

    @classmethod
    def from_dict(cls, state_dict):
        return cls(
            idx=state_dict.get("idx", 0),
            goal=state_dict.get("goal", ""),
            context=state_dict.get("context", ""),
            current_step=state_dict.get("current_step", "classify_intent"),
        )
