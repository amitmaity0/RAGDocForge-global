import json

from ragdocforge.converters.chunker import Chunker
from ragdocforge.converters.jsonl_exporter import JsonlExporter
from ragdocforge.parsers.base_parser import base_document


def test_chunker_creates_stable_ids(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), " ".join(["word"] * 250))
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"

    chunks = Chunker().chunk(document, chunk_size=300, chunk_overlap=10)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "sample_0001"


def test_chunker_is_heading_aware_and_inherits_metadata(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), "# Purpose\nGL_INTERFACE overview " + " ".join(["detail"] * 130) + "\n\n# Validation\nConfirm GL_JE_HEADERS " + " ".join(["detail"] * 130))
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"
    document.tables = ["GL_INTERFACE", "GL_JE_HEADERS"]

    chunks = Chunker().chunk(document, chunk_size=300, chunk_overlap=10)

    assert [chunk.section for chunk in chunks] == ["Purpose", "Validation"]
    assert chunks[0].erp_module == "GL"
    assert chunks[0].chunk_tables == []
    assert chunks[0].doc_tables == ["GL_INTERFACE", "GL_JE_HEADERS"]


def test_jsonl_export_serializes_chunks(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), " ".join(["word"] * 120))
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"
    chunks = Chunker().chunk(document, chunk_size=100, chunk_overlap=10)
    path = tmp_path / "chunks.jsonl"

    JsonlExporter().write(chunks, str(path))

    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["chunk_id"] == "sample_0001"
    assert "metadata" in json.loads(lines[0])
