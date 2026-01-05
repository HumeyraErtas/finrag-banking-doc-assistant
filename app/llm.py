from __future__ import annotations
import os
import requests
from app.config import settings


class LLM:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class NoneLLM(LLM):
    def generate(self, prompt: str) -> str:
        # Fallback: return prompt tail or a generic extractive note
        return "LLM kapalı. Yanıt üretilemedi. Lütfen LLM_PROVIDER=ollama veya openai olarak ayarlayın."


class OllamaLLM(LLM):
    def __init__(self):
        self.base = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def generate(self, prompt: str) -> str:
        url = f"{self.base}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return (data.get("response") or "").strip()


class OpenAILLM(LLM):
    """
    Lightweight call (no official SDK dependency).
    Requires OPENAI_API_KEY.
    """
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is empty.")
        self.key = settings.openai_api_key
        self.model = settings.openai_model

    def generate(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a careful assistant that answers using provided context only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        r = requests.post(url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()


def build_llm() -> LLM:
    p = settings.llm_provider.lower().strip()
    if p == "ollama":
        return OllamaLLM()
    if p == "openai":
        return OpenAILLM()
    return NoneLLM()
