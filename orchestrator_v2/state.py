import json
from typing import Dict, List

CONTEXT_FILE = "conversation_context.json"


class ConversationState:
    def __init__(self, history: List[Dict[str, str]]) -> None:
        self.history = history

    @classmethod
    def load(cls) -> "ConversationState":
        try:
            with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return cls(data)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return cls([])

    def save(self) -> None:
        with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def append_user(self, content: str) -> None:
        self.history.append({"role": "user", "content": content})

    def append_assistant(self, agent: str, content: str) -> None:
        self.history.append({"role": "assistant", "content": f"({agent}) {content}"})
