import asyncio
from typing import Any, Dict, List, Optional

from llm_client import resolve_model, load_model_map, _extract_text_from_response, STRATEGY_DEFAULT, MODEL_MAP_ENV
from providers.base import ChatResult, LLMProvider


class OpenAIAdapter(LLMProvider):
    def __init__(self, default_model: str, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"OpenAI SDK nao instalado: {exc}")

        self._client = OpenAI()
        self.default_model = default_model
        self.name = "openai"
        self._strategy = strategy
        self._model_map = load_model_map(_env_model_map_path())

    async def chat(
        self,
        *,
        model: Optional[str],
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        agent: Optional[str] = None,
    ) -> ChatResult:
        resolved_model = resolve_model(
            "openai",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )

        def _call() -> ChatResult:
            completion = self._client.responses.create(
                model=resolved_model,
                input=messages,
                tools=tools or None,
            )
            text = _extract_text_from_response(completion)
            usage = getattr(completion, "usage", {}) or {}
            return ChatResult(text=text, usage=usage, raw=completion)

        return await asyncio.to_thread(_call)


def _env_model_map_path() -> Optional[str]:
    import os

    return os.getenv(MODEL_MAP_ENV)
