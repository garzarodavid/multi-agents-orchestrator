import json
import subprocess
from typing import Any, Dict, List, Optional


class MCPError(Exception):
    ...


class MCPClient:
    """
    Cliente MCP simples via subprocess (stdio). Assumimos que cada servidor MCP
    é configurado no arquivo TOML e expõe comandos/args. Este cliente:
    - resolve o servidor pela chave (ex.: "postgres", "azure")
    - invoca o comando com args adicionais para a tool

    Observação: Esta é uma implementação mínima; para um cliente MCP completo,
    use o SDK específico do MCP (quando disponível) com suporte a auth e tool
    discovery. Aqui mantemos compatibilidade com o modelo conceitual do repo.
    """

    def __init__(self, servers: Dict[str, Any]) -> None:
        self.servers = servers or {}

    def call_tool(self, server_name: str, tool: str, args: Optional[List[str]] = None, env: Optional[Dict[str, str]] = None) -> str:
        server = self.servers.get(server_name)
        if not server:
            raise MCPError(f"Servidor MCP não configurado: {server_name}")

        command = server.get("command")
        base_args = server.get("args") or []
        if not command:
            raise MCPError(f"Servidor MCP sem comando: {server_name}")

        full_cmd = [command] + list(base_args) + list(args or [])
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise MCPError(f"Falha ao executar MCP {server_name}: {exc.stderr or exc}") from exc
