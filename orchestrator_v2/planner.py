from dataclasses import dataclass
from typing import List, Optional

from orchestrator_v2.router import choose_agent_for_message


@dataclass
class PlannedTask:
    name: str
    agent: str
    content: str
    priority: int = 1


def plan_tasks(user_message: str, preferred_agent: Optional[str] = None) -> List[PlannedTask]:
    """
    Plano simples: um task por mensagem, roteado pelo agente mais adequado.
    Futuras evoluções: quebrar em subtarefas, reordenar por dependências,
    classificar criticidade/custo e fan-out real.
    """
    agent = preferred_agent or choose_agent_for_message(user_message)
    task_name = f"{agent}-task"
    return [PlannedTask(name=task_name, agent=agent, content=user_message, priority=1)]
