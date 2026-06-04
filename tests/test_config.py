from ragdocforge.config import load_app_settings


def test_config_defaults_load_without_env(monkeypatch):
    for key in [
        "RAGDOCFORGE_PUBLIC_DEMO_MODE",
        "RAGDOCFORGE_DEBUG",
        "RAGDOCFORGE_MAX_FILES_PER_BATCH",
        "RAGDOCFORGE_LLM_PROVIDER",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = load_app_settings()

    assert settings.public_demo_mode is False
    assert settings.debug is False
    assert settings.max_files_per_batch == 5
    assert settings.llm_provider == "disabled"


def test_config_env_overrides_and_bool_int_parsing(monkeypatch):
    monkeypatch.setenv("RAGDOCFORGE_PUBLIC_DEMO_MODE", "true")
    monkeypatch.setenv("RAGDOCFORGE_DEBUG", "1")
    monkeypatch.setenv("RAGDOCFORGE_MAX_FILES_PER_BATCH", "3")
    monkeypatch.setenv("RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW", "2")
    monkeypatch.setenv("RAGDOCFORGE_LLM_PROVIDER", "ollama")

    settings = load_app_settings()

    assert settings.public_demo_mode is True
    assert settings.debug is True
    assert settings.max_files_per_batch == 3
    assert settings.llm_max_chunks_to_review == 2
    assert settings.llm_provider == "disabled"


def test_invalid_integer_env_falls_back(monkeypatch):
    monkeypatch.setenv("RAGDOCFORGE_MAX_UPLOAD_MB_PER_FILE", "not-a-number")

    assert load_app_settings().max_upload_mb_per_file == 10
