"""
Ponto de entrada assíncrono (V2) para o orquestrador multi-agente.

Objetivos:
- Fan-out de agentes em paralelo (asyncio).
- Respeitar estratégias de custo via llm_client (provider/strategy/model map).
- Manter compatibilidade com a V1 (main.py) sem quebrar.

Este arquivo inicializa apenas a estrutura mínima; o planner/scheduler/budget
serão enriquecidos nas próximas tasks do plano.
"""

import asyncio

from orchestrator_v2.planner import plan_tasks
from orchestrator_v2.scheduler import run_tasks
from orchestrator_v2.state import ConversationState
from orchestrator_v2.budget import BudgetManager, BudgetExceeded
from providers.factory import create_provider_adapter
from mcp_config import load_mcp_servers
from mcp.client import MCPClient


async def main_async(user_message: str, total_budget_usd: float = 1.0, provider_name: str = None, strategy: str = None) -> None:
    state = ConversationState.load()
    provider = create_provider_adapter(default_model="gpt-4.1-mini", provider=provider_name, strategy=strategy)
    budget = BudgetManager(total_budget_usd=total_budget_usd)
    mcp_servers, mcp_warning = load_mcp_servers(None)
    mcp_client = MCPClient(mcp_servers)

    tasks = plan_tasks(user_message)
    try:
        results = await run_tasks(tasks, provider, state, budget)
    except BudgetExceeded as exc:
        print(f"[Orcamento] {exc}")
        return
    except Exception as exc:
        print(f"[Erro] {exc}")
        return

    for r in results:
        print(f"{r['agent'].upper()}: {r['response']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Orquestrador V2 (assíncrono)")
    parser.add_argument("message", nargs="*", help="Mensagem do usuário")
    parser.add_argument("--budget", type=float, default=1.0, help="Orçamento em USD para a execução")
    parser.add_argument("--provider", type=str, default=None, help="LLM provider (openai|gemini|claude)")
    parser.add_argument("--strategy", type=str, default=None, help="Estratégia (quality|balance|cost)")
    args = parser.parse_args()

    msg = " ".join(args.message) if args.message else "Olá, o que posso fazer?"
    asyncio.run(main_async(msg, total_budget_usd=args.budget, provider_name=args.provider, strategy=args.strategy))
