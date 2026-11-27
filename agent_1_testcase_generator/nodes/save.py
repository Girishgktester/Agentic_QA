import json
from pathlib import Path

from graph.state import TestState

def save_test_cases(state: TestState) -> dict:
    output_file = Path(state["output_file"])
    output_file.parent.mkdir(parents=True, exist_ok=True)

    json.loads(state["test_cases"])

    output_file.write_text(state["test_cases"], encoding="utf-8")

    print(f"Approved test cases saved to: {output_file}")

    return {"output_file": str(output_file)}