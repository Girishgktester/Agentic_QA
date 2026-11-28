from .generation_response import FakeGenerationResponse


class FakeGenerationLLM:
    def with_structured_output(self, schema, method):
        self.schema = schema
        self.method = method
        return self

    def invoke(self, prompt):
        self.prompt = prompt
        return FakeGenerationResponse()
