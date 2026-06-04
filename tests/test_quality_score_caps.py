from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer, QualityCapContext, apply_quality_score_caps
from ragdocforge.parsers.base_parser import base_document
from ragdocforge.schemas.quality_models import QualityDimensionScore


def test_raw_score_with_blocking_issue_caps_to_74(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "note.md"), "# Good Title\n\n" + "word " * 200))
    capped, reasons = apply_quality_score_caps(80, QualityCapContext(document, [QualityDimensionScore(name="Chunkability", score=5, explanation="")], ["blocking"]))

    assert capped <= 74
    assert reasons


def test_unknown_erp_module_caps_to_59(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "note.md"), "# Useful Support Note\n\n## Purpose\nDo work."))
    report = QualityScorer().score(document)

    assert report.overall_score <= 59
    assert report.readiness_level in {"POOR", "NOT_RAG_READY"}
    assert report.score_cap_reasons


def test_troubleshooting_low_procedure_completeness_caps(tmp_path):
    document = MetadataExtractor().enrich(base_document(str(tmp_path / "note.md"), "# GL Journal Import Error\n\nSymptoms only GL_INTERFACE."), "GL", "TROUBLESHOOTING_NOTE")
    report = QualityScorer().score(document)

    assert report.raw_score is not None
    assert report.overall_score <= 69
