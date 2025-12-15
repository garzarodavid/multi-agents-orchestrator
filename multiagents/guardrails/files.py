import os
from typing import Protocol, Tuple


class FileIO(Protocol):
    def exists(self, path: str) -> bool: ...
    def read(self, path: str) -> str: ...
    def write(self, path: str, content: str) -> None: ...


class LocalFileIO:
    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def read(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write(self, path: str, content: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class McpFileIO(LocalFileIO):
    """
    Implementação que pode ser estendida para usar MCP filesystem.
    Por enquanto delega ao LocalFileIO; se houver tool MCP "filesystem",
    plugar chamadas reais aqui.
    """
    def __init__(self, delegate: LocalFileIO | None = None) -> None:
        self._delegate = delegate or LocalFileIO()

    def exists(self, path: str) -> bool:
        return self._delegate.exists(path)

    def read(self, path: str) -> str:
        return self._delegate.read(path)

    def write(self, path: str, content: str) -> None:
        self._delegate.write(path, content)
