from ragdocforge.analyzers.llm_gap_analyzer import enrich_suggested_sections_with_evidence
from ragdocforge.parsers.base_parser import base_document
from ragdocforge.schemas.llm_analysis_models import LLMSuggestedSection


def test_suggested_section_error_code_maps_to_source_evidence():
    document = base_document("journal_import_errors.md", "unused")
    document.error_codes = ["ORA-00054"]
    document.error_context_lines = ["ORA-00054: resource busy and acquire with NOWAIT specified."]
    sections = [
        LLMSuggestedSection(
            section_title="ORA-00054 Resolution",
            reason_needed="Add troubleshooting guidance for ORA-00054.",
            suggested_content="Document the ORA-00054 retry and lock validation steps.",
            priority="high",
            evidence_supported=False,
            requires_sme_confirmation=True,
            source_evidence=[],
            confidence="low",
        )
    ]

    enriched = enrich_suggested_sections_with_evidence(sections, document)

    assert enriched[0].evidence_supported is True
    assert enriched[0].requires_sme_confirmation is True
    assert enriched[0].confidence == "medium"
    assert enriched[0].source_evidence == ["ORA-00054: resource busy and acquire with NOWAIT specified."]


def test_missing_standard_section_remains_sme_confirmed_without_evidence():
    document = base_document("journal_import_errors.md", "unused")
    document.error_codes = ["ORA-00054"]
    section = LLMSuggestedSection(
        section_title="Validation Steps",
        reason_needed="Missing standard section.",
        suggested_content="Add validated checks.",
        priority="medium",
    )

    enriched = enrich_suggested_sections_with_evidence([section], document)

    assert enriched[0].evidence_supported is False
    assert enriched[0].requires_sme_confirmation is True
