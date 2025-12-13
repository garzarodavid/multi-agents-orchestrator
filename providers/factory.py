import os
from typing import Optional

from providers.base import LLMProvider
from providers.openai_adapter import OpenAIAdapter
from llm_client import STRATEGY_DEFAULT


def create_provider_adapter(default_model: str, provider: Optional[str] = None, strategy: Optional[str] = None) -> LLMProvider:
    selected_provider = (provider or os.getenv("LLM_PROVIDER") or "openai").lower()
    selected_strategy = (strategy or os.getenv("LLM_STRATEGY") or STRATEGY_DEFAULT).lower()

    if selected_provider == "openai":
        return OpenAIAdapter(default_model=default_model, strategy=selected_strategy)

    if selected_provider == "gemini":
        raise RuntimeError("Adapter Gemini não implementado nesta etapa (instale SDK google-generativeai e adicione o adapter).")
    if selected_provider == "claude":
        raise RuntimeError("Adapter Claude não implementado nesta etapa (instale SDK anthropic e adicione o adapter).")

    raise RuntimeError(f"Provider LLM desconhecido: {selected_provider}")
