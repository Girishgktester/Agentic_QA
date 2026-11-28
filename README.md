"# Agentic QA

Agentic QA is a Python-based, human-in-the-loop test-case generation workflow. It uses LangGraph to coordinate document loading, requirement analysis, structured test-case generation, automated evaluation, reviewer feedback, and approval-based persistence.

The current example processes a login user story for OrangeHRM and produces an approved test case in JSON format.

## Features

- Loads user stories and requirement documents from text files.
- Uses an OpenAI-compatible chat model to analyze requirements.
- Generates schema-validated manual test cases with Pydantic.
- Evaluates generated output with DeepEval answer-relevancy and faithfulness metrics.
- Pauses for human review using LangGraph interrupts.
- Supports three review decisions:
  - `approve`: save the generated test case.
  - `edit`: provide feedback and regenerate the test case.
  - `reject`: end the workflow without saving an approved result.
- Uses LangGraph `MemorySaver` checkpointing to resume the interrupted workflow.
- Provides root-level compatibility packages such as `graph`, `nodes`, `config`, and `schemas` for imports when running from the repository root.

## Workflow

The workflow is defined in `agent_1_testcase_generator/graph/workflow.py`:

```text
START
  |
  v
load_document
  |
  v
analyze_requirements
  |
  v
generate_test_cases
  |
  v
validate_test_cases
  |
  v
human_review
  |--------- approve --------> save_test_cases --> END
  |--------- edit -----------> generate_test_cases
  |--------- reject ---------> END
```

### Workflow stages

1. **Load document**
   - Reads the file specified by `input_file` as UTF-8 text.
   - Stores the contents in the workflow state as `user_story`.

2. **Analyze requirements**
   - Sends the user story to the configured LLM.
   - Extracts the user goal, expected behavior, acceptance criteria, and edge cases.
   - Instructs the model not to invent requirements.

3. **Generate test cases**
   - Uses structured output with the `TestCases` Pydantic schema.
   - Currently instructs the model to generate exactly one test case for the highest-priority scenario.
   - Leaves `actual_result` blank for execution-time completion.
   - Uses reviewer feedback when regenerating after an `edit` decision.

4. **Validate test cases**
   - Builds a DeepEval `LLMTestCase` using the original story, generated output, and requirement analysis.
   - Calculates answer relevancy and faithfulness scores.
   - Uses a threshold of `0.7` for both metrics.
   - Stores scores, reasons, and pass/fail flags in the graph state.

5. **Human review**
   - Interrupts execution and waits for a decision.
   - The CLI accepts `approve`, `edit`, or `reject`.

6. **Save approved output**
   - Validates that the generated value is valid JSON.
   - Creates the output directory if necessary.
   - Writes the approved JSON to the configured output path.

## Repository structure

```text
.
├── agent_1_testcase_generator/
│   ├── config/
│   │   └── settings.py          # Environment loading and LLM configuration
│   ├── graph/
│   │   ├── decisions.py         # Human-review routing
│   │   ├── state.py             # Typed workflow state
│   │   └── workflow.py          # LangGraph definition
│   ├── nodes/
│   │   ├── analysis.py           # Requirement analysis
│   │   ├── document.py           # Input document loading
│   │   ├── evaluation.py         # DeepEval validation
│   │   ├── generation.py         # Structured test-case generation
│   │   ├── human_review.py       # Interrupt and review state
│   │   └── save.py               # Approved JSON persistence
│   ├── prompts/
│   ├── schemas/
│   │   └── test_case.py         # Pydantic test-case models
│   ├── testcases/
│   │   └── TC001.txt             # Example requirement document
│   ├── tests/                    # Test placeholders
│   ├── main.py                   # CLI entry point
│   ├── output/
│   │   └── test_cases.json       # Example generated output
│   └── requirements.txt
├── config/                       # Root-level import compatibility wrappers
├── graph/
├── nodes/
├── prompts/
├── schemas/
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.12 or a compatible recent Python version.
- An OpenAI-compatible API key with access to the configured chat model.
- Network access for the LLM and DeepEval evaluation calls.

The project includes a project virtual environment under `agent_1_testcase_generator/.venv/` in the current workspace, but creating a fresh environment is recommended for a new checkout.

## Installation

From the repository root, create and activate a virtual environment:

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

Install the pinned dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r agent_1_testcase_generator/requirements.txt
```

## Configuration

Create `agent_1_testcase_generator/.env` locally. Do not commit this file or place API keys in source code.

Example configuration:

```dotenv
OPENAI_API_KEY=your-api-key
LLM_MODEL=gpt-4o-mini
MAX_ATTEMPTS=3
```

`agent_1_testcase_generator/config/settings.py` loads this file and exposes:

- `LLM_MODEL`: model name passed to `ChatOpenAI`; defaults to `gpt-6-luna` when unset.
- `MAX_ATTEMPTS`: configured maximum-attempt value; defaults to `3`.
- `get_llm()`: creates the configured `ChatOpenAI` client.

The generation node currently displays attempts using a hard-coded `/3` in its console message. If `MAX_ATTEMPTS` is changed, update that behavior before relying on it as an enforcement limit.

## Running the example

Run the CLI from the repository root:

```powershell
python -m agent_1_testcase_generator.main
```

The example uses these default paths:

- Input: `agent_1_testcase_generator/testcases/TC001.txt`
- Output: `agent_1_testcase_generator/output/test_cases.json`
- Checkpoint thread: `qa-practice-001`

After generation and evaluation, the program prompts for a review decision:

```text
Enter approve, edit, or reject:
```

For `edit`, it then asks for feedback and regenerates the test case. For `approve`, the JSON is saved. For `reject`, the workflow exits without writing an approved result.

## Input format

Input files are plain UTF-8 text. Markdown-style requirement documents are supported. The example contains a user story, acceptance criteria, test credentials, and an application URL:

```text
### User Story: Login Functionality

**As a** user,
**I want** to log in using my username and password,
**So that** I can securely access the application.

**Acceptance Criteria:**
1. User should be able to enter a username.
2. User should be able to enter a password.
3. Valid credentials should navigate to the dashboard.
```

To process another document, update the input path in `agent_1_testcase_generator/main.py` or invoke `build_graph()` from your own Python entry point with a custom `input_file` and `output_file`.

## Output format

Generated output follows the Pydantic models in `agent_1_testcase_generator/schemas/test_case.py`:

```json
{
  "test_cases": [
    {
      "test_case_id": "TC001",
      "title": "Valid Login Test",
      "test_data": {
        "username": "validUser",
        "password": "validPassword123"
      },
      "steps": [
        "Navigate to the login page",
        "Enter a valid username",
        "Enter a valid password",
        "Click the Login button"
      ],
      "expected_result": "The user is redirected to the dashboard.",
      "actual_result": ""
    }
  ]
}
```

Each `TestCase` contains:

| Field | Type | Description |
| --- | --- | --- |
| `test_case_id` | `string` | Unique identifier for the test case. |
| `title` | `string` | Short descriptive name. |
| `test_data` | `object` | Key-value test data; values are strings. |
| `steps` | `array[string]` | Ordered manual execution steps. |
| `expected_result` | `string` | Expected behavior after execution. |
| `actual_result` | `string` | Blank until the test is executed. |

## Using the graph programmatically

```python
from agent_1_testcase_generator.graph.workflow import build_graph

workflow = build_graph()
config = {"configurable": {"thread_id": "custom-thread"}}

workflow.invoke(
    {
        "input_file": "path/to/requirements.txt",
        "output_file": "path/to/test_cases.json",
    },
    config=config,
)
```

The initial invocation pauses at the human-review interrupt. Resume it with a LangGraph `Command`:

```python
from langgraph.types import Command

workflow.invoke(
    Command(resume={"decision": "approve", "feedback": ""}),
    config=config,
)
```

Use `decision="edit"` with feedback to regenerate, or `decision="reject"` to terminate without saving.

## Testing

The repository contains `pytest` test files under `agent_1_testcase_generator/tests/`. They currently contain placeholder test classes and do not yet provide functional coverage for the workflow nodes.

Run the available test collection with:

```powershell
python -m pytest agent_1_testcase_generator/tests
```

A full end-to-end run requires configured LLM credentials and may make external model/evaluation calls.

## Extending the project

Common extension points include:

- Add additional input formats in `nodes/document.py`.
- Generate multiple test cases by changing the generation instruction and retaining the `TestCases` list schema.
- Add domain-specific fields to `schemas/test_case.py`.
- Add more evaluation metrics in `nodes/evaluation.py`.
- Replace `MemorySaver` with a durable checkpointer for long-running or multi-user workflows.
- Add a non-interactive review adapter for CI/CD execution.
- Move prompt text from node-local strings into `prompts/prompts.py`.
- Add real unit and integration tests for each node and the conditional routing behavior.

## Security and repository hygiene

- Keep `.env` files and API keys out of version control.
- Treat requirement documents and generated test data as potentially sensitive.
- Review generated test cases before using them against a real application.
- The generator is an assistant for QA authoring; it does not execute browser or API tests.

## License

No license file is currently included. Add a license before distributing the project publicly.
" 
