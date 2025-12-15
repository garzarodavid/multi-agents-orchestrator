import os
import json
from typing import Any, Dict, List, Optional, Tuple

from agents import AgentConfig
from agents.agent_arquitetura import create_agent as create_arquitetura_agent
from agents.agent_arquitetura_backend import create_arquitetura_backend_agent
from agents.agent_arquitetura_cloud import create_arquitetura_cloud_agent
from agents.agent_arquitetura_frontend import create_arquitetura_frontend_agent
from agents.agent_arquitetura_ia import create_arquitetura_ia_agent
from agents.agent_arquitetura_solucoes import create_arquitetura_solucoes_agent
from agents.agent_builder import create_agent as create_builder_agent
from agents.agent_android import create_android_agent
from agents.agent_angular import create_angular_agent
from agents.agent_dba import create_dba_agent
from agents.agent_devops import create_devops_agent
from agents.agent_dotnet import create_dotnet_agent
from agents.agent_flutter import create_flutter_agent
from agents.agent_go import create_go_agent
from agents.agent_ios import create_ios_agent
from agents.agent_java import create_java_agent
from agents.agent_negocios import create_negocios_agent
from agents.agent_node import create_node_agent
from agents.agent_php import create_php_agent
from agents.agent_prompt import create_prompt_agent
from agents.agent_python import create_python_agent
from agents.agent_qa import create_qa_agent
from agents.agent_react import create_react_agent
from agents.agent_requisitos import create_requisitos_agent
from agents.agent_vue import create_vue_agent
from llm_client import LLMClient, create_llm_client
from mcp_config import load_mcp_servers
from multiagents.guardrails.enforcer import ContextEnforcer
import re


CONTEXT_FILE = "conversation_context.json"
# Mantem compatibilidade com configuracao existente.
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Registro central de agentes.
# A chave do dicionario e o identificador usado pelo orquestrador e pelos
# comandos do usuario (ex.: "/devops", "/python"), e o valor e a configuracao
# retornada pelas funcoes create_<nome>_agent.
#
# Para adicionar um novo agente:
#   1. Crie um arquivo em `agents/agent_<nome>.py` com uma funcao
#      `create_<nome>_agent(model: str) -> AgentConfig`.
#   2. Importe a funcao acima neste arquivo.
#   3. Registre uma nova entrada neste dicionario.
AGENTS: Dict[str, AgentConfig] = {
    # Arquitetura (alto nivel)
    "arquiteto": create_arquitetura_solucoes_agent(DEFAULT_MODEL),
    "arquitetura": create_arquitetura_agent(DEFAULT_MODEL),
    "arquitetura_solucoes": create_arquitetura_solucoes_agent(DEFAULT_MODEL),
    "arquitetura_backend": create_arquitetura_backend_agent(DEFAULT_MODEL),
    "arquitetura_frontend": create_arquitetura_frontend_agent(DEFAULT_MODEL),
    "arquitetura_ia": create_arquitetura_ia_agent(DEFAULT_MODEL),
    "arquitetura_cloud": create_arquitetura_cloud_agent(DEFAULT_MODEL),
    "agent_builder": create_builder_agent(DEFAULT_MODEL),

    # Engenharia e processos
    "devops": create_devops_agent(DEFAULT_MODEL),
    "prompt": create_prompt_agent(DEFAULT_MODEL),
    "requisitos": create_requisitos_agent(DEFAULT_MODEL),
    "negocios": create_negocios_agent(DEFAULT_MODEL),
    "qa": create_qa_agent(DEFAULT_MODEL),

    # Bancos de dados
    "dba": create_dba_agent(DEFAULT_MODEL),

    # Especialistas por tecnologia
    "dotnet": create_dotnet_agent(DEFAULT_MODEL),
    "go": create_go_agent(DEFAULT_MODEL),
    "python": create_python_agent(DEFAULT_MODEL),
    "node": create_node_agent(DEFAULT_MODEL),
    "php": create_php_agent(DEFAULT_MODEL),
    "java": create_java_agent(DEFAULT_MODEL),
    "android": create_android_agent(DEFAULT_MODEL),
    "ios": create_ios_agent(DEFAULT_MODEL),
    "react": create_react_agent(DEFAULT_MODEL),
    "vue": create_vue_agent(DEFAULT_MODEL),
    "angular": create_angular_agent(DEFAULT_MODEL),
    "flutter": create_flutter_agent(DEFAULT_MODEL),
}


class Orchestrator:
    """Simple orchestrator that routes user messages to specialized agents."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        mcp_config_path: Optional[str] = None,
        workflow: Optional[WorkflowManager] = None,
    ) -> None:
        self._llm_client = llm_client or create_llm_client(default_model=DEFAULT_MODEL)
        self._mcp_servers, self._mcp_warning = load_mcp_servers(mcp_config_path)
        self._enforcer = ContextEnforcer()

    def run_agent(
        self,
        agent_name: str,
        user_message: str,
        history: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> str:
        agent = AGENTS.get(agent_name)
        if agent is None:
            generated = self._generate_agent(agent_name, user_message, history)
            if generated is None:
                raise ValueError(f"Unknown agent and no builder available: {agent_name}")
            agent_name, agent = generated

        provider = getattr(self._llm_client, "provider", "openai")
        agent_model = agent.get("model")
        resolved_model = model or agent_model
        # Se o provider nao for OpenAI e o modelo for o default de compatibilidade,
        # deixa o client decidir (evita enviar nomes de modelo invalidos).
        if provider != "openai" and resolved_model == DEFAULT_MODEL:
            resolved_model = None

        if not resolved_model:
            resolved_model = getattr(self._llm_client, "default_model", None) or DEFAULT_MODEL

        system_message = agent.get("system_prompt") or agent.get("instructions", "")
        tool_line, missing_tools = self._build_tool_message(agent.get("tools") or [])
        if tool_line:
            system_message += "\n\n" + tool_line
        if missing_tools:
            print(f"[Orquestrador] Aviso: ferramentas MCP nao configuradas: {', '.join(missing_tools)}")

        messages = history + [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        def handler(ctx):
            try:
                resposta = self._llm_client.generate(messages=messages, model=resolved_model, agent=agent_name)
                return resposta.strip()
            except Exception as exc:
                return f"[Erro ao contatar a API]: {exc}"

        return self._enforcer.run(agent_name, user_message, handler)

    @staticmethod
    def _extract_text_from_response(resp: Any) -> str:
        """
        Mantido para compatibilidade e testes legados. Preferir extracao no LLM client.
        """
        if hasattr(resp, "output_text") and resp.output_text:
            return resp.output_text

        try:
            out = getattr(resp, "output", None) or resp.get("output")
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
                        return text
            except Exception:
                pass

        try:
            return str(resp)
        except Exception:
            return ""

    @staticmethod
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

    def _load_history(self) -> List[Dict[str, str]]:
        """Carrega o historico de conversas do arquivo JSON."""
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_history(self, history: List[Dict[str, str]]) -> None:
        """Salva o historico de conversas no arquivo JSON."""
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    def interactive_loop(self) -> None:
        print("Orquestrador multi-agent. Digite 'sair' para encerrar.\n")
        if self._mcp_warning:
            print(f"[Orquestrador] Aviso MCP: {self._mcp_warning}")
        elif self._mcp_servers:
            print(f"[Orquestrador] MCP carregado para: {', '.join(self._mcp_servers.keys())}")

        history = self._load_history()
        if history:
            print("[Orquestrador] Historico da conversa anterior carregado.")

        while True:
            try:
                user_msg = input("Voce: ")
            except (EOFError, KeyboardInterrupt):
                print("\nSaindo.")
                break

            user_msg_stripped = user_msg.strip()
            if not user_msg_stripped:
                continue

            if user_msg_stripped.lower() in ("sair", "exit", "quit"):
                print("Encerrando.")
                break

            if user_msg_stripped.lower() == "/limpar":
                history = []
                self._save_history(history)
                print("[Orquestrador] Historico da conversa foi limpo.")
                continue

            agent: Optional[str] = None
            message = user_msg_stripped

            if user_msg_stripped.startswith("/"):
                parts = user_msg_stripped.split(maxsplit=1)
                command = parts[0][1:].lower()
                if command in AGENTS:
                    agent = command
                    message = parts[1] if len(parts) > 1 else ""

            if agent is None:
                agent = self.choose_agent_for_message(message)

            print(f"[Orquestrador] Enviando para o agente: {agent}")
            resposta = self.run_agent(agent, message, history)
            print(f"{agent.upper()}: {resposta}\n")

            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": f"({agent}) {resposta}"})
            self._save_history(history)

    def non_interactive_run(self, message: str) -> int:
        agent = self.choose_agent_for_message(message)
        print(f"[Orquestrador] Enviando para o agente: {agent}")
        # O modo nao interativo nao usa historico por padrao
        resposta = self.run_agent(agent, message, history=[])
        print(resposta)
        return 0

    def _build_tool_message(self, agent_tools: List[str]) -> Tuple[str, List[str]]:
        """
        Monta a mensagem de ferramentas MCP configuradas ou pendentes.

        :param agent_tools: Lista de identificadores (ex.: ["mcp:postgres"]).
        :return: (linha_para_prompt, lista_de_ferramentas_pendentes)
        """
        if not agent_tools:
            return "", []

        configured: List[str] = []
        missing: List[str] = []
        servers = self._mcp_servers or {}

        for tool in agent_tools:
            if not tool.startswith("mcp:"):
                configured.append(tool)
                continue
            name = tool.split(":", 1)[1]
            if name in servers:
                configured.append(tool)
            else:
                missing.append(tool)

        if configured:
            return "Ferramentas MCP configuradas: " + ", ".join(configured), missing

        return "Ferramentas MCP declaradas (configure para usar): " + ", ".join(agent_tools), missing

    def _generate_agent(
        self,
        missing_agent: str,
        user_message: str,
        history: List[Dict[str, str]],
    ) -> Optional[Tuple[str, AgentConfig]]:
        builder = AGENTS.get("agent_builder")
        if builder is None:
            return None

        system_message = builder.get("system_prompt") or builder.get("instructions", "")
        prompt = (
            f"Crie um agente especialista para o tema: '{missing_agent}'. "
            f"Contexto da solicitacao: {user_message}. "
            "Retorne um JSON com campos: name, identifier, system_prompt, tools (lista)."
        )
        messages = history + [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]

        try:
            resp = self._llm_client.generate(messages=messages, model=builder.get("model"), agent="agent_builder")
        except Exception:
            return None

        data = self._parse_builder_response(resp)
        if not data:
            return None

        identifier = data.get("identifier") or data.get("slug") or self._slugify(data.get("name") or missing_agent)
        system_prompt = data.get("system_prompt") or ""
        if not identifier or not system_prompt:
            return None

        config: AgentConfig = {
            "name": data.get("name") or f"Agent.{identifier}",
            "model": data.get("model") or DEFAULT_MODEL,
            "system_prompt": system_prompt,
            "tools": data.get("tools") or [],
        }
        AGENTS[identifier] = config
        self._persist_agent_contract(identifier, config, raw_response=resp)
        return identifier, config

    def _parse_builder_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        try:
            return json.loads(response_text)
        except Exception:
            pass

        # Tenta extrair o primeiro bloco JSON em meio ao texto
        try:
            start = response_text.index("{")
            end = response_text.rindex("}")
            snippet = response_text[start : end + 1]
            return json.loads(snippet)
        except Exception:
            return None

    def _slugify(self, text: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
        return slug or "agent_generico"

    def _persist_agent_contract(self, identifier: str, config: AgentConfig, raw_response: str) -> None:
        try:
            os.makedirs("contracts/agents", exist_ok=True)
            path = os.path.join("contracts", "agents", f"generated_{identifier}.md")
            lines = [
                f"# {config.get('name', identifier)}",
                "",
                "## System prompt",
                "```",
                config.get("system_prompt", ""),
                "```",
                "",
                "## Tools",
                f"- {', '.join(config.get('tools') or []) or '(nenhuma)'}",
                "",
                "## Resposta bruta do Builder",
                "```",
                raw_response.strip(),
                "```",
            ]
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception:
            # Persistencia de contrato não deve quebrar fluxo principal
            pass
