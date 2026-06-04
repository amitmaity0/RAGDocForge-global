from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.parsers.base_parser import base_document


def test_quality_scorer_reports_missing_sections(tmp_path):
    document = base_document(str(tmp_path / "sop.md"), "# AP Invoice SOP\nPurpose\nAccounts payable invoice workbench.")
    document = MetadataExtractor().enrich(document, user_doc_type="SOP")

    report = QualityScorer().score(document)

    assert report.overall_score > 0
    assert "Prerequisites" in report.missing_sections


def test_quality_scorer_has_eight_dimensions_and_unknown_module_blocker(tmp_path):
    document = base_document(str(tmp_path / "note.md"), "Unstructured support note with vague content.")
    document = MetadataExtractor().enrich(document)

    report = QualityScorer().score(document)

    assert len(report.dimensions) == 8
    assert "Missing or unclear ERP module metadata." in report.blocking_issues


def test_quality_scorer_rewards_structured_sop_over_unstructured_text(tmp_path):
    structured = base_document(
        str(tmp_path / "structured.md"),
        "# GL Journal Import SOP\n\n## Purpose\nSupport journal import.\n\n## Scope\nGL users.\n\n## Prerequisites\nLedger is known.\n\n## Procedure\nStep 1 validate GL_INTERFACE.\n\n## Validation\nConfirm GL_JE_HEADERS rows.\n\n## Rollback\nReverse corrections if needed.",
    )
    unstructured = base_document(str(tmp_path / "plain.md"), "Journal import issue. Run this. Fix issue.")

    structured_report = QualityScorer().score(MetadataExtractor().enrich(structured, business_process="Journal Import"))
    unstructured_report = QualityScorer().score(MetadataExtractor().enrich(unstructured))

    assert structured_report.overall_score > unstructured_report.overall_score


def test_quality_scorer_rewards_sql_with_context_and_tables(tmp_path):
    contextual = base_document(str(tmp_path / "with_context.sql"), "-- Purpose: inspect AP invoice rows\nselect * from ap_invoices_all where invoice_id = :invoice_id;")
    vague = base_document(str(tmp_path / "without_context.sql"), "select 1 from dual")

    contextual_report = QualityScorer().score(MetadataExtractor().enrich(contextual))
    vague_report = QualityScorer().score(MetadataExtractor().enrich(vague))

    assert contextual_report.overall_score > vague_report.overall_score
