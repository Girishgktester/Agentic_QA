from pathlib import Path

from langgraph.types import Command

from graph.workflow import build_graph


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    input_file = base_dir / "testcases" / "TC001.txt"
    output_file = base_dir / "output" / "test_cases.json"

    graph = build_graph()
    config = {"configurable": {"thread_id": "qa-practice-001"}}

    graph.invoke(
        {"input_file": str(input_file), "output_file": str(output_file)},
        config=config,
    )

    snapshot = graph.get_state(config)

    while snapshot.next:
        decision = input("Enter approve, edit, or reject: ").strip().lower()

        while decision not in {"approve", "edit", "reject"}:
            decision = input("Please enter approve, edit, or reject: ").strip().lower()

        feedback = input("Enter feedback for the edit: ").strip() if decision == "edit" else ""

        graph.invoke(
            Command(resume={"decision": decision, "feedback": feedback}),
            config=config,
        )

        snapshot = graph.get_state(config)


if __name__ == "__main__":
    main()