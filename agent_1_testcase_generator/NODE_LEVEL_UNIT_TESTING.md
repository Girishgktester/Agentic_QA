# Agent 1 Node-Level Unit Testing Preparation

## 1. Project Structure

Relevant Agent 1 files:

```text
agent_1_testcase_generator/
├── config/
│   └── settings.py          # Environment loading and LLM creation
├── graph/
│   ├── decisions.py         # Human-review routing
│   ├── state.py             # TestState TypedDict
│   └── workflow.py          # LangGraph graph construction
├── nodes/
│   ├── analysis.py          # analyze_requirements
│   ├── document.py          # load_document
│   ├── evaluation.py        # validate_test_cases
│   ├── generation.py        # generate_test_cases
│   ├── human_review.py      # human_review and interrupt
│   └── save.py              # save_test_cases
├── schemas/
│   └── test_case.py         # Pydantic models
├── tests/
│   ├── test_nodes.py        # Placeholder node tests
│   └── test_workflow.py     # Placeholder workflow tests
├── prompts/                 # No project-specific prompt implementation
├── main.py                  # CLI workflow runner
├── testcases/TC001.txt      # Example input document
├── output/test_cases.json   # Example generated output
└── requirements.txt
```

Root-level `config`, `graph`, `nodes`, `prompts`, and `schemas` packages are compatibility wrappers that re-export Agent 1 modules.

Existing test files contain only empty placeholder classes. No functional tests, fixtures, or mocks currently exist.

## 2. State Definition

### Complete definition

File: `agent_1_testcase_generator/graph/state.py`

```python
from typing import TypedDict


class TestState(TypedDict, total=False):
    input_file: str
    user_story: str
    output_file: str
    analysis: str
    test_cases: str
    attempts: int
    feedback: str
    decision: str
    relevancy_score: float
    relevancy_reason: str
    relevancy_pass: bool
    faithfulness_score: float
    faithfulness_reason: str
    faithfulness_pass: bool
```

`total=False` means every key is optional at runtime. No field has a declared default value.

### State field usage

| Field | Read by | Written by |
|---|---|---|
| `input_file` | `load_document` | Initial workflow input |
| `user_story` | `analyze_requirements`, `validate_test_cases` | `load_document` |
| `output_file` | `save_test_cases` | Initial input; returned again by `save_test_cases` |
| `analysis` | `generate_test_cases`, `validate_test_cases` | `analyze_requirements` |
| `test_cases` | `validate_test_cases`, `save_test_cases` | `generate_test_cases` |
| `attempts` | `generate_test_cases` through `.get()` | `generate_test_cases` |
| `feedback` | `generate_test_cases` through `.get()` | `human_review` |
| `decision` | `route_after_review` | `human_review` |
| `relevancy_score` | No node currently reads it | `validate_test_cases` |
| `relevancy_reason` | No node currently reads it | `validate_test_cases` |
| `relevancy_pass` | No node currently reads it | `validate_test_cases` |
| `faithfulness_score` | No node currently reads it | `validate_test_cases` |
| `faithfulness_reason` | No node currently reads it | `validate_test_cases` |
| `faithfulness_pass` | No node currently reads it | `validate_test_cases` |

## 3. Node Inventory

### `load_document`

File: `agent_1_testcase_generator/nodes/document.py`

Signature:

```python
def load_document(state: TestState) -> dict:
```

Complete implementation:

```python
from pathlib import Path

from graph.state import TestState


def load_document(state: TestState) -> dict:
    document = Path(state["input_file"]).read_text(encoding="utf-8")
    return {"user_story": document}
```

- Reads: `input_file`
- Writes: `user_story`
- External dependency: filesystem via `pathlib.Path`
- Side effect: reads a file
- Potential exceptions:
  - `KeyError` if `input_file` is absent
  - `FileNotFoundError` if the path does not exist
  - `PermissionError` for inaccessible files
  - `UnicodeDecodeError` for non-UTF-8 input
  - Other `OSError` subclasses

Recommended unit test seam: use `tmp_path` with a real UTF-8 file, and separately test missing or invalid paths.

### `analyze_requirements`

File: `agent_1_testcase_generator/nodes/analysis.py`

Signature:

```python
def analyze_requirements(state: TestState) -> dict:
```

Complete implementation:

```python
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
```

- Reads: `user_story`
- Writes: `analysis`
- External dependencies:
  - `config.settings.get_llm`
  - `ChatOpenAI`
  - LLM `.invoke()`
- Side effects: external LLM request
- Potential exceptions:
  - `KeyError` if `user_story` is absent
  - LLM authentication, network, timeout, or provider errors
  - `AttributeError` if the mocked response lacks `.content`

Mock during unit tests:

```python
monkeypatch.setattr(
    "agent_1_testcase_generator.nodes.analysis.get_llm",
    lambda: fake_llm,
)
```

Keep the prompt construction and returned `analysis` assignment real.

### `generate_test_cases`

File: `agent_1_testcase_generator/nodes/generation.py`

Signature:

```python
def generate_test_cases(state: TestState) -> dict:
```

Complete implementation:

```python
from config.settings import get_llm
from graph.state import TestState
from schemas.test_case import TestCases


def generate_test_cases(state: TestState) -> dict:
    feedback = state.get("feedback", "").strip()
    instruction = "Generate exactly one test case for the highest-priority scenario."

    if feedback:
        instruction = (
            f"Regenerate the test case using this reviewer feedback:\n{feedback}"
        )

    prompt = f"""
             Generate manual test cases from the requirement analysis below.
            {instruction}
            Do not invent requirements. Leave actual_result blank.
            Return valid data matching the requested schema.

            Requirement analysis:
            {state["analysis"]}
    """
    response = get_llm().with_structured_output(
        TestCases, method="function_calling"
    ).invoke(prompt)
    test_cases_json = response.model_dump_json(indent=2)
    attempts = state.get("attempts", 0) + 1

    print(f"\nGenerated test cases (attempt {attempts}/3):\n{test_cases_json}")

    return {"test_cases": test_cases_json, "attempts": attempts}
```

- Reads:
  - `analysis`
  - Optional `feedback`
  - Optional `attempts`
- Writes:
  - `test_cases`
  - `attempts`
- External dependencies:
  - `get_llm`
  - LangChain structured-output wrapper
  - Pydantic `TestCases`
  - LLM `.invoke()`
- Side effects:
  - External LLM request
  - Console output through `print`
- Potential exceptions:
  - `KeyError` if `analysis` is absent
  - LLM/provider errors
  - Pydantic validation errors from invalid structured output
  - `AttributeError` if the response lacks `.model_dump_json()`
  - `TypeError` if `attempts` is not integer-like

Important observations:

- The prompt requests exactly one test case.
- The `TestCases` schema permits a list of any length; enforcement is prompt-based only.
- `MAX_ATTEMPTS` is not used.
- There is no attempt limit or retry exception in this node.
- The console output always displays `/3`, regardless of `MAX_ATTEMPTS`.

Mock the chained call:

```text
get_llm()
  .with_structured_output(TestCases, method="function_calling")
  .invoke(prompt)
```

Use a fake response implementing:

```python
model_dump_json(indent=2)
```

Test both empty feedback and non-empty feedback paths.

### `validate_test_cases`

File: `agent_1_testcase_generator/nodes/evaluation.py`

Signature:

```python
def validate_test_cases(state: TestState) -> dict:
```

Complete implementation:

```python
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase

from config.settings import MODEL_NAME
from graph.state import TestState


def validate_test_cases(state: TestState) -> dict:
    test_case = LLMTestCase(
        input=state["user_story"],
        actual_output=state["test_cases"],
        retrieval_context=[state["analysis"]],
    )

    relevancy = AnswerRelevancyMetric(
        threshold=0.7, model=MODEL_NAME, include_reason=True
    )
    faithfulness = FaithfulnessMetric(
        threshold=0.7, model=MODEL_NAME, include_reason=True
    )

    relevancy.measure(test_case)
    faithfulness.measure(test_case)

    return {
        "relevancy_score": relevancy.score,
        "relevancy_reason": relevancy.reason,
        "relevancy_pass": relevancy.success,
        "faithfulness_score": faithfulness.score,
        "faithfulness_reason": faithfulness.reason,
        "faithfulness_pass": faithfulness.success,
    }
```

- Reads:
  - `user_story`
  - `test_cases`
  - `analysis`
- Writes:
  - `relevancy_score`
  - `relevancy_reason`
  - `relevancy_pass`
  - `faithfulness_score`
  - `faithfulness_reason`
  - `faithfulness_pass`
- External dependencies:
  - DeepEval `LLMTestCase`
  - `AnswerRelevancyMetric`
  - `FaithfulnessMetric`
  - `MODEL_NAME`
- Side effects:
  - DeepEval metric evaluation
  - Potential external model calls
  - Potential telemetry/cache behavior from DeepEval
- Potential exceptions:
  - `KeyError` for missing required state fields
  - DeepEval model, network, authentication, or evaluation errors
  - Invalid test-case construction errors
  - Metric errors if `.measure()` does not populate expected properties

Mock during node-level tests:

- `LLMTestCase`
- `AnswerRelevancyMetric`
- `FaithfulnessMetric`

Keep real:

- The construction of metric arguments
- The state-to-metric mapping
- The returned score/reason/pass fields

Verify:

- Threshold `0.7`
- `model=MODEL_NAME`
- `include_reason=True`
- Each metric receives the same `LLMTestCase`
- All six output fields are returned

### `human_review`

File: `agent_1_testcase_generator/nodes/human_review.py`

Signature:

```python
def human_review(_: TestState) -> dict:
```

Complete implementation:

```python
from langgraph.types import interrupt

from graph.state import TestState


def human_review(_: TestState) -> dict:
    response = interrupt("Enter approve, edit, or reject with optional feedback")

    decision = response["decision"].strip().lower()

    return {
        "decision": decision,
        "feedback": response.get("feedback", "").strip(),
    }
```

- Reads: no state fields
- Writes:
  - `decision`
  - `feedback`
- External dependency: LangGraph `interrupt`
- Side effect: pauses graph execution for human input
- Potential exceptions:
  - Interrupt control-flow behavior when invoked inside LangGraph
  - `KeyError` if response lacks `decision`
  - `AttributeError` if `decision` is not a string
  - `AttributeError` if `feedback` is non-string
  - Errors from an invalid interrupt response object

For a direct unit test, patch the imported symbol:

```text
agent_1_testcase_generator.nodes.human_review.interrupt
```

Return values to test:

```python
{"decision": "approve", "feedback": ""}
{"decision": "edit", "feedback": "Add invalid-login coverage"}
{"decision": "reject"}
```

The node itself does not validate allowed decisions. Validation occurs in `main.py`, not in this node.

### `save_test_cases`

File: `agent_1_testcase_generator/nodes/save.py`

Signature:

```python
def save_test_cases(state: TestState) -> dict:
```

Complete implementation:

```python
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
```

- Reads:
  - `output_file`
  - `test_cases`
- Writes:
  - File at `output_file`
  - Returns `output_file`
- External dependencies:
  - `pathlib.Path`
  - Standard-library `json`
- Side effects:
  - Creates parent directories
  - Writes JSON to disk
  - Prints confirmation
- Potential exceptions:
  - `KeyError` if required state fields are absent
  - `json.JSONDecodeError` for invalid JSON
  - `PermissionError`
  - `OSError`
  - `UnicodeEncodeError`
  - Path-related errors

Important behavior: JSON is parsed before writing, so invalid JSON must not create or overwrite the output file.

Use `tmp_path` for real filesystem tests. Keep JSON parsing and writing real; do not mock them unless testing failure handling.

### Additional graph functions

#### `route_after_review`

File: `agent_1_testcase_generator/graph/decisions.py`

```python
def route_after_review(state: TestState) -> str:
    decision = state["decision"].strip().lower()

    if decision == "approve":
        return "approved"
    if decision in {"approved", "edit", "rejected"}:
        return decision
    if decision == "reject":
        return "rejected"

    raise ValueError(f"Unsupported review decision: {decision}")
```

Alias:

```python
route = route_after_review
```

Inputs:

- `decision`

Outputs:

- `"approved"`
- `"edit"`
- `"rejected"`

Accepted decisions:

| Input | Output |
|---|---|
| `approve` | `approved` |
| `approved` | `approved` |
| `edit` | `edit` |
| `reject` | `rejected` |
| `rejected` | `rejected` |

Potential exceptions:

- `KeyError` if `decision` is absent
- `AttributeError` if `decision` is not a string
- `ValueError` for unsupported decisions

#### `build_graph`

File: `agent_1_testcase_generator/graph/workflow.py`

```python
def build_graph():
    builder = StateGraph(TestState)

    builder.add_node("load_document", load_document)
    builder.add_node("analyze_requirements", analyze_requirements)
    builder.add_node("generate_test_cases", generate_test_cases)
    builder.add_node("validate_test_cases", validate_test_cases)
    builder.add_node("human_review", human_review)
    builder.add_node("save_test_cases", save_test_cases)

    builder.add_edge(START, "load_document")
    builder.add_edge("load_document", "analyze_requirements")
    builder.add_edge("analyze_requirements", "generate_test_cases")
    builder.add_edge("generate_test_cases", "validate_test_cases")
    builder.add_edge("validate_test_cases", "human_review")

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
```

The workflow has six registered nodes and uses `MemorySaver`.

## 4. External Dependencies

### LLM initialization

File: `agent_1_testcase_generator/config/settings.py`

```python
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=True)

MODEL_NAME = os.getenv("LLM_MODEL", "gpt-6-luna")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=MODEL_NAME)
```

Mock:

- `get_llm()` in analysis and generation tests
- Never make real LLM calls during node unit tests

Keep real:

- Prompt formatting
- State extraction
- Response-field extraction
- Attempt-counter logic

### Prompt templates

There are no external prompt templates currently. The prompts are inline f-strings in:

- `nodes/analysis.py`
- `nodes/generation.py`

The `prompts/` package contains only compatibility wrappers and no actual prompt constants or functions.

### Pydantic models

File: `agent_1_testcase_generator/schemas/test_case.py`

```python
from typing import Dict, List

from pydantic import BaseModel


class TestCase(BaseModel):
    test_case_id: str
    title: str
    test_data: Dict[str, str]
    steps: List[str]
    expected_result: str
    actual_result: str


class TestCases(BaseModel):
    test_cases: List[TestCase]
```

These models should remain real in generation tests when validating the shape of mocked structured output.

### DeepEval

Used only by `validate_test_cases`:

- `LLMTestCase`
- `AnswerRelevancyMetric`
- `FaithfulnessMetric`

Mock metric construction and `.measure()` calls for unit tests. DeepEval integration should be covered separately by integration tests.

### File operations

- `load_document`: real temporary files are appropriate
- `save_test_cases`: real temporary directories/files are appropriate
- Avoid mocking `Path` for normal success-path tests

### Other dependencies

- LangGraph `StateGraph`
- LangGraph `MemorySaver`
- LangGraph `interrupt`
- LangGraph `Command`
- Pydantic
- `python-dotenv`
- `pytest`

## 5. HITL and Routing

### Interrupt implementation

The implementation uses LangGraph’s imported function:

```python
response = interrupt("Enter approve, edit, or reject with optional feedback")
```

There is no project-defined wrapper around `interrupt()`.

### `Command(resume=...)` handling

`main.py` resumes the graph as follows:

```python
graph.invoke(
    Command(resume={"decision": decision, "feedback": feedback}),
    config=config,
)
```

The README documents the same programmatic pattern.

`Command` is not handled directly by any node. LangGraph delivers the resumed payload back to `human_review`.

### Conditional routing

```python
builder.add_conditional_edges(
    "human_review",
    route,
    {
        "approved": "save_test_cases",
        "rejected": END,
        "edit": "generate_test_cases",
    },
)
```

Routing uses `route`, which is an alias for `route_after_review`.

### Retry and attempt-counter logic

The only attempt logic is in `generate_test_cases`:

```python
attempts = state.get("attempts", 0) + 1
```

There is no:

- Maximum-attempt check
- Retry loop
- Retry routing
- Failure route
- Use of `MAX_ATTEMPTS`
- Automatic retry on validation failure

The `edit` route causes regeneration, but only after human review:

```text
human_review -> edit -> generate_test_cases
```

The console message uses a hard-coded maximum:

```python
print(f"\nGenerated test cases (attempt {attempts}/3):\n{test_cases_json}")
```

### Checkpoint and thread ID

`build_graph()` compiles with:

```python
MemorySaver()
```

`main.py` uses:

```python
config = {"configurable": {"thread_id": "qa-practice-001"}}
```

The same configuration is passed to the initial invocation, `get_state()`, and resumed invocations.

There is no durable database checkpointer. `MemorySaver` is process-memory checkpointing.

## 6. Existing Testing Setup

### Pytest configuration

No `pytest.ini`, `pyproject.toml`, or `tox.ini` pytest configuration was found.

### Installed testing libraries

`agent_1_testcase_generator/requirements.txt` includes:

```text
pytest==8.4.2
pytest-asyncio==1.5.0
pytest-repeat==0.9.4
pytest-rerunfailures==16.7
pytest-xdist==3.8.0
```

No dedicated mocking library is listed. Use the standard-library `unittest.mock` or pytest’s built-in `monkeypatch` fixture.

### Existing tests

`agent_1_testcase_generator/tests/test_nodes.py`:

```python
class TestDocumentNode:
    pass


class TestAnalysisNode:
    pass


class TestGenerationNode:
    pass


class TestEvaluationNode:
    pass
```

`agent_1_testcase_generator/tests/test_workflow.py`:

```python
class TestAgentWorkflow:
    pass
```

There are currently:

- No executable test functions
- No fixtures
- No mocks
- No parametrized tests
- No node-level assertions
- No workflow assertions

## 7. Recommended Unit Testing Plan

### Independent node invocation

Invoke each node directly with a minimal dictionary containing only the fields it reads:

```python
load_document({"input_file": str(input_path)})
analyze_requirements({"user_story": "..."})
generate_test_cases({"analysis": "..."})
validate_test_cases({
    "user_story": "...",
    "test_cases": "...",
    "analysis": "...",
})
human_review({})
save_test_cases({
    "output_file": str(output_path),
    "test_cases": valid_json,
})
```

Do not use the compiled graph for node-level tests. Reserve graph invocation for workflow/integration tests.

### `load_document` tests

Test:

- Reads UTF-8 content correctly
- Returns exactly `{"user_story": content}`
- Missing file raises `FileNotFoundError`
- Missing `input_file` raises `KeyError`
- Invalid UTF-8 raises `UnicodeDecodeError`

### `analyze_requirements` tests

Mock:

- `get_llm`
- LLM `.invoke()`

Assert:

- Prompt contains the supplied user story
- Prompt contains the no-invention instruction
- `.invoke()` is called once
- Returned `.content` becomes `analysis`
- Missing `user_story` raises `KeyError`
- LLM exceptions propagate

### `generate_test_cases` tests

Mock:

- `get_llm`
- Structured-output chain
- `.invoke()`

Use a real `TestCases` instance as the fake structured response.

Assert:

- Empty feedback uses the normal generation instruction
- Non-empty feedback is included in the regeneration prompt
- `attempts` defaults to `1`
- Existing `attempts=2` becomes `3`
- Returned JSON is valid and matches the Pydantic schema
- `.with_structured_output()` receives `TestCases`
- `method="function_calling"` is passed
- Missing `analysis` raises `KeyError`
- Invalid structured response raises or exposes validation failure
- No attempt limit is currently enforced

### `validate_test_cases` tests

Mock:

- `LLMTestCase`
- `AnswerRelevancyMetric`
- `FaithfulnessMetric`

Configure fake metrics with:

```python
score
reason
success
```

Assert:

- `LLMTestCase` receives:
  - `input=state["user_story"]`
  - `actual_output=state["test_cases"]`
  - `retrieval_context=[state["analysis"]]`
- Both metrics use threshold `0.7`
- Both metrics use `MODEL_NAME`
- Both metrics use `include_reason=True`
- Both `.measure()` methods receive the same test case
- All six evaluation fields are returned
- Metric failure/exception behavior is propagated

### `human_review` tests

Patch:

```text
agent_1_testcase_generator.nodes.human_review.interrupt
```

Test:

- Approve response
- Edit response with feedback
- Reject response
- Missing feedback defaults to `""`
- Decision is stripped and lowercased
- Missing decision raises `KeyError`
- Non-string values raise `AttributeError`

The node does not itself reject unsupported decisions, so test that behavior through `route_after_review`, not `human_review`.

### `save_test_cases` tests

Use `tmp_path` and real files.

Test:

- Valid JSON is written
- Missing parent directories are created
- Returned `output_file` is the string path
- Written content exactly matches `state["test_cases"]`
- Invalid JSON raises `json.JSONDecodeError`
- Invalid JSON does not write the output file
- Missing fields raise `KeyError`
- Filesystem permission errors propagate

### Routing tests

Parametrize these mappings:

```text
approve   -> approved
approved  -> approved
edit      -> edit
reject    -> rejected
rejected  -> rejected
```

Also test:

- Leading/trailing whitespace
- Uppercase/mixed-case input
- Unsupported values raise `ValueError`
- Missing `decision` raises `KeyError`

### Workflow tests

For separate integration-level tests:

- `build_graph()` registers all six expected nodes
- Initial graph edges follow the documented order
- Approve reaches `save_test_cases`
- Reject terminates without saving
- Edit returns to `generate_test_cases`
- `MemorySaver` preserves the interrupted state
- A consistent `thread_id` allows resume with `Command(resume=...)`

Mock LLM and DeepEval calls in workflow tests so the graph remains deterministic and offline.
