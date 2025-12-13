import unittest

from orchestrator_v2.planner import plan_tasks, PlannedTask
from orchestrator_v2.budget import BudgetManager, BudgetExceeded


class PlannerTests(unittest.TestCase):
    def test_plan_returns_single_task_with_agent(self) -> None:
        tasks = plan_tasks("Preciso de um schema")
        self.assertEqual(len(tasks), 1)
        self.assertIsInstance(tasks[0], PlannedTask)
        self.assertEqual(tasks[0].agent, "dba")


class BudgetTests(unittest.TestCase):
    def test_allows_within_budget(self) -> None:
        budget = BudgetManager(total_budget_usd=0.02, call_estimate_usd=0.01)
        budget.register_call()
        budget.register_call()
        self.assertEqual(budget.spent_usd, 0.02)

    def test_raises_when_exceeding(self) -> None:
        budget = BudgetManager(total_budget_usd=0.01, call_estimate_usd=0.01)
        budget.register_call()
        with self.assertRaises(BudgetExceeded):
            budget.register_call()


if __name__ == "__main__":
    unittest.main()
