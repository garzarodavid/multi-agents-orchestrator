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


class ClaudeAdapter(LLMProvider):
    def __init__(self, default_model: str, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            import anthropic  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Claude SDK (anthropic) nao instalado: {exc}")

        api_key = _get_env("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY nao definido para Claude")

        self._client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model
        self.name = "claude"
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
            "claude",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )

        def _call() -> ChatResult:
            claude_messages = [m for m in messages if m.get("role") != "system"]
            system_prompts = [m["content"] for m in messages if m.get("role") == "system"]
            system_text = "\n\n".join(system_prompts) if system_prompts else None

            resp = self._client.messages.create(
                model=resolved_model,
                system=system_text,
                messages=[{"role": m["role"], "content": m["content"]} for m in claude_messages],
                max_tokens=2048,
            )
            text = _extract_text_from_response(resp)
            usage = getattr(resp, "usage", {}) or {}
            return ChatResult(text=text, usage=usage, raw=resp)

        return await asyncio.to_thread(_call)


def _get_env(name: str) -> Optional[str]:
    import os

    return os.getenv(name)


def _env_model_map_path() -> Optional[str]:
    import os

    return os.getenv(MODEL_MAP_ENV)
