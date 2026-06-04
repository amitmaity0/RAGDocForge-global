import yaml

from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.converters.markdown_converter import MarkdownConverter
from ragdocforge.converters.metadata_sidecar_exporter import MetadataSidecarExporter
from ragdocforge.parsers.base_parser import base_document


def test_compact_frontmatter_and_metadata_body(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "journal_import_errors.md"), "# GL Journal Import Errors\n\n```sql\nSELECT * FROM gl_interface\n```"), "GL", "TROUBLESHOOTING_NOTE", "Journal Import")
    report = QualityScorer().score(document)
    markdown = MarkdownConverter().convert(document, report)
    frontmatter = yaml.safe_load(markdown.split("---", 2)[1])

    assert {"doc_id", "title", "source_file", "erp_module", "doc_type", "business_process", "quality_score", "readiness_level"} <= set(frontmatter)
    assert "tables" not in frontmatter
    assert "error_messages" not in frontmatter
    assert "## Extracted Retrieval Metadata" in markdown


def test_metadata_sidecar_contains_full_metadata(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "journal_import_errors.md"), "SELECT * FROM gl_interface"), "GL", "SQL", "Journal Import")
    path = tmp_path / "metadata_sidecar.json"

    MetadataSidecarExporter().write([document], str(path))

    text = path.read_text(encoding="utf-8")
    assert "GL_INTERFACE" in text
    assert "confidence" in text
