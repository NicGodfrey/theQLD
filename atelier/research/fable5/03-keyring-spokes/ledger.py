"""Per-provider usage ledger for Atelier.

Every spoke call appends one JSON line to ``~/.atelier/ledger.jsonl``
(created 0600). Records carry raw counters (tokens, images) plus an
estimated USD cost.

Pricing is ESTIMATION ONLY: providers change prices, and cached/batch
discounts are not modeled. Defaults below were snapshotted around
PRICES_SNAPSHOT; override any of them by dropping a
``~/.atelier/prices.json`` file (format documented at the bottom) or by
passing ``price_overrides=`` to the Ledger. Unknown models are recorded
with ``priced: false`` and est_usd 0.0 — the ledger never invents a price.

Stdlib only. Python 3.9+.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Optional, Tuple, Union

__all__ = ["Ledger", "UsageRecord", "DEFAULT_LEDGER_PATH",
           "PRICE_OVERRIDE_PATH", "PRICES_SNAPSHOT"]

DEFAULT_LEDGER_PATH = os.path.join(os.path.expanduser("~"), ".atelier", "ledger.jsonl")
PRICE_OVERRIDE_PATH = os.path.join(os.path.expanduser("~"), ".atelier", "prices.json")

PRICES_SNAPSHOT = "2026-08"

# USD per 1M tokens: "provider:model-prefix" -> (input, output).
# Longest matching prefix wins, so "openai:gpt-4o-mini" beats "openai:gpt-4o".
CHAT_PRICES_PER_MTOK: Dict[str, Tuple[float, float]] = {
    "openai:gpt-5-nano": (0.05, 0.40),
    "openai:gpt-5-mini": (0.25, 2.00),
    "openai:gpt-5": (1.25, 10.00),
    "openai:gpt-4.1-nano": (0.10, 0.40),
    "openai:gpt-4.1-mini": (0.40, 1.60),
    "openai:gpt-4.1": (2.00, 8.00),
    "openai:gpt-4o-mini": (0.15, 0.60),
    "openai:gpt-4o": (2.50, 10.00),
    "openai:o3": (2.00, 8.00),
    "openai:o4-mini": (1.10, 4.40),
    "gemini:gemini-2.5-pro": (1.25, 10.00),
    "gemini:gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini:gemini-2.5-flash": (0.30, 2.50),
    "gemini:gemini-2.0-flash": (0.10, 0.40),
    "anthropic:claude-opus-4": (15.00, 75.00),
    "anthropic:claude-sonnet-4": (3.00, 15.00),
    "anthropic:claude-3-5-haiku": (0.80, 4.00),
    # Local inference is free; the bare prefix matches every ollama model.
    "ollama:": (0.0, 0.0),
}

# USD per generated image: "provider:model-prefix" -> flat price, or a dict
# keyed "WIDTHxHEIGHT|quality" with "*" as the fallback.
IMAGE_PRICES_PER_IMAGE: Dict[str, Union[float, Dict[str, float]]] = {
    "openai:gpt-image-1": {
        "1024x1024|low": 0.011, "1024x1024|medium": 0.042, "1024x1024|high": 0.167,
        "1024x1536|low": 0.016, "1024x1536|medium": 0.063, "1024x1536|high": 0.25,
        "1536x1024|low": 0.016, "1536x1024|medium": 0.063, "1536x1024|high": 0.25,
        "*": 0.042,
    },
    "openai:dall-e-3": {"1024x1024|hd": 0.080, "*": 0.040},
    "gemini:gemini-2.5-flash-image": 0.039,   # 1290 output tokens @ $30/1M
    "gemini:imagen-4.0": 0.04,
    "gemini:imagen-3.0": 0.03,
}


@dataclass
class UsageRecord:
    """One ledger row. Serialized as a single JSON line."""
    ts: float
    provider: str
    model: str
    kind: str                 # "chat" | "image" | "video"
    input_tokens: int
    output_tokens: int
    images: int
    est_usd: float
    priced: bool              # False when no price rule matched
    meta: dict = field(default_factory=dict)


def _longest_prefix(table: Mapping[str, Any], key: str) -> Optional[Any]:
    best_len, best = -1, None
    for prefix, value in table.items():
        if key.startswith(prefix) and len(prefix) > best_len:
            best_len, best = len(prefix), value
    return best


class Ledger:
    """Append-only JSONL usage ledger with USD estimation."""

    def __init__(self, path: Optional[str] = None, *,
                 price_overrides: Optional[Mapping[str, Any]] = None,
                 override_path: Optional[str] = None) -> None:
        self.path = path or DEFAULT_LEDGER_PATH
        self.override_path = (PRICE_OVERRIDE_PATH if override_path is None
                              else override_path)
        self._lock = threading.Lock()
        self._chat: Dict[str, Tuple[float, float]] = dict(CHAT_PRICES_PER_MTOK)
        self._image: Dict[str, Union[float, Dict[str, float]]] = {
            k: (dict(v) if isinstance(v, dict) else v)
            for k, v in IMAGE_PRICES_PER_IMAGE.items()}

        file_overrides: Mapping[str, Any] = {}
        if self.override_path and os.path.exists(self.override_path):
            try:
                with open(self.override_path, encoding="utf-8") as fh:
                    file_overrides = json.load(fh)
            except (OSError, json.JSONDecodeError):
                print(f"[atelier-ledger] ignoring unreadable price override "
                      f"file {self.override_path}", file=sys.stderr)
        for src in (file_overrides, price_overrides or {}):
            self._merge_prices(src)

    def _merge_prices(self, src: Mapping[str, Any]) -> None:
        for key, val in (src.get("chat") or {}).items():
            self._chat[key] = (float(val[0]), float(val[1]))
        for key, val in (src.get("image") or {}).items():
            self._image[key] = (dict(val) if isinstance(val, dict)
                                else float(val))

    # -- estimation ---------------------------------------------------------

    def estimate_usd(self, *, provider: str, model: str, kind: str,
                     input_tokens: int = 0, output_tokens: int = 0,
                     images: int = 0, size: str = "",
                     quality: str = "") -> Tuple[float, bool]:
        """Return (estimated_usd, priced). priced=False means no rule
        matched and the 0.0 is a placeholder, not a claim of free."""
        key = f"{provider}:{model}"
        if kind == "chat":
            price = _longest_prefix(self._chat, key)
            if price is None:
                return 0.0, False
            usd = (input_tokens / 1e6) * price[0] + (output_tokens / 1e6) * price[1]
            return round(usd, 10), True
        if kind == "image":
            price = _longest_prefix(self._image, key)
            if price is None:
                return 0.0, False
            if isinstance(price, dict):
                per: Optional[float] = None
                for k in (f"{size}|{quality or 'auto'}", f"{size}|*", "*"):
                    if k in price:
                        per = float(price[k])
                        break
                if per is None:
                    return 0.0, False
            else:
                per = float(price)
            return round(per * max(0, images), 10), True
        # video: no default price table yet
        return 0.0, False

    # -- recording ----------------------------------------------------------

    def record(self, *, provider: str, model: str, kind: str,
               input_tokens: int = 0, output_tokens: int = 0, images: int = 0,
               size: str = "", quality: str = "",
               meta: Optional[Mapping[str, Any]] = None) -> UsageRecord:
        usd, priced = self.estimate_usd(
            provider=provider, model=model, kind=kind,
            input_tokens=input_tokens, output_tokens=output_tokens,
            images=images, size=size, quality=quality)
        rec = UsageRecord(
            ts=round(time.time(), 3), provider=provider, model=model,
            kind=kind, input_tokens=int(input_tokens),
            output_tokens=int(output_tokens), images=int(images),
            est_usd=usd, priced=priced, meta=dict(meta or {}))
        if size:
            rec.meta.setdefault("size", size)
        if quality:
            rec.meta.setdefault("quality", quality)
        line = json.dumps(asdict(rec), sort_keys=True,
                          separators=(",", ":")) + "\n"
        with self._lock:
            parent = os.path.dirname(self.path)
            if parent:
                os.makedirs(parent, mode=0o700, exist_ok=True)
            # O_APPEND keeps concurrent writers line-atomic on POSIX;
            # 0600 keeps usage history private.
            fd = os.open(self.path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
            try:
                os.write(fd, line.encode("utf-8"))
            finally:
                os.close(fd)
        return rec

    # -- reporting ----------------------------------------------------------

    def summary(self, since: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        """Aggregate the ledger per provider. ``since`` is a unix timestamp."""
        out: Dict[str, Dict[str, Any]] = {}
        if not os.path.exists(self.path):
            return out
        with open(self.path, encoding="utf-8") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if since is not None and rec.get("ts", 0) < since:
                    continue
                prov = rec.get("provider", "?")
                agg = out.setdefault(prov, {
                    "calls": 0, "input_tokens": 0, "output_tokens": 0,
                    "images": 0, "est_usd": 0.0, "unpriced_calls": 0})
                agg["calls"] += 1
                agg["input_tokens"] += int(rec.get("input_tokens") or 0)
                agg["output_tokens"] += int(rec.get("output_tokens") or 0)
                agg["images"] += int(rec.get("images") or 0)
                agg["est_usd"] = round(agg["est_usd"] + float(rec.get("est_usd") or 0.0), 10)
                if not rec.get("priced", False):
                    agg["unpriced_calls"] += 1
        return out


def _main(argv) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Atelier usage ledger (per-provider spend report)")
    parser.add_argument("command", nargs="?", choices=["summary"],
                        default="summary")
    parser.add_argument("--path", default=None, help="ledger file "
                        f"(default: {DEFAULT_LEDGER_PATH})")
    parser.add_argument("--since-hours", type=float, default=None,
                        help="only include records newer than N hours")
    args = parser.parse_args(argv)

    led = Ledger(path=args.path)
    since = None
    if args.since_hours is not None:
        since = time.time() - args.since_hours * 3600
    summary = led.summary(since=since)
    if not summary:
        print("ledger is empty")
        return 0
    header = f"{'provider':<20}{'calls':>7}{'in_tok':>12}{'out_tok':>12}{'images':>8}{'est_usd':>12}{'unpriced':>10}"
    print(header)
    print("-" * len(header))
    for prov in sorted(summary):
        s = summary[prov]
        print(f"{prov:<20}{s['calls']:>7}{s['input_tokens']:>12}"
              f"{s['output_tokens']:>12}{s['images']:>8}"
              f"{s['est_usd']:>12.4f}{s['unpriced_calls']:>10}")
    print("\nnote: est_usd is an estimate from the built-in price table "
          f"(snapshot {PRICES_SNAPSHOT}); override via {PRICE_OVERRIDE_PATH}")
    return 0


# Price override file format (~/.atelier/prices.json):
# {
#   "chat":  {"openai:gpt-6": [2.00, 8.00]},          # USD per 1M in/out tokens
#   "image": {"openai:gpt-image-2": 0.05,             # flat USD per image, or
#             "openai:gpt-image-1": {"1024x1024|high": 0.20, "*": 0.05}}
# }

if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
