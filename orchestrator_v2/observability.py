import json
import logging
import os
from typing import Any, Dict


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("orchestrator_v2")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_event(event: str, data: Dict[str, Any]) -> None:
    """
    Emite logs estruturados em JSON quando OBSERVABILITY_ENABLED=true.
    """
    if os.getenv("OBSERVABILITY_ENABLED", "").lower() not in ("1", "true", "yes"):
        return
    logger = _get_logger()
    payload = {"event": event, "data": data}
    try:
        logger.info(json.dumps(payload, ensure_ascii=False))
    except Exception:
        # Não deve quebrar o fluxo principal se logging falhar
        pass
