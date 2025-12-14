# Contexto do Projeto (Visao Geral e Evolucao)

Este documento resume o estado atual do orquestrador, decisoes ja tomadas e pontos de extensao, para facilitar evolucao, correcoes e analises.

## Estado atual
- V1 (sincrona): `main.py` usa `orchestrator.py` com roteamento por palavra-chave, historico em `conversation_context.json`, e agentes registrados estaticamente.
- V2 (assincrona): `orchestrator_v2/` com planner/scheduler/budget basicos, cache em `.cache/`, observabilidade opcional (`OBSERVABILITY_ENABLED=true`), wrappers CLI, e server MCP minimo (`server_mcp.py`).
- LLM agnostico: `LLM_PROVIDER` (openai|gemini|claude), `LLM_STRATEGY` (quality|balance|cost), mapa por agente (`LLM_MODEL_MAP_FILE`), Token Broker client (`transport/broker_client.py`), e adapters no `providers/` (OpenAI implementado; Gemini/Claude pendentes).
- MCP: config via `MCP_SERVERS_FILE`, cliente minimo (`mcp/client.py`, subprocess) e server MCP stub (`server_mcp.py`).
- Agent Builder: `agent_builder` gera agentes dinamicos quando nao ha especialista, registra em runtime e persiste contrato em `contracts/agents/generated_<id>.md`.
- Prompts: todos os agentes portados para `contracts/agents/` (markdown).

## Estrutura
- `orchestrator.py`: V1; fallback para agent_builder se agente desconhecido.
- `orchestrator_v2/`: planner, scheduler, budget, cache, observability, registry, router, main_async.
- `providers/`: base/factory, adapter OpenAI (async). Gemini/Claude ainda nao implementados.
- `mcp/`: client minimo; `server_mcp.py` (tool `multi_agents.chat`).
- `transport/`: token broker client e schemas.
- `contracts/agents/`: prompts versionados (inclui generated_* do Builder).

## Fluxos principais
- CLI V1: `python main.py "mensagem"` / comandos `/agente` e `/limpar`.
- CLI V2: `python -m orchestrator_v2.main_async "mensagem" --provider openai --strategy balance --budget 1.0` ou scripts `multi-agents.*`.
- MCP Server: `server_mcp.py` (stdio) expondo `multi_agents.chat` (stub).
- Token Broker: tenta HTTP `/token?provider=`; fallback `LLM_TOKEN_<PROVIDER>`.

## Limitacoes / Debitos atuais
- Adapters Gemini/Claude ausentes (factory gera erro ao selecionar).
- MCP client/server sao minimos; sem SDK MCP real, sem OAuth, server nao retorna output real do orquestrador.
- Cache simples por hash (agente+mensagem) sem escopo por repo/commit.
- Observabilidade apenas logs JSON opt-in; sem metricas reais de tokens/custo.
- Builder nao valida schema nem carrega contratos gerados no bootstrap; agentes dinamicos so vivem em memoria na execucao atual.
- Token Broker real (extensao VS Code/SecretStorage) nao implementado; apenas o cliente.

## Proximos passos priorizados (projeto 100% funcional)
1) Adapters Gemini/Claude (providers) com tests de fakes/mocks; habilitar LLM_PROVIDER sem erro.
2) MCP server real: retornar resposta do orquestrador, incluir agente/modelo/usage; erros estruturados.
3) MCP client robusto: trocar subprocess por SDK MCP com discovery e auth; testes com fakes.
4) Token Broker real: integrar com broker (VS Code ou servico local), refresh/SecretStorage; melhorar mensagens de erro/retries.
5) Builder hardening: validar JSON, slug seguro, persistencia/recarga de contratos generated_*.
6) Cache inteligente: escopo por repo/commit/arquivo; TTL; opcao NO_CACHE.
7) Observabilidade: logs estruturados com custo/usage; hooks para metricas/OTEL.
8) CLI/UX extra: `--plan-only`, `--agent`, escolha de mapa via flag, mensagens de fallback melhores.
9) Docs/playbooks: setup por provedor, MCP real, broker real, troubleshooting.
