import subprocess
from typing import Dict, Optional

from multiagents.tokens import get_token


class MCPToolInvoker:
    """Interface simples para invocar tools MCP via CLI/SDK."""

    def call(self, tool: str, args: Optional[Dict] = None) -> str:
        raise NotImplementedError


class AzureCLIInvoker(MCPToolInvoker):
    def __init__(self, resource: str = "https://management.azure.com/") -> None:
        self.resource = resource

    def call(self, tool: str, args: Optional[Dict] = None) -> str:
        token = get_token("azure")
        if not token:
            raise RuntimeError("Token Azure nao disponivel")
        # Para fins de placeholder, apenas retorna token mascarado.
        return f"[azure cli] tool={tool} args={args or {}} token=***"


class GitHubInvoker(MCPToolInvoker):
    def call(self, tool: str, args: Optional[Dict] = None) -> str:
        token = get_token("github")
        if not token:
            raise RuntimeError("Token GitHub nao disponivel")
        return f"[github cli] tool={tool} args={args or {}} token=***"


class PostgresInvoker(MCPToolInvoker):
    def call(self, tool: str, args: Optional[Dict] = None) -> str:
        pwd = get_token("postgres")
        if not pwd:
            raise RuntimeError("Senha Postgres nao disponivel (PGPASSWORD)")
        # Não executa psql de fato; placeholder de integração.
        return f"[postgres cli] tool={tool} args={args or {}} pwd=***"
