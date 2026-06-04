import os
from dataclasses import dataclass
from typing import Protocol

from ragdocforge.config import load_app_settings


class LLMProviderError(RuntimeError):
    pass


class LLMProvider(Protocol):
    provider_name: str

    def is_configured(self) -> bool:
        ...

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> dict:
        ...

    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        ...


@dataclass(frozen=True)
class LLMRuntimeConfig:
    provider: str = "disabled"
    model_name: str = ""
    base_url: str = ""
    api_key: str = ""
    timeout_seconds: int = 120
    max_doc_chars: int = 20000
    max_chunks_to_review: int = 12

    @classmethod
    def from_env(cls) -> "LLMRuntimeConfig":
        settings = load_app_settings()
        provider = settings.llm_provider
        model, base_url = provider_defaults(provider)
        return cls(
            provider=provider,
            model_name=model,
            base_url=base_url,
            api_key=settings.openai_api_key,
            timeout_seconds=settings.llm_timeout_seconds,
            max_doc_chars=settings.llm_max_doc_chars,
            max_chunks_to_review=settings.llm_max_chunks_to_review,
        )


class DisabledLLMProvider:
    provider_name = "disabled"

    def is_configured(self) -> bool:
        return False

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> dict:
        raise LLMProviderError("LLM provider is disabled.")

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        raise LLMProviderError("LLM provider is disabled.")


def build_provider(config: LLMRuntimeConfig) -> LLMProvider:
    provider = config.provider.lower()
    if provider == "mock":
        from ragdocforge.llm.mock_provider import MockLLMProvider

        return MockLLMProvider()
    if provider == "ollama":
        from ragdocforge.llm.ollama_provider import OllamaProvider

        return OllamaProvider(config.base_url, config.model_name, config.timeout_seconds)
    if provider == "openai_compatible":
        from ragdocforge.llm.openai_compatible_provider import OpenAICompatibleProvider

        return OpenAICompatibleProvider(config.base_url, config.model_name, config.api_key, config.timeout_seconds)
    return DisabledLLMProvider()


def provider_defaults(provider: str) -> tuple[str, str]:
    settings = load_app_settings()
    if provider == "ollama":
        return (
            os.getenv("RAGDOCFORGE_OLLAMA_MODEL", settings.ollama_model),
            os.getenv("RAGDOCFORGE_OLLAMA_BASE_URL", settings.ollama_base_url),
        )
    if provider == "openai_compatible":
        return (
            os.getenv("RAGDOCFORGE_OPENAI_MODEL", settings.openai_model),
            os.getenv("RAGDOCFORGE_OPENAI_BASE_URL", settings.openai_base_url),
        )
    return "", ""
