"""
Loader simples para configuracao de servidores MCP.

Usa TOML (Python 3.11+: tomllib) para ler um arquivo no formato:

[servers.postgres]
command = "psql"
args = ["--no-psqlrc"]

[servers.azure]
command = "az"
args = ["account", "show"]
"""

import os
from typing import Any, Dict, Optional, Tuple

try:
    import tomllib  # type: ignore
except Exception:  # pragma: no cover
    tomllib = None


def load_mcp_servers(config_path: Optional[str] = None) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Carrega a configuracao MCP a partir de um arquivo TOML.

    :param config_path: Caminho opcional; se omitido usa env MCP_SERVERS_FILE.
    :return: (servidores, aviso) onde aviso e uma string em caso de problema.
    """
    path = config_path or os.getenv("MCP_SERVERS_FILE")
    if not path:
        return {}, None

    if tomllib is None:
        return {}, "tomllib nao disponivel para ler TOML; use Python 3.11+ ou instale tomli"

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return {}, f"arquivo MCP nao encontrado: {path}"
    except Exception as exc:  # pragma: no cover
        return {}, f"falha ao ler MCP: {exc}"

    servers = data.get("servers") if isinstance(data, dict) else None
    if not isinstance(servers, dict):
        return {}, "formato MCP invalido: esperado bloco [servers.<nome>]"

    return servers, None
