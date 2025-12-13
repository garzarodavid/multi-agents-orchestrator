"""
Compatibilidade: agente de Arquitetura genérico.

Este módulo mantém o nome anterior `agent_arquitetura` e expõe uma função
`create_agent` que delega para o novo Agent.ArquiteturaSolucoes, garantindo
que qualquer código legado continue funcionando.
"""

from . import AgentConfig
from .agent_arquitetura_solucoes import create_arquitetura_solucoes_agent


def create_agent(model: str) -> AgentConfig:
    """
    Cria a configuração do agente de Arquitetura genérico,
    delegando para Agent.ArquiteturaSolucoes.
    """
    return create_arquitetura_solucoes_agent(model)

