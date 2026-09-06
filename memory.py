#!/usr/bin/env python3
"""
Lightweight persistent memory for the agent.

Facts are stored as a JSON dict in a local file so the agent can remember
things across sessions (your name, preferred light, AC temperature, etc.).
Nothing leaves the machine.
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

MEMORY_PATH = Path(os.getenv("MEMORY_PATH", "memory_store/facts.json"))


def _load() -> dict:
    if not MEMORY_PATH.exists():
        return {}
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    MEMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def remember_fact(key: str, value: str) -> None:
    if not key or not value:
        raise ValueError("remember_fact needs both a key and a value")
    data = _load()
    data[key.strip().lower()] = value.strip()
    _save(data)


def recall_facts() -> dict:
    return _load()


def forget_fact(key: str) -> bool:
    data = _load()
    removed = data.pop(key.strip().lower(), None) is not None
    if removed:
        _save(data)
    return removed


if __name__ == "__main__":
    print(json.dumps(recall_facts(), indent=2))
