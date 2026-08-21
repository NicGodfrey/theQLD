#!/usr/bin/env python3
"""demo_assets.py — build a complete keyless asset kit for Atelier UI work.

Composes loom's demo-mode generators into one coherent bundle derived from a
single prompt, so every asset (brief, heroes, swatches, avatars, audio,
video placeholder) shares a palette and mood. Everything is deterministic
for a given prompt: rebuilding the kit yields byte-identical SVG/PNG/WAV
files, which keeps UI snapshot tests stable.

Output layout (under --out, default ./demo_assets_out):

  manifest.json                 index of every asset (path, mime, bytes, meta)
  brief.json                    deterministic design brief
  images/hero_16x9.{svg,png}    plus 1x1 and 9x16 variants
  images/shot_N.{svg,png}       one per brief image_prompt
  palette/swatches.png          five-band palette strip
  palette/swatch_<role>.png     one flat chip per palette role
  avatars/avatar_N.png          identicon placeholders
  audio/voiceover.wav           seeded chime standing in for TTS
  video/teaser.svg              animated SVG standing in for MP4

Usage:
  python demo_assets.py [--prompt "..."] [--out DIR] [--png-size 640]
  python loom.py demo-kit [--prompt "..."] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import loom


HERO_VARIANTS = [("hero_16x9", 1280, 720), ("hero_1x1", 1080, 1080),
                 ("hero_9x16", 720, 1280)]


def _record(manifest: list, kit_dir: Path, path: Path, kind: str,
            mime: str, **meta) -> None:
    manifest.append({
        "path": str(path.relative_to(kit_dir)),
        "kind": kind,
        "mime": mime,
        "bytes": path.stat().st_size,
        "meta": meta,
    })


def build_kit(out_dir: Path, prompt: str = "Atelier — a studio for generative design",
              png_size: int = 640, avatars: int = 4) -> dict:
    """Build the kit and return the manifest dict (also written to disk)."""
    kit_dir = Path(out_dir)
    for sub in ("images", "palette", "avatars", "audio", "video"):
        (kit_dir / sub).mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    brief = loom.demo_brief(prompt)
    brief_path = kit_dir / "brief.json"
    brief_path.write_text(json.dumps(brief, indent=2), encoding="utf-8")
    _record(manifest, kit_dir, brief_path, "brief", "application/json",
            provider="demo")

    # Hero images in the three standard aspect ratios (SVG full-size,
    # PNG capped at png_size on the long edge to keep generation fast).
    for name, width, height in HERO_VARIANTS:
        svg_path = kit_dir / "images" / f"{name}.svg"
        loom.render_placeholder_svg(svg_path, prompt, width, height,
                                    label=f"LOOM DEMO {width}x{height}")
        _record(manifest, kit_dir, svg_path, "image", "image/svg+xml",
                size=f"{width}x{height}")
        scale = png_size / max(width, height)
        png_w, png_h = max(int(width * scale), 1), max(int(height * scale), 1)
        png_path = kit_dir / "images" / f"{name}.png"
        loom.render_placeholder_png(png_path, prompt, png_w, png_h)
        _record(manifest, kit_dir, png_path, "image", "image/png",
                size=f"{png_w}x{png_h}", represents=f"{width}x{height}")

    # One shot per brief image_prompt, seeded by that prompt so each differs.
    for i, shot_prompt in enumerate(brief["image_prompts"]):
        svg_path = kit_dir / "images" / f"shot_{i}.svg"
        loom.render_placeholder_svg(svg_path, shot_prompt, 960, 640)
        _record(manifest, kit_dir, svg_path, "image", "image/svg+xml",
                size="960x640", prompt=shot_prompt)
        png_path = kit_dir / "images" / f"shot_{i}.png"
        loom.render_placeholder_png(png_path, shot_prompt, png_size,
                                    png_size * 2 // 3)
        _record(manifest, kit_dir, png_path, "image", "image/png",
                size=f"{png_size}x{png_size * 2 // 3}", prompt=shot_prompt)

    # Palette: one strip plus a flat chip per role.
    hexes = [entry["hex"] for entry in brief["palette"]]
    strip_path = kit_dir / "palette" / "swatches.png"
    loom.render_swatch_png(strip_path, hexes)
    _record(manifest, kit_dir, strip_path, "palette", "image/png", colors=hexes)
    for entry in brief["palette"]:
        chip_path = kit_dir / "palette" / f"swatch_{entry['role']}.png"
        loom.render_swatch_png(chip_path, [entry["hex"]], width=120, height=120)
        _record(manifest, kit_dir, chip_path, "palette", "image/png",
                role=entry["role"], color=entry["hex"])

    for i in range(avatars):
        avatar_path = kit_dir / "avatars" / f"avatar_{i}.png"
        loom.render_identicon_png(avatar_path, f"{prompt} avatar {i}")
        _record(manifest, kit_dir, avatar_path, "avatar", "image/png",
                size="160x160")

    audio_path = kit_dir / "audio" / "voiceover.wav"
    loom.render_chime_wav(audio_path, brief["voice_script"])
    _record(manifest, kit_dir, audio_path, "speech", "audio/wav",
            script=brief["voice_script"],
            note="placeholder chime; swap for real TTS when a key is present")

    video_path = kit_dir / "video" / "teaser.svg"
    loom.render_placeholder_svg(video_path, brief["motion_prompt"], 1280, 720,
                                animated=True, label="LOOM DEMO VIDEO",
                                duration=8.0)
    _record(manifest, kit_dir, video_path, "video", "image/svg+xml",
            prompt=brief["motion_prompt"],
            note="animated SVG placeholder; swap for MP4 from Veo/Sora")

    manifest_doc = {
        "kit": "loom-demo-assets",
        "version": loom.__version__,
        "prompt": prompt,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "deterministic": True,
        "assets": manifest,
    }
    (kit_dir / "manifest.json").write_text(json.dumps(manifest_doc, indent=2),
                                           encoding="utf-8")
    return manifest_doc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="demo_assets",
        description="generate a keyless placeholder asset kit for Atelier UI dev")
    parser.add_argument("--prompt",
                        default="Atelier — a studio for generative design")
    parser.add_argument("--out", default="demo_assets_out")
    parser.add_argument("--png-size", type=int, default=640,
                        help="long edge of PNG renders (default 640)")
    parser.add_argument("--avatars", type=int, default=4)
    args = parser.parse_args(argv)

    manifest = build_kit(Path(args.out), prompt=args.prompt,
                         png_size=args.png_size, avatars=args.avatars)
    total = sum(asset["bytes"] for asset in manifest["assets"])
    print(f"demo kit: {len(manifest['assets'])} assets, "
          f"{total / 1024:.0f} KiB -> {args.out}")
    for asset in manifest["assets"]:
        print(f"  [{asset['kind']:>7}] {asset['path']} ({asset['bytes']} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
