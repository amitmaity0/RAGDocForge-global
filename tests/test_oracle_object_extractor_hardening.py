from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.oracle_object_extractor import extract_oracle_object_candidates
from ragdocforge.parsers.base_parser import base_document


def test_extracts_valid_sql_context_objects():
    text = """
    SELECT * FROM gl_interface;
    SELECT * FROM apps.gl_je_headers h JOIN gl_je_lines l ON h.je_header_id = l.je_header_id;
    UPDATE xxgl_interface_stg SET status = 'E';
    MERGE INTO xxgl_stage xs USING dual ON (1=1);
    """
    candidates, _ = extract_oracle_object_candidates(text)
    names = {candidate.name for candidate in candidates}

    assert {"GL_INTERFACE", "GL_JE_HEADERS", "GL_JE_LINES", "XXGL_INTERFACE_STG", "XXGL_STAGE"} <= names
    assert all(candidate.confidence >= 0.70 for candidate in candidates if candidate.name in names)


def test_extracts_plsql_signatures():
    text = "CREATE OR REPLACE PACKAGE xxgl_journal_diag_pkg AS PROCEDURE diagnose_group(p_group_id NUMBER); END;"
    candidates, _ = extract_oracle_object_candidates(text)
    names = {candidate.name for candidate in candidates}

    assert "XXGL_JOURNAL_DIAG_PKG" in names
    assert "DIAGNOSE_GROUP" in names


def test_rejects_stopwords_and_uppercase_prose(tmp_path):
    text = "A THE THIS CAN IS ON RETURN GENERAL ORACLE WARNING NOTE SUMMARY SOLUTION REFERENCES"
    document = base_document(str(tmp_path / "note.md"), text)
    document = MetadataExtractor().enrich(document)

    forbidden = set(text.split())
    extracted = set(document.tables + document.packages + document.procedures + document.functions)

    assert not forbidden & extracted
    assert document.false_positive_filter_count >= 0


def test_fixture_extracts_only_expected_objects(tmp_path):
    fixture = "tests/fixtures/journal_import_errors_sample.md"
    document = MetadataExtractor().enrich(base_document(fixture, open(fixture, encoding="utf-8").read()))

    assert "GL_INTERFACE" in document.tables
    assert "FND_LOOKUP_VALUES" in document.tables
    assert {"FRM-41830", "APP-00268", "ORA-00054"} <= set(document.error_messages)
    assert "ORACLE" not in document.tables
    assert "GENERAL" not in document.tables
