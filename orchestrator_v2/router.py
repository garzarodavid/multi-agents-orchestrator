from typing import Dict

from orchestrator_v2.registry import AGENTS


def choose_agent_for_message(user_msg: str) -> str:
    msg = user_msg.lower()
    if any(k in msg for k in ("novo agente", "novo especialista", "criar agente", "sem especialista", "não tenho agente", "nao tenho agente")):
        return "agent_builder"
    if any(k in msg for k in ("schema", "tabela", "coluna", "index", "sql", "postgres")):
        return "dba"
    if any(k in msg for k in ("deploy", "pipeline", "release", "infra", "ci/cd", "kubernetes", "docker")):
        return "devops"
    if any(k in msg for k in ("requisito", "requisitos", "historia de usuario", "historia de usuario", "escopo")):
        return "requisitos"
    if any(k in msg for k in ("negocio", "negocio", "kpi", "roi", "proposta de valor")):
        return "negocios"
    if any(k in msg for k in ("teste", "testes", "qa", "qualidade", "automatizacao de teste", "automacao de teste")):
        return "qa"
    if any(k in msg for k in ("frontend", "ui", "ux", "react", "vue", "angular", "spa")):
        return "arquitetura_frontend"
    if any(k in msg for k in ("backend", "api", "microservico", "microservico", "servico", "servico")):
        return "arquitetura_backend"
    if any(k in msg for k in ("ia", "ia generativa", "ml", "machine learning", "modelo de linguagem", "llm")):
        return "arquitetura_ia"
    if any(k in msg for k in ("cloud", "azure", "aws", "gcp", "vpc", "rede")):
        return "arquitetura_cloud"
    if ".net" in msg or "c#" in msg or "asp.net" in msg:
        return "dotnet"
    if "python" in msg:
        return "python"
    if "node" in msg or "node.js" in msg or "typescript" in msg or "javascript" in msg:
        return "node"
    if "java " in msg or msg.startswith("java"):
        return "java"
    if "php" in msg:
        return "php"
    if "android" in msg or "kotlin" in msg:
        return "android"
    if "ios" in msg or "swift" in msg:
        return "ios"
    if "flutter" in msg or "dart" in msg:
        return "flutter"
    return "arquiteto"


def list_agents() -> Dict[str, Dict]:
    return AGENTS
