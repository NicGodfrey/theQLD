"""Usage ledger + public list-price estimates (USD). Prices dated 2026-08-21."""

from __future__ import annotations

from typing import Optional

# Approximate public list prices. Always verify on the provider billing page.
COST_TABLE = {
    ("openai", "gpt-4.1-mini", "tokens_in"): 0.40 / 1_000_000,
    ("openai", "gpt-4.1-mini", "tokens_out"): 1.60 / 1_000_000,
    ("openai", "gpt-4o-mini", "tokens_in"): 0.15 / 1_000_000,
    ("openai", "gpt-4o-mini", "tokens_out"): 0.60 / 1_000_000,
    ("openai", "dall-e-3", "images"): 0.040,
    ("openai", "gpt-image-1", "images"): 0.040,
    ("gemini", "gemini-2.0-flash", "tokens_in"): 0.10 / 1_000_000,
    ("gemini", "gemini-2.0-flash", "tokens_out"): 0.40 / 1_000_000,
    ("gemini", "gemini-2.5-flash", "tokens_in"): 0.15 / 1_000_000,
    ("gemini", "gemini-2.5-flash", "tokens_out"): 0.60 / 1_000_000,
    ("gemini", "imagen-3.0-generate-002", "images"): 0.030,
    ("ollama", "*", "tokens_in"): 0.0,
    ("demo", "*", "tokens_in"): 0.0,
}


def estimate_usd(provider: str, model: str, unit_kind: str, units: float) -> float:
    exact = COST_TABLE.get((provider, model, unit_kind))
    if exact is not None:
        return round(exact * units, 6)
    wildcard = COST_TABLE.get((provider, "*", unit_kind))
    if wildcard is not None:
        return round(wildcard * units, 6)
    if unit_kind == "images":
        return round(0.04 * units, 6)
    if unit_kind in {"tokens_in", "tokens_out", "tokens"}:
        return round((0.5 / 1_000_000) * units, 6)
    return 0.0


def record(memory, *, provider: str, model: str, unit_kind: str, units: float, thread_id: Optional[str] = None) -> dict:
    return memory.add_usage(
        provider=provider,
        model=model,
        unit_kind=unit_kind,
        units=units,
        estimated_usd=estimate_usd(provider, model, unit_kind, units),
        thread_id=thread_id,
    )
