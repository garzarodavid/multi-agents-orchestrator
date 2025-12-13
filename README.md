# Multi-Agents Orchestrator (exemplo mínimo)

Orquestrador em Python que roteia mensagens para agentes conceituais (prompts) especializados, usando a API da OpenAI (`client.responses.create`).

## Pré-requisitos
- Defina `OPENAI_API_KEY` no ambiente.
- (Opcional) `OPENAI_MODEL` para trocar o modelo; padrão: `gpt-4.1-mini`.
- Instale dependências: `pip install -r requirements.txt` (recomendado usar um venv).

## Uso
- **Interativo:** `python main.py`
  - `/agente` força o alvo (ex.: `/dba`, `/devops`, `/python`).
  - `/limpar` zera o histórico salvo.
- **Mensagem única:** `python main.py "sua pergunta aqui"`

O histórico da conversa é persistido em `conversation_context.json` no diretório atual.

## Agentes disponíveis (identificadores)
- **Arquitetura:** `arquiteto`, `arquitetura`, `arquitetura_solucoes`, `arquitetura_backend`, `arquitetura_frontend`, `arquitetura_ia`, `arquitetura_cloud`
- **Engenharia/Processos:** `devops`, `prompt`, `requisitos`, `negocios`, `qa`
- **Dados:** `dba`
- **Tecnologias:** `dotnet`, `go`, `python`, `node`, `php`, `java`, `android`, `ios`, `react`, `vue`, `angular`, `flutter`
- **Criador de agentes:** `agent_builder` (quando não houver especialista, ele sugere um novo agente com prompt/tools)

## Como funciona
- `orchestrator.py` seleciona o agente por palavras-chave (`choose_agent_for_message`) ou pelo comando `/agente`.
- Cada agente é definido em `agents/agent_<nome>.py` via `create_<nome>_agent`, retornando `{name, model, system_prompt, tools}`.
- O campo `tools` referencia ferramentas MCP (ex.: `mcp:postgres`, `mcp:azure`, `mcp:github`). Configure os servidores MCP para usar de fato essas ferramentas.
- Respostas são extraídas de forma defensiva em `_extract_text_from_response`.

## Provedor/modelo LLM (agnóstico)
- Escolha o provedor via `LLM_PROVIDER=openai|gemini|claude` (padrão: `openai`).
- Estratégia de custo/benefício via `LLM_STRATEGY=quality|balance|cost` (padrão: `balance`). Mapas padrão:
  - OpenAI: quality=`gpt-4.1`, balance=`gpt-4.1-mini`, cost=`gpt-3.5-turbo`.
  - Gemini: quality=`gemini-1.5-pro`, balance=`gemini-1.5-flash`, cost=`gemini-1.0-pro-001`.
  - Claude: quality=`claude-3-5-sonnet-20240620`, balance=`claude-3-sonnet-20240229`, cost=`claude-3-haiku-20240307`.
- Overrides de modelo por provedor: `LLM_MODEL_OPENAI`, `LLM_MODEL_GEMINI`, `LLM_MODEL_CLAUDE` (compat: `OPENAI_MODEL`).
- Credenciais: `OPENAI_API_KEY`, `GOOGLE_API_KEY` (Gemini), `ANTHROPIC_API_KEY` (Claude). SDKs de Gemini/Claude são opcionais e não estão em `requirements.txt`; instale-os se for usar.
- Mapa de modelos por agente (opcional): `LLM_MODEL_MAP_FILE=./llm-model-map.example.toml` permite escolher modelo por provedor/estratégia/agente (veja o arquivo de exemplo). A resolução segue: modelo requisitado -> env `LLM_MODEL_*` -> mapa -> defaults por provedor/estratégia -> fallback do cliente.
- Arquitetos/agents mantêm um modelo default para compatibilidade OpenAI; se usar outro provedor, o cliente escolhe o modelo adequado segundo estratégia/mapa.
- Token Broker (quando usar com extensão VS Code ou outro IPC): cliente em `transport/broker_client.py` tenta pegar token via HTTP local (`/token?provider=`) e cai para env `LLM_TOKEN_<PROVIDER>` se não houver broker.

## Estender
1. Crie `agents/agent_novo.py` com `create_novo_agent(model: str) -> dict` incluindo `system_prompt`.
2. Importe e registre o agente em `AGENTS` em `orchestrator.py`.
3. Opcional: ajuste `choose_agent_for_message` para roteamento automático.

## V2 (assíncrona, experimental)
- Entrypoint: `python -m orchestrator_v2.main_async "sua mensagem"`.
- Usa planner/scheduler/budget básicos em `orchestrator_v2/` e o mesmo `llm_client` agnóstico.
- Mantém a V1 (`main.py`) intacta enquanto evolui.
- Cache opcional: habilitado por padrão via `orchestrator_v2/cache.py` (salva respostas por hash em `.cache/`). Logs estruturados podem ser emitidos quando `OBSERVABILITY_ENABLED=true`.

## MCP (PostgreSQL, Azure, GitHub)
- Exemplo de configuração de servidores MCP em `.docs/mcp-servers.example.toml` (ajuste comandos/args/env).
- Garanta que os binários/clients MCP estejam no `PATH` e com credenciais válidas.
- Informe o caminho do arquivo via `MCP_SERVERS_FILE=<caminho do toml>` para que o orquestrador carregue e sinalize ferramentas configuradas ou pendentes (ex.: `MCP_SERVERS_FILE=./mcp-servers.local.toml`).
- Em Python < 3.11, instale `tomli` (já listado em `requirements.txt`) para leitura do TOML.
- Cliente MCP (mínimo) em `mcp/client.py` invoca servidores configurados via subprocess/stdout. Para uso avançado, substituir por SDK MCP completo.
- Agentes que esperam MCP:
  - `dba` → `mcp:postgres`
  - `devops` → `mcp:azure`, `mcp:github`
  - `arquitetura_cloud` → `mcp:azure`
- Para testar rapidamente:
  - Preencha `mcp-servers.local.toml` (já vem com defaults locais sem segredos).
  - Exportar env (PowerShell): `$env:MCP_SERVERS_FILE = ".\\mcp-servers.local.toml"`
  - Autentique-se: `psql` com suas credenciais, `az login`, `gh auth login`.
