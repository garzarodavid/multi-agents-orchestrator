import os
from typing import Dict, Tuple

from multiagents.guardrails.files import FileIO, LocalFileIO
from multiagents.guardrails.templates import CONTEXT_TEMPLATE, DECISOES_TEMPLATE, TASKLIST_TEMPLATE


REQUIRED_FILES = ("contexto.md", "decisoes.md", "tasklist.md")


def get_root() -> str:
    return os.getenv("AGENT_STATE_ROOT") or "."


def ensure_files(io: FileIO | None = None, auto_bootstrap: bool = False) -> Tuple[bool, str]:
    io = io or LocalFileIO()
    missing = [f for f in REQUIRED_FILES if not io.exists(os.path.join(get_root(), f))]
    if missing and auto_bootstrap:
        for f in missing:
            content = _template_for(f)
            io.write(os.path.join(get_root(), f), content)
        missing = []
    if missing:
        msg = "Arquivos obrigatorios ausentes: " + ", ".join(missing) + "\n" + _templates_message(missing)
        return False, msg
    return True, ""


def read_all(io: FileIO | None = None) -> Dict[str, str]:
    io = io or LocalFileIO()
    root = get_root()
    return {f: io.read(os.path.join(root, f)) for f in REQUIRED_FILES}


def _template_for(name: str) -> str:
    if name == "contexto.md":
        return CONTEXT_TEMPLATE
    if name == "decisoes.md":
        return DECISOES_TEMPLATE
    return TASKLIST_TEMPLATE


def _templates_message(missing: list[str]) -> str:
    parts: list[str] = []
    for f in missing:
        parts.append(f"Template para {f}:\n{_template_for(f)}")
    return "\n\n".join(parts)
