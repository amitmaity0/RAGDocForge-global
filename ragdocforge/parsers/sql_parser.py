import re

from ragdocforge.parsers.base_parser import base_document
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.utils.text_utils import normalize_line_endings, unique_sorted


RISKY_SQL = ["INSERT", "UPDATE", "DELETE", "MERGE", "DROP", "TRUNCATE", "ALTER", "CREATE", "GRANT", "REVOKE", "EXECUTE IMMEDIATE"]


class SqlParser:
    def parse(self, path: str) -> ParsedDocument:
        raw = open(path, encoding="utf-8", errors="replace").read()
        text = normalize_line_endings(raw)
        warnings = [f"Potentially risky SQL statement detected: {word}" for word in RISKY_SQL if re.search(rf"\b{re.escape(word)}\b", text, re.I)]
        document = base_document(path, text, warnings)
        document.tables = unique_sorted(re.findall(r"\b(?:from|join|update|into|table)\s+([a-zA-Z][\w$#.]*)", text, re.I))
        document.packages = unique_sorted(re.findall(r"\bpackage(?:\s+body)?\s+([a-zA-Z][\w$#]*)", text, re.I))
        document.procedures = unique_sorted(re.findall(r"\bprocedure\s+([a-zA-Z][\w$#]*)", text, re.I))
        document.functions = unique_sorted(re.findall(r"\bfunction\s+([a-zA-Z][\w$#]*)", text, re.I))
        document.keywords = unique_sorted(re.findall(r":([a-zA-Z][\w$#]*)", text))
        document.detected_doc_type = "PLSQL" if document.packages or document.procedures or document.functions else "SQL"
        return document
