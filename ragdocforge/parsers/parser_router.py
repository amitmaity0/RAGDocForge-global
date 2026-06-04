from ragdocforge.parsers.base_parser import base_document
from ragdocforge.parsers.docx_parser import DocxParser
from ragdocforge.parsers.pdf_parser import PdfParser
from ragdocforge.parsers.sql_parser import SqlParser
from ragdocforge.parsers.text_parser import TextParser
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.utils.file_utils import extension_for


class ParserRouter:
    def __init__(self) -> None:
        self._parsers = {
            ".pdf": PdfParser(),
            ".docx": DocxParser(),
            ".txt": TextParser(),
            ".md": TextParser(),
            ".sql": SqlParser(),
            ".pls": SqlParser(),
            ".pkb": SqlParser(),
            ".pks": SqlParser(),
        }

    def parse(self, path: str) -> ParsedDocument:
        extension = extension_for(path)
        parser = self._parsers.get(extension)
        if parser is None:
            return base_document(path, "", [f"Unsupported file extension: {extension}"])
        return parser.parse(path)
