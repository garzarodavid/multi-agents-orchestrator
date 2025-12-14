import os
from typing import Optional

from providers.base import LLMProvider
from providers.openai_adapter import OpenAIAdapter
from providers.gemini_adapter import GeminiAdapter
from providers.claude_adapter import ClaudeAdapter
from llm_client import STRATEGY_DEFAULT, resolve_model, load_model_map


def create_provider_adapter(default_model: str, provider: Optional[str] = None, strategy: Optional[str] = None) -> LLMProvider:
    selected_provider = (provider or os.getenv("LLM_PROVIDER") or "openai").lower()
    selected_strategy = (strategy or os.getenv("LLM_STRATEGY") or STRATEGY_DEFAULT).lower()

    model_map = load_model_map(os.getenv("LLM_MODEL_MAP_FILE"))

    if selected_provider == "openai":
        resolved = resolve_model("openai", requested=None, strategy=selected_strategy, default_model=default_model, model_map=model_map)
        return OpenAIAdapter(default_model=resolved, strategy=selected_strategy)

    if selected_provider == "gemini":
        resolved = resolve_model("gemini", requested=None, strategy=selected_strategy, default_model=default_model, model_map=model_map)
        return GeminiAdapter(default_model=resolved, strategy=selected_strategy)
    if selected_provider == "claude":
        resolved = resolve_model("claude", requested=None, strategy=selected_strategy, default_model=default_model, model_map=model_map)
        return ClaudeAdapter(default_model=resolved, strategy=selected_strategy)

    raise RuntimeError(f"Provider LLM desconhecido: {selected_provider}")
