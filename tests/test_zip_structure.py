import zipfile

from ragdocforge.app import analyze


def test_zip_uses_slice3_ragdocforge_outputs_structure():
    outputs = analyze(
        ["examples/sample_gl_journal_import_sop.md"],
        "GL",
        "SOP",
        "Journal Import",
        700,
        100,
        False,
        "disabled",
        "",
        "",
        "",
        12000,
        8,
    )

    with zipfile.ZipFile(outputs[14]) as archive:
        names = set(archive.namelist())

    assert any(name.startswith("ragdocforge_outputs/markdown/") for name in names)
    assert "ragdocforge_outputs/chunks.jsonl" in names
    assert "ragdocforge_outputs/quality_report.json" in names
    assert "ragdocforge_outputs/manifest.json" in names
    assert "ragdocforge_outputs/README_OUTPUTS.md" in names


def test_mock_llm_zip_contains_llm_outputs():
    outputs = analyze(
        ["examples/sample_gl_journal_import_sop.md"],
        "GL",
        "SOP",
        "Journal Import",
        700,
        100,
        True,
        "mock",
        "",
        "",
        "",
        12000,
        2,
    )

    with zipfile.ZipFile(outputs[14]) as archive:
        names = set(archive.namelist())

    assert "ragdocforge_outputs/llm_analysis_report.json" in names
    assert "ragdocforge_outputs/suggested_sections.md" in names
