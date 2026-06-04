from ragdocforge.schemas.document_models import ParsedDocument


REQUIRED_BY_TYPE = {
    "SOP": ["Purpose", "Scope", "Prerequisites", "Procedure", "Validation", "Rollback"],
    "SQL": ["Purpose", "Parameters", "Expected Result", "Safety Notes"],
    "PLSQL": ["Purpose", "Package", "Procedure", "Error Handling", "Validation"],
    "TROUBLESHOOTING_NOTE": ["Symptoms", "Cause", "Resolution", "Validation"],
}


class GapAnalyzer:
    def missing_sections(self, document: ParsedDocument) -> list[str]:
        required = REQUIRED_BY_TYPE.get(document.detected_doc_type, ["Purpose", "Scope", "Validation"])
        present = {heading.lower() for heading in document.headings}
        return [section for section in required if section.lower() not in present]
