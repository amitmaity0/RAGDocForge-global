import json

from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.converters.chunker import Chunker
from ragdocforge.converters.jsonl_exporter import JsonlExporter
from ragdocforge.parsers.base_parser import base_document


def _document():
    text = """
# GL Interface Lookup
```sql
SELECT status, group_id
FROM gl_interface
WHERE group_id = :group_id;
```
""" + " ".join(["interface detail"] * 140) + """

# Lookup Values
```sql
SELECT lookup_code, meaning
FROM fnd_lookup_values
WHERE lookup_type = 'IMPORT_ERROR';
```
""" + " ".join(["lookup detail"] * 140) + """

# Error Codes
FRM-41830: List of Values contains no entries.
APP-00268: Unable to find period.
ORA-00054: resource busy and acquire with NOWAIT specified.
""" + " ".join(["error detail"] * 140)
    return MetadataExtractor().enrich(base_document("tests/fixtures/journal_import_errors_sample.md", text), "GL", "TROUBLESHOOTING_NOTE", "Journal Import")


def test_chunk_metadata_separates_document_and_chunk_level(tmp_path):
    document = _document()
    chunks = Chunker().chunk(document, chunk_size=150, chunk_overlap=20)

    assert "GL_INTERFACE" in document.tables
    assert "FND_LOOKUP_VALUES" in document.tables
    assert any("GL_INTERFACE" in chunk.chunk_tables for chunk in chunks)
    assert any("FND_LOOKUP_VALUES" not in chunk.chunk_tables for chunk in chunks)
    assert all("GL_INTERFACE" in chunk.doc_tables for chunk in chunks)

    path = tmp_path / "chunks.jsonl"
    JsonlExporter().write(chunks, str(path))
    first = json.loads(path.read_text(encoding="utf-8").splitlines()[0])

    assert "doc_level" in first["metadata"]
    assert "chunk_level" in first["metadata"]
    assert "tables" not in first["metadata"]


def test_chunk_level_errors_are_local_only():
    document = _document()
    chunks = Chunker().chunk(document, chunk_size=150, chunk_overlap=20)

    error_chunks = [chunk for chunk in chunks if chunk.chunk_error_messages]
    non_error_chunks = [chunk for chunk in chunks if not chunk.chunk_error_messages]

    assert error_chunks
    assert non_error_chunks
