import os
from aethernet.ai.providers import GroqProvider, MistralProvider, DeepSeekProvider, AiRouter

def test_groq_provider_no_key():
    if "GROQ_API_KEY" in os.environ:
        del os.environ["GROQ_API_KEY"]
    provider = GroqProvider()
    res = provider.ask("Hello")
    assert "GROQ_API_KEY bulunamadı" in res

def test_mistral_provider_no_key():
    if "MISTRAL_API_KEY" in os.environ:
        del os.environ["MISTRAL_API_KEY"]
    provider = MistralProvider()
    res = provider.ask("Hello")
    assert "MISTRAL_API_KEY bulunamadı" in res

def test_ai_router_factory():
    p1 = AiRouter.get_provider("groq")
    assert isinstance(p1, GroqProvider)

    p2 = AiRouter.get_provider("mistral")
    assert isinstance(p2, MistralProvider)

def test_groq_provider_payload(monkeypatch):
    import requests
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test123")
    captured = {}
    class MockResponse:
        status_code = 200
        def json(self):
            return {"choices": [{"message": {"content": "Mocked response"}}]}

    def mock_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return MockResponse()

    monkeypatch.setattr(requests, "post", mock_post)
    provider = GroqProvider()
    res = provider.ask("Test prompt")
    assert res == "Mocked response"
    assert captured["json"]["model"] == "openai/gpt-oss-120b"
    assert captured["json"]["reasoning_effort"] == "medium"

