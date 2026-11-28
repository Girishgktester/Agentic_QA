from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from config.settings import MODEL_NAME
from graph.state import TestState


def validate_test_cases(state: TestState) -> dict:
    test_case = LLMTestCase(
        input=state["user_story"],
        actual_output=state["test_cases"],
        retrieval_context=[state["analysis"]],
    )

    relevancy = AnswerRelevancyMetric(
        threshold=0.7, model=MODEL_NAME, include_reason=True
    )
    faithfulness = FaithfulnessMetric(
        threshold=0.7, model=MODEL_NAME, include_reason=True
    )

    relevancy.measure(test_case)
    faithfulness.measure(test_case)

    return {
        "relevancy_score": relevancy.score,
        "relevancy_reason": relevancy.reason,
        "relevancy_pass": relevancy.success,
        "faithfulness_score": faithfulness.score,
        "faithfulness_reason": faithfulness.reason,
        "faithfulness_pass": faithfulness.success,
    }
