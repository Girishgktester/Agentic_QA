from deepeval import evaluate
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

    evaluation_result = evaluate(
        test_cases=[test_case],
        metrics=[
            AnswerRelevancyMetric(
                threshold=0.7, model=MODEL_NAME, include_reason=True
            ),
            FaithfulnessMetric(
                threshold=0.7, model=MODEL_NAME, include_reason=True
            ),
        ],
    )

    metrics = evaluation_result.test_results[0].metrics_data

    relevancy = next(
        metric for metric in metrics if "relevancy" in metric.name.lower()
    )
    faithfulness = next(
        metric for metric in metrics if "faithfulness" in metric.name.lower()
    )

    return {
        "relevancy_score": relevancy.score,
        "relevancy_reason": relevancy.reason,
        "relevancy_pass": relevancy.success,
        "faithfulness_score": faithfulness.score,
        "faithfulness_reason": faithfulness.reason,
        "faithfulness_pass": faithfulness.success,
    }
