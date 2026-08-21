"""Loom — weave media. Demo SVG always works; official spokes spend user quota."""

from __future__ import annotations

import html
import hashlib
import re
from pathlib import Path

MIME_EXT = {
    "image/svg+xml": ".svg",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "audio/mpeg": ".mp3",
    "application/zip": ".zip",
    "application/json": ".json",
}


def ext_for_mime(mime: str) -> str:
    return MIME_EXT.get((mime or "").split(";")[0].strip(), ".bin")


def download_filename(artifact: dict) -> str:
    """ASCII filename from the brief, not the hex id."""
    prompt = (artifact.get("prompt") or "").strip()
    mime = artifact.get("mime") or ""
    ext = ext_for_mime(mime)
    stem = prompt
    lower = stem.lower()
    for candidate in sorted(set(MIME_EXT.values()) | {".jpeg"}, key=len, reverse=True):
        if lower.endswith(candidate):
            stem = stem[: -len(candidate)]
            break
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", stem).strip("-").lower()
    slug = slug[:32].rstrip("-_")
    if not slug:
        slug = (artifact.get("id") or "artifact")[:12]
    return f"{slug}{ext}"


def _hex_color(value: str, fallback: str) -> str:
    raw = (value or "").strip()
    if raw.startswith("#") and len(raw) in {4, 7}:
        return raw
    return fallback


def demo_svg(prompt: str, title: str = "Atelier", palette: list | None = None) -> str:
    digest = hashlib.sha1((prompt or "atelier").encode()).hexdigest()
    c1 = f"#{digest[:6]}"
    c2 = f"#{digest[6:12]}"
    bg = "#0c0d10"
    ink = "#f4f1ea"
    if palette:
        colors = [c for c in palette if isinstance(c, str)]
        if len(colors) >= 1:
            bg = _hex_color(colors[0], bg)
        if len(colors) >= 2:
            ink = _hex_color(colors[1], ink)
        if len(colors) >= 3:
            c1 = _hex_color(colors[2], c1)
        if len(colors) >= 4:
            c2 = _hex_color(colors[3], c2)
        elif len(colors) >= 2:
            c1 = _hex_color(colors[1], c1)
    safe = html.escape((prompt or "untitled brief")[:180])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" fill="{bg}"/>
  <circle cx="780" cy="220" r="240" fill="url(#g)" opacity="0.85"/>
  <circle cx="260" cy="760" r="200" fill="{c2}" opacity="0.35"/>
  <text x="64" y="120" fill="{ink}" font-size="42" font-family="Georgia, serif">{html.escape(title)}</text>
  <text x="64" y="900" fill="#c8c2b4" font-size="28" font-family="ui-sans-serif, system-ui">{safe}</text>
</svg>
"""


def write_bytes(root: Path, artifact_id: str, data: bytes, mime: str) -> Path:
    folder = Path(root)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{artifact_id}{ext_for_mime(mime)}"
    path.write_bytes(data)
    return path
