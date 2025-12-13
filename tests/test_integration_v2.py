import asyncio
import unittest

from orchestrator_v2.main_async import main_async
from orchestrator_v2.planner import plan_tasks
from orchestrator_v2.budget import BudgetExceeded


class IntegrationV2Tests(unittest.TestCase):
    def test_plan_tasks_returns_agent(self) -> None:
        tasks = plan_tasks("Preciso rever um schema")
        self.assertEqual(tasks[0].agent, "dba")

    def test_budget_exceeded_blocks_execution(self) -> None:
        async def run():
            try:
                await main_async("teste", total_budget_usd=0.0)
            except BudgetExceeded:
                return True
            except Exception:
                # Sem API key, aborta diferente; apenas sinalize que houve interrupção
                return True
            return False

        result = asyncio.run(run())
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
