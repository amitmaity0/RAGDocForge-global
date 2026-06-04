from ragdocforge.converters.chunker import Chunker, should_preserve_small_chunk
from ragdocforge.parsers.base_parser import base_document


def test_heading_only_chunk_merges_with_next(tmp_path):
    text = "# Tiny\n\n# Details\n" + " ".join(["GL_INTERFACE"] * 140)
    document = base_document(str(tmp_path / "sample.md"), text)
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"

    chunks = Chunker().chunk(document, chunk_size=700, chunk_overlap=100)

    assert len(chunks) == 1
    assert "Tiny" in chunks[0].text


def test_last_short_chunk_merges_with_previous(tmp_path):
    text = "# Details\n" + " ".join(["word"] * 140) + "\n\n# Tail\nshort"
    document = base_document(str(tmp_path / "sample.md"), text)
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"

    chunks = Chunker().chunk(document, chunk_size=700, chunk_overlap=100)

    assert len(chunks) == 1
    assert "Tail" in chunks[0].text


def test_preserve_small_error_chunk():
    assert should_preserve_small_chunk("ORA-00054: resource busy")
