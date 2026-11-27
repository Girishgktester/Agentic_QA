from langgraph.types import interrupt

from agent_1_testcase_generator.graph.state import TestState

def human_review(_: TestState) -> dict:
    response = interrupt("Enter approve, edit, or reject with optional feedback")

    decision = response["decision"].strip().lower()

    return {
        "decision": decision,
        "feedback": response.get("feedback", "").strip(),
    }
