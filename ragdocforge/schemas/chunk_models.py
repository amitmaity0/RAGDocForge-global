from pydantic import BaseModel, Field


class RagChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source_file: str
    text: str
    section: str | None = None
    erp_module: str
    doc_type: str
    business_process: str | None = None
    token_estimate: int
    doc_tables: list[str] = Field(default_factory=list)
    doc_views: list[str] = Field(default_factory=list)
    doc_packages: list[str] = Field(default_factory=list)
    doc_procedures: list[str] = Field(default_factory=list)
    doc_functions: list[str] = Field(default_factory=list)
    doc_error_codes: list[str] = Field(default_factory=list)
    doc_error_context_lines: list[str] = Field(default_factory=list)
    doc_error_messages: list[str] = Field(default_factory=list)
    doc_keywords: list[str] = Field(default_factory=list)
    chunk_tables: list[str] = Field(default_factory=list)
    chunk_views: list[str] = Field(default_factory=list)
    chunk_packages: list[str] = Field(default_factory=list)
    chunk_procedures: list[str] = Field(default_factory=list)
    chunk_functions: list[str] = Field(default_factory=list)
    concurrent_programs: list[str] = Field(default_factory=list)
    chunk_error_codes: list[str] = Field(default_factory=list)
    chunk_error_context_lines: list[str] = Field(default_factory=list)
    chunk_error_messages: list[str] = Field(default_factory=list)
    chunk_keywords: list[str] = Field(default_factory=list)
    rag_priority: str = "medium"
    metadata_confidence: float = 1.0

    @property
    def tables(self) -> list[str]:
        return self.chunk_tables

    @property
    def views(self) -> list[str]:
        return self.chunk_views

    @property
    def packages(self) -> list[str]:
        return self.chunk_packages

    @property
    def procedures(self) -> list[str]:
        return self.chunk_procedures

    @property
    def functions(self) -> list[str]:
        return self.chunk_functions

    @property
    def error_messages(self) -> list[str]:
        return self.chunk_error_messages

    @property
    def keywords(self) -> list[str]:
        return self.chunk_keywords
