from pathlib import Path

from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.parsers.parser_router import ParserRouter


EXAMPLES = [
    Path("examples/sample_gl_journal_import_sop.md"),
    Path("examples/sample_gl_diagnostic_sql.sql"),
    Path("examples/sample_custom_plsql_package.pks"),
    Path("examples/sample_low_quality_note.txt"),
]


def test_all_slice3_example_files_exist():
    assert all(path.exists() for path in EXAMPLES)


def test_examples_process_successfully_and_low_quality_scores_lower():
    router = ParserRouter()
    extractor = MetadataExtractor()
    scorer = QualityScorer()

    sop = extractor.enrich(router.parse(str(EXAMPLES[0])), "GL", "SOP", "Journal Import")
    low = extractor.enrich(router.parse(str(EXAMPLES[3])), "GL", "TROUBLESHOOTING_NOTE", "Journal Import")

    assert scorer.score(sop).overall_score > scorer.score(low).overall_score


def test_sample_sql_detects_gl_interface():
    document = MetadataExtractor().enrich(ParserRouter().parse(str(EXAMPLES[1])), "GL", "SQL", "Journal Import")

    assert "GL_INTERFACE" in document.tables


def test_sample_plsql_detects_package_procedure_and_function():
    document = MetadataExtractor().enrich(ParserRouter().parse(str(EXAMPLES[2])), "GL", "PLSQL", "Journal Import")

    assert "XXGL_JOURNAL_DIAG_PKG" in document.packages
    assert "DIAGNOSE_GROUP" in document.procedures
    assert "GET_INTERFACE_STATUS" in document.functions
