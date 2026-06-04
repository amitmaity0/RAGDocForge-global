from ragdocforge.converters.suggested_sections_exporter import SuggestedSectionsExporter
from ragdocforge.schemas.llm_analysis_models import LLMAnalysisBundle, LLMSuggestedSection


def test_llm_suggested_section_grounding_defaults():
    section = LLMSuggestedSection(section_title="Validation", reason_needed="Needed", suggested_content="Draft", priority="high")

    assert section.evidence_supported is False
    assert section.requires_sme_confirmation is True
    assert section.confidence == "medium"


def test_suggested_sections_export_includes_grounding_fields(tmp_path):
    section = LLMSuggestedSection(
        section_title="Validation",
        reason_needed="Needed",
        suggested_content="Draft",
        priority="high",
        evidence_supported=False,
        requires_sme_confirmation=True,
        source_evidence=["No validation section was found."],
        confidence="medium",
    )
    bundle = LLMAnalysisBundle(doc_id="doc", source_file="source.md", provider_name="mock", suggested_sections=[section])
    path = tmp_path / "suggested_sections.md"

    SuggestedSectionsExporter().write([bundle], str(path))

    text = path.read_text(encoding="utf-8")
    assert "Evidence supported: false" in text
    assert "Requires SME confirmation: true" in text
    assert "No validation section was found." in text
