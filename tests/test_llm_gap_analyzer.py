from ragdocforge.analyzers.llm_gap_analyzer import LLMGapAnalyzer
from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.llm.mock_provider import MockLLMProvider
from ragdocforge.parsers.base_parser import base_document


def test_llm_gap_analyzer_returns_suggested_sections(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), "# AP SOP\n\n## Purpose\nReview AP_INVOICES_ALL.")
    document = MetadataExtractor().enrich(document, user_doc_type="SOP")
    report = QualityScorer().score(document)
    warnings: list[str] = []

    sections = LLMGapAnalyzer(MockLLMProvider()).analyze(document, report, None, warnings)

    assert sections
    assert sections[0].section_title == "Validation Steps"
    assert not warnings


class _LooseSectionProvider(MockLLMProvider):
    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> dict:
        return {"sections": [{"title": "Diagnostic SQL", "reason": "Needed for retrieval", "content": "[Insert validated SQL]"}]}


def test_llm_gap_analyzer_normalizes_loose_section_payload(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), "# AP SOP\n\n## Purpose\nReview AP_INVOICES_ALL.")
    document = MetadataExtractor().enrich(document, user_doc_type="SOP")
    report = QualityScorer().score(document)
    warnings: list[str] = []

    sections = LLMGapAnalyzer(_LooseSectionProvider()).analyze(document, report, None, warnings)

    assert sections[0].section_title == "Diagnostic SQL"
    assert sections[0].suggested_content == "[Insert validated SQL]"
