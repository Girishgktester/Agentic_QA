from typing import Dict, List

from pydantic import BaseModel

class TestCase(BaseModel):
    test_case_id: str
    title: str
    test_data: Dict[str, str]
    steps: List[str]
    expected_result: str
    actual_result: str = ""

class TestCases(BaseModel):
    test_cases: List[TestCase]