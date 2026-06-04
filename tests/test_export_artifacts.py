import json
import zipfile

from ragdocforge.app import analyze


def _analyze_disabled(files):
    return analyze(files, "", "", "", 700, 100, False, "disabled", "", "", "", 20000, 12)


def test_analyze_exports_manifest_and_zip_layout():
    outputs = _analyze_disabled(["examples/sample_sop.md", "examples/sample_sql.sql", "examples/sample_plsql.pks"])
    manifest_path = outputs[13]
    zip_path = outputs[14]

    manifest = json.load(open(manifest_path, encoding="utf-8"))

    assert manifest["documents_processed"] == 3
    assert manifest["documents_failed"] == 0
    assert manifest["llm_analysis_enabled"] is False
    assert manifest["chunks_created"] >= 3
    assert manifest["outputs"]["markdown_dir"] == "ragdocforge_outputs/markdown/"
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
    assert "ragdocforge_outputs/chunks.jsonl" in names
    assert "ragdocforge_outputs/quality_report.json" in names
    assert "ragdocforge_outputs/manifest.json" in names
    assert "ragdocforge_outputs/metadata_sidecar.json" in names
    assert "ragdocforge_outputs/README_OUTPUTS.md" in names
    assert any(name.startswith("ragdocforge_outputs/markdown/") and name.endswith(".md") for name in names)


def test_analyze_continues_when_one_document_fails(tmp_path):
    bad_path = tmp_path / "missing.md"
    outputs = _analyze_disabled(["examples/sample_sop.md", str(bad_path)])
    analysis = outputs[2]
    manifest = json.load(open(outputs[13], encoding="utf-8"))

    assert manifest["documents_processed"] == 1
    assert manifest["documents_failed"] == 1
    assert "FAILED" in set(analysis["doc_type"])


def test_analyze_mock_llm_exports_reports():
    outputs = analyze(["examples/sample_sop.md"], "", "", "", 700, 100, True, "mock", "", "", "", 20000, 2)
    llm_review = outputs[4]
    suggested_sections = outputs[5]
    manifest = json.load(open(outputs[13], encoding="utf-8"))
    with zipfile.ZipFile(outputs[14]) as archive:
        names = set(archive.namelist())

    assert llm_review["provider_used"] == "mock"
    assert len(suggested_sections) >= 1
    assert manifest["llm_analysis_enabled"] is True
    assert manifest["llm_provider"] == "mock"
    assert "ragdocforge_outputs/llm_analysis_report.json" in names
    assert "ragdocforge_outputs/suggested_sections.md" in names
    assert "ragdocforge_outputs/output_summary.md" in names
    assert "ragdocforge_outputs/metadata_sidecar.json" in names


def test_gradio_analyze_pipeline_uses_hardened_slice_2_5_and_2_6_exports(tmp_path):
    source = tmp_path / "journal_import_errors.md"
    source.write_text(
        """
# Journal Import Errors

## Summary

This troubleshooting note describes Journal Import failures.
Function Err Message: Preparing main_prep from main_stmt.
General Oracle warning text should not become object metadata.

## Solution

```sql
SELECT gi.status, fl.meaning
FROM apps.gl_interface gi, apps.fnd_lookups fl
WHERE gi.status = fl.lookup_code;
```

FRM-41830: List of Values contains no entries.
APP-00268: Unable to find period.
ORA-00054: resource busy and acquire with NOWAIT specified.

## References

Oracle General Ledger User Guide.
"""
        + " ".join(["journal import interface diagnostic detail"] * 140),
        encoding="utf-8",
    )
    outputs = analyze(
        [str(source)],
        "GL",
        "TROUBLESHOOTING_NOTE",
        "Journal Import",
        700,
        100,
        False,
        "disabled",
        "",
        "",
        "",
        20000,
        12,
    )
    zip_path = outputs[14]
    forbidden = {"A", "GENERAL", "ORACLE", "CAN", "IS", "ERR", "ON", "RETURN", "WARNING"}

    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        assert "ragdocforge_outputs/metadata_sidecar.json" in names
        assert "ragdocforge_outputs/manifest.json" in names
        assert "ragdocforge_outputs/chunks.jsonl" in names
        assert "ragdocforge_outputs/quality_report.json" in names

        manifest = json.loads(archive.read("ragdocforge_outputs/manifest.json").decode("utf-8"))
        chunks = [json.loads(line) for line in archive.read("ragdocforge_outputs/chunks.jsonl").decode("utf-8").splitlines()]
        quality_report = json.loads(archive.read("ragdocforge_outputs/quality_report.json").decode("utf-8"))
        metadata_sidecar = json.loads(archive.read("ragdocforge_outputs/metadata_sidecar.json").decode("utf-8"))

    assert manifest["metadata_quality_hardening_enabled"] is True
    assert manifest["metadata_precision_refinement_enabled"] is True
    assert manifest["chunk_metadata_mode"] == "document_and_chunk_level_separated"
    assert manifest["error_metadata_mode"] == "split_error_codes_and_context_lines"
    assert manifest["chunk_doc_metadata_mode"] == "compact_ref_with_counts"
    assert manifest["include_full_doc_metadata_in_chunks"] is False
    assert manifest["metadata_sidecar_path"] == "metadata_sidecar.json"

    first_chunk = chunks[0]
    assert "tables" not in first_chunk["metadata"]
    assert "functions" not in first_chunk["metadata"]
    assert "error_messages" not in first_chunk["metadata"]
    assert "doc_level" in first_chunk["metadata"]
    assert "chunk_level" in first_chunk["metadata"]
    assert first_chunk["metadata"]["doc_level"]["metadata_ref"].startswith("metadata_sidecar.json#")

    document_entry = metadata_sidecar["documents"][0]
    object_names = set()
    for candidates in document_entry["oracle_objects"].values():
        object_names.update(candidate["name"] for candidate in candidates)
    assert forbidden.isdisjoint(object_names)
    assert "FND_LOOKUPS" in object_names
    assert document_entry["error_codes"]
    assert document_entry["error_context_lines"]

    report = quality_report["reports"][0]
    assert report["blocking_issues"]
    assert report["raw_score"] >= report["overall_score"]
    assert report["final_score"] == report["overall_score"]
    assert report["overall_score"] < 75
    assert report["readiness_level"] != "GOOD"
    assert report["score_cap_reasons"]

    assert all(chunk["metadata"]["doc_level"]["metadata_ref"] for chunk in chunks)
    assert min(chunk["metadata"]["doc_level"]["tables_count"] for chunk in chunks) >= 1
    assert all(chunk["metadata"]["chunk_level"].get("error_codes") is not None for chunk in chunks)
