import importlib

from ragdocforge.config import load_app_settings


def test_public_demo_mode_defaults_provider_safely(monkeypatch):
    monkeypatch.setenv("RAGDOCFORGE_PUBLIC_DEMO_MODE", "true")
    monkeypatch.setenv("RAGDOCFORGE_LLM_PROVIDER", "ollama")

    settings = load_app_settings()

    assert settings.public_demo_mode is True
    assert settings.llm_provider == "disabled"


def test_sample_files_can_be_loaded():
    app = importlib.import_module("ragdocforge.app")

    assert app.load_sample_sop() == ["examples/sample_gl_journal_import_sop.md"]
    assert len(app.load_all_samples()) == 4


def test_upload_limits_are_enforced(tmp_path):
    app = importlib.import_module("ragdocforge.app")
    files = []
    for index in range(app.SETTINGS.max_files_per_batch + 1):
        path = tmp_path / f"sample_{index}.md"
        path.write_text("sample", encoding="utf-8")
        files.append(str(path))

    outputs = app.analyze(files, "", "", "", 700, 100, False, "disabled", "", "", "", 12000, 8)

    assert "Upload validation failed" in outputs[0]
    assert outputs[14] is None
