from ragdocforge.llm.mock_provider import MockLLMProvider


def test_mock_provider_returns_document_critique_json():
    payload = MockLLMProvider().generate_json("", "", "LLMDocumentCritique")

    assert payload["summary"]
    assert payload["recommended_additions"]


def test_mock_provider_returns_suggested_sections_json():
    payload = MockLLMProvider().generate_json("", "", "LLMSuggestedSectionList")

    assert payload["suggested_sections"][0]["priority"] == "high"


def test_mock_provider_returns_chunk_critique_json():
    payload = MockLLMProvider().generate_json("", "", "LLMChunkCritiqueList")

    assert payload["chunk_critiques"][0]["retrieval_usefulness_score"] == 4
