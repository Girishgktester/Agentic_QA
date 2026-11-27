from pathlib import Path

from agent_1_testcase_generator.graph.state import TestState


def load_document(state: TestState) -> dict:
    document = Path(state["input_file"]).read_text(encoding="utf-8")
    return {"user_story": document}