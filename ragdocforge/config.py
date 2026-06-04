import os
from typing import Literal

from pydantic import BaseModel, Field


LLMProviderName = Literal["disabled", "mock", "ollama", "openai_compatible"]


class AppSettings(BaseModel):
    public_demo_mode: bool = False
    debug: bool = False
    max_files_per_batch: int = Field(default=5, ge=1)
    max_upload_mb_per_file: int = Field(default=10, ge=1)
    llm_provider: LLMProviderName = "disabled"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    llm_timeout_seconds: int = Field(default=60, ge=1)
    llm_max_doc_chars: int = Field(default=12000, ge=1000)
    llm_max_chunks_to_review: int = Field(default=8, ge=0)


def load_app_settings() -> AppSettings:
    public_demo_mode = _env_bool("RAGDOCFORGE_PUBLIC_DEMO_MODE", False)
    provider = os.getenv("RAGDOCFORGE_LLM_PROVIDER", "disabled").strip().lower()
    if public_demo_mode and provider not in {"disabled", "mock"}:
        provider = "disabled"
    if provider not in {"disabled", "mock", "ollama", "openai_compatible"}:
        provider = "disabled"
    return AppSettings(
        public_demo_mode=public_demo_mode,
        debug=_env_bool("RAGDOCFORGE_DEBUG", False),
        max_files_per_batch=_env_int("RAGDOCFORGE_MAX_FILES_PER_BATCH", 5),
        max_upload_mb_per_file=_env_int("RAGDOCFORGE_MAX_UPLOAD_MB_PER_FILE", 10),
        llm_provider=provider,  # type: ignore[arg-type]
        openai_base_url=os.getenv("RAGDOCFORGE_OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_api_key=os.getenv("RAGDOCFORGE_OPENAI_API_KEY", ""),
        openai_model=os.getenv("RAGDOCFORGE_OPENAI_MODEL", "gpt-4.1-mini"),
        ollama_base_url=os.getenv("RAGDOCFORGE_OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("RAGDOCFORGE_OLLAMA_MODEL", "qwen2.5:7b"),
        llm_timeout_seconds=_env_int("RAGDOCFORGE_LLM_TIMEOUT_SECONDS", 60),
        llm_max_doc_chars=_env_int("RAGDOCFORGE_LLM_MAX_DOC_CHARS", 12000),
        llm_max_chunks_to_review=_env_int("RAGDOCFORGE_LLM_MAX_CHUNKS_TO_REVIEW", 8),
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default
