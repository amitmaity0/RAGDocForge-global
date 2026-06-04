import json
import re
from pathlib import Path

from pydantic import BaseModel, Field

from ragdocforge.llm.json_utils import validate_or_warn
from ragdocforge.llm.provider import LLMProvider, LLMProviderError
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.llm_analysis_models import LLMDocumentCritique, LLMSuggestedSection
from ragdocforge.schemas.quality_models import QualityReport


class _SuggestedSectionList(BaseModel):
    suggested_sections: list[LLMSuggestedSection] = Field(default_factory=list)


class LLMGapAnalyzer:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider
        self.system_prompt = _read_prompt("llm_gap_analysis.md")

    def analyze(
        self,
        document: ParsedDocument,
        quality_report: QualityReport,
        critique: LLMDocumentCritique | None,
        warnings: list[str],
    ) -> list[LLMSuggestedSection]:
        try:
            payload = self.provider.generate_json(
                self.system_prompt,
                self._build_user_prompt(document, quality_report, critique),
                "LLMSuggestedSectionList",
            )
        except LLMProviderError as exc:
            warnings.append(str(exc))
            return self._fallback_sections(quality_report)
        normalized = self._normalize_payload(payload)
        result = validate_or_warn(_SuggestedSectionList, normalized, warnings)
        if isinstance(result, _SuggestedSectionList) and result.suggested_sections:
            return enrich_suggested_sections_with_evidence(result.suggested_sections, document)
        return enrich_suggested_sections_with_evidence(self._fallback_sections(quality_report), document)

    def _build_user_prompt(self, document: ParsedDocument, quality_report: QualityReport, critique: LLMDocumentCritique | None) -> str:
        payload = {
            "task": "Return exactly one JSON object with key suggested_sections. Do not return a raw array.",
            "required_schema": {
                "suggested_sections": [
                    {
                        "section_title": "string",
                        "reason_needed": "string",
                        "suggested_content": "string with placeholders for unknown site-specific facts",
                        "priority": "critical | high | medium | low",
                        "evidence_supported": "boolean",
                        "requires_sme_confirmation": "boolean",
                        "source_evidence": ["string"],
                        "confidence": "low | medium | high",
                    }
                ]
            },
            "source_file": document.source_file,
            "doc_id": document.doc_id,
            "headings": document.headings,
            "missing_sections": quality_report.missing_sections,
            "blocking_issues": quality_report.blocking_issues,
            "document_critique": critique.model_dump() if critique else None,
        }
        return json.dumps(payload, indent=2)

    def _normalize_payload(self, payload) -> dict:
        if isinstance(payload, list):
            return {"suggested_sections": payload}
        if not isinstance(payload, dict):
            return {"suggested_sections": []}
        if "suggested_sections" in payload:
            return payload
        for key in ("sections", "missing_sections", "recommendations", "suggestions"):
            value = payload.get(key)
            if isinstance(value, list):
                normalized = []
                for item in value:
                    if isinstance(item, dict):
                        normalized.append(
                            {
                                "section_title": item.get("section_title") or item.get("title") or item.get("name") or "Suggested Section",
                                "reason_needed": item.get("reason_needed") or item.get("reason") or "Improves RAG completeness.",
                                "suggested_content": item.get("suggested_content") or item.get("content") or "[Add validated content here]",
                                "priority": item.get("priority") if item.get("priority") in {"critical", "high", "medium", "low"} else "medium",
                                "evidence_supported": bool(item.get("evidence_supported", False)),
                                "requires_sme_confirmation": bool(item.get("requires_sme_confirmation", True)),
                                "source_evidence": item.get("source_evidence") if isinstance(item.get("source_evidence"), list) else [],
                                "confidence": item.get("confidence") if item.get("confidence") in {"low", "medium", "high"} else "medium",
                            }
                        )
                    elif isinstance(item, str):
                        normalized.append(
                            {
                                "section_title": item,
                                "reason_needed": "Suggested by the LLM as missing or useful context.",
                                "suggested_content": f"## {item}\n\n[Add validated {item.lower()} details here]",
                                "priority": "medium",
                                "evidence_supported": False,
                                "requires_sme_confirmation": True,
                                "source_evidence": [],
                                "confidence": "medium",
                            }
                        )
                return {"suggested_sections": normalized}
        return {"suggested_sections": []}

    def _fallback_sections(self, quality_report: QualityReport) -> list[LLMSuggestedSection]:
        sections = quality_report.missing_sections[:4] or ["Validation Steps"]
        return [
            LLMSuggestedSection(
                section_title=section,
                reason_needed="Deterministic fallback because the LLM did not return a valid suggested_sections payload.",
                suggested_content=f"## {section}\n\n[Add validated {section.lower()} details here]\n\nExpected evidence:\n[Describe source-backed checks or placeholders]",
                priority="high" if index == 0 else "medium",
                evidence_supported=False,
                requires_sme_confirmation=True,
                source_evidence=["No complete section was detected in the source document."],
                confidence="medium",
            )
            for index, section in enumerate(sections)
        ]


def enrich_suggested_sections_with_evidence(
    suggested_sections: list[LLMSuggestedSection],
    parsed_document: ParsedDocument,
    metadata_sidecar_entry: dict | None = None,
) -> list[LLMSuggestedSection]:
    sidecar_codes = list(metadata_sidecar_entry.get("error_codes", [])) if metadata_sidecar_entry else []
    sidecar_context = list(metadata_sidecar_entry.get("error_context_lines", [])) if metadata_sidecar_entry else []
    error_codes = parsed_document.error_codes or sidecar_codes
    context_lines = parsed_document.error_context_lines or sidecar_context
    for section in suggested_sections:
        searchable = " ".join([section.section_title, section.reason_needed, section.suggested_content])
        matched_codes = [code for code in error_codes if re.search(rf"\b{re.escape(code)}\b", searchable, re.I)]
        if not matched_codes:
            section.evidence_supported = False
            section.requires_sme_confirmation = True
            section.confidence = section.confidence or "medium"
            continue
        evidence = [
            line
            for line in context_lines
            if any(re.search(rf"\b{re.escape(code)}\b", line, re.I) for code in matched_codes)
        ]
        if not evidence:
            evidence = matched_codes
        section.evidence_supported = True
        section.requires_sme_confirmation = True
        section.source_evidence = sorted(set(section.source_evidence + evidence))
        section.confidence = "medium"
    return suggested_sections


def _read_prompt(name: str) -> str:
    return (Path(__file__).resolve().parents[1] / "prompts" / name).read_text(encoding="utf-8")
