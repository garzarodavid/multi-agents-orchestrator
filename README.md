# Multi-Agents Orchestrator

Orquestrador em Python que roteia mensagens para agentes especializados, suporta múltiplos provedores de LLM (OpenAI/Gemini/Claude) e integrações MCP básicas.

## Pré-requisitos
- Python 3.10+
- `pip install -r requirements.txt` (SDKs de Gemini/Claude são opcionais; use os scripts em `scripts/install-llm-sdk-*.sh|ps1`).
- Defina credenciais conforme o provedor: `OPENAI_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY`.

## Uso rápido
- V1 (sincrona): `python main.py "sua pergunta"`
- V2 (assíncrona, experimental):  
  `python -m orchestrator_v2.main_async "sua mensagem" --provider openai --strategy balance --budget 1.0`
- Wrappers: `scripts/multi-agents.sh` ou `scripts/multi-agents.ps1`
- Histórico: salvo em `conversation_context.json`

## Agentes disponíveis (identificadores)
- Arquitetura: `arquiteto`, `arquitetura_solucoes`, `arquitetura_backend`, `arquitetura_frontend`, `arquitetura_ia`, `arquitetura_cloud`
- Engenharia/Processos: `devops`, `prompt`, `requisitos`, `negocios`, `qa`
- Dados: `dba`
- Tecnologias: `dotnet`, `go`, `python`, `node`, `php`, `java`, `android`, `ios`, `react`, `vue`, `angular`, `flutter`
- Criador de agentes: `agent_builder` (quando não houver especialista, ele propõe e registra um novo agente; contrato gerado em `contracts/agents/generated_<id>.md`)

## LLM (agnóstico)
- Provedor: `LLM_PROVIDER=openai|gemini|claude` (padrão: openai)
- Estratégia custo/benefício: `LLM_STRATEGY=quality|balance|cost` (padrão: balance)
- Overrides por provedor: `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`, `LLM_MODEL_CLAUDE` (compat: `OPENAI_MODEL`)
- Mapa por agente/estratégia: `LLM_MODEL_MAP_FILE=./llm-model-map.example.toml`

## Token Broker
- Cliente em `transport/broker_client.py`: tenta `/token?provider=` via HTTP local; fallback para `LLM_TOKEN_<PROVIDER>`.

## MCP (PostgreSQL, Azure, GitHub)
- Config: `MCP_SERVERS_FILE=./mcp-servers.local.toml` (exemplo e defaults locais).
- Cliente mínimo: `mcp/client.py` (subprocess/stdout); server MCP stdio: `server_mcp.py` expondo `multi_agents.chat`.
- Agentes que esperam MCP: `dba` (postgres), `devops` (azure, github), `arquitetura_cloud` (azure).

## V2 (assíncrona)
- Planner/scheduler/budget básicos; cache em `.cache/`; observabilidade opcional (`OBSERVABILITY_ENABLED=true`).
- Usa o mesmo `llm_client` agnóstico e roteamento por palavra-chave.

## Estender
1) Adicionar agente: `agents/agent_novo.py` com `create_novo_agent`; registrar em `orchestrator.py`.
2) Ajustar roteamento: `choose_agent_for_message` em `orchestrator.py` e `orchestrator_v2/router.py`.
3) Para prompts versionados, use `contracts/agents/` (markdown).*** End Patch
