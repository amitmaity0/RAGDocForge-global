class OutputReadmeWriter:
    def write(self, path: str) -> str:
        content = """# RAGDocForge Outputs

This ZIP contains deterministic artifacts generated from the uploaded or sample documents.

## Files

- `markdown/`: RAG-ready markdown conversions with compact YAML front matter.
- `chunks.jsonl`: one JSON object per chunk for downstream RAG ingestion.
- `quality_report.json`: deterministic quality scores, readiness levels, blocking issues, and score-cap reasons.
- `metadata_sidecar.json`: full document-level Oracle object, error, and keyword metadata referenced by chunks.
- `llm_analysis_report.json`: optional LLM qualitative critique bundles and provider warnings.
- `suggested_sections.md`: suggested missing or improved sections for human review.
- `output_summary.md`: concise batch summary.
- `manifest.json`: batch-level export inventory and runtime flags.

## Using chunks.jsonl

Each chunk has `metadata.doc_level` for compact document references and counts, and `metadata.chunk_level` for local retrieval metadata. Use `metadata.doc_level.metadata_ref` to join back to `metadata_sidecar.json` when full document metadata is needed.

## Reviewing suggested sections

Suggested sections are recommendations, not authoritative content. Review LLM-generated text with a subject matter expert before adding it to enterprise knowledge sources.
"""
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return path
