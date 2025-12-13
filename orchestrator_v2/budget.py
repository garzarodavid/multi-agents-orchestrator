from dataclasses import dataclass


class BudgetExceeded(Exception):
    """Lancado quando o orcamento estoura."""


@dataclass
class BudgetManager:
    total_budget_usd: float = 1.0
    call_estimate_usd: float = 0.01

    def __post_init__(self) -> None:
        self.spent_usd = 0.0

    def can_run(self, estimate_usd: float = None) -> bool:
        est = self._estimate(estimate_usd)
        return (self.spent_usd + est) <= self.total_budget_usd

    def register_call(self, cost_usd: float = None) -> None:
        est = self._estimate(cost_usd)
        if not self.can_run(est):
            raise BudgetExceeded(f"Orcamento excedido: gasto previsto {self.spent_usd + est} > limite {self.total_budget_usd}")
        self.spent_usd += est

    def _estimate(self, override: float = None) -> float:
        if override is not None:
            return max(override, 0.0)
        return self.call_estimate_usd
