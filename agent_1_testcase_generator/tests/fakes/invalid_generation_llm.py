from .invalid_generation_response import InvalidGenerationResponse


class InvalidGenerationLLM:
    def with_structured_output(self, schema, method):
        return self

    def invoke(self, prompt):
        return InvalidGenerationResponse()
