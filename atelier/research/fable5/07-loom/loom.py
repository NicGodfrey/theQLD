#!/usr/bin/env python3
"""loom.py — Atelier media generation pipelines (Fable5#7 "loom").

Bring-your-own-key (BYOK) pipelines against *official* vendor APIs only:

  * Images  — OpenAI Images API (gpt-image-1 / dall-e-3) and
              Gemini API native image models (gemini-2.5-flash-image,
              a.k.a. "Nano Banana"; legacy Imagen adapter kept for reference).
  * Briefs  — text -> structured design-brief expansion via OpenAI chat
              completions or Gemini generateContent (JSON mode), with a
              deterministic offline expander for demo mode.
  * Audio   — TTS via OpenAI /v1/audio/speech or Gemini TTS preview models;
              demo mode synthesizes a WAV chime with the stdlib.
  * Video   — a small job-shaped stub interface (submit / poll / download)
              with optional adapters for the *documented* official endpoints
              (OpenAI Sora 2 Videos API [deprecated], Google Veo via
              predictLongRunning). Demo mode emits an animated SVG.
  * Demo    — every pipeline has a keyless local mode that renders SVG/PNG/WAV
              placeholders with the standard library only, so a UI can be
              built and tested without any API keys or spend.

Design constraints:
  - Standard library only. HTTP via urllib; PNG via zlib+struct; WAV via wave.
  - No third-party SDKs, no aggregators, no scraping. Official endpoints only.
  - Every generated file gets a JSON sidecar describing provenance.

Environment variables:
  OPENAI_API_KEY        key for api.openai.com
  GEMINI_API_KEY        key for generativelanguage.googleapis.com
                        (GOOGLE_API_KEY accepted as a fallback)
  OPENAI_BASE_URL       override, default https://api.openai.com/v1
  GEMINI_BASE_URL       override, default https://generativelanguage.googleapis.com/v1beta
  LOOM_PROVIDER         default provider routing: openai | gemini | demo
  LOOM_TIMEOUT          HTTP timeout seconds (default 120)

CLI:
  python loom.py image  "a poster of ..." [--provider auto] [--out DIR] ...
  python loom.py brief  "a coffee brand ..." [--provider demo]
  python loom.py speech "welcome to atelier" [--provider auto]
  python loom.py video  "orbiting camera ..." [--provider demo]
  python loom.py demo-kit [--out DIR]
  python loom.py selftest

See PIPELINES.md for full documentation.
"""

from __future__ import annotations

import argparse
import base64
import colorsys
import hashlib
import json
import math
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
import wave
import zlib
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Optional
from xml.sax.saxutils import escape as _xml_escape

__version__ = "0.1.0"

DEFAULT_OPENAI_BASE = "https://api.openai.com/v1"
DEFAULT_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Live model defaults (checked against vendor docs, 2026-08).
OPENAI_IMAGE_MODEL = "gpt-image-1"
OPENAI_IMAGE_MODEL_LEGACY = "dall-e-3"
OPENAI_TEXT_MODEL = "gpt-4o-mini"
OPENAI_TTS_MODEL = "gpt-4o-mini-tts"
OPENAI_VIDEO_MODEL = "sora-2"            # deprecated; removal 2026-09-24

GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"   # "Nano Banana", GA
GEMINI_IMAGEN_MODEL = "imagen-4.0-generate-001"  # shut down 2026-08-17
GEMINI_TEXT_MODEL = "gemini-2.5-flash"
GEMINI_TTS_MODEL = "gemini-2.5-flash-preview-tts"
GEMINI_VIDEO_MODEL = "veo-3.0-generate-001"

GEMINI_PCM_RATE = 24_000  # Gemini TTS returns s16le mono PCM at 24 kHz


# --------------------------------------------------------------------------
# Errors and configuration
# --------------------------------------------------------------------------

class LoomError(RuntimeError):
    """Base error for pipeline failures."""


class MissingKeyError(LoomError):
    """Raised when a provider is requested but its API key is absent."""


class ProviderHTTPError(LoomError):
    """Raised when an official endpoint returns a non-2xx response."""

    def __init__(self, status: int, url: str, body: str):
        self.status = status
        self.url = url
        self.body = body
        super().__init__(f"HTTP {status} from {url}: {body[:400]}")


@dataclass
class Config:
    """Runtime configuration, normally derived from the environment."""

    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openai_base_url: str = DEFAULT_OPENAI_BASE
    gemini_base_url: str = DEFAULT_GEMINI_BASE
    timeout: float = 120.0
    retries: int = 2
    default_provider: Optional[str] = None  # openai | gemini | demo | None

    @classmethod
    def from_env(cls, env: Optional[dict] = None) -> "Config":
        env = dict(os.environ if env is None else env)
        return cls(
            openai_api_key=env.get("OPENAI_API_KEY") or None,
            gemini_api_key=env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY") or None,
            openai_base_url=(env.get("OPENAI_BASE_URL") or DEFAULT_OPENAI_BASE).rstrip("/"),
            gemini_base_url=(env.get("GEMINI_BASE_URL") or DEFAULT_GEMINI_BASE).rstrip("/"),
            timeout=float(env.get("LOOM_TIMEOUT", "120")),
            default_provider=(env.get("LOOM_PROVIDER") or "").strip().lower() or None,
        )


# --------------------------------------------------------------------------
# Asset records
# --------------------------------------------------------------------------

@dataclass
class Asset:
    """Provenance record for one generated file. Serialized as a sidecar."""

    kind: str                 # image | brief | speech | video
    path: str
    mime: str
    provider: str             # openai | gemini | demo
    model: str
    prompt: str
    created_at: float = field(default_factory=time.time)
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def write_sidecar(self) -> Path:
        sidecar = Path(self.path).with_suffix(Path(self.path).suffix + ".json")
        sidecar.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return sidecar


@dataclass
class VideoJob:
    """Provider-neutral video render job (see VideoPipeline)."""

    provider: str
    model: str
    prompt: str
    job_id: str
    status: str = "queued"    # queued | in_progress | completed | failed
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# HTTP helpers (urllib only)
# --------------------------------------------------------------------------

_RETRIABLE = {429, 500, 502, 503, 504}


def _http(method: str, url: str, headers: Optional[dict] = None,
          body: Optional[bytes] = None, timeout: float = 120.0,
          retries: int = 2) -> bytes:
    """One HTTP round-trip with small exponential backoff on 429/5xx."""
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=body, method=method,
                                     headers=dict(headers or {}))
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as err:
            detail = err.read().decode("utf-8", errors="replace")
            if err.code in _RETRIABLE and attempt < retries:
                time.sleep(2.0 * (2 ** attempt))
                attempt += 1
                continue
            raise ProviderHTTPError(err.code, url, detail) from None
        except urllib.error.URLError as err:
            if attempt < retries:
                time.sleep(2.0 * (2 ** attempt))
                attempt += 1
                continue
            raise LoomError(f"network error reaching {url}: {err.reason}") from None


def _http_json(method: str, url: str, headers: Optional[dict] = None,
               payload: Optional[dict] = None, timeout: float = 120.0,
               retries: int = 2) -> dict:
    headers = dict(headers or {})
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    raw = _http(method, url, headers, body, timeout, retries)
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise LoomError(f"non-JSON response from {url} ({len(raw)} bytes)") from None


def _openai_headers(cfg: Config) -> dict:
    if not cfg.openai_api_key:
        raise MissingKeyError(
            "OPENAI_API_KEY is not set; export it or use --provider demo")
    return {"Authorization": f"Bearer {cfg.openai_api_key}"}


def _gemini_headers(cfg: Config) -> dict:
    if not cfg.gemini_api_key:
        raise MissingKeyError(
            "GEMINI_API_KEY is not set; export it or use --provider demo")
    return {"x-goog-api-key": cfg.gemini_api_key}


# --------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------

def _slug(text: str, limit: int = 40) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:limit].rstrip("-")) or "asset"


def _stamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def _digest(seed: str) -> bytes:
    return hashlib.sha256(seed.encode("utf-8")).digest()


def _pick(digest: bytes, index: int, options: list) -> Any:
    return options[digest[index % len(digest)] % len(options)]


def _hex_rgb(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _hls_color(hue: float, light: float, sat: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hls_to_rgb(hue % 1.0, max(0.0, min(1.0, light)),
                                  max(0.0, min(1.0, sat)))
    return int(r * 255), int(g * 255), int(b * 255)


def _mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def _parse_size(size: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)\s*[xX]\s*(\d+)", size.strip())
    if not match:
        raise LoomError(f"bad --size {size!r}; expected WIDTHxHEIGHT, e.g. 1024x1024")
    return int(match.group(1)), int(match.group(2))


def _closest_aspect(width: int, height: int) -> str:
    """Map a WxH request onto the aspect-ratio enum Gemini image models take."""
    ratios = {"1:1": 1.0, "3:2": 1.5, "2:3": 2 / 3, "4:3": 4 / 3, "3:4": 0.75,
              "5:4": 1.25, "4:5": 0.8, "16:9": 16 / 9, "9:16": 9 / 16, "21:9": 21 / 9}
    want = width / height
    return min(ratios, key=lambda k: abs(ratios[k] - want))


def _seed_palette(digest: bytes) -> dict:
    """Deterministic five-swatch palette derived from a prompt digest."""
    base_hue = digest[0] / 255.0
    scheme = _pick(digest, 1, ["analogous", "complementary", "triadic"])
    offsets = {"analogous": [0.0, 0.06, -0.06, 0.12, 0.5],
               "complementary": [0.0, 0.5, 0.04, 0.46, 0.25],
               "triadic": [0.0, 1 / 3, 2 / 3, 0.05, 0.38]}[scheme]
    roles = ["primary", "secondary", "accent", "surface", "contrast"]
    lights = [0.42, 0.55, 0.62, 0.92, 0.16]
    sats = [0.62, 0.55, 0.78, 0.18, 0.30]
    swatches = []
    for role, off, light, sat in zip(roles, offsets, lights, sats):
        rgb = _hls_color(base_hue + off, light, sat)
        swatches.append({"role": role, "hex": _hex_rgb(rgb), "rgb": list(rgb)})
    return {"scheme": scheme, "swatches": swatches}


# --------------------------------------------------------------------------
# Pure-stdlib PNG writer + placeholder renderers
# --------------------------------------------------------------------------

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    blob = tag + data
    return struct.pack(">I", len(data)) + blob + struct.pack(">I", zlib.crc32(blob) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int,
              rows: Iterable[bytes]) -> None:
    """Write an 8-bit RGB PNG from an iterable of raw scanlines (3*width bytes)."""
    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter type 0 (None)
        raw += row
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    payload = (b"\x89PNG\r\n\x1a\n"
               + _png_chunk(b"IHDR", header)
               + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 6))
               + _png_chunk(b"IEND", b""))
    Path(path).write_bytes(payload)


def _placeholder_rows(width: int, height: int, digest: bytes) -> Iterator[bytes]:
    """Diagonal two-color gradient with a mirrored 8x8 glyph overlay."""
    palette = _seed_palette(digest)["swatches"]
    c0 = tuple(palette[0]["rgb"])
    c1 = tuple(palette[1]["rgb"])
    accent = tuple(palette[2]["rgb"])
    span = max(width + height - 2, 1)
    ramp = [_mix(c0, c1, i / span) for i in range(width + height - 1)]
    bits = hashlib.sha256(digest + b"|grid").digest()
    grid = [[(bits[(r * 4 + c) % len(bits)] >> ((r + c) % 8)) & 1
             for c in range(4)] for r in range(8)]
    alpha = 0.30
    for y in range(height):
        gy = (y * 8) // height
        row = bytearray()
        for x in range(width):
            r, g, b = ramp[x + y]
            gx = (x * 8) // width
            if grid[gy][gx if gx < 4 else 7 - gx]:
                r = int(r + (accent[0] - r) * alpha)
                g = int(g + (accent[1] - g) * alpha)
                b = int(b + (accent[2] - b) * alpha)
            row += bytes((r, g, b))
        yield bytes(row)


def render_placeholder_png(path: Path, prompt: str, width: int, height: int) -> None:
    """Keyless PNG placeholder: deterministic gradient + glyph from the prompt."""
    write_png(path, width, height, _placeholder_rows(width, height, _digest(prompt)))


def render_identicon_png(path: Path, seed: str, size: int = 160) -> None:
    """5x5 mirrored identicon (avatar placeholder)."""
    digest = _digest(seed)
    palette = _seed_palette(digest)["swatches"]
    bg = tuple(palette[3]["rgb"])
    fg = tuple(palette[0]["rgb"])
    cells = [[(digest[(r * 3 + c) % len(digest)] >> ((r * c) % 8)) & 1
              for c in range(3)] for r in range(5)]
    margin = size // 10
    inner = size - 2 * margin

    def rows() -> Iterator[bytes]:
        for y in range(size):
            row = bytearray()
            for x in range(size):
                color = bg
                if margin <= x < size - margin and margin <= y < size - margin:
                    cx = ((x - margin) * 5) // inner
                    cy = ((y - margin) * 5) // inner
                    if cells[cy][cx if cx < 3 else 4 - cx]:
                        color = fg
                row += bytes(color)
            yield bytes(row)

    write_png(path, size, size, rows())


def render_swatch_png(path: Path, hex_colors: list[str], width: int = 500,
                      height: int = 100) -> None:
    """Horizontal palette strip: one flat band per color."""
    rgbs = [tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
            for h in hex_colors]
    band = max(width // len(rgbs), 1)

    def rows() -> Iterator[bytes]:
        line = bytearray()
        for x in range(width):
            line += bytes(rgbs[min(x // band, len(rgbs) - 1)])
        row = bytes(line)
        for _ in range(height):
            yield row

    write_png(path, width, height, rows())


# --------------------------------------------------------------------------
# SVG placeholder renderers (image + animated "video")
# --------------------------------------------------------------------------

def _wrap_text(text: str, limit: int = 34, max_lines: int = 2) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > limit and current:
            lines.append(current)
            current = word
        else:
            current = candidate
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(lines)) < len(text):
        lines[-1] = lines[-1][: limit - 1] + "…"
    return lines or ["placeholder"]


def render_placeholder_svg(path: Path, prompt: str, width: int, height: int,
                           animated: bool = False, label: str = "LOOM DEMO",
                           duration: float = 8.0) -> None:
    """Keyless SVG placeholder. With animated=True this doubles as the demo
    'video': SMIL animation loops so a UI can preview motion without MP4s."""
    digest = _digest(prompt)
    palette = _seed_palette(digest)["swatches"]
    c0, c1 = palette[0]["hex"], palette[1]["hex"]
    accent, contrast = palette[2]["hex"], palette[4]["hex"]
    lines = _wrap_text(prompt)
    font = max(min(width, height) // 18, 12)
    cx, cy = width / 2, height / 2
    radius = min(width, height) / 5

    text_spans = "".join(
        f'<tspan x="{cx:.0f}" dy="{"0" if i == 0 else "1.4em"}">{_xml_escape(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    motion = ""
    if animated:
        motion = f"""
  <g>
    <polygon points="{cx - radius:.0f},{cy:.0f} {cx:.0f},{cy - radius:.0f} {cx + radius:.0f},{cy:.0f} {cx:.0f},{cy + radius:.0f}"
             fill="{accent}" opacity="0.55">
      <animateTransform attributeName="transform" type="rotate"
        from="0 {cx:.0f} {cy:.0f}" to="360 {cx:.0f} {cy:.0f}"
        dur="{duration:.1f}s" repeatCount="indefinite"/>
    </polygon>
    <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{radius * 0.4:.0f}" fill="{contrast}" opacity="0.8">
      <animate attributeName="r"
        values="{radius * 0.4:.0f};{radius * 0.55:.0f};{radius * 0.4:.0f}"
        dur="{duration / 2:.1f}s" repeatCount="indefinite"/>
    </circle>
  </g>"""
    else:
        motion = f"""
  <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{radius:.0f}" fill="{accent}" opacity="0.45"/>
  <circle cx="{cx:.0f}" cy="{cy:.0f}" r="{radius * 0.55:.0f}" fill="{contrast}" opacity="0.7"/>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}" role="img" aria-label="{_xml_escape(prompt)}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{c0}"/>
      <stop offset="1" stop-color="{c1}"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bg)"/>{motion}
  <text x="{cx:.0f}" y="{height - font * 3.2:.0f}" text-anchor="middle"
        font-family="ui-sans-serif, system-ui, sans-serif" font-size="{font}"
        fill="#ffffff" opacity="0.92">{text_spans}</text>
  <text x="{cx:.0f}" y="{height - font * 1.2:.0f}" text-anchor="middle"
        font-family="ui-monospace, monospace" font-size="{max(font * 2 // 3, 9)}"
        fill="#ffffff" opacity="0.6">{_xml_escape(label)}</text>
</svg>
"""
    Path(path).write_text(svg, encoding="utf-8")


# --------------------------------------------------------------------------
# WAV demo synthesizer
# --------------------------------------------------------------------------

_PENTATONIC = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25]


def render_chime_wav(path: Path, seed: str, seconds: float = 2.4,
                     rate: int = GEMINI_PCM_RATE) -> None:
    """Keyless audio placeholder: a short seeded pentatonic chime (mono s16le)."""
    digest = _digest(seed)
    notes = [_PENTATONIC[digest[i] % len(_PENTATONIC)] for i in range(4)]
    per_note = seconds / len(notes)
    frames = bytearray()
    for i, freq in enumerate(notes):
        n = int(per_note * rate)
        for j in range(n):
            t = j / rate
            envelope = math.exp(-3.2 * t / per_note)
            sample = (0.55 * math.sin(2 * math.pi * freq * t)
                      + 0.25 * math.sin(2 * math.pi * freq * 2 * t))
            frames += struct.pack("<h", int(max(-1.0, min(1.0, sample * envelope)) * 32767))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(bytes(frames))


def pcm_to_wav(path: Path, pcm: bytes, rate: int = GEMINI_PCM_RATE,
               channels: int = 1, sample_width: int = 2) -> None:
    """Wrap raw PCM (as returned by Gemini TTS) in a WAV container."""
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(rate)
        wav.writeframes(pcm)


# --------------------------------------------------------------------------
# Pipeline 1: text -> design brief expansion
# --------------------------------------------------------------------------

BRIEF_KEYS = ["title", "tagline", "summary", "audience", "tone", "palette",
              "typography", "imagery", "deliverables", "image_prompts",
              "voice_script", "motion_prompt"]

BRIEF_SYSTEM_PROMPT = """You are a senior brand designer. Expand the user's \
one-line idea into a design brief. Respond with a single JSON object with \
exactly these keys:
  title (string), tagline (string), summary (string, 2-3 sentences),
  audience (string), tone (array of 3 adjectives),
  palette (array of 5 objects {role, hex}),
  typography (object {display, body}),
  imagery (array of 3 art-direction strings),
  deliverables (array of objects {name, kind, size}),
  image_prompts (array of 3 detailed prompts for an image model),
  voice_script (string, <= 40 words, suitable for TTS),
  motion_prompt (string, one shot description for a video model).
Return JSON only, no markdown."""

_TYPE_PAIRS = [
    {"display": "Fraunces", "body": "Inter"},
    {"display": "Space Grotesk", "body": "IBM Plex Sans"},
    {"display": "Playfair Display", "body": "Source Sans 3"},
    {"display": "Archivo Black", "body": "Archivo"},
    {"display": "Clash Display", "body": "General Sans"},
    {"display": "Cormorant Garamond", "body": "Work Sans"},
]
_TONES = ["warm", "bold", "quiet", "playful", "precise", "organic",
          "electric", "editorial", "handmade", "monumental"]
_IMAGERY = [
    "macro textures with shallow depth of field",
    "isometric line illustration, single accent color",
    "high-contrast studio photography on seamless backdrop",
    "grainy risograph shapes, two-ink overprint",
    "soft gradient fields with floating geometric forms",
    "documentary candids, natural light, honest color",
]
_AUDIENCES = [
    "independent makers and small studios",
    "design-curious early adopters",
    "busy professionals who value craft",
    "students and lifelong learners",
    "local communities and neighborhood regulars",
]


def demo_brief(prompt: str) -> dict:
    """Deterministic offline brief expansion (same schema as the LLM path)."""
    digest = _digest(prompt)
    palette = _seed_palette(digest)
    title_words = [w.capitalize() for w in re.findall(r"[A-Za-z0-9]+", prompt)[:4]]
    title = " ".join(title_words) or "Untitled Project"
    tones = []
    for i in range(3):
        tone = _TONES[(digest[i + 2] + i) % len(_TONES)]
        if tone not in tones:
            tones.append(tone)
    while len(tones) < 3:
        tones.append(_TONES[(digest[9] + len(tones)) % len(_TONES)])
    typography = _pick(digest, 5, _TYPE_PAIRS)
    imagery = [_IMAGERY[(digest[6] + i * 7) % len(_IMAGERY)] for i in range(3)]
    hexes = [s["hex"] for s in palette["swatches"]]
    return {
        "title": title,
        "tagline": f"{tones[0].capitalize()} by design.",
        "summary": (f"{title} explores '{prompt}'. The direction is {tones[0]} and "
                    f"{tones[1]}, anchored by a {palette['scheme']} palette led by "
                    f"{hexes[0]}. Deliverables prioritize a strong hero image and a "
                    f"flexible social kit."),
        "audience": _pick(digest, 7, _AUDIENCES),
        "tone": tones,
        "palette": [{"role": s["role"], "hex": s["hex"]} for s in palette["swatches"]],
        "typography": typography,
        "imagery": imagery,
        "deliverables": [
            {"name": "hero", "kind": "image", "size": "1920x1080"},
            {"name": "social_square", "kind": "image", "size": "1080x1080"},
            {"name": "story", "kind": "image", "size": "1080x1920"},
            {"name": "teaser", "kind": "video", "size": "1280x720"},
            {"name": "voiceover", "kind": "speech", "size": "~10s"},
        ],
        "image_prompts": [
            f"{prompt}, {imagery[0]}, palette {hexes[0]} {hexes[2]}, {tones[0]} mood",
            f"{prompt}, {imagery[1]}, minimal composition, generous negative space",
            f"{prompt}, {imagery[2]}, centered subject, {tones[2]} atmosphere",
        ],
        "voice_script": (f"Welcome to {title}. {tones[0].capitalize()}, {tones[1]}, "
                         f"and made for you. This is {title}."),
        "motion_prompt": (f"Slow push-in on {prompt}; {imagery[0]}; soft light; "
                          f"{tones[0]} mood; seamless loop"),
        "_provenance": {"provider": "demo", "deterministic": True,
                        "seed": hashlib.sha256(prompt.encode()).hexdigest()[:16]},
    }


def _validate_brief(data: dict) -> dict:
    missing = [k for k in BRIEF_KEYS if k not in data]
    if missing:
        raise LoomError(f"brief response missing keys: {missing}")
    return data


def openai_brief(cfg: Config, prompt: str, model: str = OPENAI_TEXT_MODEL) -> dict:
    """POST {openai}/chat/completions with JSON-object response format."""
    url = f"{cfg.openai_base_url}/chat/completions"
    payload = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": BRIEF_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    data = _http_json("POST", url, _openai_headers(cfg), payload,
                      cfg.timeout, cfg.retries)
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise LoomError(f"unexpected chat.completions shape: {str(data)[:300]}")
    brief = _validate_brief(json.loads(content))
    brief["_provenance"] = {"provider": "openai", "model": model}
    return brief


def gemini_brief(cfg: Config, prompt: str, model: str = GEMINI_TEXT_MODEL) -> dict:
    """POST {gemini}/models/{model}:generateContent with responseMimeType JSON."""
    url = f"{cfg.gemini_base_url}/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": BRIEF_SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }
    data = _http_json("POST", url, _gemini_headers(cfg), payload,
                      cfg.timeout, cfg.retries)
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise LoomError(f"unexpected generateContent shape: {str(data)[:300]}")
    brief = _validate_brief(json.loads(text))
    brief["_provenance"] = {"provider": "gemini", "model": model}
    return brief


# --------------------------------------------------------------------------
# Pipeline 2: images
# --------------------------------------------------------------------------

def openai_images(cfg: Config, prompt: str, out_dir: Path,
                  model: str = OPENAI_IMAGE_MODEL, size: str = "1024x1024",
                  n: int = 1, quality: Optional[str] = None) -> list[Asset]:
    """POST {openai}/images/generations.

    gpt-image-1 always returns base64 (`b64_json`); dall-e-3 needs
    response_format=b64_json requested explicitly and only supports n=1.
    """
    url = f"{cfg.openai_base_url}/images/generations"
    payload: dict[str, Any] = {"model": model, "prompt": prompt,
                               "size": size, "n": n}
    if model.startswith("dall-e"):
        payload["response_format"] = "b64_json"
        payload["n"] = 1
        if quality:
            payload["quality"] = quality  # standard | hd
    elif quality:
        payload["quality"] = quality      # low | medium | high | auto
    data = _http_json("POST", url, _openai_headers(cfg), payload,
                      cfg.timeout, cfg.retries)
    assets = []
    for i, item in enumerate(data.get("data", [])):
        if item.get("b64_json"):
            blob = base64.b64decode(item["b64_json"])
        elif item.get("url"):
            blob = _http("GET", item["url"], timeout=cfg.timeout)
        else:
            raise LoomError(f"image item without b64_json or url: {item}")
        path = out_dir / f"image_{_slug(prompt)}_{_stamp()}_{i}.png"
        path.write_bytes(blob)
        asset = Asset("image", str(path), "image/png", "openai", model, prompt,
                      meta={"size": size, "quality": quality,
                            "revised_prompt": item.get("revised_prompt")})
        asset.write_sidecar()
        assets.append(asset)
    if not assets:
        raise LoomError(f"images/generations returned no data: {str(data)[:300]}")
    return assets


def gemini_images(cfg: Config, prompt: str, out_dir: Path,
                  model: str = GEMINI_IMAGE_MODEL, size: str = "1024x1024",
                  n: int = 1) -> list[Asset]:
    """POST {gemini}/models/{model}:generateContent with IMAGE modality.

    Nano Banana models return one image per call as inlineData parts, so n>1
    loops requests. Size is mapped to the closest supported aspectRatio.
    """
    url = f"{cfg.gemini_base_url}/models/{model}:generateContent"
    width, height = _parse_size(size)
    aspect = _closest_aspect(width, height)
    assets: list[Asset] = []
    for i in range(max(n, 1)):
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseModalities": ["IMAGE"],
                "imageConfig": {"aspectRatio": aspect},
            },
        }
        data = _http_json("POST", url, _gemini_headers(cfg), payload,
                          cfg.timeout, cfg.retries)
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        inline = [p["inlineData"] for p in parts if "inlineData" in p]
        if not inline:
            raise LoomError(f"no inlineData image in response: {str(data)[:300]}")
        for j, item in enumerate(inline):
            mime = item.get("mimeType", "image/png")
            ext = "png" if mime.endswith("png") else mime.split("/")[-1]
            path = out_dir / f"image_{_slug(prompt)}_{_stamp()}_{i}{j}.{ext}"
            path.write_bytes(base64.b64decode(item["data"]))
            asset = Asset("image", str(path), mime, "gemini", model, prompt,
                          meta={"aspect_ratio": aspect, "requested_size": size})
            asset.write_sidecar()
            assets.append(asset)
    return assets


def gemini_imagen_images(cfg: Config, prompt: str, out_dir: Path,
                         model: str = GEMINI_IMAGEN_MODEL,
                         n: int = 1, aspect_ratio: str = "1:1") -> list[Asset]:
    """LEGACY — POST {gemini}/models/{model}:predict (Imagen).

    Imagen models on the Gemini API were shut down 2026-08-17. This adapter
    is retained because the same :predict request shape still applies on
    Vertex AI; expect a 4xx if called against generativelanguage.googleapis.com.
    """
    url = f"{cfg.gemini_base_url}/models/{model}:predict"
    payload = {"instances": [{"prompt": prompt}],
               "parameters": {"sampleCount": max(1, min(n, 4)),
                              "aspectRatio": aspect_ratio}}
    data = _http_json("POST", url, _gemini_headers(cfg), payload,
                      cfg.timeout, cfg.retries)
    assets = []
    for i, pred in enumerate(data.get("predictions", [])):
        blob = base64.b64decode(pred["bytesBase64Encoded"])
        path = out_dir / f"image_{_slug(prompt)}_{_stamp()}_{i}.png"
        path.write_bytes(blob)
        asset = Asset("image", str(path), pred.get("mimeType", "image/png"),
                      "gemini", model, prompt, meta={"aspect_ratio": aspect_ratio,
                                                     "legacy": True})
        asset.write_sidecar()
        assets.append(asset)
    if not assets:
        raise LoomError(f"imagen :predict returned no predictions: {str(data)[:300]}")
    return assets


def demo_images(prompt: str, out_dir: Path, size: str = "1024x1024",
                n: int = 1, fmt: str = "both") -> list[Asset]:
    """Keyless placeholders. fmt: svg | png | both."""
    width, height = _parse_size(size)
    assets = []
    for i in range(max(n, 1)):
        seed = prompt if n == 1 else f"{prompt} [{i}]"
        base = out_dir / f"image_{_slug(prompt)}_{_stamp()}_{i}"
        if fmt in ("svg", "both"):
            path = base.with_suffix(".svg")
            render_placeholder_svg(path, seed, width, height)
            asset = Asset("image", str(path), "image/svg+xml", "demo",
                          "loom-placeholder-svg", prompt, meta={"size": size})
            asset.write_sidecar()
            assets.append(asset)
        if fmt in ("png", "both"):
            png_w = min(width, 1024)
            png_h = max(int(png_w * height / width), 1)
            path = base.with_suffix(".png")
            render_placeholder_png(path, seed, png_w, png_h)
            asset = Asset("image", str(path), "image/png", "demo",
                          "loom-placeholder-png", prompt,
                          meta={"size": f"{png_w}x{png_h}", "requested_size": size})
            asset.write_sidecar()
            assets.append(asset)
    return assets


# --------------------------------------------------------------------------
# Pipeline 3: speech / TTS
# --------------------------------------------------------------------------

def openai_speech(cfg: Config, text: str, out_dir: Path,
                  model: str = OPENAI_TTS_MODEL, voice: str = "alloy",
                  audio_format: str = "mp3",
                  instructions: Optional[str] = None) -> Asset:
    """POST {openai}/audio/speech — returns the audio bytes directly."""
    url = f"{cfg.openai_base_url}/audio/speech"
    payload: dict[str, Any] = {"model": model, "input": text, "voice": voice,
                               "response_format": audio_format}
    if instructions and model == "gpt-4o-mini-tts":
        payload["instructions"] = instructions
    headers = dict(_openai_headers(cfg))
    headers["Content-Type"] = "application/json"
    blob = _http("POST", url, headers, json.dumps(payload).encode("utf-8"),
                 cfg.timeout, cfg.retries)
    path = out_dir / f"speech_{_slug(text)}_{_stamp()}.{audio_format}"
    path.write_bytes(blob)
    mime = {"mp3": "audio/mpeg", "wav": "audio/wav", "opus": "audio/ogg",
            "aac": "audio/aac", "flac": "audio/flac",
            "pcm": "audio/L16"}.get(audio_format, "application/octet-stream")
    asset = Asset("speech", str(path), mime, "openai", model, text,
                  meta={"voice": voice, "format": audio_format})
    asset.write_sidecar()
    return asset


def gemini_speech(cfg: Config, text: str, out_dir: Path,
                  model: str = GEMINI_TTS_MODEL, voice: str = "Kore") -> Asset:
    """POST {gemini}/models/{model}:generateContent with AUDIO modality.

    Gemini TTS returns raw 24 kHz s16le mono PCM base64-encoded; we wrap it
    in a WAV container with the stdlib `wave` module.
    """
    url = f"{cfg.gemini_base_url}/models/{model}:generateContent"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {
                "prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    data = _http_json("POST", url, _gemini_headers(cfg), payload,
                      cfg.timeout, cfg.retries)
    parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
    inline = next((p["inlineData"] for p in parts if "inlineData" in p), None)
    if not inline:
        raise LoomError(f"no audio inlineData in response: {str(data)[:300]}")
    pcm = base64.b64decode(inline["data"])
    rate = GEMINI_PCM_RATE
    match = re.search(r"rate=(\d+)", inline.get("mimeType", ""))
    if match:
        rate = int(match.group(1))
    path = out_dir / f"speech_{_slug(text)}_{_stamp()}.wav"
    pcm_to_wav(path, pcm, rate=rate)
    asset = Asset("speech", str(path), "audio/wav", "gemini", model, text,
                  meta={"voice": voice, "pcm_rate": rate,
                        "source_mime": inline.get("mimeType")})
    asset.write_sidecar()
    return asset


def demo_speech(text: str, out_dir: Path, seconds: float = 2.4) -> Asset:
    """Keyless audio placeholder — a seeded chime, not synthesized speech."""
    path = out_dir / f"speech_{_slug(text)}_{_stamp()}.wav"
    render_chime_wav(path, text, seconds=seconds)
    asset = Asset("speech", str(path), "audio/wav", "demo", "loom-chime", text,
                  meta={"seconds": seconds,
                        "note": "placeholder chime; real speech requires a key"})
    asset.write_sidecar()
    return asset


# --------------------------------------------------------------------------
# Pipeline 4: video — stub interface + optional official adapters
# --------------------------------------------------------------------------

class VideoPipeline:
    """Job-shaped stub interface every video backend implements.

    submit() starts a render and returns a VideoJob; poll() refreshes its
    status; download() writes the finished file. generate() is the blocking
    convenience wrapper. UIs should persist VideoJob.to_dict() and poll.
    """

    provider = "stub"

    def submit(self, prompt: str, **options: Any) -> VideoJob:
        raise NotImplementedError

    def poll(self, job: VideoJob) -> VideoJob:
        raise NotImplementedError

    def download(self, job: VideoJob, out_dir: Path) -> Asset:
        raise NotImplementedError

    def generate(self, prompt: str, out_dir: Path, poll_interval: float = 10.0,
                 timeout: float = 900.0, **options: Any) -> Asset:
        job = self.submit(prompt, **options)
        deadline = time.monotonic() + timeout
        while job.status not in ("completed", "failed"):
            if time.monotonic() > deadline:
                raise LoomError(f"video job {job.job_id} timed out after {timeout}s")
            time.sleep(poll_interval)
            job = self.poll(job)
        if job.status == "failed":
            raise LoomError(f"video job {job.job_id} failed: {job.meta.get('error')}")
        return self.download(job, out_dir)


class DemoVideo(VideoPipeline):
    """Keyless backend: emits an animated SVG that completes instantly."""

    provider = "demo"

    def submit(self, prompt: str, **options: Any) -> VideoJob:
        return VideoJob("demo", "loom-animated-svg", prompt,
                        job_id=f"demo-{_digest(prompt).hex()[:12]}",
                        status="completed",
                        meta={"size": options.get("size", "1280x720"),
                              "seconds": float(options.get("seconds", 8))})

    def poll(self, job: VideoJob) -> VideoJob:
        return job

    def download(self, job: VideoJob, out_dir: Path) -> Asset:
        width, height = _parse_size(job.meta.get("size", "1280x720"))
        path = out_dir / f"video_{_slug(job.prompt)}_{_stamp()}.svg"
        render_placeholder_svg(path, job.prompt, width, height, animated=True,
                               label="LOOM DEMO VIDEO (animated SVG)",
                               duration=job.meta.get("seconds", 8.0))
        asset = Asset("video", str(path), "image/svg+xml", "demo",
                      job.model, job.prompt, meta=job.meta)
        asset.write_sidecar()
        return asset


class SoraVideo(VideoPipeline):
    """DEPRECATED official backend — OpenAI Videos API (Sora 2).

    Deprecated 2026-03-24; scheduled for removal 2026-09-24 with no announced
    replacement. Kept as a documented adapter for teams still inside the
    migration window. Endpoints:
      POST {openai}/videos                    -> job {id, status}
      GET  {openai}/videos/{id}               -> job status
      GET  {openai}/videos/{id}/content       -> MP4 bytes
    """

    provider = "openai"

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def submit(self, prompt: str, **options: Any) -> VideoJob:
        sys.stderr.write("loom: warning: the Sora 2 Videos API is deprecated "
                         "(removal scheduled 2026-09-24)\n")
        payload = {"model": options.get("model", OPENAI_VIDEO_MODEL),
                   "prompt": prompt,
                   "size": options.get("size", "1280x720"),
                   "seconds": str(options.get("seconds", "4"))}
        data = _http_json("POST", f"{self.cfg.openai_base_url}/videos",
                          _openai_headers(self.cfg), payload,
                          self.cfg.timeout, self.cfg.retries)
        return VideoJob("openai", payload["model"], prompt,
                        job_id=data["id"], status=data.get("status", "queued"),
                        meta={"size": payload["size"], "seconds": payload["seconds"]})

    def poll(self, job: VideoJob) -> VideoJob:
        data = _http_json("GET", f"{self.cfg.openai_base_url}/videos/{job.job_id}",
                          _openai_headers(self.cfg), None,
                          self.cfg.timeout, self.cfg.retries)
        job.status = data.get("status", job.status)
        job.meta["progress"] = data.get("progress")
        if data.get("error"):
            job.meta["error"] = data["error"]
        return job

    def download(self, job: VideoJob, out_dir: Path) -> Asset:
        blob = _http("GET",
                     f"{self.cfg.openai_base_url}/videos/{job.job_id}/content",
                     _openai_headers(self.cfg), timeout=self.cfg.timeout)
        path = out_dir / f"video_{_slug(job.prompt)}_{_stamp()}.mp4"
        path.write_bytes(blob)
        asset = Asset("video", str(path), "video/mp4", "openai", job.model,
                      job.prompt, meta=job.meta)
        asset.write_sidecar()
        return asset


class VeoVideo(VideoPipeline):
    """Official backend — Google Veo on the Gemini API (long-running op).

    Endpoints:
      POST {gemini}/models/{model}:predictLongRunning -> {"name": operation}
      GET  {gemini}/{operation}                       -> {done, response|error}
    The finished operation carries a download URI (fetched with the API key
    header) or, on some surfaces, inline base64 video bytes.
    """

    provider = "gemini"

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def submit(self, prompt: str, **options: Any) -> VideoJob:
        model = options.get("model", GEMINI_VIDEO_MODEL)
        parameters: dict[str, Any] = {}
        if options.get("aspect_ratio"):
            parameters["aspectRatio"] = options["aspect_ratio"]
        if options.get("negative_prompt"):
            parameters["negativePrompt"] = options["negative_prompt"]
        payload: dict[str, Any] = {"instances": [{"prompt": prompt}]}
        if parameters:
            payload["parameters"] = parameters
        data = _http_json("POST",
                          f"{self.cfg.gemini_base_url}/models/{model}:predictLongRunning",
                          _gemini_headers(self.cfg), payload,
                          self.cfg.timeout, self.cfg.retries)
        return VideoJob("gemini", model, prompt, job_id=data["name"],
                        status="in_progress", meta={})

    def poll(self, job: VideoJob) -> VideoJob:
        data = _http_json("GET", f"{self.cfg.gemini_base_url}/{job.job_id}",
                          _gemini_headers(self.cfg), None,
                          self.cfg.timeout, self.cfg.retries)
        if data.get("error"):
            job.status = "failed"
            job.meta["error"] = data["error"]
        elif data.get("done"):
            job.status = "completed"
            job.meta["response"] = data.get("response", {})
        return job

    def download(self, job: VideoJob, out_dir: Path) -> Asset:
        response = job.meta.get("response", {})
        samples = (response.get("generateVideoResponse", {})
                   .get("generatedSamples", []))
        if not samples:  # alternate response shape
            samples = response.get("generatedVideos", [])
        if not samples:
            raise LoomError(f"no video samples in operation: {str(response)[:300]}")
        video = samples[0].get("video", samples[0])
        path = out_dir / f"video_{_slug(job.prompt)}_{_stamp()}.mp4"
        if video.get("uri"):
            blob = _http("GET", video["uri"], _gemini_headers(self.cfg),
                         timeout=max(self.cfg.timeout, 300))
        elif video.get("bytesBase64Encoded"):
            blob = base64.b64decode(video["bytesBase64Encoded"])
        else:
            raise LoomError(f"video sample without uri or bytes: {str(video)[:300]}")
        path.write_bytes(blob)
        asset = Asset("video", str(path), "video/mp4", "gemini", job.model,
                      job.prompt, meta={k: v for k, v in job.meta.items()
                                        if k != "response"})
        asset.write_sidecar()
        return asset


# --------------------------------------------------------------------------
# Facade with provider routing
# --------------------------------------------------------------------------

class Loom:
    """Facade over all pipelines with auto provider routing.

    Routing for images/briefs/speech: explicit argument > LOOM_PROVIDER env >
    first configured key (OpenAI, then Gemini) > demo. Video never auto-routes
    to a paid backend: it defaults to demo unless a provider is named.
    """

    def __init__(self, config: Optional[Config] = None):
        self.cfg = config or Config.from_env()

    def resolve(self, provider: Optional[str] = None) -> str:
        choice = (provider or "auto").lower()
        if choice == "auto":
            choice = self.cfg.default_provider or "auto"
        if choice == "auto":
            if self.cfg.openai_api_key:
                choice = "openai"
            elif self.cfg.gemini_api_key:
                choice = "gemini"
            else:
                choice = "demo"
        if choice not in ("openai", "gemini", "demo"):
            raise LoomError(f"unknown provider {choice!r}")
        return choice

    # -- briefs -------------------------------------------------------------
    def brief(self, prompt: str, provider: Optional[str] = None,
              model: Optional[str] = None) -> dict:
        chosen = self.resolve(provider)
        if chosen == "openai":
            return openai_brief(self.cfg, prompt, model or OPENAI_TEXT_MODEL)
        if chosen == "gemini":
            return gemini_brief(self.cfg, prompt, model or GEMINI_TEXT_MODEL)
        return demo_brief(prompt)

    # -- images -------------------------------------------------------------
    def image(self, prompt: str, out_dir: Path, provider: Optional[str] = None,
              model: Optional[str] = None, size: str = "1024x1024", n: int = 1,
              quality: Optional[str] = None, demo_format: str = "both") -> list[Asset]:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        chosen = self.resolve(provider)
        if chosen == "openai":
            return openai_images(self.cfg, prompt, out_dir,
                                 model or OPENAI_IMAGE_MODEL, size, n, quality)
        if chosen == "gemini":
            if model and model.startswith("imagen"):
                width, height = _parse_size(size)
                return gemini_imagen_images(self.cfg, prompt, out_dir, model,
                                            n, _closest_aspect(width, height))
            return gemini_images(self.cfg, prompt, out_dir,
                                 model or GEMINI_IMAGE_MODEL, size, n)
        return demo_images(prompt, out_dir, size, n, demo_format)

    # -- speech -------------------------------------------------------------
    def speech(self, text: str, out_dir: Path, provider: Optional[str] = None,
               model: Optional[str] = None, voice: Optional[str] = None,
               audio_format: str = "mp3") -> Asset:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        chosen = self.resolve(provider)
        if chosen == "openai":
            return openai_speech(self.cfg, text, out_dir,
                                 model or OPENAI_TTS_MODEL,
                                 voice or "alloy", audio_format)
        if chosen == "gemini":
            return gemini_speech(self.cfg, text, out_dir,
                                 model or GEMINI_TTS_MODEL, voice or "Kore")
        return demo_speech(text, out_dir)

    # -- video --------------------------------------------------------------
    def video_pipeline(self, provider: Optional[str] = None) -> VideoPipeline:
        chosen = (provider or "demo").lower()
        if chosen in ("auto", "demo"):
            return DemoVideo()
        if chosen in ("openai", "sora"):
            return SoraVideo(self.cfg)
        if chosen in ("gemini", "veo"):
            return VeoVideo(self.cfg)
        raise LoomError(f"unknown video provider {chosen!r}")

    def video(self, prompt: str, out_dir: Path, provider: Optional[str] = None,
              **options: Any) -> Asset:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        return self.video_pipeline(provider).generate(prompt, out_dir, **options)


# --------------------------------------------------------------------------
# Self-test (demo mode end-to-end; no network, no keys)
# --------------------------------------------------------------------------

def selftest(out_dir: Path) -> int:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    loom = Loom(Config())  # empty config forces demo routing
    failures: list[str] = []

    brief = loom.brief("a night market food festival")
    if not all(k in brief for k in BRIEF_KEYS):
        failures.append("brief missing keys")
    (out_dir / "selftest_brief.json").write_text(json.dumps(brief, indent=2))

    images = loom.image("a night market food festival", out_dir,
                        size="640x400", n=1)
    for asset in images:
        blob = Path(asset.path).read_bytes()
        if asset.mime == "image/png" and not blob.startswith(b"\x89PNG\r\n\x1a\n"):
            failures.append(f"bad PNG signature: {asset.path}")
        if asset.mime == "image/svg+xml" and b"<svg" not in blob:
            failures.append(f"bad SVG: {asset.path}")

    speech = loom.speech("welcome to the night market", out_dir)
    with wave.open(speech.path, "rb") as wav:
        if wav.getnframes() <= 0 or wav.getframerate() != GEMINI_PCM_RATE:
            failures.append("bad WAV output")

    video = loom.video("lanterns swaying over the market", out_dir,
                       size="640x360", seconds=6)
    if b"animateTransform" not in Path(video.path).read_bytes():
        failures.append("demo video is not animated")

    render_identicon_png(out_dir / "selftest_avatar.png", "atelier")
    render_swatch_png(out_dir / "selftest_swatch.png",
                      [s["hex"] for s in _seed_palette(_digest("atelier"))["swatches"]])

    determinism = demo_brief("same seed") == demo_brief("same seed")
    if not determinism:
        failures.append("demo brief is not deterministic")

    if failures:
        print("SELFTEST FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    produced = sorted(str(p.relative_to(out_dir)) for p in out_dir.rglob("*")
                      if p.is_file())
    print(f"SELFTEST OK — {len(produced)} files in {out_dir}")
    for name in produced:
        print(f"  {name}")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_assets(assets: list[Asset]) -> None:
    print(json.dumps([a.to_dict() for a in assets], indent=2))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="loom", description="Atelier media generation pipelines (BYOK + demo mode)")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    default_out = os.environ.get("LOOM_OUT", "loom-out")

    p_img = sub.add_parser("image", help="generate image(s)")
    p_img.add_argument("prompt")
    p_img.add_argument("--provider", default="auto",
                       choices=["auto", "openai", "gemini", "demo"])
    p_img.add_argument("--model", default=None,
                       help="e.g. gpt-image-1, dall-e-3, gemini-2.5-flash-image")
    p_img.add_argument("--size", default="1024x1024")
    p_img.add_argument("--n", type=int, default=1)
    p_img.add_argument("--quality", default=None,
                       help="gpt-image-1: low|medium|high|auto; dall-e-3: standard|hd")
    p_img.add_argument("--demo-format", default="both", choices=["svg", "png", "both"])
    p_img.add_argument("--out", default=default_out)

    p_brief = sub.add_parser("brief", help="expand text into a design brief (JSON)")
    p_brief.add_argument("prompt")
    p_brief.add_argument("--provider", default="auto",
                         choices=["auto", "openai", "gemini", "demo"])
    p_brief.add_argument("--model", default=None)
    p_brief.add_argument("--out", default="-", help="output file or - for stdout")

    p_speech = sub.add_parser("speech", help="text-to-speech")
    p_speech.add_argument("text")
    p_speech.add_argument("--provider", default="auto",
                          choices=["auto", "openai", "gemini", "demo"])
    p_speech.add_argument("--model", default=None)
    p_speech.add_argument("--voice", default=None,
                          help="openai: alloy/echo/nova/...; gemini: Kore/Puck/...")
    p_speech.add_argument("--format", dest="audio_format", default="mp3",
                          help="openai only: mp3|wav|opus|aac|flac|pcm")
    p_speech.add_argument("--out", default=default_out)

    p_video = sub.add_parser("video", help="video generation (default: demo stub)")
    p_video.add_argument("prompt")
    p_video.add_argument("--provider", default="demo",
                         choices=["demo", "openai", "sora", "gemini", "veo"])
    p_video.add_argument("--model", default=None)
    p_video.add_argument("--size", default="1280x720")
    p_video.add_argument("--seconds", default="4")
    p_video.add_argument("--aspect-ratio", default=None, help="veo only, e.g. 16:9")
    p_video.add_argument("--timeout", type=float, default=900.0)
    p_video.add_argument("--out", default=default_out)

    p_kit = sub.add_parser("demo-kit", help="build a full keyless asset kit for UI dev")
    p_kit.add_argument("--prompt", default="Atelier — a studio for generative design")
    p_kit.add_argument("--out", default="demo_assets_out")
    p_kit.add_argument("--png-size", type=int, default=640)

    p_test = sub.add_parser("selftest", help="run demo-mode pipelines end to end")
    p_test.add_argument("--out", default="selftest-out")

    args = parser.parse_args(argv)
    loom = Loom()

    try:
        if args.command == "image":
            assets = loom.image(args.prompt, Path(args.out), args.provider,
                                args.model, args.size, args.n, args.quality,
                                args.demo_format)
            _print_assets(assets)
        elif args.command == "brief":
            brief = loom.brief(args.prompt, args.provider, args.model)
            text = json.dumps(brief, indent=2)
            if args.out == "-":
                print(text)
            else:
                Path(args.out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.out).write_text(text, encoding="utf-8")
                print(f"wrote {args.out}")
        elif args.command == "speech":
            asset = loom.speech(args.text, Path(args.out), args.provider,
                                args.model, args.voice, args.audio_format)
            _print_assets([asset])
        elif args.command == "video":
            options: dict[str, Any] = {"size": args.size, "seconds": args.seconds,
                                       "timeout": args.timeout}
            if args.model:
                options["model"] = args.model
            if args.aspect_ratio:
                options["aspect_ratio"] = args.aspect_ratio
            asset = loom.video(args.prompt, Path(args.out), args.provider, **options)
            _print_assets([asset])
        elif args.command == "demo-kit":
            import demo_assets
            manifest = demo_assets.build_kit(Path(args.out), prompt=args.prompt,
                                             png_size=args.png_size)
            print(json.dumps({"out": str(args.out),
                              "assets": len(manifest["assets"])}, indent=2))
        elif args.command == "selftest":
            return selftest(Path(args.out))
    except MissingKeyError as err:
        print(f"loom: missing key: {err}", file=sys.stderr)
        return 2
    except LoomError as err:
        print(f"loom: error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
