from ragdocforge.analyzers.llm_document_analyzer import LLMDocumentAnalyzer
from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.converters.markdown_converter import MarkdownConverter
from ragdocforge.llm.mock_provider import MockLLMProvider
from ragdocforge.llm.provider import LLMProviderError
from ragdocforge.parsers.base_parser import base_document


class _FailingProvider(MockLLMProvider):
    provider_name = "failing"

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> dict:
        raise LLMProviderError("controlled failure")


class _InvalidProvider(MockLLMProvider):
    provider_name = "invalid"

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> dict:
        return {"bad": "payload"}


def _sample_inputs(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), "# GL SOP\n\n## Purpose\nValidate GL_INTERFACE rows.")
    document = MetadataExtractor().enrich(document, business_process="Journal Import")
    report = QualityScorer().score(document)
    markdown = MarkdownConverter().convert(document)
    return document, report, markdown


def test_llm_document_analyzer_returns_critique(tmp_path):
    document, report, markdown = _sample_inputs(tmp_path)
    warnings: list[str] = []

    critique = LLMDocumentAnalyzer(MockLLMProvider()).analyze(document, report, markdown, warnings)

    assert critique is not None
    assert critique.doc_id == document.doc_id
    assert not warnings


def test_llm_document_analyzer_provider_failure_does_not_crash(tmp_path):
    document, report, markdown = _sample_inputs(tmp_path)
    warnings: list[str] = []

    critique = LLMDocumentAnalyzer(_FailingProvider()).analyze(document, report, markdown, warnings)

    assert critique is None
    assert "controlled failure" in warnings


def test_llm_document_analyzer_validation_failure_records_warning(tmp_path):
    document, report, markdown = _sample_inputs(tmp_path)
    warnings: list[str] = []

    critique = LLMDocumentAnalyzer(_InvalidProvider()).analyze(document, report, markdown, warnings)

    assert critique is None
    assert warnings
