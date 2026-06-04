import json
from pathlib import Path

from ragdocforge.llm.json_utils import extract_first_json_object, validate_or_warn
from ragdocforge.llm.provider import LLMProvider, LLMProviderError
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.llm_analysis_models import LLMDocumentCritique
from ragdocforge.schemas.quality_models import QualityReport


class LLMDocumentAnalyzer:
    def __init__(self, provider: LLMProvider, max_doc_chars: int = 20000) -> None:
        self.provider = provider
        self.max_doc_chars = max_doc_chars
        self.system_prompt = _read_prompt("llm_document_critique.md")

    def analyze(self, document: ParsedDocument, quality_report: QualityReport, rag_markdown: str, warnings: list[str]) -> LLMDocumentCritique | None:
        try:
            payload = self.provider.generate_json(
                self.system_prompt,
                self._build_user_prompt(document, quality_report, rag_markdown),
                "LLMDocumentCritique",
                max_tokens=1400,
            )
        except LLMProviderError as exc:
            warnings.append(str(exc))
            return None
        if not payload:
            warnings.append("LLM document critique returned an empty payload.")
            return None
        normalized = dict(payload)
        normalized["doc_id"] = document.doc_id
        normalized["source_file"] = document.source_file
        result = validate_or_warn(LLMDocumentCritique, normalized, warnings)
        if result is None:
            extracted = extract_first_json_object(json.dumps(payload))
            if isinstance(extracted, dict):
                extracted["doc_id"] = document.doc_id
                extracted["source_file"] = document.source_file
                return validate_or_warn(LLMDocumentCritique, extracted, warnings)  # type: ignore[return-value]
        return result  # type: ignore[return-value]

    def _build_user_prompt(self, document: ParsedDocument, quality_report: QualityReport, rag_markdown: str) -> str:
        input_payload = {
            "task": "Return exactly one JSON object matching the required_schema. Use empty arrays when evidence is missing.",
            "required_schema": {
                "summary": "string",
                "rag_readiness_assessment": "string",
                "main_strengths": ["string"],
                "major_weaknesses": ["string"],
                "missing_context": ["string"],
                "missing_sections": ["string"],
                "metadata_improvements": ["string"],
                "retrieval_risk_factors": ["string"],
                "hallucination_risk_factors": ["string"],
                "recommended_additions": ["string"],
                "rewritten_title": "string or null",
                "suggested_tags": ["string"],
                "support_questions_answerable": ["string"],
                "support_questions_not_answerable": ["string"],
            },
            "source_file": document.source_file,
            "title": document.title,
            "erp_module": document.detected_erp_module,
            "doc_type": document.detected_doc_type,
            "business_process": document.business_process,
            "headings": document.headings,
            "tables": document.tables,
            "views": document.views,
            "packages": document.packages,
            "procedures": document.procedures,
            "quality_report": quality_report.model_dump(),
            "document_text": document.raw_text[: self.max_doc_chars],
            "rag_markdown_preview": rag_markdown[: min(self.max_doc_chars, 8000)],
        }
        return json.dumps(input_payload, indent=2)


def _read_prompt(name: str) -> str:
    return (Path(__file__).resolve().parents[1] / "prompts" / name).read_text(encoding="utf-8")
