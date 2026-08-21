"""Usage ledger + public list-price estimates (USD).

Prices dated 2026-08-21 from official OpenAI / Gemini pricing pages
(see atelier/research/fable5/08-security-quota/COST_TABLE.md).
The provider invoice is authoritative.
"""

from __future__ import annotations

import os
import time
from typing import Optional

PRICES_AS_OF = "2026-08-21"
DAILY_BUDGET_USD = float(os.environ.get("ATELIER_DAILY_BUDGET", "10"))
THREAD_BUDGET_USD = float(os.environ.get("ATELIER_THREAD_BUDGET", "2"))

# Approximate public list prices. Always verify on the provider billing page.
COST_TABLE = {
    ("openai", "gpt-5.6-sol", "tokens_in"): 5.00 / 1_000_000,
    ("openai", "gpt-5.6-sol", "tokens_out"): 30.00 / 1_000_000,
    ("openai", "gpt-5.6-terra", "tokens_in"): 2.00 / 1_000_000,
    ("openai", "gpt-5.6-terra", "tokens_out"): 12.00 / 1_000_000,
    ("openai", "gpt-5.6-luna", "tokens_in"): 0.20 / 1_000_000,
    ("openai", "gpt-5.6-luna", "tokens_out"): 1.20 / 1_000_000,
    ("openai", "gpt-4.1", "tokens_in"): 2.00 / 1_000_000,
    ("openai", "gpt-4.1", "tokens_out"): 8.00 / 1_000_000,
    ("openai", "gpt-4.1-mini", "tokens_in"): 0.40 / 1_000_000,
    ("openai", "gpt-4.1-mini", "tokens_out"): 1.60 / 1_000_000,
    ("openai", "gpt-4o-mini", "tokens_in"): 0.15 / 1_000_000,
    ("openai", "gpt-4o-mini", "tokens_out"): 0.60 / 1_000_000,
    ("openai", "dall-e-3", "images"): 0.040,
    ("openai", "gpt-image-1", "images"): 0.040,
    ("openai", "gpt-image-1-mini", "images"): 0.020,
    ("gemini", "gemini-2.0-flash", "tokens_in"): 0.10 / 1_000_000,
    ("gemini", "gemini-2.0-flash", "tokens_out"): 0.40 / 1_000_000,
    ("gemini", "gemini-2.5-flash", "tokens_in"): 0.15 / 1_000_000,
    ("gemini", "gemini-2.5-flash", "tokens_out"): 0.60 / 1_000_000,
    ("gemini", "gemini-3.5-flash", "tokens_in"): 1.50 / 1_000_000,
    ("gemini", "gemini-3.5-flash", "tokens_out"): 9.00 / 1_000_000,
    ("gemini", "gemini-3.1-pro-preview", "tokens_in"): 2.00 / 1_000_000,
    ("gemini", "gemini-3.1-pro-preview", "tokens_out"): 12.00 / 1_000_000,
    ("gemini", "gemini-3.1-flash-lite", "tokens_in"): 0.25 / 1_000_000,
    ("gemini", "gemini-3.1-flash-lite", "tokens_out"): 1.50 / 1_000_000,
    ("gemini", "gemini-3-pro-image", "images"): 0.134,
    ("gemini", "gemini-3.1-flash-image", "images"): 0.067,
    ("gemini", "gemini-2.5-flash-image", "images"): 0.039,
    ("gemini", "imagen-3.0-generate-002", "images"): 0.030,
    ("gemini", "imagen-4.0-generate", "images"): 0.040,
    ("ollama", "*", "tokens_in"): 0.0,
    ("ollama", "*", "tokens_out"): 0.0,
    ("demo", "*", "tokens_in"): 0.0,
    ("demo", "*", "tokens_out"): 0.0,
    ("demo", "*", "images"): 0.0,
}


def is_priced(provider: str, model: str, unit_kind: str) -> bool:
    """True only when the cost table has a real row. Unknown ≠ free."""
    if (provider, model, unit_kind) in COST_TABLE:
        return True
    if (provider, "*", unit_kind) in COST_TABLE:
        return True
    return False


def estimate_usd(provider: str, model: str, unit_kind: str, units: float) -> float:
    exact = COST_TABLE.get((provider, model, unit_kind))
    if exact is not None:
        return round(exact * units, 6)
    wildcard = COST_TABLE.get((provider, "*", unit_kind))
    if wildcard is not None:
        return round(wildcard * units, 6)
    # Conservative hold for budget math only — callers must check is_priced().
    if unit_kind == "images":
        return round(0.04 * units, 6)
    if unit_kind in {"tokens_in", "tokens_out", "tokens"}:
        return round((0.5 / 1_000_000) * units, 6)
    return 0.0


class BudgetExceeded(RuntimeError):
    pass


def spent_since(memory, *, since_ts: float, thread_id: Optional[str] = None) -> float:
    if thread_id:
        rows = memory.conn.execute(
            "SELECT COALESCE(SUM(estimated_usd), 0) FROM usage_events WHERE thread_id=? AND created_at>=?",
            (thread_id, since_ts),
        ).fetchone()
    else:
        rows = memory.conn.execute(
            "SELECT COALESCE(SUM(estimated_usd), 0) FROM usage_events WHERE created_at>=?",
            (since_ts,),
        ).fetchone()
    return float(rows[0] or 0)


def assert_budget(memory, *, thread_id: Optional[str] = None, extra_usd: float = 0.0) -> None:
    day_start = time.time() - 86400
    daily = spent_since(memory, since_ts=day_start) + extra_usd
    if daily > DAILY_BUDGET_USD:
        raise BudgetExceeded(f"daily budget ${DAILY_BUDGET_USD:.2f} exceeded (${daily:.4f})")
    if thread_id:
        thread = spent_since(memory, since_ts=0, thread_id=thread_id) + extra_usd
        if thread > THREAD_BUDGET_USD:
            raise BudgetExceeded(f"thread budget ${THREAD_BUDGET_USD:.2f} exceeded (${thread:.4f})")


def record(memory, *, provider: str, model: str, unit_kind: str, units: float, thread_id: Optional[str] = None) -> dict:
    cost = estimate_usd(provider, model, unit_kind, units)
    if provider != "demo":
        assert_budget(memory, thread_id=thread_id, extra_usd=cost)
    return memory.add_usage(
        provider=provider,
        model=model,
        unit_kind=unit_kind,
        units=units,
        estimated_usd=cost,
        thread_id=thread_id,
    )
