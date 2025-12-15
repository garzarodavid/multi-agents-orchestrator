import os
import json
import subprocess
from typing import Optional


def _env_token(name: str) -> Optional[str]:
    val = os.getenv(name)
    return val if val else None


def _from_az_cli(resource: str = "https://management.azure.com/") -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["az", "account", "get-access-token", "--resource", resource, "--output", "json"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(out)
        return data.get("accessToken")
    except Exception:
        return None


def _from_gh_cli() -> Optional[str]:
    try:
        out = subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL)
        return out.strip() or None
    except Exception:
        return None


def get_token(provider: str) -> Optional[str]:
    """
    Obtém token herdando do CLI ou env. Providers suportados:
    - openai, gemini, claude (usa OPENAI_API_KEY/GOOGLE_API_KEY/ANTHROPIC_API_KEY)
    - azure (AZURE_ACCESS_TOKEN ou az cli)
    - github (GITHUB_TOKEN ou gh auth token)
    - postgres (PGPASSWORD, se existir)
    """
    prov = provider.lower()
    env_override = _env_token(f"LLM_TOKEN_{prov.upper()}")
    if env_override:
        return env_override

    if prov == "openai":
        return _env_token("OPENAI_API_KEY")
    if prov == "gemini":
        return _env_token("GOOGLE_API_KEY")
    if prov == "claude":
        return _env_token("ANTHROPIC_API_KEY")
    if prov == "azure":
        return _env_token("AZURE_ACCESS_TOKEN") or _from_az_cli()
    if prov == "github":
        return _env_token("GITHUB_TOKEN") or _from_gh_cli()
    if prov == "postgres":
        return _env_token("PGPASSWORD")
    return None
