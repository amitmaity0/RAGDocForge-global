from ragdocforge.analyzers.llm_chunk_analyzer import LLMChunkAnalyzer
from ragdocforge.converters.chunker import Chunker
from ragdocforge.llm.mock_provider import MockLLMProvider
from ragdocforge.parsers.base_parser import base_document


def test_llm_chunk_analyzer_returns_chunk_critiques(tmp_path):
    document = base_document(str(tmp_path / "sample.md"), "# Purpose\n" + " ".join(["GL_INTERFACE"] * 150))
    document.detected_erp_module = "GL"
    document.detected_doc_type = "SOP"
    chunks = Chunker().chunk(document, chunk_size=100, chunk_overlap=10, min_chunk_tokens=10)
    warnings: list[str] = []

    critiques = LLMChunkAnalyzer(MockLLMProvider(), max_chunks_to_review=2).analyze(chunks, warnings)

    assert len(critiques) == 2
    assert critiques[0].chunk_id == chunks[0].chunk_id
    assert not warnings
