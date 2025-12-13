import os
from typing import Optional
from urllib.parse import urlencode

import requests

from transport.schemas import TokenResponse


class TokenBrokerClient:
    """
    Cliente para o Token Broker (ex.: extensão VS Code expondo HTTP local).

    Ordem de resolução:
    1) Se env `LLM_TOKEN_<PROVIDER>` existir, usa direto (fallback).
    2) Caso contrário, chama o broker via HTTP GET /token?provider=<...>.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:17870") -> None:
        self.base_url = base_url.rstrip("/")

    def get_token(self, provider: str) -> str:
        env_key = f"LLM_TOKEN_{provider.upper()}"
        env_val = os.getenv(env_key)
        if env_val:
            return env_val

        query = urlencode({"provider": provider})
        url = f"{self.base_url}/token?{query}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data: TokenResponse = resp.json()  # type: ignore
        return data["access_token"]
