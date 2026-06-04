from pathlib import Path
from typing import Protocol

from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.utils.file_utils import build_doc_id, extension_for


class DocumentParser(Protocol):
    def parse(self, path: str) -> ParsedDocument:
        ...


def base_document(path: str, raw_text: str, warnings: list[str] | None = None) -> ParsedDocument:
    return ParsedDocument(
        doc_id=build_doc_id(path),
        source_file=Path(path).name,
        file_extension=extension_for(path),
        raw_text=raw_text,
        warnings=warnings or [],
    )
