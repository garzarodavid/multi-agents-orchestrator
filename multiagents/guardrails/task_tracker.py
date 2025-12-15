from dataclasses import dataclass, field
from typing import List


@dataclass
class TaskItem:
    ordem: int
    titulo: str
    descricao: str
    status: str = "Pendente"  # Pendente | Em andamento | Concluido | Bloqueado


@dataclass
class ExecutionPlan:
    plan_id: str
    items: List[TaskItem] = field(default_factory=list)

    def mark(self, ordem: int, status: str) -> None:
        for item in self.items:
            if item.ordem == ordem:
                item.status = status
                return
