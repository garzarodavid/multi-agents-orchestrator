from typing import Dict

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

DEFAULT_MODEL = "gpt-4.1-mini"

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
