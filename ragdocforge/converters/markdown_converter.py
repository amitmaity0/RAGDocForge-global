import yaml

from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.quality_models import QualityReport

MAX_METADATA_DISPLAY = 30


class MarkdownConverter:
    def convert(self, document: ParsedDocument, quality_report: QualityReport | None = None) -> str:
        front_matter = {
            "doc_id": document.doc_id,
            "title": document.title,
            "source_file": document.source_file,
            "erp_module": document.detected_erp_module,
            "doc_type": document.detected_doc_type,
            "business_process": document.business_process,
            "rag_priority": "high" if document.error_messages or document.tables else "medium",
            "quality_score": quality_report.overall_score if quality_report else None,
            "readiness_level": quality_report.readiness_level if quality_report else None,
        }
        front_matter = {key: value for key, value in front_matter.items() if value is not None}
        body = document.raw_text.strip() or "_No extractable text was found._"
        source_summary = [
            f"# {document.title or document.doc_id}",
            "",
            "## Source Summary",
            "",
            f"- Source file: {document.source_file}",
            f"- ERP module: {document.detected_erp_module}",
            f"- Document type: {document.detected_doc_type}",
            f"- Business process: {document.business_process or 'UNKNOWN'}",
            "",
            "## Extracted Retrieval Metadata",
            "",
            "### Document-Level Oracle Objects",
            "",
            "#### Tables and Views",
            *_limited_list(document.tables + document.views),
            "",
            "#### Packages",
            *_limited_list(document.packages),
            "",
            "#### Procedures",
            *_limited_list(document.procedures),
            "",
            "#### Functions",
            *_limited_list(document.functions),
            "",
            "### Error Codes",
            *_limited_list(document.error_codes),
            "",
            "### Error Context Lines",
            *_limited_list(document.error_context_lines),
            "",
            "### Keywords",
            *_limited_list(document.keywords),
        ]
        if document.warnings:
            source_summary.extend(["", "## Conversion Warnings", "", *(f"- {warning}" for warning in document.warnings)])
        source_summary.extend(["", "## Original Content", "", body])
        return "---\n" + yaml.safe_dump(front_matter, sort_keys=False).strip() + "\n---\n\n" + "\n".join(source_summary).strip() + "\n"


def _limited_list(values: list[str]) -> list[str]:
    if not values:
        return ["- None detected"]
    displayed = values[:MAX_METADATA_DISPLAY]
    lines = [f"- {value}" for value in displayed]
    if len(values) > MAX_METADATA_DISPLAY:
        lines.append(f"- ... and {len(values) - MAX_METADATA_DISPLAY} more. See metadata_sidecar.json for full metadata.")
    return lines
