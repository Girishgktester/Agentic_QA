from pydantic import BaseModel


class TestCase(BaseModel):
    id: str
    title: str
    description: str
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    priority: str
    test_type: str


class TestCases(BaseModel):
    test_cases: list[TestCase]
