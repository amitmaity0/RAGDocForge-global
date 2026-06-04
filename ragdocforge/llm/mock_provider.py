from ragdocforge.llm.provider import LLMProvider


class MockLLMProvider(LLMProvider):
    provider_name = "mock"

    def is_configured(self) -> bool:
        return True

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        if schema_name == "LLMDocumentCritique":
            return {
                "doc_id": "mock_doc",
                "source_file": "mock_source",
                "summary": "Deterministic mock critique for enterprise RAG readiness.",
                "rag_readiness_assessment": "Useful but should include more operational context and validation evidence.",
                "main_strengths": ["Contains source material for support knowledge."],
                "major_weaknesses": ["Missing environment-specific assumptions."],
                "missing_context": ["Owner/version/date", "validated navigation or request parameters"],
                "missing_sections": ["Validation Steps", "Rollback Steps"],
                "metadata_improvements": ["Add business process", "Add module-specific tags"],
                "retrieval_risk_factors": ["Sparse synonyms may reduce recall."],
                "hallucination_risk_factors": ["Missing expected outputs may invite unsupported answers."],
                "recommended_additions": ["Add expected result checks.", "Add object glossary."],
                "rewritten_title": "Mock Enterprise RAG Support Document",
                "suggested_tags": ["oracle-ebs", "support", "rag-ready"],
                "support_questions_answerable": ["What Oracle object is referenced?"],
                "support_questions_not_answerable": ["Which local responsibility should be used?"],
            }
        if schema_name == "LLMSuggestedSectionList":
            return {
                "suggested_sections": [
                    {
                        "section_title": "Validation Steps",
                        "reason_needed": "Support engineers need evidence that remediation succeeded.",
                        "suggested_content": "## Validation Steps\n\n[Insert validated SQL or screen checks]\n\nExpected output:\n[Describe expected status or row count]",
                        "priority": "high",
                    }
                ]
            }
        if schema_name == "LLMChunkCritiqueList":
            return {
                "chunk_critiques": [
                    {
                        "chunk_id": "mock_chunk_0001",
                        "retrieval_usefulness_score": 4,
                        "answerability_score": 3,
                        "chunk_issue_summary": "Chunk is useful but needs more metadata.",
                        "missing_metadata": ["business_process"],
                        "improved_chunk_title": "Mock Chunk Review",
                        "suggested_keywords": ["oracle ebs", "validation"],
                        "should_split": False,
                        "should_merge_with_neighbors": False,
                    }
                ]
            }
        return {}

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        return "Deterministic mock text response."
