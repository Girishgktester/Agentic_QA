from pathlib import Path

from graph.state import TestState


def load_document(state: TestState) -> dict:
    document = Path(state["input_file"]).read_text(encoding="utf-8")
    return {"user_story": document}