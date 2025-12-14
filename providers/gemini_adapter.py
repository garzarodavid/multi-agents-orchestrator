import asyncio
from typing import Any, Dict, List, Optional

from llm_client import (
    resolve_model,
    load_model_map,
    _extract_text_from_response,
    STRATEGY_DEFAULT,
    MODEL_MAP_ENV,
)
from providers.base import ChatResult, LLMProvider


class GeminiAdapter(LLMProvider):
    def __init__(self, default_model: str, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Gemini SDK (google-generativeai) nao instalado: {exc}")

        api_key = _get_env("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY nao definido para Gemini")

        genai.configure(api_key=api_key)
        self._genai = genai
        self.default_model = default_model
        self.name = "gemini"
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
            "gemini",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )

        def _call() -> ChatResult:
            gen_model = self._genai.GenerativeModel(model_name=resolved_model)
            converted = _to_gemini_messages(messages)
            resp = gen_model.generate_content(converted)
            text = _extract_text_from_response(resp)
            # SDK do Gemini pode nao expor usage; devolve vazio.
            usage: Dict[str, Any] = {}
            return ChatResult(text=text, usage=usage, raw=resp)

        return await asyncio.to_thread(_call)


def _to_gemini_messages(messages: List[Dict[str, str]]) -> List[Dict[str, object]]:
    converted: List[Dict[str, object]] = []
    for msg in messages:
        role = msg.get("role") or "user"
        content = msg.get("content") or ""
        converted.append({"role": role, "parts": [{"text": content}]})
    return converted


def _get_env(name: str) -> Optional[str]:
    import os

    return os.getenv(name)


def _env_model_map_path() -> Optional[str]:
    import os

    return os.getenv(MODEL_MAP_ENV)
