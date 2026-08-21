"""Helix integration catalog — TOP related GitHub projects (patterns, not vendored)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "top100.json"


@lru_cache(maxsize=1)
def load() -> dict:
    return json.loads(DATA.read_text())


def public() -> dict:
    payload = load()
    return {
        "title": payload.get("title"),
        "architecture": payload.get("architecture"),
        "mvp_wire": payload.get("mvp_wire"),
        "count": len(payload.get("projects") or []),
        "projects": payload.get("projects") or [],
        "categories": payload.get("categories") or {},
    }
