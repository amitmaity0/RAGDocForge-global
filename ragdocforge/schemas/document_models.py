from pydantic import BaseModel, Field

from ragdocforge.schemas.metadata_models import OracleObjectCandidate


class ParsedDocument(BaseModel):
    doc_id: str
    source_file: str
    file_extension: str
    raw_text: str
    title: str | None = None
    headings: list[str] = Field(default_factory=list)
    detected_erp_module: str = "UNKNOWN"
    detected_doc_type: str = "UNKNOWN"
    user_erp_module: str | None = None
    user_doc_type: str | None = None
    business_process: str | None = None
    tables: list[str] = Field(default_factory=list)
    views: list[str] = Field(default_factory=list)
    packages: list[str] = Field(default_factory=list)
    procedures: list[str] = Field(default_factory=list)
    functions: list[str] = Field(default_factory=list)
    concurrent_programs: list[str] = Field(default_factory=list)
    error_codes: list[str] = Field(default_factory=list)
    error_context_lines: list[str] = Field(default_factory=list)
    error_messages: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    oracle_object_candidates: list[OracleObjectCandidate] = Field(default_factory=list)
    metadata_confidence: float = 1.0
    false_positive_filter_count: int = 0
