import httpx

from ragdocforge.llm.ollama_provider import OllamaProvider


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.text = str(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("failed", request=httpx.Request("GET", "http://test"), response=self)

    def json(self):
        return self._payload


def test_ollama_provider_resolves_single_tagged_model(monkeypatch):
    provider = OllamaProvider("http://ollama", "gemma3")

    def fake_get(url, timeout):
        return _FakeResponse({"models": [{"name": "gemma3:4b"}]})

    monkeypatch.setattr(httpx, "get", fake_get)

    assert provider._resolve_model_name() == "gemma3:4b"


def test_ollama_provider_reports_available_models(monkeypatch):
    provider = OllamaProvider("http://ollama", "missing")

    def fake_get(url, timeout):
        return _FakeResponse({"models": [{"name": "gemma3:4b"}, {"name": "llama3.2:3b"}]})

    monkeypatch.setattr(httpx, "get", fake_get)

    try:
        provider._resolve_model_name()
    except Exception as exc:
        message = str(exc)
    else:
        message = ""

    assert "Available models" in message
