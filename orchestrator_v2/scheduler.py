import asyncio
from typing import List, Dict

from orchestrator_v2.budget import BudgetManager, BudgetExceeded
from orchestrator_v2.planner import PlannedTask
from orchestrator_v2.state import ConversationState
from orchestrator_v2.cache import (
    build_cache_key,
    get_cached_response,
    set_cached_response,
    load_cache,
)
from orchestrator_v2.observability import log_event
from providers.base import LLMProvider


async def _run_task(task: PlannedTask, provider: LLMProvider, state: ConversationState, budget: BudgetManager, cache: Dict[str, str]) -> Dict[str, str]:
    """
    Executa um task (um agente) com checagem básica de orçamento.
    Uso de to_thread para manter compatibilidade com clientes síncronos.
    """
    # Reserva orçamento (estimativa simples por chamada)
    budget.register_call()

    cache_key = build_cache_key(task.agent, task.content, None)
    cached = get_cached_response(cache_key, cache)
    if cached:
        response_text = cached
        usage = {"cached": True}
    else:
        messages = [
            {"role": "system", "content": f"Agente {task.agent}. Tarefa: {task.content}"},
            {"role": "user", "content": task.content},
        ]
        result = await provider.chat(model=None, messages=messages, tools=None, agent=task.agent)
        response_text = result.text
        usage = result.usage
        set_cached_response(cache_key, response_text, cache)

    state.append_user(task.content)
    state.append_assistant(task.agent, response_text)
    state.save()

    result = {"agent": task.agent, "task": task.name, "response": response_text, "usage": usage}
    log_event("task_completed", result)
    return result


async def run_tasks(tasks: List[PlannedTask], provider: LLMProvider, state: ConversationState, budget: BudgetManager) -> List[Dict[str, str]]:
    cache = load_cache()
    coros = []
    for t in tasks:
        if not budget.can_run():
            raise BudgetExceeded("Orcamento insuficiente para rodar todas as tarefas.")
        coros.append(_run_task(t, provider, state, budget, cache))
    return await asyncio.gather(*coros)
