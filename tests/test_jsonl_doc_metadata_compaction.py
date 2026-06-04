import json

from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.converters.chunker import Chunker
from ragdocforge.converters.jsonl_exporter import INCLUDE_FULL_DOC_METADATA_IN_CHUNKS, JsonlExporter
from ragdocforge.parsers.base_parser import base_document


def test_jsonl_uses_compact_doc_metadata_reference(tmp_path):
    text = """
    # Journal Import
    ```sql
    SELECT * FROM gl_interface gi, gl_je_lines l WHERE gi.group_id = :group_id;
    ```
    ORA-00054: resource busy and acquire with NOWAIT specified.
    Resolution: rerun after the locking session completes.
    """
    document = MetadataExtractor().enrich(base_document("journal_import_errors.md", text), "GL", "TROUBLESHOOTING_NOTE", "Journal Import")
    chunks = Chunker().chunk(document, chunk_size=120, chunk_overlap=10)
    path = tmp_path / "chunks.jsonl"

    JsonlExporter().write(chunks, str(path))
    record = json.loads(path.read_text(encoding="utf-8").splitlines()[0])
    doc_level = record["metadata"]["doc_level"]
    chunk_level = record["metadata"]["chunk_level"]

    assert INCLUDE_FULL_DOC_METADATA_IN_CHUNKS is False
    assert doc_level["metadata_ref"] == f"metadata_sidecar.json#{document.doc_id}"
    assert doc_level["tables_count"] >= 2
    assert doc_level["error_codes_count"] == 1
    assert doc_level["top_error_codes"] == ["ORA-00054"]
    assert "tables" not in doc_level
    assert "error_context_lines" not in doc_level
    assert "error_codes" in chunk_level
    assert "error_context_lines" in chunk_level
