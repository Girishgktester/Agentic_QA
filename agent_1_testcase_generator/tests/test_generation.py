import json

import pytest

from agent_1_testcase_generator.nodes.generation import generate_test_cases
from agent_1_testcase_generator.tests.fakes.generation_llm import FakeGenerationLLM
from agent_1_testcase_generator.tests.fakes.invalid_generation_llm import (
    InvalidGenerationLLM,
)
from agent_1_testcase_generator.tests.fakes.failing_generation_llm import (
    FailingGenerationLLM,
)


class TestGenerationNode:
    def test_generate_test_cases(self, monkeypatch):
        fake_llm = FakeGenerationLLM()

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.generation.get_llm",
            lambda: fake_llm,
        )

        state = {
            "analysis": "User should be able to login."
        }

        result = generate_test_cases(state)
        generated_test_cases = json.loads(result["test_cases"])

        print(f"Generation result: {result}")

        assert isinstance(generated_test_cases, dict)
        assert "test_cases" in generated_test_cases
        assert generated_test_cases["test_cases"][0]["test_case_id"] == "TC001"
        assert result["attempts"] == 1

    def test_generate_test_cases_with_feedback(self, monkeypatch):
        fake_llm = FakeGenerationLLM()

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.generation.get_llm",
            lambda: fake_llm,
        )

        state = {
            "analysis": "User should be able to login.",
            "feedback": "Add invalid login coverage",
        }

        result = generate_test_cases(state)

        print(f"Generation result with feedback: {result}")
        print(f"Prompt sent to LLM: {fake_llm.prompt}")

        assert "Add invalid login coverage" in fake_llm.prompt
        assert result["attempts"] == 1

    def test_generate_test_cases_increments_attempts(self, monkeypatch):
        fake_llm = FakeGenerationLLM()

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.generation.get_llm",
            lambda: fake_llm,
        )

        state = {
            "analysis": "User should be able to login.",
            "attempts": 2,
        }

        result = generate_test_cases(state)

        print(f"Attempt counter result: {result}")

        assert result["attempts"] == 3

    def test_generate_test_cases_missing_analysis(self):
        with pytest.raises(KeyError):
            generate_test_cases({})

    def test_generate_test_cases_invalid_json(self, monkeypatch):
        fake_llm = InvalidGenerationLLM()

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.generation.get_llm",
            lambda: fake_llm,
        )

        result = generate_test_cases({"analysis": "Login requirements"})

        with pytest.raises(json.JSONDecodeError):
            json.loads(result["test_cases"])

    def test_generate_test_cases_llm_failure(self, monkeypatch):
        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.generation.get_llm",
            lambda: FailingGenerationLLM(),
        )

        with pytest.raises(RuntimeError, match="LLM API failed"):
            generate_test_cases({"analysis": "Login requirements"})
