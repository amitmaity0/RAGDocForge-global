from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.parsers.base_parser import base_document
from ragdocforge.parsers.parser_router import ParserRouter


def test_metadata_extractor_detects_title_and_module(tmp_path):
    path = tmp_path / "gl.md"
    document = base_document(str(path), "# Journal Import\nPurpose\nGL_INTERFACE rows for general ledger journal import.")

    enriched = MetadataExtractor().enrich(document)

    assert enriched.title == "Journal Import"
    assert enriched.detected_erp_module == "GL"
    assert "Purpose" in enriched.headings


def test_metadata_extractor_detects_sql_and_sop_types(tmp_path):
    sql_doc = base_document(str(tmp_path / "query.sql"), "select * from ap_invoices_all")
    sop_doc = base_document(str(tmp_path / "sop.md"), "# AP Invoice SOP\n## Prerequisites\n## Validation\nStep 1: confirm invoice.")

    assert MetadataExtractor().enrich(sql_doc).detected_doc_type == "SQL"
    assert MetadataExtractor().enrich(sop_doc).detected_doc_type == "SOP"


def test_parser_router_returns_warning_for_unsupported_extension(tmp_path):
    path = tmp_path / "image.png"
    path.write_text("not supported", encoding="utf-8")

    document = ParserRouter().parse(str(path))

    assert document.raw_text == ""
    assert "Unsupported file extension" in document.warnings[0]
