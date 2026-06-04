from pydantic import BaseModel

from ragdocforge.llm.json_utils import extract_first_json_object, validate_or_warn


class _ExampleModel(BaseModel):
    name: str


def test_extract_first_json_object_valid_json():
    assert extract_first_json_object('{"name": "ok"}') == {"name": "ok"}


def test_extract_first_json_object_from_markdown_fence():
    assert extract_first_json_object('```json\n{"name": "ok"}\n```') == {"name": "ok"}


def test_extract_first_json_object_handles_surrounding_text_and_array():
    assert extract_first_json_object('prefix [{"name": "ok"}] suffix') == [{"name": "ok"}]


def test_validate_or_warn_records_invalid_payload():
    warnings: list[str] = []

    result = validate_or_warn(_ExampleModel, {"wrong": "field"}, warnings)

    assert result is None
    assert warnings
