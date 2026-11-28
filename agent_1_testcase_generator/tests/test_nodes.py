
from pathlib import Path
from agent_1_testcase_generator.nodes.document import load_document

import pytest

class TestDocumentNode:

    def test_load_document_reads_file(self, tmp_path):
        input_file = (Path(__file__).resolve().parents[1]/ "testcases"/ "TC001.txt")
        state = {"input_file": str(input_file)}
        result = load_document(state)
        expected_user_story = input_file.read_text(encoding="utf-8")
        print(f"Result returned by load_document(): {result}")
        assert result == {
            "user_story": input_file.read_text(encoding="utf-8")
        }

    def test_load_document_raises_when_file_does_not_exist(self, tmp_path):
        missing_file = tmp_path / "missing.txt"
        state = {"input_file": str(missing_file)}
        
        with pytest.raises(FileNotFoundError):
            load_document(state)

    def test_load_document_raises_when_input_file_is_missing(self):
        with pytest.raises(KeyError):
            load_document({})

    def test_load_document_raises_for_invalid_utf8(self, tmp_path):
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_bytes(b"\xff\xfe\xfd")
        
        with pytest.raises(UnicodeDecodeError):
            load_document({"input_file": str(invalid_file)})
