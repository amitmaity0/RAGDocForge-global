import re

from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.metadata_models import ErrorMetadata, EvidenceType, OracleObjectCandidate
from ragdocforge.utils.text_utils import unique_sorted


ORACLE_OBJECT_STOPWORDS = {
    "A", "AN", "AND", "ARE", "AS", "AT", "BE", "BY", "CAN", "DO",
    "FOR", "FROM", "GENERAL", "IF", "IN", "IS", "IT", "NOTE", "OF",
    "ON", "ONE", "OR", "ORACLE", "RETURN", "SELECT", "SET", "THE",
    "THEN", "THIS", "TO", "VALUE", "WARNING", "WHEN", "WHERE",
    "WITH", "YOUR", "ERROR", "FIELD", "TABLE", "VIEW", "PACKAGE",
    "PROCEDURE", "FUNCTION", "DATA", "PROCESS", "STATUS", "TYPE",
    "NUMBER", "DATE", "USER", "SYSTEM", "SUMMARY", "SOLUTION",
    "REFERENCES", "DETAILS", "OVERVIEW", "PURPOSE", "SCOPE",
}

KNOWN_EBS_OBJECT_PREFIXES = {
    "GL_", "AP_", "AR_", "PO_", "INV_", "MTL_", "OE_", "ONT_",
    "FND_", "XLA_", "CE_", "FA_", "HR_", "PER_", "PAY_", "HZ_",
    "RA_", "ZX_", "WF_", "WIP_", "BOM_", "QP_", "MRP_", "PA_",
    "OKC_", "OKS_", "CSI_", "IBY_", "XDO_", "AD_", "ICX_",
    "XX_", "XXX_", "CUX_",
}
PROSE_FUNCTION_LABEL_FOLLOWERS = {
    "MESSAGE", "DESCRIPTION", "NUMBER", "STATUS", "FIELD", "VALUE",
    "NAME", "CODE", "TEXT", "TYPE",
}
FROM_CLAUSE_TERMINATORS = {
    "WHERE", "GROUP", "ORDER", "HAVING", "UNION", "INTERSECT", "MINUS",
    "CONNECT", "START", "MODEL", "FETCH", "FOR",
}

MIN_OBJECT_CONFIDENCE = 0.70
MIN_CHUNK_OBJECT_CONFIDENCE = 0.75

_IDENTIFIER = r"([a-zA-Z][\w$#]*(?:\.[a-zA-Z][\w$#]*)?)"
_SQL_PATTERNS: list[tuple[str, EvidenceType]] = [
    (rf"\bjoin\s+{_IDENTIFIER}", "sql_join"),
    (rf"\bupdate\s+{_IDENTIFIER}", "sql_update"),
    (rf"\binsert\s+into\s+{_IDENTIFIER}", "sql_insert_into"),
    (rf"\bdelete\s+from\s+{_IDENTIFIER}", "sql_delete_from"),
    (rf"\bmerge\s+into\s+{_IDENTIFIER}", "sql_merge_into"),
    (rf"\btable\s*\(\s*{_IDENTIFIER}\s*\)", "sql_from"),
]
_ERROR_CODE_RE = re.compile(r"\b(?:ORA|FRM|APP|REP|PLS|FND|FORM)-\d{3,6}\b", re.I)
_ERROR_CONTEXT_TRIGGER_RE = re.compile(
    r"\b(?:completed with error|completed with warning|concurrent manager encountered an error|"
    r"invalid object|not imported|failed|exception|unable to|cannot)\b|"
    r"\b(?:ORA|FRM|APP|REP|PLS|FND|FORM)-\d{3,6}\b",
    re.I,
)


def normalize_oracle_identifier(name: str) -> str:
    normalized = re.sub(r"\s+", "", name.strip().strip(",;()")).upper()
    if "." in normalized:
        parts = [part for part in normalized.split(".") if part]
        if len(parts) >= 2:
            return parts[-1]
    return normalized


def is_valid_oracle_object_name(name: str, evidence_type: EvidenceType | None = None) -> bool:
    normalized = normalize_oracle_identifier(name)
    if normalized in ORACLE_OBJECT_STOPWORDS:
        return False
    if len(normalized) < 3 or len(normalized) > 128:
        return False
    if normalized.isnumeric() or " " in normalized:
        return False
    if not re.match(r"^[A-Z][A-Z0-9_$#]*(\.[A-Z][A-Z0-9_$#]*)?$", normalized):
        return False
    if evidence_type in {"create_package", "create_package_body", "create_procedure", "create_function", "plsql_signature", "package_member_call"}:
        return True
    if "_" in normalized:
        return True
    if any(normalized.startswith(prefix) for prefix in KNOWN_EBS_OBJECT_PREFIXES):
        return True
    return False


def object_confidence_score(name: str, evidence_type: str | None) -> float:
    normalized = normalize_oracle_identifier(name)
    if not is_valid_oracle_object_name(normalized, evidence_type):  # type: ignore[arg-type]
        return 0.0
    if evidence_type in {"create_package", "create_package_body", "create_procedure", "create_function", "plsql_signature"}:
        return 0.98
    if evidence_type in {"sql_from", "sql_join", "sql_update", "sql_insert_into", "sql_delete_from", "sql_merge_into"}:
        return 0.90
    if evidence_type == "schema_qualified":
        return 0.90
    if any(normalized.startswith(prefix) for prefix in KNOWN_EBS_OBJECT_PREFIXES):
        return 0.85
    if evidence_type == "package_member_call":
        return 0.80
    return 0.30


def extract_oracle_object_candidates(text: str, min_confidence: float = MIN_OBJECT_CONFIDENCE) -> tuple[list[OracleObjectCandidate], int]:
    candidates: list[OracleObjectCandidate] = []
    rejected = 0

    from_candidates, from_rejected = _extract_from_clause_objects_with_rejections(text)
    candidates.extend(from_candidates)
    rejected += from_rejected

    for pattern, evidence_type in _SQL_PATTERNS:
        for match in re.finditer(pattern, text, re.I):
            rejected += _append_candidate(candidates, match.group(1), "table", evidence_type, match.group(0), match.start(1), match.end(1))

    for match in re.finditer(rf"\bcreate\s+or\s+replace\s+package\s+body\s+{_IDENTIFIER}", text, re.I):
        rejected += _append_candidate(candidates, match.group(1), "package", "create_package_body", match.group(0), match.start(1), match.end(1))
    for match in re.finditer(rf"\bcreate\s+or\s+replace\s+package\s+{_IDENTIFIER}", text, re.I):
        rejected += _append_candidate(candidates, match.group(1), "package", "create_package", match.group(0), match.start(1), match.end(1))
    for match in re.finditer(rf"\b(?:create\s+or\s+replace\s+)?procedure\s+{_IDENTIFIER}", text, re.I):
        rejected += _append_candidate(candidates, match.group(1), "procedure", "create_procedure" if "create" in match.group(0).lower() else "plsql_signature", match.group(0), match.start(1), match.end(1))
    function_candidates, function_rejected = _extract_plsql_functions_with_rejections(text)
    candidates.extend(function_candidates)
    rejected += function_rejected
    for match in re.finditer(r"\b([a-zA-Z][\w$#]*(?:_pkg|_api))\.([a-zA-Z][\w$#]*)\b", text, re.I):
        rejected += _append_candidate(candidates, match.group(1), "package", "package_member_call", match.group(0), match.start(1), match.end(1))
        rejected += _append_candidate(candidates, match.group(2), "procedure", "package_member_call", match.group(0), match.start(2), match.end(2))

    deduped: dict[tuple[str, str], OracleObjectCandidate] = {}
    for candidate in candidates:
        if candidate.confidence < min_confidence:
            rejected += 1
            continue
        key = (candidate.name, candidate.object_type)
        if key not in deduped or candidate.confidence > deduped[key].confidence:
            deduped[key] = candidate
    return sorted(deduped.values(), key=lambda item: (item.object_type, item.name)), rejected


def extract_plsql_functions(text: str) -> list[OracleObjectCandidate]:
    candidates, _ = _extract_plsql_functions_with_rejections(text)
    return candidates


def _extract_plsql_functions_with_rejections(text: str) -> tuple[list[OracleObjectCandidate], int]:
    candidates: list[OracleObjectCandidate] = []
    rejected = 0
    patterns: list[tuple[str, EvidenceType]] = [
        (rf"\bcreate\s+or\s+replace\s+function\s+{_IDENTIFIER}", "create_function"),
        (rf"\bfunction\s+{_IDENTIFIER}\s*\(", "plsql_signature"),
        (rf"\bfunction\s+{_IDENTIFIER}\s+return\b", "plsql_signature"),
    ]
    for pattern, evidence_type in patterns:
        for match in re.finditer(pattern, text, re.I):
            name = match.group(1)
            if _is_prose_function_label(text, match.end(1)):
                rejected += 1
                continue
            rejected += _append_candidate(candidates, name, "function", evidence_type, match.group(0), match.start(1), match.end(1))
    return candidates, rejected


def extract_from_clause_objects(text: str) -> list[OracleObjectCandidate]:
    candidates, _ = _extract_from_clause_objects_with_rejections(text)
    return candidates


def _extract_from_clause_objects_with_rejections(text: str) -> tuple[list[OracleObjectCandidate], int]:
    candidates: list[OracleObjectCandidate] = []
    rejected = 0
    for match in re.finditer(r"\bfrom\b\s+", text, re.I):
        if not _has_sql_from_context(text, match.start()):
            continue
        clause_start = match.end()
        clause_end = _from_clause_end(text, clause_start)
        clause = text[clause_start:clause_end]
        for item_match in re.finditer(_IDENTIFIER, clause):
            identifier = item_match.group(1)
            previous = clause[: item_match.start(1)].rstrip()
            if previous and not previous.endswith(",") and item_match.start(1) > 0:
                continue
            absolute_start = clause_start + item_match.start(1)
            absolute_end = clause_start + item_match.end(1)
            rejected += _append_candidate(candidates, identifier, "table", "sql_from", f"FROM {clause.strip()}", absolute_start, absolute_end)
    return candidates, rejected


def extract_error_metadata(text: str) -> ErrorMetadata:
    error_codes = unique_sorted(code.upper() for code in _ERROR_CODE_RE.findall(text))
    context_lines: list[str] = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line or len(line) < 15 or len(line) > 300:
            continue
        if line.rstrip(":").strip().upper() in {"ERROR", "ERRORS", "WARNING", "WARNINGS"}:
            continue
        if _ERROR_CONTEXT_TRIGGER_RE.search(line):
            context_lines.append(line)
    return ErrorMetadata(error_codes=error_codes, error_context_lines=_unique_sorted_preserve_case(context_lines))


def extract_error_messages(text: str) -> list[str]:
    error_metadata = extract_error_metadata(text)
    return _unique_sorted_preserve_case(error_metadata.error_codes + error_metadata.error_context_lines)


def enrich_oracle_objects(document: ParsedDocument) -> ParsedDocument:
    candidates, rejected = extract_oracle_object_candidates(document.raw_text)
    document.oracle_object_candidates = candidates
    document.false_positive_filter_count += rejected
    document.tables = unique_sorted(document.tables + [item.name for item in candidates if item.object_type == "table"])
    document.views = unique_sorted(document.views + [item.name for item in candidates if item.object_type == "view"])
    document.packages = unique_sorted(document.packages + [item.name for item in candidates if item.object_type == "package"])
    document.procedures = unique_sorted(document.procedures + [item.name for item in candidates if item.object_type == "procedure"])
    document.functions = unique_sorted(document.functions + [item.name for item in candidates if item.object_type == "function"])
    document.concurrent_programs = unique_sorted(re.findall(r"(?:concurrent program|request)\s+([A-Z][A-Z0-9 _-]{3,})", document.raw_text, re.I))
    error_metadata = extract_error_metadata(document.raw_text)
    document.error_codes = unique_sorted(document.error_codes + error_metadata.error_codes)
    document.error_context_lines = _unique_sorted_preserve_case(document.error_context_lines + error_metadata.error_context_lines)
    document.error_messages = _unique_sorted_preserve_case(document.error_messages + document.error_codes + document.error_context_lines)
    document.metadata_confidence = _metadata_confidence(document, rejected)
    return document


def _is_prose_function_label(text: str, name_end: int) -> bool:
    follower = re.match(r"\s+([a-zA-Z][\w$#]*)", text[name_end:])
    return bool(follower and follower.group(1).upper() in PROSE_FUNCTION_LABEL_FOLLOWERS)


def _from_clause_end(text: str, clause_start: int) -> int:
    terminator_pattern = r"\b(?:" + "|".join(sorted(FROM_CLAUSE_TERMINATORS)) + r")\b"
    match = re.search(terminator_pattern, text[clause_start:], re.I)
    return clause_start + match.start() if match else len(text)


def _has_sql_from_context(text: str, from_start: int) -> bool:
    statement_start = max(text.rfind(";", 0, from_start), text.rfind("```", 0, from_start), text.rfind("\n\n", 0, from_start))
    context = text[statement_start + 1 : from_start]
    return bool(re.search(r"\b(?:select|delete)\b", context, re.I))


def _unique_sorted_preserve_case(values: list[str]) -> list[str]:
    deduped: dict[str, str] = {}
    for value in values:
        cleaned = value.strip()
        if cleaned and cleaned.upper() not in deduped:
            deduped[cleaned.upper()] = cleaned
    return [deduped[key] for key in sorted(deduped)]


def _append_candidate(
    candidates: list[OracleObjectCandidate],
    name: str,
    object_type: str,
    evidence_type: EvidenceType,
    evidence: str,
    start: int,
    end: int,
) -> int:
    normalized = normalize_oracle_identifier(name)
    confidence = object_confidence_score(name, evidence_type)
    if confidence <= 0:
        return 1
    candidates.append(
        OracleObjectCandidate(
            name=normalized,
            object_type=object_type,  # type: ignore[arg-type]
            confidence=confidence,
            evidence=evidence.strip()[:240],
            evidence_type=evidence_type,
            source_span_start=start,
            source_span_end=end,
        )
    )
    return 0


def _metadata_confidence(document: ParsedDocument, rejected: int) -> float:
    score = 1.0
    if rejected:
        score -= min(0.3, rejected * 0.02)
    if not (document.tables or document.packages or document.error_messages):
        score -= 0.2
    if document.detected_erp_module == "UNKNOWN":
        score -= 0.2
    return max(0.1, round(score, 2))
