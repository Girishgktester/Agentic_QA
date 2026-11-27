from .state import TestState


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from graph.state import TestState
from graph.decisions import route
from nodes.document import load_document
from nodes.analysis import analyze_requirements
from nodes.generation import generate_test_cases
from nodes.evaluation import validate_test_cases
from nodes.human_review import human_review
from nodes.save import save_test_cases

def build_graph():
    builder = StateGraph(TestState)

    # Register nodes
    builder.add_node("load_document", load_document)
    builder.add_node("analyze_requirements", analyze_requirements)
    builder.add_node("generate_test_cases", generate_test_cases)
    builder.add_node("validate_test_cases", validate_test_cases)
    builder.add_node("human_review", human_review)
    builder.add_node("save_test_cases", save_test_cases)

    # Define workflow
    builder.add_edge(START, "load_document")
    builder.add_edge("load_document", "analyze_requirements")
    builder.add_edge("analyze_requirements", "generate_test_cases")
    builder.add_edge("generate_test_cases", "validate_test_cases")
    builder.add_edge("validate_test_cases", "human_review")

    # Human decision routing
    builder.add_conditional_edges(
        "human_review",
        route,
        {
            "approved": "save_test_cases",
            "rejected": END,
            "edit": "generate_test_cases",
        },
    )

    builder.add_edge("save_test_cases", END)

    return builder.compile(checkpointer=MemorySaver())
