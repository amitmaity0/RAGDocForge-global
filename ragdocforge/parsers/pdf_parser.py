from ragdocforge.parsers.base_parser import base_document
from ragdocforge.schemas.document_models import ParsedDocument


class PdfParser:
    def parse(self, path: str) -> ParsedDocument:
        try:
            import fitz
        except ImportError:
            return base_document(path, "", ["PDF parsing requires pymupdf."])

        pages: list[str] = []
        warnings: list[str] = []
        try:
            with fitz.open(path) as doc:
                for index, page in enumerate(doc, start=1):
                    pages.append(f"<!-- page: {index} -->\n{page.get_text()}")
        except Exception as exc:  # pragma: no cover - depends on external files
            warnings.append(f"PDF text extraction failed: {exc}")
        return base_document(path, "\n\n".join(pages), warnings)
