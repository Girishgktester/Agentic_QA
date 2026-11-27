from langgraph.types import interrupt

from graph.state import TestState

def human_review(_: TestState) -> dict:
    response = interrupt("Enter approve, edit, or reject with optional feedback")

    decision = response["decision"].strip().lower()

    return {
        "decision": decision,
        "feedback": response.get("feedback", "").strip(),
    }
