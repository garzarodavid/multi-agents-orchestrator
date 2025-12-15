import datetime
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from multiagents.guardrails.context_files import ensure_files, read_all, get_root
from multiagents.guardrails.task_tracker import TaskItem, ExecutionPlan
from multiagents.guardrails.files import FileIO, LocalFileIO
from multiagents.guardrails.templates import TASKLIST_TEMPLATE, DECISOES_TEMPLATE, CONTEXT_TEMPLATE


def is_context_relevant(user_request: str, override: Optional[bool] = None) -> bool:
    if override is not None:
        return override
    short = len(user_request) < 40 and not any(k in user_request.lower() for k in ("arquitetura", "deploy", "schema", "pipelines"))
    return not short


@dataclass
class ExecutionContext:
    root: str
    contexto: str
    decisoes: str
    tasklist: str
    plan: ExecutionPlan
    auto_bootstrap: bool
    strict_mode: bool


class ContextEnforcer:
    def __init__(self, io: FileIO | None = None) -> None:
        self.io = io or LocalFileIO()

    def run(
        self,
        agent: str,
        user_request: str,
        handler_fn: Callable[[ExecutionContext], str],
        *,
        context_relevant: Optional[bool] = None,
    ) -> str:
        auto_bootstrap = os.getenv("WORKFLOW_AUTO_BOOTSTRAP", "").lower() in ("1", "true", "yes")
        strict_mode = os.getenv("WORKFLOW_STRICT_MODE", "").lower() in ("1", "true", "yes")
        ok, msg = ensure_files(self.io, auto_bootstrap=auto_bootstrap)
        if not ok:
            return f"[BLOCKED_MISSING_FILES] {msg}"

        files = read_all(self.io)
        if is_context_relevant(user_request, override=context_relevant):
            if not self._is_coherent(files):
                return "[BLOCKED_INVALID_CONTEXT] Estrutura minima ausente em contexto/decisoes/tasklist."

        plan = self._prepare_plan(agent, user_request, files["tasklist"])
        ctx = ExecutionContext(
            root=get_root(),
            contexto=files["contexto.md"],
            decisoes=files["decisoes.md"],
            tasklist=files["tasklist.md"],
            plan=plan,
            auto_bootstrap=auto_bootstrap,
            strict_mode=strict_mode,
        )
        self._write_tasklist(plan)
        self._mark_plan(plan, "Em andamento")
        result = handler_fn(ctx)
        if result is None:
            result = ""
        status = "Concluido" if "[Erro" not in result else "Bloqueado"
        self._mark_plan(plan, status)
        if status == "Concluido":
            self._append_decision(agent, result)
        return result

    def _prepare_plan(self, agent: str, request: str, existing_tasklist: str) -> ExecutionPlan:
        plan_id = self._generate_plan_id(agent)
        items = [
            TaskItem(1, "Entender pedido", self._shorten(request, 120), "Pendente"),
            TaskItem(2, "Executar", f"Execucao pelo agente {agent}", "Pendente"),
            TaskItem(3, "Registrar decisoes", "Atualizar decisoes/contexto conforme impacto", "Pendente"),
        ]
        return ExecutionPlan(plan_id=plan_id, items=items)

    def _write_tasklist(self, plan: ExecutionPlan) -> None:
        path = os.path.join(get_root(), "tasklist.md")
        if not self.io.exists(path):
            self.io.write(path, TASKLIST_TEMPLATE)
        existing = self.io.read(path)
        if "## Dimensao 2" in existing:
            pre = existing.split("## Dimensao 2", 1)[0].rstrip() + "\n\n"
        elif "## Dimensão 2" in existing:
            pre = existing.split("## Dimensão 2", 1)[0].rstrip() + "\n\n"
        else:
            pre = existing.rstrip() + "\n\n"
        lines = [
            "## Dimensao 2 - Execucao Atual (Ultimo Pedido do Usuario)",
            "| Ordem | Titulo | Descricao | Status |",
            "|-------|--------|-----------|--------|",
        ]
        for item in plan.items:
            lines.append(f"| {item.ordem} | {item.titulo} | {item.descricao} | {item.status} |")
        content = pre + "\n".join(lines) + "\n"
        self.io.write(path, content)

    def _mark_plan(self, plan: ExecutionPlan, status: str) -> None:
        path = os.path.join(get_root(), "tasklist.md")
        if not self.io.exists(path):
            return
        content = self.io.read(path)
        def replace(line: str) -> str:
            if re.match(r"\|\s*\d+\s*\|", line):
                return re.sub(r"\|\s*(Pendente|Em andamento|Concluido|Bloqueado)\s*\|", f"| {status} |", line)
            return line
        updated = "\n".join(replace(l) for l in content.splitlines())
        self.io.write(path, updated)

    def _append_decision(self, agent: str, summary: str) -> None:
        path = os.path.join(get_root(), "decisoes.md")
        if not self.io.exists(path):
            self.io.write(path, DECISOES_TEMPLATE)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- Data: {ts}\n- Decisao: Execucao do agente {agent}\n- Contexto: {self._shorten(summary,140)}\n- Alternativas: n/a\n- Consequencias: n/a\n"
        existing = self.io.read(path).rstrip() + "\n\n" + entry
        self.io.write(path, existing)

    def _is_coherent(self, files: Dict[str, str]) -> bool:
        return all([
            "Arquitetura" in files.get("contexto.md", ""),
            "Decis" in files.get("decisoes.md", ""),
            "Dimensao" in files.get("tasklist.md", "") or "Dimensão" in files.get("tasklist.md", ""),
        ])

    def _generate_plan_id(self, agent: str) -> str:
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{agent}_{ts}"

    def _shorten(self, text: str, limit: int) -> str:
        return text if len(text) <= limit else text[:limit] + "..."
