from agent_1_testcase_generator.nodes.analysis import analyze_requirements
from agent_1_testcase_generator.tests.fakes.llm import FakeLLM

class TestAnalysisNode:

    def test_analyze_requirements(self, monkeypatch):

        fake_llm = FakeLLM()

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.analysis.get_llm",
            lambda: fake_llm
        )

        state = {
            "user_story": "As a user, I want to login."
        }

        result = analyze_requirements(state)

        print(f"Input state: {state}")
        print(f"Analysis result: {result}")

        assert result == {
            "analysis": "Identified login requirements and edge cases."
        }

    def test_analyze_requirements_prompt_contains_requirements(self, monkeypatch):
        fake_llm = FakeLLM()
        
        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.analysis.get_llm",
            lambda: fake_llm,
        )

        analyze_requirements({"user_story": "As a user, I want to login."})

        assert "As a user, I want to login." in fake_llm.prompt
        assert "acceptance criteria" in fake_llm.prompt
        assert "As a user, I want to login." in fake_llm.prompt
        assert "main user goal" in fake_llm.prompt
        assert "expected behavior" in fake_llm.prompt
        assert "acceptance criteria" in fake_llm.prompt
        assert "edge cases" in fake_llm.prompt
        assert "Do not invent requirements" in fake_llm.prompt
