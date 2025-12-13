"""
Clientes LLM agnosticos para OpenAI, Gemini e Claude, com selecao de modelo
orientada a custo/beneficio.

Env vars:
- LLM_PROVIDER=openai|gemini|claude (padrao: openai)
- LLM_STRATEGY=quality|balance|cost (padrao: balance)
- LLM_MODEL_OPENAI / LLM_MODEL_GEMINI / LLM_MODEL_CLAUDE (override por provedor)
- OPENAI_MODEL (compatibilidade) / OPENAI_API_KEY
- GOOGLE_API_KEY (Gemini), ANTHROPIC_API_KEY (Claude)
"""

import os
from typing import Dict, List, Optional, Protocol, Tuple, Any

try:
    import tomllib  # type: ignore
except Exception:  # pragma: no cover
    tomllib = None


class LLMClient(Protocol):
    def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, agent: Optional[str] = None) -> str:  # pragma: no cover - interface
        ...


STRATEGY_DEFAULT = "balance"
MODEL_MAP_ENV = "LLM_MODEL_MAP_FILE"

PROVIDER_MODELS: Dict[str, Dict[str, str]] = {
    "openai": {
        "quality": "gpt-4.1",
        "balance": "gpt-4.1-mini",
        "cost": "gpt-3.5-turbo",
    },
    "gemini": {
        "quality": "gemini-1.5-pro",
        "balance": "gemini-1.5-flash",
        "cost": "gemini-1.0-pro-001",
    },
    "claude": {
        "quality": "claude-3-5-sonnet-20240620",
        "balance": "claude-3-sonnet-20240229",
        "cost": "claude-3-haiku-20240307",
    },
}


def load_model_map(path: Optional[str]) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Carrega um mapa TOML de modelos por provedor->estrategia->chave."""
    if not path:
        return {}
    if tomllib is None:
        return {}
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    # esperado: {provider: {strategy: {default/agent_<nome>: modelo}}}
    out: Dict[str, Dict[str, Dict[str, str]]] = {}
    for provider, strat_map in data.items():
        if not isinstance(strat_map, dict):
            continue
        out[provider] = {}
        for strat, values in strat_map.items():
            if isinstance(values, dict):
                out[provider][strat] = {k: str(v) for k, v in values.items()}
    return out


def resolve_model(
    provider: str,
    requested: Optional[str],
    strategy: str,
    default_model: Optional[str] = None,
    model_map: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None,
    agent: Optional[str] = None,
) -> str:
    """Resolve o modelo considerando override do usuario, mapa por agente, strategy e defaults por provedor."""
    if requested:
        return requested

    env_override = os.getenv(f"LLM_MODEL_{provider.upper()}")
    if env_override:
        return env_override

    if provider == "openai":
        legacy = os.getenv("OPENAI_MODEL")
        if legacy:
            return legacy

    if model_map:
        chosen = _resolve_from_map(model_map, provider, strategy, agent)
        if chosen:
            return chosen

    provider_defaults = PROVIDER_MODELS.get(provider, {})
    chosen = provider_defaults.get(strategy) or provider_defaults.get(STRATEGY_DEFAULT)
    if chosen:
        return chosen

    if default_model:
        return default_model

    if provider_defaults:
        return next(iter(provider_defaults.values()))

    raise RuntimeError(f"Sem modelo configurado para provider {provider}")


def create_llm_client(provider: Optional[str] = None, default_model: Optional[str] = None) -> LLMClient:
    """
    Cria o cliente LLM baseado na env LLM_PROVIDER/LLM_STRATEGY.

    :param provider: override opcional.
    :param default_model: modelo a usar se nada mais estiver definido (compat com OPENAI_MODEL).
    """
    selected_provider = (provider or os.getenv("LLM_PROVIDER") or "openai").lower()
    strategy = (os.getenv("LLM_STRATEGY") or STRATEGY_DEFAULT).lower()
    if strategy not in ("quality", "balance", "cost"):
        strategy = STRATEGY_DEFAULT

    model_map = load_model_map(os.getenv(MODEL_MAP_ENV))

    if selected_provider == "openai":
        model = resolve_model("openai", requested=None, strategy=strategy, default_model=default_model, model_map=model_map)
        return OpenAIClient(model, model_map=model_map, strategy=strategy)

    if selected_provider == "gemini":
        model = resolve_model("gemini", requested=None, strategy=strategy, default_model=default_model, model_map=model_map)
        return GeminiClient(model, model_map=model_map, strategy=strategy)

    if selected_provider == "claude":
        model = resolve_model("claude", requested=None, strategy=strategy, default_model=default_model, model_map=model_map)
        return ClaudeClient(model, model_map=model_map, strategy=strategy)

    raise RuntimeError(f"Provider LLM desconhecido: {selected_provider}")


class OpenAIClient:
    def __init__(self, default_model: str, model_map: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"OpenAI SDK nao instalado: {exc}")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY nao definido")

        self._client = OpenAI(api_key=api_key)
        self.default_model = default_model
        self.provider = "openai"
        self._model_map = model_map or {}
        self._strategy = strategy

    def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, agent: Optional[str] = None) -> str:
        resolved_model = resolve_model(
            "openai",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )
        completion = self._client.responses.create(
            model=resolved_model,
            input=messages,
        )
        return _extract_text_from_response(completion)


class GeminiClient:
    def __init__(self, default_model: str, model_map: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"SDK Gemini (google-generativeai) nao instalado: {exc}")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY nao definido para Gemini")

        genai.configure(api_key=api_key)
        self._genai = genai
        self.default_model = default_model
        self.provider = "gemini"
        self._model_map = model_map or {}
        self._strategy = strategy

    def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, agent: Optional[str] = None) -> str:
        resolved_model = resolve_model(
            "gemini",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )
        gen_model = self._genai.GenerativeModel(model_name=resolved_model)
        converted = _to_gemini_messages(messages)
        resp = gen_model.generate_content(converted)
        return _extract_text_from_response(resp)


class ClaudeClient:
    def __init__(self, default_model: str, model_map: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None, strategy: str = STRATEGY_DEFAULT) -> None:
        try:
            import anthropic  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"SDK Claude (anthropic) nao instalado: {exc}")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY nao definido para Claude")

        self._client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model
        self.provider = "claude"
        self._model_map = model_map or {}
        self._strategy = strategy

    def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, agent: Optional[str] = None) -> str:
        resolved_model = resolve_model(
            "claude",
            requested=model,
            strategy=self._strategy,
            default_model=self.default_model,
            model_map=self._model_map,
            agent=agent,
        )
        # Claude espera lista de mensagens role/content, sem mensagem de sistema aqui.
        claude_messages = [m for m in messages if m.get("role") != "system"]
        system_prompts = [m["content"] for m in messages if m.get("role") == "system"]
        system_text = "\n\n".join(system_prompts) if system_prompts else None

        resp = self._client.messages.create(
            model=resolved_model,
            system=system_text,
            messages=[{"role": m["role"], "content": m["content"]} for m in claude_messages],
            max_tokens=2048,
        )
        return _extract_text_from_response(resp)


def _extract_text_from_response(resp: object) -> str:
    """Extrai texto de respostas heterogeneas (OpenAI, Gemini, Claude) de forma defensiva."""
    # OpenAI responses.create compat: resp.output_text
    if hasattr(resp, "output_text"):
        out_text = getattr(resp, "output_text", None)
        if out_text:
            return str(out_text)

    # OpenAI responses.create: resp.output[0].content[0].text
    try:
        out = getattr(resp, "output", None) or resp.get("output")  # type: ignore
    except Exception:
        out = None

    if out and isinstance(out, list) and out:
        first = out[0]
        try:
            content = first.get("content") if isinstance(first, dict) else getattr(first, "content", None)
            if isinstance(content, list) and content:
                c0 = content[0]
                text = c0.get("text") if isinstance(c0, dict) else getattr(c0, "text", None)
                if text:
                    return str(text)
        except Exception:
            pass

    # Gemini: resp.text
    if hasattr(resp, "text"):
        maybe = getattr(resp, "text", None)
        if maybe:
            return str(maybe)

    # Claude: resp.content list of TextBlock
    if hasattr(resp, "content"):
        try:
            content = getattr(resp, "content")
            if isinstance(content, list) and content:
                first = content[0]
                if hasattr(first, "text"):
                    return str(getattr(first, "text"))
        except Exception:
            pass

    return str(resp)


def _to_gemini_messages(messages: List[Dict[str, str]]) -> List[Dict[str, object]]:
    """Converte mensagens role/content para o formato esperado pelo Gemini."""
    converted: List[Dict[str, object]] = []
    for msg in messages:
        role = msg.get("role") or "user"
        content = msg.get("content") or ""
        converted.append({"role": role, "parts": [{"text": content}]})
    return converted


def _resolve_from_map(
    model_map: Dict[str, Dict[str, Dict[str, str]]],
    provider: str,
    strategy: str,
    agent: Optional[str],
) -> Optional[str]:
    prov = model_map.get(provider)
    if not prov:
        return None
    strat_map = prov.get(strategy) or prov.get(STRATEGY_DEFAULT)
    if not strat_map:
        return None
    if agent:
        key = f"agent_{agent}"
        if key in strat_map:
            return strat_map[key]
    return strat_map.get("default")
