from ragdocforge.analyzers.metadata_extractor import MetadataExtractor, extract_best_title
from ragdocforge.parsers.base_parser import base_document


def test_summary_heading_is_rejected_as_title(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "journal_import_errors.md"), "# Summary\n\n## Solution\nGL_INTERFACE details."), "GL", "TROUBLESHOOTING_NOTE", "Journal Import")

    assert document.title == "Journal Import Errors"


def test_filename_title_cleanup():
    assert extract_best_title("# Summary", "journal_import_errors.md", ["Summary"], None, None, None) == "Journal Import Errors"


def test_generated_title_when_filename_is_generic():
    title = extract_best_title("# Summary", "summary.md", ["Summary"], "GL", "Journal Import", "TROUBLESHOOTING_NOTE")

    assert title == "GL Journal Import Troubleshooting Note"


def test_non_generic_h1_is_accepted():
    assert extract_best_title("# GL Journal Import Errors", "summary.md", ["GL Journal Import Errors"], None, None, None) == "GL Journal Import Errors"


def test_numbered_question_heading_is_rejected():
    title = extract_best_title("# Summary\n\n### 1. What is Group ID used for?", "journal_import_errors.md", ["Summary", "1. What is Group ID used for?"], "GL", "Journal Import", "TROUBLESHOOTING_NOTE")

    assert title == "Journal Import Errors"
