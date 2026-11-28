from schemas.test_case import TestCase, TestCases


class FakeGenerationResponse:
    def model_dump_json(self, indent=2):
        return TestCases(
            test_cases=[
                TestCase(
                    test_case_id="TC001",
                    title="Valid login",
                    test_data={"username": "Admin", "password": "admin123"},
                    steps=["Open login page", "Enter valid credentials"],
                    expected_result="Dashboard is displayed",
                    actual_result="",
                )
            ]
        ).model_dump_json(indent=indent)
