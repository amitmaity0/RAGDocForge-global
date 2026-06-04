import json

from ragdocforge.schemas.document_models import ParsedDocument


class MetadataSidecarExporter:
    def write(self, documents: list[ParsedDocument], path: str) -> str:
        payload = {
            "documents": [
                {
                    "doc_id": document.doc_id,
                    "source_file": document.source_file,
                    "title": document.title,
                    "erp_module": document.detected_erp_module,
                    "doc_type": document.detected_doc_type,
                    "business_process": document.business_process,
                    "metadata_confidence": document.metadata_confidence,
                    "false_positive_filter_count": document.false_positive_filter_count,
                    "oracle_objects": {
                        "tables": _candidates(document, "table"),
                        "views": _candidates(document, "view"),
                        "packages": _candidates(document, "package"),
                        "procedures": _candidates(document, "procedure"),
                        "functions": _candidates(document, "function"),
                    },
                    "error_codes": document.error_codes,
                    "error_context_lines": document.error_context_lines,
                    "error_messages": document.error_messages,
                    "keywords": document.keywords,
                }
                for document in documents
            ]
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return path


def _candidates(document: ParsedDocument, object_type: str) -> list[dict]:
    return [
        {
            "name": candidate.name,
            "confidence": candidate.confidence,
            "evidence_type": candidate.evidence_type,
            "evidence": candidate.evidence,
        }
        for candidate in document.oracle_object_candidates
        if candidate.object_type == object_type
    ]
