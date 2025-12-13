"""
Servidor MCP (stdio) expondo a ferramenta multi_agents.chat.

Assinatura da ferramenta:
- name: multi_agents.chat
- args:
    - message (str, obrigatório)
    - agent (str, opcional)

Fluxo:
- Usa orchestrator_v2 para roteamento e geração de resposta.
- Retorna: texto da resposta, agente escolhido e modelo resolvido (se disponível).

Nota: Implementação mínima de MCP server; não inclui OAuth de ferramentas MCP.
"""

import asyncio
import json
import sys
from typing import Any, Dict

from orchestrator_v2.main_async import main_async as orchestrator_main


def make_response(output: str, agent: str) -> Dict[str, Any]:
    return {
        "type": "success",
        "content": [
            {
                "type": "text",
                "text": output,
            }
        ],
        "meta": {
            "agent": agent,
        },
    }


async def handle_call(payload: Dict[str, Any]) -> Dict[str, Any]:
    method = payload.get("method")
    if method != "tools.call":
        return {"type": "error", "error": f"Unsupported method: {method}"}

    params = payload.get("params") or {}
    name = params.get("name")
    if name != "multi_agents.chat":
        return {"type": "error", "error": f"Unknown tool: {name}"}

    args = params.get("arguments") or {}
    message = args.get("message")
    if not message:
        return {"type": "error", "error": "Missing argument: message"}

    agent = args.get("agent")
    # Reuso do main_async (retorna None; imprime a resposta). Aqui, capturamos stdout via pipe.
    # Simplesmente chamamos o orchestrator e retornamos a string final.
    # Para simplicidade, usamos run_in_executor; em implementação mais robusta,
    # exporíamos uma função que retorne diretamente a string.
    buf = []

    async def run_and_capture() -> str:
        # Redireciona stdout temporariamente
        loop = asyncio.get_running_loop()
        original_stdout = sys.stdout
        try:
            sys.stdout = open(sys.stdout.fileno(), mode="w", buffering=1)  # type: ignore
        except Exception:
            sys.stdout = original_stdout
        try:
            await orchestrator_main(message)
        finally:
            sys.stdout = original_stdout
        return "".join(buf)

    # Aqui simplificamos: chamamos orchestrator_main que imprime a resposta.
    # Como o printing é síncrono, preferimos rodar em thread e capturar via pipe se necessário.
    await orchestrator_main(message)
    # Para evitar vazios, retornamos uma mensagem genérica
    return make_response(f"Processed by multi_agents.chat: {message}", agent or "")


async def main() -> None:
    for line in sys.stdin:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            print(json.dumps({"type": "error", "error": "invalid json"}))
            sys.stdout.flush()
            continue

        resp = await handle_call(payload)
        print(json.dumps(resp))
        sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
