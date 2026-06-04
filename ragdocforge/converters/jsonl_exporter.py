import json

from ragdocforge.schemas.chunk_models import RagChunk

INCLUDE_FULL_DOC_METADATA_IN_CHUNKS = False


class JsonlExporter:
    def write(self, chunks: list[RagChunk], path: str) -> str:
        with open(path, "w", encoding="utf-8") as handle:
            for chunk in chunks:
                handle.write(json.dumps(self._record(chunk), ensure_ascii=True) + "\n")
        return path

    def _record(self, chunk: RagChunk) -> dict:
        return {
            "chunk_id": chunk.chunk_id,
            "doc_id": chunk.doc_id,
            "source_file": chunk.source_file,
            "text": chunk.text,
            "metadata": {
                "erp_module": chunk.erp_module,
                "doc_type": chunk.doc_type,
                "business_process": chunk.business_process,
                "section": chunk.section,
                "rag_priority": chunk.rag_priority,
                "metadata_confidence": chunk.metadata_confidence,
                "doc_level": {
                    **_doc_level_metadata(chunk),
                },
                "chunk_level": {
                    "tables": chunk.chunk_tables,
                    "views": chunk.chunk_views,
                    "packages": chunk.chunk_packages,
                    "procedures": chunk.chunk_procedures,
                    "functions": chunk.chunk_functions,
                    "error_codes": chunk.chunk_error_codes,
                    "error_context_lines": chunk.chunk_error_context_lines,
                    "keywords": chunk.chunk_keywords,
                },
            },
        }


def _doc_level_metadata(chunk: RagChunk) -> dict:
    compact = {
        "metadata_ref": f"metadata_sidecar.json#{chunk.doc_id}",
        "tables_count": len(chunk.doc_tables),
        "packages_count": len(chunk.doc_packages),
        "procedures_count": len(chunk.doc_procedures),
        "functions_count": len(chunk.doc_functions),
        "error_codes_count": len(chunk.doc_error_codes),
        "error_context_lines_count": len(chunk.doc_error_context_lines),
        "keywords_count": len(chunk.doc_keywords),
        "top_tables": chunk.doc_tables[:10],
        "top_error_codes": chunk.doc_error_codes[:10],
    }
    if not INCLUDE_FULL_DOC_METADATA_IN_CHUNKS:
        return compact
    return {
        **compact,
        "tables": chunk.doc_tables,
        "views": chunk.doc_views,
        "packages": chunk.doc_packages,
        "procedures": chunk.doc_procedures,
        "functions": chunk.doc_functions,
        "error_codes": chunk.doc_error_codes,
        "error_context_lines": chunk.doc_error_context_lines,
        "keywords": chunk.doc_keywords,
    }
