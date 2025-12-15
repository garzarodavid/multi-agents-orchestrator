import os
import re
import datetime
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


TASKLIST_PATH = "tasklist.md"
CONTEXT_PATH = "contexto.md"
DECISOES_PATH = "decisoes.md"

TEMPLATE_CONTEXTO = """# Contexto do Projeto

## Visao Geral
- Descreva aqui o dominio, objetivos e escopo.

## Arquitetura
- Resuma a arquitetura atual (componentes, integrações, constraints).

## Requisitos Nao Funcionais
- Liste NFRs relevantes (perf, seg, disponibilidade, etc.).
"""

TEMPLATE_DECISOES = """# Registro de Decisoes

- (preencha) AAAA-MM-DD HH:MM | tema | decisao | racional | impactos
"""

TEMPLATE_TASKLIST = """# Tasklist

## Dimensao 1 - Backlog
- Adicione aqui itens futuros.

## Dimensao 2 - Plano em execucao
- Ainda nao ha plano ativo.
"""


@dataclass
class WorkflowResult:
    blocked: bool
    message: str
    plan_id: Optional[str] = None
    plan_title: Optional[str] = None


class WorkflowManager:
    def __init__(self) -> None:
        pass

    def _root(self) -> str:
        return os.getenv("WORKFLOW_ROOT", ".")

    def _auto_bootstrap(self) -> bool:
        return os.getenv("WORKFLOW_AUTO_BOOTSTRAP", "").lower() in ("1", "true", "yes", "on")

    def preprocess(self, user_message: str, agent_name: str) -> WorkflowResult:
        root = self._root()
        auto_bootstrap = self._auto_bootstrap()
        missing = self._missing_files(root)
        if missing:
            if auto_bootstrap:
                self._bootstrap_files(root, missing)
            else:
                template_msg = self._missing_files_message(missing)
                return WorkflowResult(
                    blocked=True,
                    message=f"[BLOCKED_MISSING_FILES] Arquivos ausentes: {', '.join(missing)}\n{template_msg}",
                )

        ctx_text = self._read_file(os.path.join(root, CONTEXT_PATH))
        dec_text = self._read_file(os.path.join(root, DECISOES_PATH))
        task_text = self._read_file(os.path.join(root, TASKLIST_PATH))
        if not self._is_context_coherent(ctx_text, dec_text, task_text):
            return WorkflowResult(
                blocked=True,
                message="[BLOCKED_INVALID_CONTEXT] Estrutura minima ausente em contexto/decisoes/tasklist.",
            )

        # Atualiza plano na Dimensao 2
        plan_id = self._generate_plan_id(agent_name)
        plan_title = f"Atender pedido: {self._shorten(user_message, 80)}"
        self._update_tasklist(root, task_text, plan_id, plan_title, agent_name, user_message)
        return WorkflowResult(blocked=False, message="", plan_id=plan_id, plan_title=plan_title)

    def mark_in_progress(self, plan_id: str) -> None:
        self._update_task_status(plan_id, "Em andamento")

    def mark_done(self, plan_id: str, agent: str, summary: str) -> None:
        self._update_task_status(plan_id, "Concluido")
        self._append_decision(agent=agent, summary=summary)

    # Internals
    def _missing_files(self, root: str) -> Tuple[str, ...]:
        required = (CONTEXT_PATH, DECISOES_PATH, TASKLIST_PATH)
        missing = []
        for f in required:
            if not os.path.exists(os.path.join(root, f)):
                missing.append(f)
        return tuple(missing)

    def _bootstrap_files(self, root: str, missing: Tuple[str, ...]) -> None:
        os.makedirs(root, exist_ok=True)
        for f in missing:
            path = os.path.join(root, f)
            if f == CONTEXT_PATH:
                content = TEMPLATE_CONTEXTO
            elif f == DECISOES_PATH:
                content = TEMPLATE_DECISOES
            else:
                content = TEMPLATE_TASKLIST
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(content)

    def _missing_files_message(self, missing: Tuple[str, ...]) -> str:
        parts = []
        for f in missing:
            if f == CONTEXT_PATH:
                parts.append(f"Template para {f}:\n{TEMPLATE_CONTEXTO}")
            elif f == DECISOES_PATH:
                parts.append(f"Template para {f}:\n{TEMPLATE_DECISOES}")
            else:
                parts.append(f"Template para {f}:\n{TEMPLATE_TASKLIST}")
        return "\n\n".join(parts)

    def _read_file(self, path: str) -> str:
        try:
            with open(path, "r", encoding="utf-8") as fp:
                return fp.read()
        except FileNotFoundError:
            return ""

    def _is_context_coherent(self, ctx: str, dec: str, task: str) -> bool:
        return all([
            "Arquitetura" in ctx or "Visao" in ctx,
            "-" in dec or "Decis" in dec,
            "Dimensao 2" in task or "Dimensão 2" in task,
        ])

    def _generate_plan_id(self, agent: str) -> str:
        ts = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"{agent}_{ts}"

    def _shorten(self, text: str, limit: int) -> str:
        return text if len(text) <= limit else text[:limit] + "..."

    def _update_tasklist(self, root: str, existing: str, plan_id: str, plan_title: str, agent: str, request: str) -> None:
        section_header = "## Dimensao 2"
        if section_header not in existing:
            section_header = "## Dimensão 2"

        pre = ""
        post = ""
        if section_header in existing:
            parts = existing.split(section_header, 1)
            pre = parts[0].rstrip() + "\n\n"
            # descarta o resto da antiga Dimensao 2 e recria
        else:
            pre = existing.rstrip() + "\n\n"

        new_section = [
            "## Dimensao 2 - Plano em execucao",
            f"- Plano ID: {plan_id}",
            f"- Agente: {agent}",
            f"- Titulo: {plan_title}",
            "- Itens:",
            f"  1. [Pendente] Entender pedido: {self._shorten(request, 120)}",
            f"  2. [Pendente] Executar solucao para {agent}",
            "  3. [Pendente] Registrar resultados e decisoes",
            "",
        ]
        updated = pre + "\n".join(new_section) + post
        path = os.path.join(root, TASKLIST_PATH)
        with open(path, "w", encoding="utf-8") as fp:
            fp.write(updated)

    def _update_task_status(self, plan_id: str, status: str) -> None:
        path = os.path.join(self._root(), TASKLIST_PATH)
        try:
            with open(path, "r", encoding="utf-8") as fp:
                content = fp.read()
        except FileNotFoundError:
            return

        def replace_line(line: str) -> str:
            if "[Pendente]" in line or "[Em andamento]" in line or "[Concluido]" in line:
                # marca todas as etapas do plano atual
                return re.sub(r"\[(Pendente|Em andamento|Concluido)\]", f"[{status}]", line)
            return line

        lines = content.splitlines()
        updated_lines = [replace_line(l) for l in lines]
        with open(path, "w", encoding="utf-8") as fp:
            fp.write("\n".join(updated_lines))

    def _append_decision(self, agent: str, summary: str) -> None:
        path = os.path.join(self._root(), DECISOES_PATH)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- {ts} | agente {agent} | {self._shorten(summary, 140)}"
        try:
            with open(path, "a", encoding="utf-8") as fp:
                fp.write("\n" + entry + "\n")
        except Exception:
            pass
