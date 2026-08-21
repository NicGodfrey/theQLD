#!/usr/bin/env python3
"""OPTIONAL live smoke test — spends a tiny amount of the user's own quota.

This is deliberately NOT part of the unit suite. It refuses to run unless
ATELIER_LIVE=1 is set, so it can never fire from CI by accident.

Usage:
    ATELIER_LIVE=1 python live_smoke.py openai            # ~$0.0001
    ATELIER_LIVE=1 python live_smoke.py gemini            # ~$0.0001
    ATELIER_LIVE=1 python live_smoke.py anthropic         # ~$0.001
    ATELIER_LIVE=1 python live_smoke.py ollama            # free, local
    ATELIER_LIVE=1 python live_smoke.py openai --image    # ~$0.01-0.04

Keys come from the keyring / env vars as usual. Results (and the ledger
row each call produced) are printed.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gateway import Gateway               # noqa: E402
from spokes_base import ChatMessage       # noqa: E402

CHEAP_CHAT_MODEL = {
    "openai": "gpt-4o-mini",
    "gemini": "gemini-2.5-flash-lite",
    "anthropic": "claude-3-5-haiku-latest",
    "ollama": None,             # spoke default
    "openai_compatible": None,
}


def main(argv):
    if os.environ.get("ATELIER_LIVE") != "1":
        print("refusing to spend quota: set ATELIER_LIVE=1 to run "
              "(see TESTS.md)", file=sys.stderr)
        return 2
    if not argv or argv[0].startswith("-"):
        print(__doc__, file=sys.stderr)
        return 2
    provider = argv[0]
    want_image = "--image" in argv[1:]

    gateway = Gateway()
    if want_image:
        result = gateway.generate_image(
            provider, "a single red apple on a wooden table, oil sketch",
            size="1024x1024", quality="low" if provider == "openai" else None)
        out_path = os.path.join(HERE, f"smoke_{provider}.png")
        with open(out_path, "wb") as fh:
            fh.write(result.images[0])
        print(f"image -> {out_path}  model={result.model} "
              f"est_usd={result.usage.est_usd}")
    else:
        result = gateway.chat(
            provider,
            [ChatMessage("user", "Reply with exactly: OK")],
            model=CHEAP_CHAT_MODEL.get(provider), max_tokens=16)
        print(f"chat -> {result.text!r}  model={result.model} "
              f"tokens={result.usage.input_tokens}/"
              f"{result.usage.output_tokens} est_usd={result.usage.est_usd}")

    print("\nledger summary:")
    for prov, agg in gateway.usage_summary().items():
        print(f"  {prov}: {agg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
