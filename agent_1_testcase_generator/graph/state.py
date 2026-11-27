from typing import TypedDict


from typing import TypedDict


class TestState(TypedDict, total=False):
    input_file: str
    user_story: str
    output_file: str
    analysis: str
    test_cases: str
    attempts: int
    feedback: str
    decision: str
    relevancy_score: float
    relevancy_reason: str
    relevancy_pass: bool
    faithfulness_score: float
    faithfulness_reason: str
    faithfulness_pass: bool
