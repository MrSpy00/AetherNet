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
