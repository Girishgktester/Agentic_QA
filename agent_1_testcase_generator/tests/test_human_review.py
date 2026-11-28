from agent_1_testcase_generator.nodes.human_review import human_review


class TestHumanReviewNode:
    def test_human_review_returns_decision_and_feedback(self, monkeypatch):
        monkeypatch.setattr(
            "agent_1_testcase_generator.nodes.human_review.interrupt",
            lambda message: {
                "decision": " approve ",
                "feedback": " Looks good ",
            },
        )

        result = human_review({})

        print(f"Human review result: {result}")

        assert result == {
            "decision": "approve",
            "feedback": "Looks good",
        }
