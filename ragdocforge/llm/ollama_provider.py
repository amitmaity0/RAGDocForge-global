import json

import httpx

from ragdocforge.llm.json_utils import extract_first_json_object
from ragdocforge.llm.provider import LLMProvider, LLMProviderError


class OllamaProvider(LLMProvider):
    provider_name = "ollama"

    def __init__(self, base_url: str, model_name: str, timeout_seconds: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.base_url and self.model_name)

    def generate_json(self, system_prompt: str, user_prompt: str, schema_name: str, temperature: float = 0.1, max_tokens: int = 2048) -> dict:
        content = self.generate_text(system_prompt, user_prompt, temperature, max_tokens)
        payload = extract_first_json_object(content)
        if not isinstance(payload, dict):
            raise LLMProviderError(f"{self.provider_name} returned invalid JSON for {schema_name}.")
        return payload

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, max_tokens: int = 2048) -> str:
        if not self.is_configured():
            raise LLMProviderError("Ollama provider is not configured.")
        model_name = self._resolve_model_name()
        request = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        try:
            response = httpx.post(f"{self.base_url}/api/chat", content=json.dumps(request), timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except httpx.HTTPStatusError as exc:
            detail = _safe_error_detail(exc.response)
            raise LLMProviderError(f"Ollama provider request failed: HTTP {exc.response.status_code}. {detail}") from exc
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            raise LLMProviderError(f"Ollama provider request failed: {type(exc).__name__}. Base URL: {self.base_url}; model: {self.model_name}") from exc

    def _resolve_model_name(self) -> str:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=min(self.timeout_seconds, 10))
            response.raise_for_status()
            models = [item.get("name", "") for item in response.json().get("models", [])]
        except (httpx.HTTPError, ValueError):
            return self.model_name
        if self.model_name in models:
            return self.model_name
        prefix_matches = [name for name in models if name.startswith(f"{self.model_name}:")]
        if len(prefix_matches) == 1:
            return prefix_matches[0]
        if models:
            raise LLMProviderError(f"Ollama model '{self.model_name}' was not found. Available models: {', '.join(models)}")
        return self.model_name


def _safe_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text[:240]
    if isinstance(payload, dict) and payload.get("error"):
        return str(payload["error"])
    return str(payload)[:240]
