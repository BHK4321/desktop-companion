from ..coder import Coder
from .registry import register_tool


@register_tool("interfacer", "assign-to-coder")
def assign(request: str, messages: list[dict] | None = None) -> str:
    """Delegate a coding request to the coder agent and return its answer.
    The coding agent is meant for writing and registering functions which you (interface agent) can use.
    """
    print("ASSIGNED")
    print("Request to assign to coder:", request)
    print("Messages:", messages)
    conversation = list(messages or [])
    if request:
        conversation.append({"role": "user", "content": request})

    coder = Coder()
    response = coder.generate(conversation)
    print(response)
    
    return response
# assign(request="Write a function that adds two numbers.")