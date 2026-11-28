class FailingGenerationLLM:
    def with_structured_output(self, schema, method):
        raise RuntimeError("LLM API failed")
