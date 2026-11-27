from config.settings import get_llm
from graph.state import TestState


def analyze_requirements(state: TestState) -> dict:
    prompt = f"""
            Analyze the following user story or requirement document.
            Identify the main user goal, expected behavior, acceptance criteria, and important edge cases.
            Do not invent requirements. Clearly label assumptions.

Document:
    {state["user_story"]}
"""
    response = get_llm().invoke(prompt)
    return {"analysis": response.content}
