from typing import Literal

from pydantic import BaseModel, Field


EvidenceType = Literal[
    "sql_from",
    "sql_join",
    "sql_update",
    "sql_insert_into",
    "sql_delete_from",
    "sql_merge_into",
    "create_package",
    "create_package_body",
    "create_procedure",
    "create_function",
    "package_member_call",
    "known_ebs_prefix",
    "schema_qualified",
    "plsql_signature",
    "weak_text_match",
]


class OracleObjectCandidate(BaseModel):
    name: str
    object_type: Literal["table", "view", "package", "procedure", "function", "unknown"]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str | None = None
    evidence_type: EvidenceType | None = None
    source_span_start: int | None = None
    source_span_end: int | None = None


class ErrorMetadata(BaseModel):
    error_codes: list[str] = Field(default_factory=list)
    error_context_lines: list[str] = Field(default_factory=list)
