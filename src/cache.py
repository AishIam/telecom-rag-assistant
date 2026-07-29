"""
Simple disk-based cache for LLM answers.
Avoids re-calling the API for questions already answered.
"""

import json
import hashlib
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / "answer_cache.json"


def _make_key(question: str, model: str, prompt_version: str) -> str:
    """Hash the inputs that affect the answer. Change any -> cache miss."""
    raw = f"{question.strip().lower()}|{model}|{prompt_version}"
    return hashlib.sha256(raw.encode()).hexdigest()


def _load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save_cache(cache: dict):
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def get_cached(question: str, model: str, prompt_version: str):
    """Return cached result dict, or None if not present."""
    cache = _load_cache()
    return cache.get(_make_key(question, model, prompt_version))


def set_cached(question: str, model: str, prompt_version: str, result: dict):
    """Store a result in the cache."""
    cache = _load_cache()
    cache[_make_key(question, model, prompt_version)] = result
    _save_cache(cache)