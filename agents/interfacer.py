import ollama

class Interfacer:
    def __init__(self):
        self.model_name = "gemma3:1b"

    def chat(self, messages: list[dict], stream: bool = False):
        if stream:
            return ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=True,
            )
        else:
            return ollama.chat(
                model=self.model_name,
                messages=messages,
            )

