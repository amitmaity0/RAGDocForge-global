import json
import shutil
import tempfile
import time
from pathlib import Path

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from ragdocforge.config import load_app_settings
from ragdocforge.analyzers.llm_chunk_analyzer import LLMChunkAnalyzer
from ragdocforge.analyzers.llm_document_analyzer import LLMDocumentAnalyzer
from ragdocforge.analyzers.llm_gap_analyzer import LLMGapAnalyzer
from ragdocforge.analyzers.metadata_extractor import MetadataExtractor
from ragdocforge.analyzers.quality_scorer import QualityScorer
from ragdocforge.converters.chunker import Chunker
from ragdocforge.converters.jsonl_exporter import JsonlExporter
from ragdocforge.converters.manifest_writer import ManifestWriter
from ragdocforge.converters.markdown_converter import MarkdownConverter
from ragdocforge.converters.metadata_sidecar_exporter import MetadataSidecarExporter
from ragdocforge.converters.output_readme_writer import OutputReadmeWriter
from ragdocforge.converters.output_summary_writer import OutputSummaryWriter
from ragdocforge.converters.suggested_sections_exporter import SuggestedSectionsExporter
from ragdocforge.converters.zip_exporter import ZipExporter
from ragdocforge.llm.provider import LLMRuntimeConfig, build_provider, provider_defaults
from ragdocforge.parsers.parser_router import ParserRouter
from ragdocforge.schemas.llm_analysis_models import LLMAnalysisBundle
from ragdocforge.utils.file_utils import safe_copy_upload_to_workdir, sanitize_filename, uploaded_path, validate_upload_batch
from ragdocforge.utils.logging_utils import get_logger, log_processing_status

load_dotenv()

SETTINGS = load_app_settings()
LOGGER = get_logger(__name__)
ERP_MODULES = ["", "GL", "AP", "AR", "PO", "INV", "OM", "HRMS", "FA", "CM", "SYSADMIN", "GENERIC", "UNKNOWN"]
DOC_TYPES = ["", "SOP", "SQL", "PLSQL", "ORACLE_DOC", "FUNCTIONAL_DESIGN", "TECHNICAL_DESIGN", "TROUBLESHOOTING_NOTE", "FAQ", "UNKNOWN"]
LLM_PROVIDERS = ["disabled", "mock", "ollama", "openai_compatible"]
ENV_LLM_CONFIG = LLMRuntimeConfig.from_env()
SAMPLE_FILES = {
    "sop": "examples/sample_gl_journal_import_sop.md",
    "sql": "examples/sample_gl_diagnostic_sql.sql",
    "plsql": "examples/sample_custom_plsql_package.pks",
    "low_quality": "examples/sample_low_quality_note.txt",
}
ANALYSIS_COLUMNS = [
    "source_file",
    "doc_type",
    "erp_module",
    "title",
    "headings",
    "tables",
    "views",
    "packages",
    "procedures",
    "functions",
    "errors",
    "error_codes_count",
    "error_context_lines_count",
    "tables_count",
    "functions_count",
    "score",
    "raw_score",
    "final_score",
    "readiness",
    "score_cap_reasons",
    "metadata_confidence",
    "false_positive_filter_count",
    "strengths",
    "blocking_issues",
    "warnings",
]
SUGGESTED_SECTION_COLUMNS = [
    "priority",
    "section_title",
    "confidence",
    "evidence_supported",
    "requires_sme_confirmation",
    "source_evidence",
    "reason_needed",
    "suggested_content",
]
CHUNK_COLUMNS = [
    "chunk_id",
    "doc_id",
    "source_file",
    "section",
    "erp_module",
    "doc_type",
    "token_estimate",
    "doc_metadata_ref",
    "chunk_tables",
    "chunk_functions",
    "chunk_packages",
    "chunk_procedures",
    "chunk_error_codes",
    "chunk_error_context_lines_preview",
    "rag_priority",
    "metadata_confidence",
    "retrieval_usefulness_score",
    "answerability_score",
    "chunk_issue_summary",
    "suggested_keywords",
    "should_split",
    "should_merge_with_neighbors",
    "text_preview",
]


def analyze(
    files,
    erp_module,
    doc_type,
    business_process,
    chunk_size,
    chunk_overlap,
    enable_llm,
    llm_provider_name,
    model_name,
    base_url,
    api_key,
    max_doc_chars,
    max_chunks_to_review,
):
    if not files:
        return _empty_outputs("No files selected. Upload documents or load sample files, then click Analyze.")

    files = list(files)
    validation_errors = validate_upload_batch(files, SETTINGS)
    if validation_errors:
        return _empty_outputs("Upload validation failed:\n\n" + "\n".join(f"- {error}" for error in validation_errors))

    router = ParserRouter()
    extractor = MetadataExtractor()
    scorer = QualityScorer()
    converter = MarkdownConverter()
    chunker = Chunker()

    output_dir = Path(tempfile.mkdtemp(prefix="ragdocforge_"))
    input_dir = output_dir / "uploads"
    input_dir.mkdir(parents=True, exist_ok=True)
    documents = []
    reports = []
    chunks = []
    markdown_files = []
    markdown_by_doc = {}
    chunks_by_doc = {}
    failures = []

    for file_obj in files:
        source_path = uploaded_path(file_obj)
        started = time.perf_counter()
        try:
            working_path = safe_copy_upload_to_workdir(file_obj, input_dir)
            document = extractor.enrich(router.parse(str(working_path)), erp_module or None, doc_type or None, business_process or None)
            document.source_file = sanitize_filename(document.source_file)
            report = scorer.score(document)
            markdown = converter.convert(document, report)
            markdown_path = output_dir / f"{document.doc_id}.md"
            markdown_path.write_text(markdown, encoding="utf-8")
            doc_chunks = chunker.chunk(document, int(chunk_size), int(chunk_overlap))
            documents.append(document)
            reports.append(report)
            chunks.extend(doc_chunks)
            markdown_files.append(str(markdown_path))
            markdown_by_doc[document.doc_id] = markdown
            chunks_by_doc[document.doc_id] = doc_chunks
            log_processing_status(
                LOGGER,
                doc_id=document.doc_id,
                source_file=document.source_file,
                status="processed",
                warnings_count=len(document.warnings),
                duration_seconds=time.perf_counter() - started,
                debug=SETTINGS.debug,
            )
        except Exception as exc:
            safe_source = sanitize_filename(source_path)
            message = str(exc)[:500] if SETTINGS.debug else _short_error_message(exc)
            failures.append({"source_file": safe_source, "error": message})
            log_processing_status(
                LOGGER,
                doc_id=None,
                source_file=safe_source,
                status="failed",
                warnings_count=1,
                duration_seconds=time.perf_counter() - started,
                debug=SETTINGS.debug,
                error=exc,
            )

    llm_config = _ui_llm_config(enable_llm, llm_provider_name, model_name, base_url, api_key, max_doc_chars, max_chunks_to_review)
    llm_bundles = _run_llm_analysis(llm_config, documents, reports, markdown_by_doc, chunks_by_doc) if enable_llm and llm_config.provider != "disabled" else []
    chunk_critiques_by_id = {critique.chunk_id: critique for bundle in llm_bundles for critique in bundle.chunk_critiques}

    chunks_path = JsonlExporter().write(chunks, str(output_dir / "chunks.jsonl"))
    quality_path = output_dir / "quality_report.json"
    quality_path.write_text(json.dumps({"reports": [report.model_dump() for report in reports], "failures": failures}, indent=2), encoding="utf-8")
    llm_report_path = output_dir / "llm_analysis_report.json"
    llm_report_path.write_text(json.dumps([bundle.model_dump() for bundle in llm_bundles], indent=2), encoding="utf-8")
    suggested_sections_path = SuggestedSectionsExporter().write(llm_bundles, str(output_dir / "suggested_sections.md"))
    output_summary_path = OutputSummaryWriter().write(documents, reports, llm_bundles, str(output_dir / "output_summary.md"))
    output_readme_path = OutputReadmeWriter().write(str(output_dir / "README_OUTPUTS.md"))
    metadata_sidecar_path = MetadataSidecarExporter().write(documents, str(output_dir / "metadata_sidecar.json"))
    manifest_path = ManifestWriter().write(
        documents,
        reports,
        chunks,
        str(output_dir / "manifest.json"),
        failures,
        llm_enabled=bool(enable_llm and llm_config.provider != "disabled"),
        llm_provider=llm_config.provider,
        llm_model=llm_config.model_name,
        llm_bundles=llm_bundles,
    )
    zip_path = ZipExporter().write(markdown_files + [chunks_path, str(quality_path), str(llm_report_path), suggested_sections_path, output_summary_path, metadata_sidecar_path, manifest_path, output_readme_path], str(output_dir / "all_outputs.zip"))
    shutil.rmtree(input_dir, ignore_errors=True)

    analysis_rows = [
        {
            "source_file": doc.source_file,
            "doc_type": doc.detected_doc_type,
            "erp_module": doc.detected_erp_module,
            "title": doc.title,
            "headings": ", ".join(doc.headings[:8]),
            "tables": ", ".join(doc.tables[:10]),
            "views": ", ".join(doc.views[:10]),
            "packages": ", ".join(doc.packages[:10]),
            "procedures": ", ".join(doc.procedures[:10]),
            "functions": ", ".join(doc.functions[:10]),
            "errors": ", ".join(doc.error_messages[:10]),
            "error_codes_count": len(doc.error_codes),
            "error_context_lines_count": len(doc.error_context_lines),
            "tables_count": len(doc.tables),
            "functions_count": len(doc.functions),
            "score": report.overall_score,
            "raw_score": report.raw_score,
            "final_score": report.overall_score,
            "readiness": report.readiness_level,
            "score_cap_reasons": "; ".join(report.score_cap_reasons),
            "metadata_confidence": doc.metadata_confidence,
            "false_positive_filter_count": doc.false_positive_filter_count,
            "strengths": "; ".join(report.strengths),
            "blocking_issues": "; ".join(report.blocking_issues),
            "warnings": "; ".join(report.warnings),
        }
        for doc, report in zip(documents, reports)
    ]
    analysis_rows.extend(
        {
            "source_file": failure["source_file"],
            "doc_type": "FAILED",
            "erp_module": "UNKNOWN",
            "title": "",
            "headings": "",
            "tables": "",
            "views": "",
            "packages": "",
            "procedures": "",
            "functions": "",
            "errors": "",
            "error_codes_count": 0,
            "error_context_lines_count": 0,
            "tables_count": 0,
            "functions_count": 0,
            "score": 0,
            "raw_score": 0,
            "final_score": 0,
            "readiness": "NOT_RAG_READY",
            "score_cap_reasons": "",
            "metadata_confidence": 0,
            "false_positive_filter_count": 0,
            "strengths": "",
            "blocking_issues": failure["error"],
            "warnings": "Document failed; remaining batch continued.",
        }
        for failure in failures
    )
    chunk_rows = [
        {
            "chunk_id": chunk.chunk_id,
            "doc_id": chunk.doc_id,
            "source_file": chunk.source_file,
            "section": chunk.section,
            "erp_module": chunk.erp_module,
            "doc_type": chunk.doc_type,
            "token_estimate": chunk.token_estimate,
            "doc_metadata_ref": f"metadata_sidecar.json#{chunk.doc_id}",
            "chunk_tables": ", ".join(chunk.chunk_tables[:6]),
            "chunk_functions": ", ".join(chunk.chunk_functions[:6]),
            "chunk_packages": ", ".join(chunk.chunk_packages[:6]),
            "chunk_procedures": ", ".join(chunk.chunk_procedures[:6]),
            "chunk_error_codes": ", ".join(chunk.chunk_error_codes[:6]),
            "chunk_error_context_lines_preview": " | ".join(chunk.chunk_error_context_lines[:3]),
            "rag_priority": chunk.rag_priority,
            "metadata_confidence": chunk.metadata_confidence,
            "retrieval_usefulness_score": chunk_critiques_by_id[chunk.chunk_id].retrieval_usefulness_score if chunk.chunk_id in chunk_critiques_by_id else None,
            "answerability_score": chunk_critiques_by_id[chunk.chunk_id].answerability_score if chunk.chunk_id in chunk_critiques_by_id else None,
            "chunk_issue_summary": chunk_critiques_by_id[chunk.chunk_id].chunk_issue_summary if chunk.chunk_id in chunk_critiques_by_id else "",
            "suggested_keywords": ", ".join(chunk_critiques_by_id[chunk.chunk_id].suggested_keywords) if chunk.chunk_id in chunk_critiques_by_id else "",
            "should_split": chunk_critiques_by_id[chunk.chunk_id].should_split if chunk.chunk_id in chunk_critiques_by_id else None,
            "should_merge_with_neighbors": chunk_critiques_by_id[chunk.chunk_id].should_merge_with_neighbors if chunk.chunk_id in chunk_critiques_by_id else None,
            "text_preview": chunk.text[:240],
        }
        for chunk in chunks
    ]
    llm_review = _llm_review_payload(llm_config, llm_bundles, enable_llm)
    suggested_rows = [
        {
            "priority": section.priority,
            "section_title": section.section_title,
            "confidence": section.confidence,
            "evidence_supported": section.evidence_supported,
            "requires_sme_confirmation": section.requires_sme_confirmation,
            "source_evidence": " | ".join(section.source_evidence[:5]),
            "reason_needed": section.reason_needed,
            "suggested_content": section.suggested_content,
        }
        for bundle in llm_bundles
        for section in bundle.suggested_sections
    ]
    first_markdown = Path(markdown_files[0]).read_text(encoding="utf-8") if markdown_files else ""
    uploaded = [doc.source_file for doc in documents]
    uploaded.extend(failure["source_file"] for failure in failures)
    first_markdown_file = markdown_files[0] if markdown_files else None
    status = _completion_status(len(documents), len(failures), bool(enable_llm and llm_config.provider != "disabled"), llm_config.provider, llm_bundles)
    result_summary = _result_summary(documents, reports, chunks, failures, llm_config.provider, zip_path)
    quality_rows = _quality_summary_rows(documents, reports, chunks)
    return (
        status,
        uploaded,
        pd.DataFrame(analysis_rows, columns=ANALYSIS_COLUMNS),
        first_markdown,
        llm_review,
        pd.DataFrame(suggested_rows, columns=SUGGESTED_SECTION_COLUMNS),
        pd.DataFrame(chunk_rows, columns=CHUNK_COLUMNS),
        first_markdown_file,
        chunks_path,
        str(quality_path),
        str(llm_report_path),
        suggested_sections_path,
        metadata_sidecar_path,
        manifest_path,
        zip_path,
        result_summary,
        pd.DataFrame(quality_rows, columns=QUALITY_SUMMARY_COLUMNS),
    )


def analysis_started_status(files, enable_llm, llm_provider_name) -> str:
    file_count = len(files or [])
    llm_note = f" LLM review is enabled with `{llm_provider_name}`; this may take a while." if enable_llm and llm_provider_name != "disabled" else ""
    return f"Analyze request accepted. Processing {file_count} file(s)...{llm_note}"


QUALITY_SUMMARY_COLUMNS = [
    "source_file",
    "doc_type",
    "erp_module",
    "quality_score",
    "readiness_level",
    "blocking_issues_count",
    "warnings_count",
    "chunks_created",
]


def _empty_outputs(status: str):
    return (
        status,
        [],
        pd.DataFrame(columns=ANALYSIS_COLUMNS),
        "Upload documents or load sample files, then click Analyze.",
        {"provider_used": "disabled", "document_critiques": [], "provider_warnings": []},
        pd.DataFrame(columns=SUGGESTED_SECTION_COLUMNS),
        pd.DataFrame(columns=CHUNK_COLUMNS),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        "Upload documents or load sample files, then click Analyze.",
        pd.DataFrame(columns=QUALITY_SUMMARY_COLUMNS),
    )


def _completion_status(processed_count: int, failure_count: int, llm_enabled: bool, provider: str, bundles: list[LLMAnalysisBundle]) -> str:
    warning_count = sum(len(bundle.raw_provider_warnings) for bundle in bundles)
    llm_note = ""
    if llm_enabled:
        llm_note = f" LLM provider `{provider}` completed with {warning_count} warning(s)."
    return f"Analysis complete. Processed {processed_count} document(s); {failure_count} failed.{llm_note}"


def _result_summary(documents, reports, chunks, failures, llm_provider: str, zip_path: str) -> str:
    average_score = round(sum(report.overall_score for report in reports) / len(reports)) if reports else 0
    readiness = _batch_readiness(reports)
    return "\n".join(
        [
            f"Documents processed: {len(documents)}",
            f"Documents failed: {len(failures)}",
            f"Chunks created: {len(chunks)}",
            f"Average quality score: {average_score}",
            f"Readiness: {readiness}",
            f"LLM analysis: {llm_provider}",
            f"Export ZIP: {'ready' if zip_path else 'not ready'}",
        ]
    )


def _quality_summary_rows(documents, reports, chunks) -> list[dict]:
    reports_by_doc = {report.doc_id: report for report in reports}
    return [
        {
            "source_file": document.source_file,
            "doc_type": document.detected_doc_type,
            "erp_module": document.detected_erp_module,
            "quality_score": reports_by_doc[document.doc_id].overall_score,
            "readiness_level": reports_by_doc[document.doc_id].readiness_level,
            "blocking_issues_count": len(reports_by_doc[document.doc_id].blocking_issues),
            "warnings_count": len(reports_by_doc[document.doc_id].warnings),
            "chunks_created": sum(1 for chunk in chunks if chunk.doc_id == document.doc_id),
        }
        for document in documents
        if document.doc_id in reports_by_doc
    ]


def _batch_readiness(reports) -> str:
    if not reports:
        return "NOT_RAG_READY"
    rank = {"NOT_RAG_READY": 0, "POOR": 1, "NEEDS_IMPROVEMENT": 2, "GOOD": 3, "EXCELLENT": 4}
    inverse = {value: key for key, value in rank.items()}
    return inverse[min(rank.get(report.readiness_level, 0) for report in reports)]


def _short_error_message(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return str(exc)[:300]
    if isinstance(exc, FileNotFoundError):
        return "File could not be found or read."
    return "Document failed during parsing or analysis. Enable RAGDOCFORGE_DEBUG=true for details."


def load_sample_sop() -> list[str]:
    return [SAMPLE_FILES["sop"]]


def load_sample_sql() -> list[str]:
    return [SAMPLE_FILES["sql"]]


def load_sample_plsql() -> list[str]:
    return [SAMPLE_FILES["plsql"]]


def load_all_samples() -> list[str]:
    return list(SAMPLE_FILES.values())


def _ui_llm_config(enable_llm, provider_name, model_name, base_url, api_key, max_doc_chars, max_chunks_to_review) -> LLMRuntimeConfig:
    provider = provider_name or ENV_LLM_CONFIG.provider
    if not enable_llm:
        provider = "disabled"
    if SETTINGS.public_demo_mode and provider not in {"disabled", "mock"}:
        provider = "disabled"
    default_model, default_base_url = provider_defaults(provider)
    env_config = LLMRuntimeConfig.from_env()
    return LLMRuntimeConfig(
        provider=provider,
        model_name=model_name or default_model,
        base_url=base_url or default_base_url,
        api_key=api_key or env_config.api_key,
        timeout_seconds=env_config.timeout_seconds,
        max_doc_chars=min(int(max_doc_chars or env_config.max_doc_chars), SETTINGS.llm_max_doc_chars),
        max_chunks_to_review=min(int(max_chunks_to_review or env_config.max_chunks_to_review), SETTINGS.llm_max_chunks_to_review),
    )


def _run_llm_analysis(
    config: LLMRuntimeConfig,
    documents,
    reports,
    markdown_by_doc,
    chunks_by_doc,
) -> list[LLMAnalysisBundle]:
    provider = build_provider(config)
    if not provider.is_configured():
        return [
            LLMAnalysisBundle(
                doc_id=document.doc_id,
                source_file=document.source_file,
                provider_name=provider.provider_name,
                raw_provider_warnings=[f"Provider {provider.provider_name} is not configured."],
            )
            for document in documents
        ]
    bundles: list[LLMAnalysisBundle] = []
    reports_by_doc = {report.doc_id: report for report in reports}
    for document in documents:
        warnings: list[str] = []
        report = reports_by_doc[document.doc_id]
        critique = LLMDocumentAnalyzer(provider, config.max_doc_chars).analyze(document, report, markdown_by_doc.get(document.doc_id, ""), warnings)
        suggested_sections = LLMGapAnalyzer(provider).analyze(document, report, critique, warnings)
        chunk_critiques = LLMChunkAnalyzer(provider, config.max_chunks_to_review).analyze(chunks_by_doc.get(document.doc_id, []), warnings)
        bundles.append(
            LLMAnalysisBundle(
                doc_id=document.doc_id,
                source_file=document.source_file,
                provider_name=provider.provider_name,
                document_critique=critique,
                suggested_sections=suggested_sections,
                chunk_critiques=chunk_critiques,
                raw_provider_warnings=warnings,
            )
        )
    return bundles


def _llm_review_payload(config: LLMRuntimeConfig, bundles: list[LLMAnalysisBundle], enabled) -> dict:
    if not enabled or config.provider == "disabled":
        return {"provider_used": "disabled", "document_critiques": [], "provider_warnings": []}
    return {
        "provider_used": config.provider,
        "document_critiques": [bundle.document_critique.model_dump() for bundle in bundles if bundle.document_critique],
        "main_strengths": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.main_strengths],
        "major_weaknesses": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.major_weaknesses],
        "missing_context": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.missing_context],
        "retrieval_risk_factors": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.retrieval_risk_factors],
        "hallucination_risk_factors": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.hallucination_risk_factors],
        "recommended_additions": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.recommended_additions],
        "support_questions_answerable": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.support_questions_answerable],
        "support_questions_not_answerable": [item for bundle in bundles if bundle.document_critique for item in bundle.document_critique.support_questions_not_answerable],
        "provider_warnings": [warning for bundle in bundles for warning in bundle.raw_provider_warnings],
    }


with gr.Blocks(title="RAGDocForge") as demo:
    gr.Markdown("# RAGDocForge — Enterprise RAG Document Quality Analyzer")
    gr.Markdown("Upload SOPs, SQL, PL/SQL, Oracle EBS notes, and design documents. Analyze RAG readiness, convert to structured markdown, generate JSONL chunks, and receive improvement suggestions.")
    if SETTINGS.public_demo_mode:
        gr.Markdown("**Public Demo Mode Enabled**\n\nThis Space is for demonstration with sample or non-confidential documents only.")
    gr.Markdown("**Privacy warning:** Do not upload confidential enterprise documents to a public hosted demo. Use local/private deployment for sensitive files.")
    with gr.Tab("Upload & Settings"):
        files = gr.File(label="Documents", file_count="multiple", file_types=[".pdf", ".docx", ".txt", ".md", ".sql", ".pls", ".pkb", ".pks"])
        with gr.Row():
            sample_sop_button = gr.Button("Load Sample SOP")
            sample_sql_button = gr.Button("Load Sample SQL")
            sample_plsql_button = gr.Button("Load Sample PL/SQL")
            sample_all_button = gr.Button("Load All Samples", variant="secondary")
        erp_module = gr.Dropdown(ERP_MODULES, label="ERP Module", value="")
        doc_type = gr.Dropdown(DOC_TYPES, label="Document Type", value="")
        business_process = gr.Textbox(label="Business Process")
        chunk_size = gr.Number(label="Chunk Size", value=900, precision=0)
        chunk_overlap = gr.Number(label="Chunk Overlap", value=120, precision=0)
        with gr.Accordion("LLM Qualitative Analysis", open=False):
            gr.Markdown("**LLM warning:** When LLM analysis is enabled, document content may be sent to the selected provider. Use Ollama for local/private processing.")
            enable_llm = gr.Checkbox(label="Enable LLM qualitative analysis", value=False)
            llm_provider = gr.Dropdown(LLM_PROVIDERS, label="LLM Provider", value=ENV_LLM_CONFIG.provider if ENV_LLM_CONFIG.provider in LLM_PROVIDERS else "disabled")
            model_name = gr.Textbox(label="Model Name", value=ENV_LLM_CONFIG.model_name)
            base_url = gr.Textbox(label="Base URL", value=ENV_LLM_CONFIG.base_url)
            api_key = gr.Textbox(label="API Key", type="password", value="", visible=not SETTINGS.public_demo_mode)
            max_doc_chars = gr.Number(label="Max Document Characters", value=ENV_LLM_CONFIG.max_doc_chars, precision=0)
            max_chunks_to_review = gr.Number(label="Max Chunks To Review", value=ENV_LLM_CONFIG.max_chunks_to_review, precision=0)
        analyze_button = gr.Button("Analyze", variant="primary")
        analysis_status = gr.Markdown("Ready.")
    with gr.Tab("Document Analysis"):
        result_summary_panel = gr.Markdown("Upload documents or load sample files, then click Analyze.")
        quality_summary_table = gr.Dataframe(label="Quality Summary", wrap=True)
        uploaded_files = gr.JSON(label="Uploaded Files")
        analysis_table = gr.Dataframe(label="Analysis Results", wrap=True)
    with gr.Tab("RAG Markdown Preview"):
        markdown_preview = gr.Code(label="Markdown", language="markdown", lines=28, value="Upload documents or load sample files, then click Analyze.")
    with gr.Tab("LLM Quality Review"):
        llm_review = gr.JSON(label="LLM Document Critique")
    with gr.Tab("Suggested Sections"):
        suggested_sections = gr.Dataframe(label="Suggested Sections", wrap=True)
    with gr.Tab("Chunk Preview"):
        chunk_table = gr.Dataframe(label="Chunks", wrap=True)
    with gr.Tab("Export"):
        markdown_download = gr.File(label="First Markdown File")
        chunks_download = gr.File(label="chunks.jsonl")
        quality_download = gr.File(label="quality_report.json")
        llm_report_download = gr.File(label="llm_analysis_report.json")
        suggested_sections_download = gr.File(label="suggested_sections.md")
        metadata_sidecar_download = gr.File(label="metadata_sidecar.json")
        manifest_download = gr.File(label="manifest.json")
        zip_download = gr.File(label="all_outputs.zip")

    sample_sop_button.click(load_sample_sop, outputs=[files], queue=False)
    sample_sql_button.click(load_sample_sql, outputs=[files], queue=False)
    sample_plsql_button.click(load_sample_plsql, outputs=[files], queue=False)
    sample_all_button.click(load_all_samples, outputs=[files], queue=False)

    analyze_button.click(
        analysis_started_status,
        inputs=[files, enable_llm, llm_provider],
        outputs=[analysis_status],
        queue=False,
    ).then(
        analyze,
        inputs=[files, erp_module, doc_type, business_process, chunk_size, chunk_overlap, enable_llm, llm_provider, model_name, base_url, api_key, max_doc_chars, max_chunks_to_review],
        outputs=[
            analysis_status,
            uploaded_files,
            analysis_table,
            markdown_preview,
            llm_review,
            suggested_sections,
            chunk_table,
            markdown_download,
            chunks_download,
            quality_download,
            llm_report_download,
            suggested_sections_download,
            metadata_sidecar_download,
            manifest_download,
            zip_download,
            result_summary_panel,
            quality_summary_table,
        ],
        queue=False,
    )
