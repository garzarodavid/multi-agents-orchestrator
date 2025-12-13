from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ChatResult:
    text: str
    usage: Dict[str, Any]
    raw: Any = None


class LLMProvider(ABC):
    name: str
    default_model: str

    @abstractmethod
    async def chat(
        self,
        *,
        model: Optional[str],
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        agent: Optional[str] = None,
    ) -> ChatResult:
        ...
