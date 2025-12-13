import hashlib
import json
import os
from typing import Dict, Optional, Tuple

CACHE_FILE = ".cache/orchestrator_v2_cache.json"


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_cache() -> Dict[str, str]:
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_cache(cache: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def get_cached_response(key: str, cache: Dict[str, str]) -> Optional[str]:
    return cache.get(key)


def set_cached_response(key: str, value: str, cache: Dict[str, str]) -> None:
    cache[key] = value
    save_cache(cache)


def build_cache_key(agent: str, message: str, context_signature: Optional[str] = None) -> str:
    base = f"{agent}:{message}"
    if context_signature:
        base += f":{context_signature}"
    return _hash_content(base)
