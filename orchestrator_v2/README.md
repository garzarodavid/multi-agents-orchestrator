# Orquestrador V2 (assíncrono)

Estado: esqueleto inicial. Mantém compatibilidade com a V1 (`main.py`), mas oferece `orchestrator_v2/main_async.py` para evolução:

- Fan-out futuro com asyncio.
- Registry de agentes em `orchestrator_v2/registry.py`.
- Router em `orchestrator_v2/router.py`.
- Estado em `orchestrator_v2/state.py`.
- Planner/scheduler/budget em `orchestrator_v2/planner.py`, `orchestrator_v2/scheduler.py`, `orchestrator_v2/budget.py`.
- Cliente LLM agnóstico via `llm_client.create_llm_client()`.

Como rodar (modo simples, 1 turno):
```bash
python -m orchestrator_v2.main_async "sua mensagem"
```

Próximos passos (do plano):
- Adicionar planner/scheduler/budget mais ricos (subtarefas, retries, custo real).
- Adapters LLM async e retorno de usage/custo.
- Tool MCP real e server MCP.
- Integração com Token Broker.
