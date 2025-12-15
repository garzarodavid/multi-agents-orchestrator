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
from workflow import WorkflowManager, WorkflowResult


async def _run_task(task: PlannedTask, provider: LLMProvider, state: ConversationState, budget: BudgetManager, cache: Dict[str, str], workflow: WorkflowManager) -> Dict[str, str]:
    """
    Executa um task (um agente) com checagem básica de orçamento.
    Uso de to_thread para manter compatibilidade com clientes síncronos.
    """
    # Reserva orçamento (estimativa simples por chamada)
    budget.register_call()

    wf = workflow.preprocess(task.content, task.agent)
    if wf.blocked:
        return {"agent": task.agent, "task": task.name, "response": wf.message, "usage": {"blocked": True}}
    if wf.plan_id:
        workflow.mark_in_progress(wf.plan_id)

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
        try:
            result = await provider.chat(model=None, messages=messages, tools=None, agent=task.agent)
            response_text = result.text
            usage = result.usage
            set_cached_response(cache_key, response_text, cache)
        except Exception as exc:
            response_text = f"[Erro ao contatar LLM]: {exc}"
            usage = {"error": True}

    if wf.plan_id:
        workflow.mark_done(wf.plan_id, task.agent, response_text)

    state.append_user(task.content)
    state.append_assistant(task.agent, response_text)
    state.save()

    result = {"agent": task.agent, "task": task.name, "response": response_text, "usage": usage}
    log_event("task_completed", result)
    return result


async def run_tasks(tasks: List[PrannedTask], provider: LLMProvider, state: ConversationState, budget: BudgetManager) -> List[Dict[str, str]]:
    cache = load_cache()
    workflow = WorkflowManager()
    coros = []
    for t in tasks:
        if not budget.can_run():
            raise BudgetExceeded("Orcamento insuficiente para rodar todas as tarefas.")
        coros.append(_run_task(t, provider, state, budget, cache, workflow))
    return await asyncio.gather(*coros)
