"""
Pacote com definições de agentes especializados para o orquestrador.

Cada módulo define uma função `create_<nome>_agent(model: str)` que retorna
um dicionário de configuração com, no mínimo:

- name: nome lógico do agente (ex.: "Agent.ArquiteturaSolucoes")
- model: nome do modelo da OpenAI a ser usado
- system_prompt: prompt de sistema completo do agente
- tools: lista opcional de ferramentas MCP conceituais
"""

from typing import Any, Dict

AgentConfig = Dict[str, Any]

