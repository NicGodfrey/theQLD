from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any
from uuid import uuid4

from sol_pool.settings import Settings


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _money(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_EVEN))


class BillingLedger:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.root = settings.billing_dir()
        self.events: list[dict[str, Any]] = []
        self.by_call: dict[str, dict[str, Any]] = {}

    def _rate(self, meter: str) -> Decimal:
        mapping = {
            "input_uncached_tokens": self.settings.price_input_uncached,
            "input_cached_tokens": self.settings.price_input_cached,
            "output_visible_tokens": self.settings.price_output_visible,
            "reasoning_tokens": self.settings.price_reasoning,
        }
        return Decimal(mapping[meter])

    def finalize_call(
        self,
        *,
        session_id: str,
        session_epoch: int,
        worker_id: int,
        model_call_id: str,
        logical_request_id: str,
        termination: str,
        input_tokens: int,
        cached_input_tokens: int,
        visible_output_tokens: int,
        reasoning_tokens: int,
        bound_wall_clock_ms: int,
        stream_interrupted: bool,
    ) -> dict[str, Any]:
        if model_call_id in self.by_call:
            return self.by_call[model_call_id]

        uncached = max(0, input_tokens - cached_input_tokens)
        meters = [
            ("input_uncached_tokens", uncached),
            ("input_cached_tokens", cached_input_tokens),
            ("output_visible_tokens", visible_output_tokens),
            ("reasoning_tokens", reasoning_tokens),
        ]
        lines = []
        customer_total = Decimal("0")
        for meter, quantity in meters:
            unit_price = self._rate(meter)
            amount = unit_price * Decimal(quantity)
            customer_total += amount
            lines.append(
                {
                    "meter": meter,
                    "quantity": quantity,
                    "unit_size": 1,
                    "unit_price": str(unit_price),
                    "amount": _money(amount),
                    "charge_owner": "customer",
                }
            )

        event = {
            "schema_version": "1",
            "event_id": str(uuid4()),
            "event_type": "billing.model_call.finalized",
            "scope": {
                "session_id": session_id,
                "session_epoch": session_epoch,
                "worker_id": worker_id,
            },
            "identity": {
                "logical_request_id": logical_request_id,
                "model_call_id": model_call_id,
            },
            "model": {
                "billing_sku": "gpt-5.6-sol-xhigh",
                "requested_model": "GPT5.6 sol",
                "effective_model": "GPT5.6 sol",
                "reasoning_effort": "xhigh",
            },
            "timing": {
                "finalized_at": _utcnow(),
                "bound_wall_clock_ms": bound_wall_clock_ms,
            },
            "termination": {
                "status": termination,
                "stream_interrupted": stream_interrupted,
            },
            "usage": {
                "input_tokens_total": input_tokens,
                "cached_input_tokens": cached_input_tokens,
                "uncached_input_tokens": uncached,
                "output_tokens_total": visible_output_tokens + reasoning_tokens,
                "reasoning_tokens": reasoning_tokens,
                "visible_output_tokens": visible_output_tokens,
                "usage_source": "local_stream_meter",
                "usage_completeness": "complete",
            },
            "rating": {
                "pricebook_id": self.settings.pricebook_id,
                "pricebook_version": self.settings.pricebook_version,
                "currency": self.settings.currency,
                "billing_disposition": "customer_billable",
                "lines": lines,
                "customer_subtotal": _money(customer_total),
            },
        }
        self.events.append(event)
        self.by_call[model_call_id] = event
        path = self.root / f"{session_id}.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
            handle.flush()
        return event

    def session_summary(self, session_id: str) -> dict[str, Any]:
        events = [e for e in self.events if e["scope"]["session_id"] == session_id]
        totals = {
            "input_tokens_total": 0,
            "cached_input_tokens": 0,
            "uncached_input_tokens": 0,
            "visible_output_tokens": 0,
            "reasoning_tokens": 0,
        }
        amount = Decimal("0")
        for event in events:
            usage = event["usage"]
            for key in totals:
                totals[key] += int(usage[key])
            amount += Decimal(event["rating"]["customer_subtotal"])
        return {
            "session_id": session_id,
            "status": "final" if events else "provisional",
            "currency": self.settings.currency,
            "usage": totals,
            "charges": [
                {
                    "meter": event["rating"]["lines"][0]["meter"] if False else "aggregated",
                    "amount": _money(amount),
                }
            ],
            "lines": [line for event in events for line in event["rating"]["lines"]],
            "event_count": len(events),
            "total": _money(amount),
            "events": events,
        }
