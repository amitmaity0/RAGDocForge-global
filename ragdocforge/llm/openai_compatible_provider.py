import json

import httpx

from ragdocforge.llm.json_utils import extract_first_json_object
from ragdocforge.llm.provider import LLMProvider, LLMProviderError


class OpenAICompatibleProvider(LLMProvider):
    provider_name = "openai_compatible"

    def __init__(self, base_url: str, model_name: str, api_key: str = "", timeout_seconds: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.api_key = api_key
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
            raise LLMProviderError("OpenAI-compatible provider is not configured.")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            response = httpx.post(f"{self.base_url}/chat/completions", headers=headers, content=json.dumps(request), timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise LLMProviderError(f"OpenAI-compatible provider request failed: {type(exc).__name__}") from exc
