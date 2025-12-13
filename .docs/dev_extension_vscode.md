# Guia Dev / Extensão VS Code (MCP + Token Broker)

## Objetivo
Orientar como integrar o orquestrador V2 a uma extensão VS Code:
- Servidor MCP (stdio) expondo `multi_agents.chat`
- Token Broker para fornecer tokens LLM (OpenAI/Anthropic/Gemini)

## Componentes
- Servidor MCP: `server_mcp.py` (stdio)
- Cliente MCP (mínimo): `mcp/client.py` (subprocess para servers externos)
- Token Broker client: `transport/broker_client.py` (HTTP local / fallback env)
- Orquestrador V2: `orchestrator_v2/main_async.py`

## Configuração (lado VS Code)
1) Registrar servidor MCP stdio no client MCP da extensão:
   - command: `python`
   - args: `["server_mcp.py"]`
2) Broker de tokens exposto via HTTP local (ex.: `http://127.0.0.1:17870/token?provider=openai`):
   - Retorno esperado: `{ "access_token": "...", "expires_in": 3600, "provider": "openai" }`
3) Definir envs para fallback:
   - `LLM_TOKEN_OPENAI`, `LLM_TOKEN_ANTHROPIC`, `LLM_TOKEN_GEMINI` (opcional, usado se broker não estiver disponível).

## Execução manual (CLI)
- V2 com flags: `python -m orchestrator_v2.main_async "mensagem" --provider openai --strategy balance --budget 1.5`
- Wrapper (PowerShell): `scripts/multi-agents.ps1 "mensagem"`
- Wrapper (sh): `scripts/multi-agents.sh "mensagem"`

## LLM Provider/Strategy
- Env: `LLM_PROVIDER` (openai|gemini|claude), `LLM_STRATEGY` (quality|balance|cost)
- Mapas de modelos: `LLM_MODEL_MAP_FILE=./llm-model-map.example.toml`

## MCP Servers externos (Postgres, Azure, GitHub)
- Config: `MCP_SERVERS_FILE=./mcp-servers.local.toml`
- Cliente mínimo chama o comando/args do TOML; para uso avançado, trocar por SDK MCP real.

## Pendências/Next
- Implementar adapters Gemini/Claude no `providers/`.
- Integrar Token Broker real (extensão VS Code) com refresh/SecretStorage.
- Melhorar MCP server para retornar modelo/custo e suporte a tools MCP internas.
