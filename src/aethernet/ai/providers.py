import os
import requests
from abc import ABC, abstractmethod
from typing import Optional
from loguru import logger

class BaseAiProvider(ABC):
    """Base AI provider interface"""

    @abstractmethod
    def ask(self, prompt: str, system_prompt: str = "") -> str:
        pass

class DeepSeekProvider(BaseAiProvider):
    def ask(self, prompt: str, system_prompt: str = "") -> str:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            return "DEEPSEEK_API_KEY bulunamadı."
        try:
            res = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt or "Sen bir ağ uzmanısın."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"DeepSeek AI Error: {e}")
        return "DeepSeek yanıt üretemedi."

class GroqProvider(BaseAiProvider):
    """Groq Cloud (openai/gpt-oss-120b) API Provider (https://console.groq.com/keys)"""
    def ask(self, prompt: str, system_prompt: str = "") -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "GROQ_API_KEY bulunamadı (https://console.groq.com/keys)."
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "openai/gpt-oss-120b",
                    "reasoning_effort": "medium",
                    "messages": [
                        {"role": "system", "content": system_prompt or "Sen kıdemli bir ağ ve güvenlik uzmanısın."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                return f"Groq API Hatası: HTTP {res.status_code}"
        except Exception as e:
            logger.error(f"Groq AI Error: {e}")
            return f"Groq isteğinde hata: {e}"

class MistralProvider(BaseAiProvider):
    """Mistral AI Provider (https://console.mistral.ai/)"""
    def ask(self, prompt: str, system_prompt: str = "") -> str:
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            return "MISTRAL_API_KEY bulunamadı (https://console.mistral.ai/)."
        try:
            res = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "mistral-small-latest",
                    "messages": [
                        {"role": "system", "content": system_prompt or "Sen kıdemli bir ağ ve güvenlik uzmanısın."},
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=10
            )
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            else:
                return f"Mistral API Hatası: HTTP {res.status_code}"
        except Exception as e:
            logger.error(f"Mistral AI Error: {e}")
            return f"Mistral isteğinde hata: {e}"

class AiRouter:
    """AI Provider Router with fallback support"""
    PROVIDERS = {
        "deepseek": DeepSeekProvider,
        "groq": GroqProvider,
        "mistral": MistralProvider,
    }

    @classmethod
    def get_provider(cls, name: str = "deepseek") -> BaseAiProvider:
        provider_cls = cls.PROVIDERS.get(name.lower(), DeepSeekProvider)
        return provider_cls()
