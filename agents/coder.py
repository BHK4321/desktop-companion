import ollama

class Coder:
    def __init__(self):
        self.model_name = "llama3"

    def generate(self, messages: list[dict]):
        return ollama.chat(
            model=self.model_name,
            messages=messages,
        )