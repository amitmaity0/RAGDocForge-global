from typing import Literal

from pydantic import BaseModel, Field


class LLMDocumentCritique(BaseModel):
    doc_id: str
    source_file: str
    summary: str
    rag_readiness_assessment: str
    main_strengths: list[str] = Field(default_factory=list)
    major_weaknesses: list[str] = Field(default_factory=list)
    missing_context: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    metadata_improvements: list[str] = Field(default_factory=list)
    retrieval_risk_factors: list[str] = Field(default_factory=list)
    hallucination_risk_factors: list[str] = Field(default_factory=list)
    recommended_additions: list[str] = Field(default_factory=list)
    rewritten_title: str | None = None
    suggested_tags: list[str] = Field(default_factory=list)
    support_questions_answerable: list[str] = Field(default_factory=list)
    support_questions_not_answerable: list[str] = Field(default_factory=list)


class LLMSuggestedSection(BaseModel):
    section_title: str
    reason_needed: str
    suggested_content: str
    priority: Literal["critical", "high", "medium", "low"]
    evidence_supported: bool = False
    requires_sme_confirmation: bool = True
    source_evidence: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"] = "medium"


class LLMChunkCritique(BaseModel):
    chunk_id: str
    retrieval_usefulness_score: int
    answerability_score: int
    chunk_issue_summary: str
    missing_metadata: list[str] = Field(default_factory=list)
    improved_chunk_title: str | None = None
    suggested_keywords: list[str] = Field(default_factory=list)
    should_split: bool = False
    should_merge_with_neighbors: bool = False


class LLMAnalysisBundle(BaseModel):
    doc_id: str
    source_file: str
    provider_name: str
    document_critique: LLMDocumentCritique | None = None
    suggested_sections: list[LLMSuggestedSection] = Field(default_factory=list)
    chunk_critiques: list[LLMChunkCritique] = Field(default_factory=list)
    raw_provider_warnings: list[str] = Field(default_factory=list)
