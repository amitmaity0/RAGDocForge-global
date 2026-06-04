import json
from datetime import datetime, timezone
from uuid import uuid4

from ragdocforge.schemas.chunk_models import RagChunk
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.llm_analysis_models import LLMAnalysisBundle
from ragdocforge.schemas.quality_models import QualityReport
from ragdocforge.analyzers.oracle_object_extractor import MIN_OBJECT_CONFIDENCE
from ragdocforge.converters.jsonl_exporter import INCLUDE_FULL_DOC_METADATA_IN_CHUNKS


class ManifestWriter:
    def write(
        self,
        documents: list[ParsedDocument],
        reports: list[QualityReport],
        chunks: list[RagChunk],
        path: str,
        failures: list[dict] | None = None,
        llm_enabled: bool = False,
        llm_provider: str = "disabled",
        llm_model: str = "",
        llm_bundles: list[LLMAnalysisBundle] | None = None,
    ) -> str:
        failures = failures or []
        llm_bundles = llm_bundles or []
        llm_warnings = [warning for bundle in llm_bundles for warning in bundle.raw_provider_warnings]
        reports_by_doc = {report.doc_id: report for report in reports}
        chunks_by_doc = {document.doc_id: [chunk for chunk in chunks if chunk.doc_id == document.doc_id] for document in documents}
        manifest = {
            "batch_id": str(uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "documents_processed": len(documents),
            "documents_failed": len(failures),
            "chunks_created": len(chunks),
            "supported_file_types": [".pdf", ".docx", ".txt", ".md", ".sql", ".pls", ".pkb", ".pks"],
            "outputs": {
                "root_dir": "ragdocforge_outputs/",
                "markdown_dir": "ragdocforge_outputs/markdown/",
                "chunks_jsonl": "ragdocforge_outputs/chunks.jsonl",
                "quality_report": "ragdocforge_outputs/quality_report.json",
                "llm_analysis_report": "ragdocforge_outputs/llm_analysis_report.json",
                "suggested_sections": "ragdocforge_outputs/suggested_sections.md",
                "output_summary": "ragdocforge_outputs/output_summary.md",
                "metadata_sidecar": "ragdocforge_outputs/metadata_sidecar.json",
                "readme_outputs": "ragdocforge_outputs/README_OUTPUTS.md",
            },
            "documents": [
                {
                    "doc_id": doc.doc_id,
                    "source_file": doc.source_file,
                    "erp_module": doc.detected_erp_module,
                    "doc_type": doc.detected_doc_type,
                    "quality_score": reports_by_doc[doc.doc_id].overall_score if doc.doc_id in reports_by_doc else None,
                    "raw_quality_score": reports_by_doc[doc.doc_id].raw_score if doc.doc_id in reports_by_doc else None,
                    "score_cap_reasons": reports_by_doc[doc.doc_id].score_cap_reasons if doc.doc_id in reports_by_doc else [],
                    "metadata_confidence": doc.metadata_confidence,
                    "error_codes_count": len(doc.error_codes),
                    "error_context_lines_count": len(doc.error_context_lines),
                    "doc_level_metadata_ref": f"metadata_sidecar.json#{doc.doc_id}",
                    "chunks_created": len(chunks_by_doc.get(doc.doc_id, [])),
                }
                for doc in documents
            ],
            "failures": failures,
            "llm_analysis_enabled": llm_enabled,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
            "llm_documents_analyzed": sum(1 for bundle in llm_bundles if bundle.document_critique is not None),
            "llm_chunk_critiques_created": sum(len(bundle.chunk_critiques) for bundle in llm_bundles),
            "llm_provider_warnings": llm_warnings,
            "metadata_quality_hardening_enabled": True,
            "object_extraction": {
                "min_object_confidence": MIN_OBJECT_CONFIDENCE,
                "stopword_filtering_enabled": True,
                "known_ebs_prefix_filtering_enabled": True,
            },
            "chunk_metadata_mode": "document_and_chunk_level_separated",
            "metadata_precision_refinement_enabled": True,
            "error_metadata_mode": "split_error_codes_and_context_lines",
            "chunk_doc_metadata_mode": "compact_ref_with_counts",
            "include_full_doc_metadata_in_chunks": INCLUDE_FULL_DOC_METADATA_IN_CHUNKS,
            "llm_evidence_postprocessing_enabled": True,
            "quality_score_caps_enabled": True,
            "metadata_sidecar_path": "metadata_sidecar.json",
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
        return path
