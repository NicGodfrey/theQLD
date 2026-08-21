"""Demo-lane eval — run a fixture through the live conductor and score it.

This is not the research craft graph. It checks what live Helix actually
emits in demo: a plan, a board pin, and (when a kit is set) palette ink
in the SVG. `crafts_required` / `lanes_required` stay on the fixture as
documentation of the richer graph; they are not scored here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVAL_DIR = Path(__file__).resolve().parent.parent / "data" / "eval"


def load_fixture(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "request" not in data or "expected" not in data:
        raise ValueError(f"fixture missing request/expected: {path}")
    return data


def list_fixtures(folder: str | Path | None = None) -> list[Path]:
    root = Path(folder) if folder else EVAL_DIR
    return sorted(p for p in root.glob("brief_*.json") if p.is_file())


def _haystack(result: dict) -> str:
    bits = [str(result.get("message") or "")]
    bits.append(json.dumps(result.get("plan") or {}, ensure_ascii=False))
    for art in result.get("artifacts") or []:
        bits.append(str(art.get("prompt") or ""))
    return "\n".join(bits)


def score_result(fixture: dict, result: dict, svg_blobs: list[bytes] | None = None) -> dict[str, Any]:
    expected = fixture.get("expected") or {}
    hay = _haystack(result)
    mentions = []
    for needle in expected.get("must_mention") or []:
        mentions.append({"needle": needle, "hit": needle.lower() in hay.lower()})
    palette = []
    blobs = svg_blobs or []
    joined = b"\n".join(blobs)
    for hex_color in expected.get("palette") or []:
        raw = (hex_color or "").strip()
        palette.append({"hex": raw, "hit": raw.encode("ascii", errors="ignore") in joined if raw else False})
    forbidden = []
    for art in result.get("artifacts") or []:
        kind = (art.get("kind") or art.get("mime") or "").lower()
        for lane in expected.get("lanes_forbidden") or []:
            if lane.lower() in kind:
                forbidden.append(lane)
    ok = all(m["hit"] for m in mentions) and not forbidden
    if expected.get("palette") and blobs:
        ok = ok and all(p["hit"] for p in palette)
    return {
        "id": fixture.get("id"),
        "ok": ok,
        "must_mention": mentions,
        "palette": palette,
        "forbidden_hits": forbidden,
        "artifact_count": len(result.get("artifacts") or []),
        "node_count": len(result.get("nodes") or []),
    }


def run_fixture(fixture: dict, *, memory, conductor, artifacts_dir: Path) -> dict:
    brand = fixture.get("brand") or {}
    project = memory.create_project(fixture.get("title") or fixture.get("id") or "eval", brand)
    if brand:
        memory.update_brand_kit(project["id"], brand)
    thread = memory.create_thread(project["id"], topic=fixture.get("id") or "eval")
    result = conductor.run(
        project_id=project["id"],
        thread_id=thread["id"],
        prompt=fixture["request"],
        provider="demo",
        mode="fast",
    )
    blobs = []
    for art in result.get("artifacts") or []:
        path = Path(art.get("path") or "")
        if not path.is_file():
            path = artifacts_dir / f"{art.get('id', '')}.svg"
        if path.is_file():
            blobs.append(path.read_bytes())
    return score_result(fixture, result, blobs)
