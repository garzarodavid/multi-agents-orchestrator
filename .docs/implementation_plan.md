# Plano de Implementacao (Multi-Agentes Agnostico, VS Code + MCP)

| Prioridade | Task | Descricao detalhada | Status |
|------------|------|---------------------|--------|
| Alta | Fundar esqueleto V2 (arquitetura em camadas) | Criar estrutura `orchestrator_v2/`, preparar pontos para `providers/`, `transport/`, `mcp/`, `contracts/` mantendo CLI atual como compat. Incluir `main_async.py` para fan-out e sintese; manter `main.py` legada. | Pronto |
| Alta | Planner/Scheduler assincrono | Implementar `planner.py` (quebra de job em subtarefas com metadados de prioridade), `budget.py` (bolsas por agente, corte por orcamento), e orquestracao `asyncio` para fan-out + retry leve. | Pendente |
| Alta | Adapters LLM unificados | Refatorar `llm_client` em adapters `providers/openai_adapter.py`, `providers/anthropic_adapter.py`, `providers/gemini_adapter.py` com interface `chat()` async, retorno de `ChatResult` (texto, usage/custo, raw). Respeitar `LLM_PROVIDER/LLM_STRATEGY` e `LLM_MODEL_MAP_FILE`. | Pendente |
| Alta | Token Broker (integracao VS Code) | Definir client IPC/HTTP (`transport/broker_client.py`) que pede token ao Broker da extensao. Especificar contrato JSON (`transport/schemas.py`). Incluir fallback para env vars se broker indisponivel. | Pronto |
| Alta | MCP Client real | Implementar `mcp/client.py` para descoberta/invocacao de tools via MCP, com suporte a OAuth/creds delegadas. Mapear tools padrao (git/fs/github/azure/postgres). | Pendente |
| Alta | Tool multi_agents.chat via MCP Server | Criar `server_mcp.py` stdio expondo tool `multi_agents.chat(message, agent?)`, usando orquestrador V2; retornar tambem agente escolhido, modelo, custo e tools MCP usadas. | Pronto |
| Media | Prompts/Agentes: portar e versionar | Portar agentes atuais (`agents/*`) para `contracts/agents/` (markdown ou yaml) e gerar prompts consumidos pelo orquestrador V2. | Pronto |
| Media | Testes de integracao | Adicionar suite async cobrindo planner+fan-out, adapters com fakes, budget gating e MCP server. | Pronto |
| Media | CLI/UX | Adicionar wrapper `multi-agents` (sh/ps1) e flags em `main_async.py` (`--provider`, `--strategy`, `--agent`, `--plan-only`, `--budget`). | Pronto |
| Media | Docs Dev/Extensao VS Code | Documentar como registrar servidor MCP, como o Token Broker expoe tokens, e fluxos de auth (OpenAI/Anthropic/Gemini + MCP tools). Atualizar README/decision_log. | Pendente |
| Baixa | Cache/Context Packing | Implementar cache por hash de arquivo/commit, reuso de contextos e packing sob demanda via MCP (lazy fetch de arquivos). | Pronto |
| Baixa | Observabilidade | Adicionar logs estruturados, metricas basicas (tokens/custo por agente) e tracers opcionalmente via OpenTelemetry. | Pronto |
