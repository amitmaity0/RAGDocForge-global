from ragdocforge.analyzers.gap_analyzer import GapAnalyzer
from ragdocforge.schemas.document_models import ParsedDocument
from ragdocforge.schemas.quality_models import QualityDimensionScore, QualityReport


class QualityCapContext:
    def __init__(self, document: ParsedDocument, dimensions: list[QualityDimensionScore], blocking_issues: list[str]) -> None:
        self.document = document
        self.dimensions = {dimension.name: dimension.score for dimension in dimensions}
        self.blocking_issues = blocking_issues


class QualityScorer:
    def score(self, document: ParsedDocument) -> QualityReport:
        missing = GapAnalyzer().missing_sections(document)
        dimensions = [
            self._dimension("Metadata completeness", self._metadata_score(document), "ERP module, document type, and business process metadata improve retrieval filters."),
            self._dimension("Chunkability", self._chunkability_score(document), "Heading structure, paragraph shape, and section size support deterministic chunk boundaries."),
            self._dimension("Retrieval specificity", self._retrieval_score(document), "Oracle objects, errors, parameters, process terms, and concurrent programs provide query anchors."),
            self._dimension("Operational usefulness", self._operational_score(document), "Actionable steps, diagnostics, expected results, validation, and troubleshooting details matter for support use."),
            self._dimension("Grounding quality", self._grounding_score(document), "Source filename, section names, examples, SQL snippets, and navigation cues improve answer grounding."),
            self._dimension("Procedure completeness", max(1, 5 - len(missing)), "Missing required sections reduce answer completeness."),
            self._dimension("SQL safety and context", self._sql_score(document), "SQL should include purpose, bind parameters, risk notes, and expected output interpretation."),
            self._dimension("Ambiguity risk", self._ambiguity_score(document), "Clear title, module, audience, process, and specific references reduce ambiguity."),
        ]
        blocking = self._blocking_issues(document, missing)
        raw_score = round(sum(d.score for d in dimensions) / (len(dimensions) * 5) * 100)
        overall, cap_reasons = apply_quality_score_caps(raw_score, QualityCapContext(document, dimensions, blocking))
        if document.detected_erp_module == "UNKNOWN":
            document.warnings.append("ERP module could not be detected deterministically.")
        if document.detected_doc_type == "UNKNOWN":
            document.warnings.append("Document type could not be detected deterministically.")
        if cap_reasons:
            document.warnings.append("Quality score was capped because blocking issues or metadata quality problems were detected.")
        return QualityReport(
            doc_id=document.doc_id,
            source_file=document.source_file,
            raw_score=raw_score,
            overall_score=overall,
            readiness_level=self._readiness(overall),
            dimensions=dimensions,
            strengths=self._strengths(document),
            blocking_issues=blocking,
            warnings=document.warnings,
            recommended_actions=self._actions(document, missing),
            missing_sections=missing,
            score_cap_reasons=cap_reasons,
        )

    def _dimension(self, name: str, score: int, explanation: str) -> QualityDimensionScore:
        return QualityDimensionScore(name=name, score=max(0, min(5, score)), explanation=explanation)

    def _metadata_score(self, document: ParsedDocument) -> int:
        score = 0
        score += 1 if document.title else 0
        score += 2 if document.detected_erp_module != "UNKNOWN" else 0
        score += 1 if document.detected_doc_type != "UNKNOWN" else 0
        score += 1 if document.business_process else 0
        if document.file_extension in {".sql", ".pls", ".pkb", ".pks"}:
            score += 1 if document.tables or document.views or document.packages or document.procedures else 0
        elif score < 5:
            score += 1 if document.source_file else 0
        return score

    def _chunkability_score(self, document: ParsedDocument) -> int:
        paragraphs = [part for part in document.raw_text.split("\n\n") if part.strip()]
        if len(document.headings) >= 3 and paragraphs:
            return 5
        if document.headings:
            return 4
        if len(paragraphs) >= 3:
            return 3
        if len(document.raw_text.split()) > 700:
            return 1
        return 2

    def _retrieval_score(self, document: ParsedDocument) -> int:
        anchors = len(document.tables + document.views + document.packages + document.procedures + document.error_messages + document.concurrent_programs + document.keywords)
        if document.business_process:
            anchors += 1
        if document.detected_erp_module != "UNKNOWN":
            anchors += 1
        return min(5, anchors)

    def _operational_score(self, document: ParsedDocument) -> int:
        text = document.raw_text.lower()
        signals = ["step", "diagnostic", "expected", "validation", "resolution", "troubleshooting", "rerun", "confirm"]
        return min(5, sum(1 for signal in signals if signal in text))

    def _grounding_score(self, document: ParsedDocument) -> int:
        text = document.raw_text.lower()
        score = 1 if document.source_file else 0
        score += 1 if document.headings else 0
        score += 1 if "select " in text and " from " in text else 0
        score += 1 if "example" in text or "screen" in text or "responsibility" in text else 0
        score += 1 if document.tables or document.error_messages else 0
        return score

    def _sql_score(self, document: ParsedDocument) -> int:
        text = document.raw_text.lower()
        has_sql = document.file_extension in {".sql", ".pls", ".pkb", ".pks"} or ("select " in text and " from " in text)
        if not has_sql:
            return 3
        score = 0
        score += 1 if "select " in text and not any(term in text for term in ["update ", "delete ", "insert ", "merge ", "drop ", "truncate ", "alter "]) else 0
        score += 1 if document.keywords or ":" in document.raw_text else 0
        score += 1 if "purpose" in text else 0
        score += 1 if "expected" in text or "interpret" in text else 0
        score += 1 if "risk" in text or "read-only" in text or not document.warnings else 0
        return score

    def _ambiguity_score(self, document: ParsedDocument) -> int:
        text = document.raw_text.lower()
        score = 0
        score += 1 if document.title and len(document.title.split()) >= 3 else 0
        score += 1 if document.detected_erp_module != "UNKNOWN" else 0
        score += 1 if document.business_process else 0
        score += 1 if document.tables or document.packages or document.error_messages else 0
        vague_refs = sum(text.count(term) for term in ["run this", "check the table", "fix issue", "do the needful"])
        score += 1 if vague_refs == 0 else 0
        return score

    def _readiness(self, score: int) -> str:
        if score >= 90:
            return "EXCELLENT"
        if score >= 75:
            return "GOOD"
        if score >= 60:
            return "NEEDS_IMPROVEMENT"
        if score >= 40:
            return "POOR"
        return "NOT_RAG_READY"

    def _blocking_issues(self, document: ParsedDocument, missing: list[str]) -> list[str]:
        issues: list[str] = []
        if len(document.raw_text.strip()) < 80:
            issues.append("Raw text is too short for reliable RAG conversion.")
        if not document.title:
            issues.append("Missing title.")
        if document.detected_erp_module == "UNKNOWN":
            issues.append("Missing or unclear ERP module metadata.")
        if document.detected_doc_type == "UNKNOWN":
            issues.append("Missing or unclear document type.")
        if not document.headings and len(document.raw_text) > 1500:
            issues.append("Long document has no detectable headings.")
        if document.file_extension in {".sql", ".pls", ".pkb", ".pks"} and not (document.tables or document.views or document.packages):
            issues.append("SQL/PLSQL file has no detected tables, views, or packages.")
        heading_text = " ".join(document.headings).lower()
        raw_lower = document.raw_text.lower()
        if document.detected_doc_type == "SOP" and not any(term in heading_text or term in raw_lower for term in ["procedure", "steps", "step "]):
            issues.append("SOP-like document has no procedure or steps.")
        if document.detected_doc_type == "TROUBLESHOOTING_NOTE" and not any(term in heading_text or term in raw_lower for term in ["resolution", "validation"]):
            issues.append("Troubleshooting-like document has no resolution or validation.")
        if missing:
            issues.append("Missing required sections: " + ", ".join(missing))
        return issues

    def _strengths(self, document: ParsedDocument) -> list[str]:
        strengths = []
        if document.headings:
            strengths.append("Contains extractable section headings.")
        if document.tables or document.packages:
            strengths.append("Includes Oracle object names useful for retrieval.")
        if document.error_messages:
            strengths.append("Includes explicit error messages.")
        return strengths or ["Document content was parsed successfully."]

    def _actions(self, document: ParsedDocument, missing: list[str]) -> list[str]:
        actions = [f"Add a {section} section." for section in missing]
        if document.detected_erp_module == "UNKNOWN":
            actions.append("Add explicit Oracle EBS module metadata.")
        if document.file_extension in {".sql", ".pls", ".pkb", ".pks"}:
            actions.append("Document SQL purpose, bind parameters, expected output, and safety classification.")
        if document.error_messages:
            actions.append("Add error-message variants users may search for.")
        if document.tables or document.views:
            actions.append("Add a table/view glossary.")
        if not document.headings and len(document.raw_text) > 1500:
            actions.append("Split long sections with descriptive headings.")
        if document.detected_doc_type in {"SOP", "TROUBLESHOOTING_NOTE"}:
            actions.append("Add rollback or recovery steps.")
        return actions


def apply_quality_score_caps(raw_score: int, report_context: QualityCapContext) -> tuple[int, list[str]]:
    caps: list[tuple[int, str]] = []
    document = report_context.document
    blocking_count = len(report_context.blocking_issues)
    if blocking_count >= 1:
        caps.append((74, "Blocking issues detected; maximum score capped at 74."))
    if blocking_count >= 2:
        caps.append((69, "Multiple blocking issues detected; maximum score capped at 69."))
    if document.detected_erp_module == "UNKNOWN":
        caps.append((59, "ERP module is UNKNOWN; maximum score capped at 59."))
    if document.detected_doc_type == "UNKNOWN":
        caps.append((64, "Document type is UNKNOWN; maximum score capped at 64."))
    if document.detected_doc_type in {"SOP", "TROUBLESHOOTING_NOTE"} and report_context.dimensions.get("Procedure completeness", 0) <= 1:
        caps.append((69, "Procedure completeness is very low; maximum score capped at 69."))
    if document.detected_doc_type in {"SQL", "PLSQL"} and report_context.dimensions.get("SQL safety and context", 0) <= 1:
        caps.append((69, "SQL safety/context is very low; maximum score capped at 69."))
    if not document.headings and len(document.raw_text) > 1500:
        caps.append((64, "Long document has no headings; maximum score capped at 64."))
    if document.metadata_confidence < 0.70:
        caps.append((74, "Metadata extraction confidence is below 0.70; maximum score capped at 74."))
    if report_context.dimensions.get("Chunkability", 0) <= 1:
        caps.append((69, "Chunkability is very low; maximum score capped at 69."))
    if not caps:
        return raw_score, []
    max_score = min(cap for cap, _ in caps)
    return min(raw_score, max_score), [reason for _, reason in caps]
