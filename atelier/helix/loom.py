"""Loom — weave media. Demo SVG always works; official spokes spend user quota."""

from __future__ import annotations

import html
import hashlib
import math
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


HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\Z")
MAX_BRAND_COLORS = 6


def brand_colors(palette, limit: int = MAX_BRAND_COLORS) -> list[str]:
    """Validated hex swatches from a free-form brand kit palette.

    The kit is a JSON textarea, so entries arrive in any shape. Demo SVG and
    the paid StyleLock must read the same list, or "ground" means one colour
    on the board and a different one in the prompt.
    """
    if not isinstance(palette, (list, tuple)):
        return []
    colors: list[str] = []
    for item in palette:
        raw = ""
        if isinstance(item, str):
            raw = item.strip()
        elif isinstance(item, dict):
            raw = str(item.get("hex") or item.get("value") or item.get("color") or "").strip()
        if HEX_COLOR.match(raw):
            colors.append(raw)
            if len(colors) >= limit:
                break
    return colors


def brand_name(title) -> str:
    """Brand name safe to sit inside the [StyleLock …] frame."""
    if not isinstance(title, str):
        return ""
    return " ".join(re.sub(r"[\[\]]+", " ", title).split())[:48]


FONT_SIZE_MIN = 12
FONT_SIZE_MAX = 96
# Family names only. A ';' '{' '}' '(' ')' '<' '>' or newline would let a
# stored value close the declaration it is pasted into, so those are refused
# rather than mangled — the board, an export renderer and an SVG caption all
# read this same string.
FONT_FAMILY = re.compile(r"[A-Za-z0-9 ,.'\"_-]{1,120}\Z")
# What CSS letter-spacing actually accepts; a unitless number is ignored by
# the browser, so keeping it would only pretend the tracking was applied.
LETTER_SPACING = re.compile(r"(?:normal|-?\d{1,4}(?:\.\d{1,4})?(?:px|em|rem|ch|pt))\Z")


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def text_meta(meta) -> dict:
    """Node meta with the typography keys clamped to what a board can render.

    Only the browser clamped these, so anything that reached `add_node` by
    another door — the HTTP route, the conductor, a future export renderer —
    could carry a 99999px headline or a font-family with a stray ';'. Keys the
    board does not read pass through untouched.
    """
    if not isinstance(meta, dict):
        return {}
    out = dict(meta)
    if "font_size" in out:
        size = _number(out.get("font_size"))
        if size is None:
            out.pop("font_size")
        else:
            size = min(FONT_SIZE_MAX, max(FONT_SIZE_MIN, size))
            out["font_size"] = int(size) if size.is_integer() else size
    for key, pattern in (("font_family", FONT_FAMILY), ("letter_spacing", LETTER_SPACING)):
        if key not in out:
            continue
        raw = out[key]
        raw = raw.strip() if isinstance(raw, str) else ""
        if pattern.match(raw):
            out[key] = raw
        else:
            out.pop(key)
    return out


def style_lock(prompt: str, palette=None, title: str | None = None) -> str:
    """Prefix a paid image prompt with brand name + hex palette.

    Official image APIs have no structured style token, so the lock has to
    ride in the prompt text. Demo SVG still tints fills directly.
    """
    colors = brand_colors(palette)
    bits = []
    name = brand_name(title)
    if name:
        bits.append(f"brand={name}")
    if colors:
        bits.append("palette=" + ",".join(colors))
        bits.append(f"ground={colors[0]}")
        if len(colors) >= 2:
            bits.append(f"ink={colors[1]}")
    if not bits:
        return prompt
    return f"[StyleLock {' '.join(bits)}]\n{prompt}"


def demo_svg(prompt: str, title: str = "Atelier", palette: list | None = None) -> str:
    digest = hashlib.sha1((prompt or "atelier").encode()).hexdigest()
    c1 = f"#{digest[:6]}"
    c2 = f"#{digest[6:12]}"
    bg = "#0c0d10"
    ink = "#f4f1ea"
    colors = brand_colors(palette)
    if colors:
        bg = colors[0]
        if len(colors) >= 2:
            ink = colors[1]
        if len(colors) >= 3:
            c1 = colors[2]
        elif len(colors) >= 2:
            c1 = colors[1]
        if len(colors) >= 4:
            c2 = colors[3]
        elif colors:
            c2 = colors[0]
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
