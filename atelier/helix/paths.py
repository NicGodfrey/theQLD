"""Path confinement — never serve or write outside a declared root."""

from __future__ import annotations

from pathlib import Path


def safe_under(root: Path, candidate: Path) -> Path | None:
    try:
        root_r = Path(root).resolve()
        cand = Path(candidate).resolve()
        cand.relative_to(root_r)
    except (ValueError, OSError):
        return None
    if cand.is_file():
        return cand
    return None
