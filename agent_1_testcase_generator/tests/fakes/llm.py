from .response import FakeResponse


class FakeLLM:
    def invoke(self, prompt):
        self.prompt = prompt
        return FakeResponse()
