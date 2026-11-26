from typing import TypedDict


class TestState(TypedDict, total=False):
    document: str
    requirements: str
    test_cases: list[dict]
    validation_results: list[str]
    human_feedback: str
    approved: bool
    output_path: str
