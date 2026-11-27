from agent_1_testcase_generator.config.settings import get_llm
from agent_1_testcase_generator.graph.state import TestState
from agent_1_testcase_generator.schemas.test_case import TestCases


def generate_test_cases(state: TestState) -> dict:
    feedback = state.get("feedback", "").strip()
    instruction = "Generate exactly one test case for the highest-priority scenario."

    if feedback:
        instruction = (
            f"Regenerate the test case using this reviewer feedback:\n{feedback}"
        )

    prompt = f"""
             Generate manual test cases from the requirement analysis below.
            {instruction}
            Do not invent requirements. Leave actual_result blank.
            Return valid data matching the requested schema.

            Requirement analysis:
            {state["analysis"]}
    """
    response = get_llm().with_structured_output(TestCases).invoke(prompt)
    test_cases_json = response.model_dump_json(indent=2)
    attempts = state.get("attempts", 0) + 1

    print(f"\nGenerated test cases (attempt {attempts}/3):\n{test_cases_json}")

    return {"test_cases": test_cases_json, "attempts": attempts}
