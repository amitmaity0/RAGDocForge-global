from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.llm_analysis_models import LLMAnalysisBundle
from ragdocforge.schemas.quality_models import QualityReport


class OutputSummaryWriter:
    def write(
        self,
        documents: list[ParsedDocument],
        reports: list[QualityReport],
        llm_bundles: list[LLMAnalysisBundle],
        path: str,
    ) -> str:
        reports_by_doc = {report.doc_id: report for report in reports}
        warnings = [warning for bundle in llm_bundles for warning in bundle.raw_provider_warnings]
        lines = [
            "# RAGDocForge Output Summary",
            "",
            "## Artifacts",
            "",
            "- `ragdocforge_outputs/markdown/`: RAG-ready markdown files with YAML front matter.",
            "- `ragdocforge_outputs/chunks.jsonl`: one JSON object per chunk for ingestion.",
            "- `ragdocforge_outputs/quality_report.json`: deterministic quality reports and failed-file records.",
            "- `ragdocforge_outputs/metadata_sidecar.json`: full document-level metadata referenced by chunks.",
            "- `ragdocforge_outputs/llm_analysis_report.json`: optional LLM critique bundles and provider warnings.",
            "- `ragdocforge_outputs/suggested_sections.md`: suggested content additions, when generated.",
            "- `ragdocforge_outputs/manifest.json`: batch metadata and export inventory.",
            "- `ragdocforge_outputs/README_OUTPUTS.md`: guide to the generated artifacts.",
            "",
            "## Documents",
            "",
        ]
        if not documents:
            lines.append("No documents were processed successfully.")
        for document in documents:
            report = reports_by_doc.get(document.doc_id)
            lines.extend(
                [
                    f"### {document.source_file}",
                    "",
                    f"- Document ID: `{document.doc_id}`",
                    f"- ERP module: `{document.detected_erp_module}`",
                    f"- Document type: `{document.detected_doc_type}`",
                    f"- Quality score: `{report.overall_score if report else 'N/A'}`",
                    f"- Readiness: `{report.readiness_level if report else 'N/A'}`",
                    "",
                ]
            )
        if warnings:
            lines.extend(["## LLM Provider Warnings", ""])
            lines.extend(f"- {warning}" for warning in warnings)
            lines.append("")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines).strip() + "\n")
        return path
