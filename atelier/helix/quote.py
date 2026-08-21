"""Quote-before-commit — estimate the next weave without spending quota."""

from __future__ import annotations

from typing import Optional

from . import usage


def as_int(value, default: int = 0, lo: int | None = None, hi: int | None = None) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError):
        n = default
    if lo is not None:
        n = max(lo, n)
    if hi is not None:
        n = min(hi, n)
    return n


def image_model_for(provider: str) -> str:
    provider = (provider or "demo").lower()
    if provider == "openai":
        return "gpt-image-1"
    if provider == "gemini":
        return "gemini-2.5-flash-image"
    if provider == "ollama":
        return "llama3.2"
    return "demo-svg"


def chat_model_for(provider: str, model: str = "") -> str:
    if model:
        return model
    provider = (provider or "demo").lower()
    if provider == "openai":
        return "gpt-4o-mini"
    if provider == "gemini":
        return "gemini-2.0-flash"
    if provider == "ollama":
        return "llama3.2"
    return "demo-conductor"


def quote_run(
    *,
    provider: str = "demo",
    model: str = "",
    prompt: str = "",
    count: int = 1,
    capability: str = "image",
    memory=None,
    thread_id: Optional[str] = None,
) -> dict:
    provider = (provider or "demo").strip().lower()
    count = as_int(count, default=1, lo=1, hi=8)
    chat_model = chat_model_for(provider, model)
    image_model = image_model_for(provider)

    tokens_in = max(120, min(len(prompt or "") // 3 + 400, 4000))
    tokens_out = 400
    chat_in = usage.estimate_usd(provider, chat_model, "tokens_in", tokens_in)
    chat_out = usage.estimate_usd(provider, chat_model, "tokens_out", tokens_out)
    images_usd = (
        usage.estimate_usd(provider, image_model, "images", count)
        if capability != "chat"
        else 0.0
    )

    chat_priced = usage.is_priced(provider, chat_model, "tokens_in") or provider in {
        "demo",
        "ollama",
    }
    image_priced = capability == "chat" or usage.is_priced(
        provider, image_model, "images"
    ) or provider in {"demo", "ollama"}
    priced = bool(chat_priced and image_priced)

    estimated = round(chat_in + chat_out + images_usd, 6)
    if provider in {"demo", "ollama"}:
        estimated = 0.0
    conservative = estimated if priced else round(0.04 * count + 0.01, 6)
    billed = estimated if priced else conservative

    would_exceed = False
    reason = ""
    if memory is not None and provider not in {"demo", "ollama"}:
        try:
            usage.assert_budget(memory, thread_id=thread_id, extra_usd=billed)
        except usage.BudgetExceeded as exc:
            would_exceed = True
            reason = str(exc)

    return {
        "provider": provider,
        "model": chat_model,
        "image_model": image_model,
        "count": count,
        "capability": capability,
        "estimated_usd": billed,
        "conservative_usd": conservative,
        "priced": priced,
        "would_exceed": would_exceed,
        "reason": reason,
        "daily_budget_usd": usage.DAILY_BUDGET_USD,
        "thread_budget_usd": usage.THREAD_BUDGET_USD,
        "breakdown": [
            {"kind": "tokens_in", "model": chat_model, "usd": chat_in, "priced": chat_priced},
            {"kind": "tokens_out", "model": chat_model, "usd": chat_out, "priced": chat_priced},
            {"kind": "images", "model": image_model, "usd": images_usd, "priced": image_priced},
        ],
        "prompt_chars": len(prompt or ""),
    }
