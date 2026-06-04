from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.oracle_object_extractor import extract_error_metadata, extract_error_messages
from ragdocforge.parsers.base_parser import base_document


def test_extract_error_metadata_splits_codes_and_context_lines():
    text = """
    Error
    FRM-41830: List of Values contains no entries.
    Journal import completed with warning for group 100.
    Concurrent Manager encountered an error while running import.
    A short failed
    """

    metadata = extract_error_metadata(text)

    assert metadata.error_codes == ["FRM-41830"]
    assert "Error" not in metadata.error_context_lines
    assert "FRM-41830: List of Values contains no entries." in metadata.error_context_lines
    assert "Journal import completed with warning for group 100." in metadata.error_context_lines
    assert "Concurrent Manager encountered an error while running import." in metadata.error_context_lines
    assert "A short failed" not in metadata.error_context_lines


def test_document_keeps_error_messages_compatibility(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "note.md"), "ORA-00054: resource busy and acquire failed."))

    assert document.error_codes == ["ORA-00054"]
    assert "ORA-00054" in document.error_messages
    assert extract_error_messages(document.raw_text) == document.error_messages
