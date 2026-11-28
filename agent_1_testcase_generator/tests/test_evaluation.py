from types import SimpleNamespace
from unittest.mock import Mock

from agent_1_testcase_generator.nodes.evaluation import validate_test_cases


class TestEvaluationNode:
    def test_validate_test_cases_returns_metric_results(self, monkeypatch):
        fake_test_case = object()
        fake_llm_test_case = Mock(return_value=fake_test_case)
        fake_relevancy = SimpleNamespace(
            score=0.9,
            reason="The output is relevant.",
            success=True,
            measure=Mock(),
        )
        fake_faithfulness = SimpleNamespace(
            score=0.8,
            reason="The output is faithful.",
            success=True,
            measure=Mock(),
        )
        fake_relevancy_metric = Mock(return_value=fake_relevancy)
        fake_faithfulness_metric = Mock(return_value=fake_faithfulness)

        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.evaluation.LLMTestCase",
            fake_llm_test_case,
        )
        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.evaluation.AnswerRelevancyMetric",
            fake_relevancy_metric,
        )
        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.evaluation.FaithfulnessMetric",
            fake_faithfulness_metric,
        )

        state = {
            "user_story": "A user logs in.",
            "test_cases": '{"test_cases": []}',
            "analysis": "Login requires valid credentials.",
        }

        result = validate_test_cases(state)

        print(f"Validation result: {result}")

        assert result == {
            "relevancy_score": 0.9,
            "relevancy_reason": "The output is relevant.",
            "relevancy_pass": True,
            "faithfulness_score": 0.8,
            "faithfulness_reason": "The output is faithful.",
            "faithfulness_pass": True,
        }
        fake_llm_test_case.assert_called_once_with(
            input="A user logs in.",
            actual_output='{"test_cases": []}',
            retrieval_context=["Login requires valid credentials."],
        )
        fake_relevancy_metric.assert_called_once()
        fake_faithfulness_metric.assert_called_once()
        fake_relevancy.measure.assert_called_once_with(fake_test_case)
        fake_faithfulness.measure.assert_called_once_with(fake_test_case)
