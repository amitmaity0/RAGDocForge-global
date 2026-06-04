import re
from pathlib import Path

import yaml

from ragdocforge.analyzers.oracle_object_extractor import enrich_oracle_objects
from ragdocforge.schemas.document_models import ParsedDocument


ERP_MODULE_KEYWORDS = {
    "GL": ["general ledger", "journal import", "gl_interface", "gl_je_headers", "ledger", "accounting period"],
    "AP": ["accounts payable", "invoice workbench", "ap_invoices_all", "supplier invoice"],
    "AR": ["accounts receivable", "ra_customer_trx_all", "receipt", "customer transaction"],
    "PO": ["purchase order", "po_headers_all", "po_lines_all", "requisition"],
    "INV": ["inventory", "mtl_system_items", "on hand", "item master"],
    "OM": ["order management", "oe_order_headers_all", "sales order"],
    "HRMS": ["hrms", "per_all_people_f", "payroll", "employee"],
    "FA": ["fixed assets", "fa_additions", "asset workbench"],
    "CM": ["cash management", "ce_statement_headers", "bank statement"],
    "SYSADMIN": ["fnd_user", "responsibility", "profile option", "concurrent manager"],
}

COMMON_HEADINGS = ["Purpose", "Scope", "Overview", "Prerequisites", "Procedure", "Steps", "Setup", "Troubleshooting", "Known Issues", "Resolution", "Validation", "SQL", "Diagnostic SQL", "Rollback", "References", "Appendix"]
GENERIC_TITLE_DENYLIST = {
    "SUMMARY", "OVERVIEW", "PURPOSE", "SCOPE", "INTRODUCTION", "DETAILS",
    "PROBLEM", "ISSUE", "SOLUTION", "RESOLUTION", "REFERENCES", "APPENDIX",
    "BACKGROUND", "NOTES", "DESCRIPTION",
}


class MetadataExtractor:
    def enrich(self, document: ParsedDocument, user_erp_module: str | None = None, user_doc_type: str | None = None, business_process: str | None = None) -> ParsedDocument:
        text = document.raw_text
        document.headings = self._headings(text)
        detected_module, secondary_modules = self._detect_module(text)
        document.detected_erp_module = user_erp_module or detected_module
        document.detected_doc_type = user_doc_type or (document.detected_doc_type if document.detected_doc_type != "UNKNOWN" else self._detect_doc_type(document))
        document.user_erp_module = user_erp_module
        document.user_doc_type = user_doc_type
        document.business_process = business_process or None
        document.title = extract_best_title(
            document.raw_text,
            document.source_file,
            document.headings,
            document.detected_erp_module,
            document.business_process,
            document.detected_doc_type,
        )
        if secondary_modules and not user_erp_module:
            document.keywords = list(dict.fromkeys(document.keywords + secondary_modules))
            document.warnings.append("Secondary ERP module candidates: " + ", ".join(secondary_modules))
        return enrich_oracle_objects(document)

    def _title(self, document: ParsedDocument) -> str:
        return extract_best_title(document.raw_text, document.source_file, document.headings, document.detected_erp_module, document.business_process, document.detected_doc_type)

    def _headings(self, text: str) -> list[str]:
        headings: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            if re.match(r"^#{1,6}\s+", stripped):
                headings.append(stripped.lstrip("#").strip())
            elif re.match(r"^\d+(?:\.\d+)*\s+[A-Z].{2,80}$", stripped):
                headings.append(stripped)
            elif stripped in COMMON_HEADINGS or (stripped.isupper() and 4 <= len(stripped) <= 80):
                headings.append(stripped.title())
        return list(dict.fromkeys(headings))

    def _detect_module(self, text: str) -> tuple[str, list[str]]:
        lower = text.lower()
        scores = {module: sum(1 for keyword in keywords if keyword in lower) for module, keywords in ERP_MODULE_KEYWORDS.items()}
        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        module, score = ranked[0]
        if not score:
            return "UNKNOWN", []
        secondary = [candidate for candidate, candidate_score in ranked[1:] if candidate_score > 0]
        return module, secondary

    def _detect_doc_type(self, document: ParsedDocument) -> str:
        text = document.raw_text.lower()
        upper = document.raw_text.upper()
        if document.file_extension in {".sql"}:
            return "SQL"
        if document.file_extension in {".pls", ".pkb", ".pks"}:
            return "PLSQL"
        if "CREATE OR REPLACE PACKAGE" in upper:
            return "PLSQL"
        if len(re.findall(r"\bselect\b.+?\bfrom\b", text, re.S)) >= 2:
            return "SQL"
        if ("q:" in text and "a:" in text) or "faq" in text or "frequently asked" in text:
            return "FAQ"
        if any(term in text for term in ["br100", "md050", "functional requirement", "functional design"]):
            return "FUNCTIONAL_DESIGN"
        if any(term in text for term in ["technical design", "interface", "package", "table mapping"]):
            return "TECHNICAL_DESIGN"
        if any(term in text for term in ["error", "resolution", "root cause", "symptom", "troubleshooting"]):
            return "TROUBLESHOOTING_NOTE"
        if any(term in text for term in ["step", "procedure", "prerequisite", "validation"]):
            return "SOP"
        if any(term in text for term in ["oracle", "ebs", "my oracle support", "doc id", "responsibility"]):
            return "ORACLE_DOC"
        return "UNKNOWN"


def extract_best_title(
    raw_text: str,
    filename: str,
    headings: list[str],
    erp_module: str | None,
    business_process: str | None,
    doc_type: str | None,
    llm_suggested_title: str | None = None,
) -> str:
    yaml_title = _yaml_title(raw_text)
    if _is_meaningful_title(yaml_title):
        return yaml_title  # type: ignore[return-value]
    for line in raw_text.splitlines():
        stripped = line.strip()
        if re.match(r"^#\s+", stripped):
            title = stripped.lstrip("#").strip()
            if _is_meaningful_title(title):
                return title
            break
    filename_title = _filename_title(filename)
    if _is_meaningful_title(filename_title):
        return filename_title
    for heading in headings:
        if len(heading.split()) > 3 and _is_meaningful_title(heading):
            return heading
    if _is_meaningful_title(llm_suggested_title):
        return llm_suggested_title  # type: ignore[return-value]
    generated = _generated_title(erp_module, business_process, doc_type)
    return generated or filename_title or "Untitled Document"


def _yaml_title(raw_text: str) -> str | None:
    if not raw_text.lstrip().startswith("---"):
        return None
    try:
        parts = raw_text.split("---", 2)
        if len(parts) >= 3:
            data = yaml.safe_load(parts[1]) or {}
            title = data.get("title") if isinstance(data, dict) else None
            return str(title).strip() if title else None
    except yaml.YAMLError:
        return None
    return None


def _is_meaningful_title(title: str | None) -> bool:
    if not title:
        return False
    stripped = title.strip().strip("*").strip()
    if re.match(r"^\d+[\.)]\s+", stripped):
        return False
    if re.match(r"^[A-Z](?:-\d+)?[\.)]\s+", stripped):
        return False
    if stripped.endswith("?"):
        return False
    normalized = re.sub(r"[^A-Z0-9]+", " ", stripped.upper()).strip()
    if normalized in GENERIC_TITLE_DENYLIST:
        return False
    return len(stripped) >= 4


def _filename_title(filename: str) -> str:
    stem = Path(filename).stem
    return re.sub(r"[_-]+", " ", stem).strip().title()


def _generated_title(erp_module: str | None, business_process: str | None, doc_type: str | None) -> str:
    if erp_module and erp_module != "UNKNOWN" and business_process:
        doc_label = (doc_type or "Document").replace("_", " ").title()
        return f"{erp_module} {business_process} {doc_label}"
    return ""
