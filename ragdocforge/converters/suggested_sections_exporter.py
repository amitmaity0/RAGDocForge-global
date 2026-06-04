from collections import defaultdict

from ragdocforge.schemas.llm_analysis_models import LLMAnalysisBundle


class SuggestedSectionsExporter:
    def write(self, bundles: list[LLMAnalysisBundle], path: str) -> str:
        lines = ["# Suggested Content Improvements", ""]
        by_source = defaultdict(list)
        for bundle in bundles:
            by_source[bundle.source_file].extend(bundle.suggested_sections)
        if not by_source:
            lines.extend(["No LLM suggested sections were generated.", ""])
        for source_file, sections in by_source.items():
            lines.extend([f"## Source: {source_file}", ""])
            for section in sections:
                lines.extend(
                    [
                        f"### {section.priority.title()}: {section.section_title}",
                        "",
                        f"Confidence: {section.confidence}  ",
                        f"Evidence supported: {str(section.evidence_supported).lower()}  ",
                        f"Requires SME confirmation: {str(section.requires_sme_confirmation).lower()}  ",
                        "",
                        "Reason needed:",
                        section.reason_needed,
                        "",
                        "Source evidence:",
                        *[f"- {item}" for item in (section.source_evidence or ["No direct source evidence supplied."])],
                        "",
                        "Suggested draft content:",
                        "```markdown",
                        section.suggested_content.strip(),
                        "```",
                        "",
                    ]
                )
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(lines).strip() + "\n")
        return path
