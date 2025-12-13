## Guia para Assistentes de IA

Contexto rápido do codebase para quem vai sugerir mudanças.

### Visão geral
- **Entrada:** `main.py` roda em modo interativo ou com uma mensagem única e delega para `Orchestrator`.
- **Núcleo:** `orchestrator.py` registra agentes em `AGENTS`, chama `client.responses.create` com `system_prompt` e persiste histórico em `conversation_context.json`.
- **Comandos no chat:** `/agente` força um alvo (ex.: `/dba`, `/devops`, `/python`); `/limpar` remove o histórico salvo. O modo não interativo não carrega histórico por padrão.
- **Roteamento:** `choose_agent_for_message` usa palavras-chave para decidir o agente quando não há comando explícito.

### Agentes
- Cada agente vive em `agents/agent_<nome>.py` e expõe `create_<nome>_agent(model: str) -> dict`, retornando `{name, model, system_prompt, tools}`.
- O campo `tools` referencia MCP (ex.: `mcp:postgres`, `mcp:azure`, `mcp:github`); configure servidores MCP se quiser usar ferramentas reais.
- Agentes registrados:  
  Arquitetura (`arquiteto`, `arquitetura`, `arquitetura_solucoes`, `arquitetura_backend`, `arquitetura_frontend`, `arquitetura_ia`, `arquitetura_cloud`);  
  Engenharia/Processos (`devops`, `prompt`, `requisitos`, `negocios`, `qa`);  
  Dados (`dba`);  
  Tecnologias (`dotnet`, `go`, `python`, `node`, `php`, `java`, `android`, `ios`, `react`, `vue`, `angular`, `flutter`).
- Para criar um novo agente: adicionar `agents/agent_novo.py`, importar e registrar em `AGENTS` em `orchestrator.py`, e (opcional) ajustar `choose_agent_for_message` para roteamento automático.

### Configuração
- Requer `OPENAI_API_KEY`; `OPENAI_MODEL` é opcional (padrão `gpt-4.1-mini`).
- Dependências em `requirements.txt` (`openai>=1.0.0`). Considere usar um ambiente virtual.
- MCP: coloque `MCP_SERVERS_FILE=<caminho do toml>`; exemplo em `.docs/mcp-servers.example.toml` (ajuste comandos/args/env para postgres, azure e github). O orquestrador imprime aviso se não encontrar as ferramentas MCP declaradas pelo agente. Em Python < 3.11, o TOML requer `tomli` (já listado em `requirements.txt`).
- Para uso local rápido: `mcp-servers.local.toml` tem defaults (localhost para Postgres, `az account show`, `gh status`). Exporte `MCP_SERVERS_FILE=./mcp-servers.local.toml` e autentique-se em `psql`/`az login`/`gh auth login` conforme necessário.
- LLM agnóstico: `LLM_PROVIDER=openai|gemini|claude` (padrão openai), `LLM_STRATEGY=quality|balance|cost` controla custo/benefício. Overrides: `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`, `LLM_MODEL_CLAUDE` (compat: `OPENAI_MODEL`). Credenciais: `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`. SDKs de Gemini/Claude são opcionais (scripts em `scripts/install-llm-sdk-*.{ps1,sh}`).
- Mapa de modelos por agente (opcional): `LLM_MODEL_MAP_FILE` aponta para um TOML como `llm-model-map.example.toml` para definir modelos por provedor/estratégia/agente.

### Notas de implementação
- `_extract_text_from_response` é defensiva porque formatos da SDK podem variar; adapte se o formato de resposta for diferente.
- O histórico fica em `conversation_context.json`; `/limpar` o apaga. Evite crescer indefinidamente se usar conversas longas.
