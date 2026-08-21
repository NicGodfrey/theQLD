"""Designer export — board SVG, sheet PNG/PDF, per-artifact formats (stdlib).

The zip remains the archive. These formats are the deliverable:

* `board.svg` — vector. Text layers stay `<text>`, not pixels.
* `sheet.png` / `sheet.pdf` — a contact sheet painted here, not a browser
  raster of the live board. SVG artifacts are framed, not re-interpreted.
* JPEG is refused (no DCT encoder in this tree).
"""

from __future__ import annotations

import base64
import html
import re
import struct
import zlib
from pathlib import Path
from typing import Any, Optional

from atelier.helix.loom import download_filename, ext_for_mime
from atelier.helix.quote import as_int

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

RIGHTS_TEXT = """Atelier does not grant commercial rights to generated images.
Output rights follow the provider you called:

  OpenAI  — https://openai.com/policies/terms-of-use
  Gemini  — https://ai.google.dev/gemini-api/terms
  Ollama  — your weights, your machine
  Demo    — generated locally by Atelier; no third-party model

Atelier is a BYOK studio. It spends your quota and grants nothing.
"""

SUPPORTED_PROJECT = {"zip", "archive", "svg", "png", "pdf"}
SUPPORTED_ARTIFACT = {"native", "svg", "png", "pdf"}


class FormatError(ValueError):
    def __init__(self, message: str, code: str = "unsupported_fmt"):
        super().__init__(message)
        self.code = code


def export_scale(value: Any) -> int:
    n = as_int(value, default=1, lo=1, hi=4)
    return 4 if n >= 4 else (2 if n >= 2 else 1)


def _slug(name: str, fallback: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", (name or "").strip()).strip("-").lower()[:32]
    return slug or fallback[:12]


# --------------------------------------------------------------------------
# PNG
# --------------------------------------------------------------------------

def encode_png(width: int, height: int, rgb: bytes) -> bytes:
    if width < 1 or height < 1 or len(rgb) != width * height * 3:
        raise ValueError("bad rgb buffer")
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride : (y + 1) * stride]
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)

    def chunk(tag: bytes, data: bytes) -> bytes:
        blob = tag + data
        return struct.pack(">I", len(data)) + blob + struct.pack(">I", zlib.crc32(blob) & 0xFFFFFFFF)

    return PNG_MAGIC + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b"")


# 5×7 glyphs, bits left-to-right. Enough for a contact-sheet caption.
_FONT = {
    " ": 0,
    "-": 0x001C0,
    ".": 0x00004,
    "0": 0x0E54E,
    "1": 0x0C92F,
    "2": 0x1D12F,
    "3": 0x1C51C,
    "4": 0x127E4,
    "5": 0x1E41C,
    "6": 0x0E4CE,
    "7": 0x1C444,
    "8": 0x0E55C,
    "9": 0x0E71C,
    "A": 0x0E5F1,
    "B": 0x1D5DD,
    "C": 0x0E446,
    "D": 0x1D55D,
    "E": 0x1E4CF,
    "F": 0x1E4C8,
    "G": 0x0E4D6,
    "H": 0x117D1,
    "I": 0x1C92F,
    "K": 0x11551,
    "L": 0x1084F,
    "M": 0x11B51,
    "N": 0x11B59,
    "O": 0x0E551,
    "P": 0x1D4C8,
    "R": 0x1D551,
    "S": 0x0E45C,
    "T": 0x1C920,
    "U": 0x11556,
    "V": 0x11554,
    "X": 0x11511,
    "Y": 0x11520,
    "Z": 0x1C92F,
}


def _caption(text: str, limit: int = 28) -> str:
    out = []
    for ch in (text or "").upper():
        if ch in _FONT:
            out.append(ch)
        elif ch.isalnum():
            out.append("·")
        elif ch in {" ", "-", ".", "_"}:
            out.append("-" if ch == "_" else ch)
    return "".join(out).strip()[:limit] or "LAYER"


def _put(buf: bytearray, w: int, h: int, x: int, y: int, color: bytes) -> None:
    if 0 <= x < w and 0 <= y < h:
        i = (y * w + x) * 3
        buf[i : i + 3] = color


def _fill(buf: bytearray, w: int, h: int, x: int, y: int, rw: int, rh: int, color: bytes) -> None:
    for yy in range(y, y + rh):
        for xx in range(x, x + rw):
            _put(buf, w, h, xx, yy, color)


def _text(buf: bytearray, w: int, h: int, x: int, y: int, text: str, color: bytes, px: int = 1) -> None:
    cx = x
    for ch in text:
        bits = _FONT.get(ch, 0x1F1F1)
        for row in range(7):
            row_bits = (bits >> ((6 - row) * 5)) & 0x1F
            for col in range(5):
                if row_bits & (1 << (4 - col)):
                    for dy in range(px):
                        for dx in range(px):
                            _put(buf, w, h, cx + col * px + dx, y + row * px + dy, color)
        cx += 6 * px


def render_sheet_rgb(project: dict, nodes: list[dict], scale: int = 1) -> tuple[int, int, bytes]:
    scale = export_scale(scale)
    width = 640 * scale
    pad = 20 * scale
    title_h = 36 * scale
    foot = 28 * scale
    height = max(480 * scale, title_h + foot + pad * 2 + max(len(nodes), 1) * 8 * scale)
    if nodes:
        minx = min(n.get("x", 0) for n in nodes)
        miny = min(n.get("y", 0) for n in nodes)
        maxx = max(n.get("x", 0) + n.get("w", 1) for n in nodes)
        maxy = max(n.get("y", 0) + n.get("h", 1) for n in nodes)
        bw = max(maxx - minx, 1)
        bh = max(maxy - miny, 1)
        inner_w = width - pad * 2
        # One node dragged to y=1e12 must not size the pixel buffer: x/y are
        # only checked for finiteness on write, so cap the sheet's aspect.
        inner_h = int(min(max(inner_w * bh / bw, 80.0 * scale), inner_w * 4.0))
        height = title_h + foot + pad * 2 + inner_h
    else:
        minx = miny = 0
        bw = bh = 1
        inner_w = width - pad * 2
        inner_h = height - title_h - foot - pad * 2

    bg = bytes((12, 13, 16))
    ink = bytes((244, 241, 234))
    muted = bytes((154, 148, 136))
    accent = bytes((212, 163, 115))
    panel = bytes((27, 30, 38))
    buf = bytearray(bg * width * height)
    _fill(buf, width, height, 0, 0, width, title_h, bytes((20, 22, 28)))
    name = _caption(project.get("name") or "ATELIER", 22)
    _text(buf, width, height, pad, 10 * scale, name, ink, px=max(1, scale))
    _text(buf, width, height, pad, height - foot + 8 * scale, "RIGHTS FOLLOW THE PROVIDER", muted, px=1)

    def map_box(node):
        x = pad + int((node.get("x", 0) - minx) / bw * inner_w)
        y = title_h + pad + int((node.get("y", 0) - miny) / bh * inner_h)
        w = max(8 * scale, int(node.get("w", 1) / bw * inner_w))
        h = max(8 * scale, int(node.get("h", 1) / bh * inner_h))
        return x, y, w, h

    for node in nodes:
        x, y, w, h = map_box(node)
        color = accent if node.get("type") == "text" else panel
        _fill(buf, width, height, x, y, w, h, color)
        label = _caption(node.get("text") or node.get("type") or "NODE", 18)
        _text(buf, width, height, x + 2 * scale, y + 2 * scale, label, ink if node.get("type") == "text" else muted, px=1)

    return width, height, bytes(buf)


def sheet_png(project: dict, nodes: list[dict], scale: int = 1) -> bytes:
    w, h, rgb = render_sheet_rgb(project, nodes, scale)
    return encode_png(w, h, rgb)


# --------------------------------------------------------------------------
# PDF (one page, DeviceRGB image)
# --------------------------------------------------------------------------

def rgb_to_pdf(width: int, height: int, rgb: bytes, extra_text: str = "") -> bytes:
    if len(rgb) != width * height * 3:
        raise ValueError("bad rgb buffer")
    content = f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q"
    if extra_text:
        safe = extra_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")[:180]
        content += f"\nBT /F1 9 Tf 16 16 Td ({safe}) Tj ET"
    content_b = content.encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 6 0 R >> /XObject << /Im0 5 0 R >> >> "
            f"/Contents 4 0 R >>"
        ).encode(),
        b"<< /Length " + str(len(content_b)).encode() + b" >>\nstream\n" + content_b + b"\nendstream",
        (
            f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Length {len(rgb)} >>\n"
            f"stream\n"
        ).encode()
        + rgb
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(out)


def sheet_pdf(project: dict, nodes: list[dict], scale: int = 1) -> bytes:
    w, h, rgb = render_sheet_rgb(project, nodes, scale)
    return rgb_to_pdf(w, h, rgb, extra_text="Rights follow the image provider. Atelier grants none.")


# --------------------------------------------------------------------------
# Board SVG (text stays type)
# --------------------------------------------------------------------------

_SVG_OPEN = re.compile(r"<svg\b[^>]*>", re.I)


def _board_box(nodes: list[dict]) -> tuple[float, float, float, float]:
    if not nodes:
        return 0.0, 0.0, 1024.0, 1024.0
    minx = min(float(n.get("x") or 0) for n in nodes)
    miny = min(float(n.get("y") or 0) for n in nodes)
    maxx = max(float(n.get("x") or 0) + float(n.get("w") or 1) for n in nodes)
    maxy = max(float(n.get("y") or 0) + float(n.get("h") or 1) for n in nodes)
    pad = 40.0
    return minx - pad, miny - pad, max(maxx - minx + 2 * pad, 1.0), max(maxy - miny + 2 * pad, 1.0)


def _place_svg(raw: str, x: float, y: float, w: float, h: float) -> str:
    cleaned = re.sub(r"<\?xml[^>]*\?>", "", raw)
    cleaned = re.sub(r"<!DOCTYPE[^>]*>", "", cleaned, flags=re.I)

    def inject(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r'\s(?:x|y|width|height)="[^"]*"', "", tag)
        attrs = f' x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"'
        if tag.endswith("/>"):
            return tag[:-2] + attrs + "/>"
        return tag[:-1] + attrs + ">"

    out, n = _SVG_OPEN.subn(inject, cleaned, count=1)
    return out if n else f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#1b1e26"/>'


def _read_artifact(artifacts_dir: Path, art: Optional[dict]) -> tuple[bytes, str]:
    if not art:
        return b"", ""
    path = Path(art.get("path") or "")
    if not path.is_file():
        path = Path(artifacts_dir) / f"{art.get('id', '')}{ext_for_mime(art.get('mime') or '')}"
    if not path.is_file():
        return b"", art.get("mime") or ""
    return path.read_bytes(), art.get("mime") or ""


def board_svg(memory, artifacts_dir, project_id: str, scale: int = 1) -> str:
    project = memory.get_project(project_id)
    if not project:
        raise ValueError("missing project")
    nodes = memory.list_nodes(project_id)
    scale = export_scale(scale)
    ox, oy, bw, bh = _board_box(nodes)
    width = bw * scale
    height = bh * scale
    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height:.1f}" '
        f'viewBox="{ox:.1f} {oy:.1f} {bw:.1f} {bh:.1f}">',
        f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="#0c0d10"/>',
    ]
    for node in nodes:
        x, y = float(node.get("x") or 0), float(node.get("y") or 0)
        w, h = float(node.get("w") or 1), float(node.get("h") or 1)
        kind = node.get("type") or "note"
        art = memory.get_artifact(node["artifact_id"]) if node.get("artifact_id") else None
        data, mime = _read_artifact(Path(artifacts_dir), art)
        if kind == "image" and data:
            if "svg" in (mime or "") or data.lstrip().startswith(b"<svg") or data.lstrip().startswith(b"<?xml"):
                bits.append(_place_svg(data.decode("utf-8", errors="replace"), x, y, w, h))
            else:
                href = f"data:{mime or 'image/png'};base64,{base64.b64encode(data).decode('ascii')}"
                bits.append(
                    f'<image x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" href="{href}"/>'
                )
        else:
            meta = node.get("meta") or {}
            size = meta.get("font_size") or 22
            family = html.escape(str(meta.get("font_family") or "Georgia, serif"), quote=True)
            tracking = html.escape(str(meta.get("letter_spacing") or "normal"), quote=True)
            fill = "#f4f1ea"
            text = html.escape(str(node.get("text") or ""))
            bits.append(
                f'<text x="{x:.1f}" y="{y + float(size):.1f}" fill="{fill}" '
                f'font-size="{float(size):.1f}" font-family="{family}" '
                f'letter-spacing="{tracking}">{text}</text>'
            )
    bits.append("</svg>")
    return "\n".join(bits)


def scale_svg(data: bytes, scale: int) -> bytes:
    """Scale only the root <svg> tag. A blind first-two-attributes pass used
    to bump a nested <rect> when an uploaded root carried no width/height."""
    scale = export_scale(scale)
    if scale == 1:
        return data
    text = data.decode("utf-8", errors="replace")
    root = _SVG_OPEN.search(text)
    if not root:
        return data
    tag = root.group(0)

    def bump(match: re.Match) -> str:
        attr, quote, num, unit = match.group(1), match.group(2), float(match.group(3)), match.group(4)
        return f"{attr}={quote}{num * scale:g}{unit}{quote}"

    new_tag, hits = re.subn(
        r'\b(width|height)=(["\'])(\d+(?:\.\d+)?)([^"\']*)\2',
        bump,
        tag,
    )
    if not hits:
        box = re.search(
            r'viewBox=(["\'])\s*[-\d.eE]+[\s,]+[-\d.eE]+[\s,]+([\d.eE]+)[\s,]+([\d.eE]+)\s*\1',
            tag,
        )
        if not box:
            return data
        attrs = (
            f' width="{float(box.group(2)) * scale:g}"'
            f' height="{float(box.group(3)) * scale:g}"'
        )
        new_tag = tag[:-2] + attrs + "/>" if tag.endswith("/>") else tag[:-1] + attrs + ">"
    return (text[: root.start()] + new_tag + text[root.end() :]).encode("utf-8")


def png_dimensions(data: bytes) -> Optional[tuple[int, int]]:
    """Width/height from the IHDR. Dimensions need no decoder."""
    if not data.startswith(PNG_MAGIC) or len(data) < 24:
        return None
    w, h = struct.unpack(">II", data[16:24])
    if 0 < w <= 65536 and 0 < h <= 65536:
        return w, h
    return None


def wrap_raster_svg(data: bytes, mime: str, scale: int = 1) -> bytes:
    scale = export_scale(scale)
    href = f"data:{mime or 'image/png'};base64,{base64.b64encode(data).decode('ascii')}"
    w, h = png_dimensions(data) or (1024, 1024)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * scale}" height="{h * scale}" '
        f'viewBox="0 0 {w} {h}">'
        f'<image width="{w}" height="{h}" href="{href}"/></svg>'
    ).encode("utf-8")


def artifact_card_png(art: dict, scale: int = 1) -> bytes:
    w, h, rgb = render_sheet_rgb(
        {"name": art.get("prompt") or art.get("id") or "artifact"},
        [{"type": "image", "text": art.get("prompt") or "SVG", "x": 40, "y": 40, "w": 400, "h": 300}],
        scale,
    )
    return encode_png(w, h, rgb)


def export_artifact_bytes(art: dict, artifacts_dir: Path, fmt: str = "native", scale: int = 1) -> tuple[bytes, str, str]:
    fmt = (fmt or "native").strip().lower()
    scale = export_scale(scale)
    if fmt in {"jpeg", "jpg"}:
        raise FormatError("jpeg export is not in the stdlib slice")
    if fmt not in SUPPORTED_ARTIFACT:
        raise FormatError(f"unsupported format: {fmt}")
    data, mime = _read_artifact(Path(artifacts_dir), art)
    if not data:
        raise FileNotFoundError("missing artifact bytes")
    mime = (mime or "").split(";")[0].strip() or "application/octet-stream"
    stem = download_filename(art)
    if "." in stem:
        stem = stem.rsplit(".", 1)[0]
    if fmt == "native":
        return data, mime, download_filename(art)
    is_svg = "svg" in mime or data.lstrip()[:4] in {b"<svg", b"<?xm"}
    is_png = mime.endswith("png") or data.startswith(PNG_MAGIC)
    if fmt == "svg":
        body = scale_svg(data, scale) if is_svg else wrap_raster_svg(data, mime, scale)
        return body, "image/svg+xml", f"{stem}.svg"
    if fmt == "png":
        body = data if is_png else artifact_card_png(art, scale)
        return body, "image/png", f"{stem}.png"
    w, h, rgb = render_sheet_rgb(
        {"name": art.get("prompt") or "artifact"},
        [{"type": "image", "text": art.get("prompt") or "art", "x": 40, "y": 40, "w": 400, "h": 300}],
        scale,
    )
    return rgb_to_pdf(w, h, rgb, extra_text="Rights follow the image provider."), "application/pdf", f"{stem}.pdf"


def export_project_bytes(memory, artifacts_dir, project_id: str, fmt: str = "zip", scale: int = 1) -> tuple[bytes, str, str]:
    project = memory.get_project(project_id)
    if not project:
        raise ValueError("missing project")
    fmt = (fmt or "zip").strip().lower()
    scale = export_scale(scale)
    if fmt in {"jpeg", "jpg"}:
        raise FormatError("jpeg export is not in the stdlib slice")
    if fmt not in SUPPORTED_PROJECT:
        raise FormatError(f"unsupported format: {fmt}")
    slug = _slug(project.get("name") or "", project_id)
    nodes = memory.list_nodes(project_id)
    if fmt in {"zip", "archive"}:
        from atelier.helix.exportzip import export_project_zip

        return export_project_zip(memory, artifacts_dir, project_id, scale=scale), "application/zip", f"atelier-{slug}.zip"
    if fmt == "svg":
        return board_svg(memory, artifacts_dir, project_id, scale).encode("utf-8"), "image/svg+xml", f"atelier-{slug}-board.svg"
    if fmt == "png":
        return sheet_png(project, nodes, scale), "image/png", f"atelier-{slug}-sheet.png"
    return sheet_pdf(project, nodes, scale), "application/pdf", f"atelier-{slug}-sheet.pdf"
