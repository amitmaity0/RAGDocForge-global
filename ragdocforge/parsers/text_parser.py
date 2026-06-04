from ragdocforge.parsers.base_parser import base_document
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.utils.text_utils import normalize_line_endings


class TextParser:
    def parse(self, path: str) -> ParsedDocument:
        warnings: list[str] = []
        try:
            raw = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            raw = open(path, encoding="latin-1").read()
            warnings.append("Read with latin-1 fallback because UTF-8 decoding failed.")
        return base_document(path, normalize_line_endings(raw), warnings)
