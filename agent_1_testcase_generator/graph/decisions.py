from .state import TestState


def route_after_review(state: TestState) -> str:
    decision = state["decision"].strip().lower()

    if decision == "approve":
        return "approved"
    if decision in {"approved", "edit", "rejected"}:
        return decision
    if decision == "reject":
        return "rejected"

    raise ValueError(f"Unsupported review decision: {decision}")


route = route_after_review
