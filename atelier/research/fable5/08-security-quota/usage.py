"""Usage ledger and budget guard for Atelier (local BYOK design studio).

Records every provider call as an immutable ledger row:

    provider, model, units, estimated_cost_usd, thread_id  (+ timestamp, metadata)

and enforces spend quotas (global daily and per-thread) *before* a call is made.

Design notes
------------
- SQLite (WAL) in the app data dir; stdlib only, safe across processes.
- ``units`` is a JSON map of unit-name -> quantity, e.g.
  ``{"input_tokens": 1200, "output_tokens": 340}`` or ``{"images": 2}``.
  Unit names must match the price table so costs are computable.
- Costs are *estimates* from public list prices (see COST_TABLE.md, and
  ``PRICES_AS_OF`` below). The provider's bill is authoritative.
- Decimal arithmetic for prices; stored as REAL (6 dp) — plenty for estimates.
- Security: rows never contain API keys. As defense in depth, free-form
  metadata is scrubbed of key-shaped strings before writing (see POLICY.md).

Typical use::

    ledger = UsageLedger(path)
    guard = BudgetGuard(ledger, daily_usd=10.0, per_thread_usd=2.0)

    units = {"input_tokens": n_in_est, "output_tokens": n_out_est}
    guard.check("thread-42", ledger.estimate_cost("openai", "gpt-5.6-terra", units))
    ...  # make the provider call
    ledger.record("openai", "gpt-5.6-terra", actual_units, thread_id="thread-42")
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Iterator, Mapping, Optional

__all__ = [
    "UsageLedger",
    "UsageEvent",
    "BudgetGuard",
    "QuotaExceeded",
    "UnknownPriceError",
    "estimate_cost",
    "PRICES",
    "PRICES_AS_OF",
]

# --------------------------------------------------------------------------
# Price table (USD). Public list prices, standard tier; see COST_TABLE.md.
# Keys: (provider, model) -> {unit_name: Decimal USD per ONE unit}.
# Token prices are entered per 1M tokens and divided down, to match how the
# providers publish them.
# --------------------------------------------------------------------------

PRICES_AS_OF = "2026-08-21"

_M = Decimal(1_000_000)


def _per_m(usd_per_million: str) -> Decimal:
    return Decimal(usd_per_million) / _M


PRICES: dict[tuple[str, str], dict[str, Decimal]] = {
    # ---- OpenAI: text / multimodal (per-token) ----
    ("openai", "gpt-5.6-sol"): {
        "input_tokens": _per_m("5.00"),
        "cached_input_tokens": _per_m("0.50"),
        "output_tokens": _per_m("30.00"),
    },
    ("openai", "gpt-5.6-terra"): {
        "input_tokens": _per_m("2.00"),
        "cached_input_tokens": _per_m("0.20"),
        "output_tokens": _per_m("12.00"),
    },
    ("openai", "gpt-5.6-luna"): {
        "input_tokens": _per_m("0.20"),
        "cached_input_tokens": _per_m("0.02"),
        "output_tokens": _per_m("1.20"),
    },
    ("openai", "gpt-4.1"): {
        "input_tokens": _per_m("2.00"),
        "cached_input_tokens": _per_m("0.50"),
        "output_tokens": _per_m("8.00"),
    },
    # ---- OpenAI: image generation (token-billed) ----
    ("openai", "gpt-image-2"): {
        "image_input_tokens": _per_m("8.00"),
        "cached_image_input_tokens": _per_m("2.00"),
        "text_input_tokens": _per_m("5.00"),
        "cached_text_input_tokens": _per_m("1.25"),
        "image_output_tokens": _per_m("30.00"),
    },
    ("openai", "gpt-image-1-mini"): {
        "image_input_tokens": _per_m("2.50"),
        "cached_image_input_tokens": _per_m("0.25"),
        "image_output_tokens": _per_m("8.00"),
    },
    # ---- Gemini: text / multimodal (per-token, prompts <= 200k) ----
    ("gemini", "gemini-3.1-pro-preview"): {
        "input_tokens": _per_m("2.00"),
        "output_tokens": _per_m("12.00"),
        "cached_input_tokens": _per_m("0.20"),
    },
    ("gemini", "gemini-3.5-flash"): {
        "input_tokens": _per_m("1.50"),
        "output_tokens": _per_m("9.00"),
        "cached_input_tokens": _per_m("0.15"),
    },
    ("gemini", "gemini-3.1-flash-lite"): {
        "input_tokens": _per_m("0.25"),
        "output_tokens": _per_m("1.50"),
        "audio_input_tokens": _per_m("0.50"),
    },
    # ---- Gemini: image generation (token-billed + per-image convenience) ----
    ("gemini", "gemini-3-pro-image"): {
        "input_tokens": _per_m("2.00"),
        "output_tokens": _per_m("12.00"),          # text + thinking
        "image_output_tokens": _per_m("120.00"),
        "images_1k": Decimal("0.134"),             # 1K/2K image = 1120 out tokens
        "images_4k": Decimal("0.24"),              # 4K image = 2000 out tokens
    },
    ("gemini", "gemini-3.1-flash-image"): {
        "input_tokens": _per_m("0.50"),
        "output_tokens": _per_m("3.00"),
        "image_output_tokens": _per_m("60.00"),
        "images_1k": Decimal("0.067"),
        "images_2k": Decimal("0.101"),
        "images_4k": Decimal("0.151"),
    },
    ("gemini", "imagen-4.0-generate-001"): {"images": Decimal("0.04")},
    ("gemini", "imagen-4.0-fast-generate-001"): {"images": Decimal("0.02")},
    ("gemini", "imagen-4.0-ultra-generate-001"): {"images": Decimal("0.06")},
}

_CENTS6 = Decimal("0.000001")


class UnknownPriceError(LookupError):
    """No list price is known for a (provider, model) or a unit within it."""


def estimate_cost(
    provider: str,
    model: str,
    units: Mapping[str, float],
    *,
    prices: Mapping[tuple[str, str], Mapping[str, Decimal]] = PRICES,
    strict: bool = False,
) -> Optional[float]:
    """Estimated USD cost for ``units`` of ``model``, or None if unpriceable.

    With ``strict=True``, unknown models/units raise ``UnknownPriceError``
    instead of returning None — use strict mode in the pre-call quota check so
    unpriced calls cannot silently bypass budgets.
    """
    table = prices.get((provider.lower(), model.lower()))
    if table is None:
        if strict:
            raise UnknownPriceError(f"no price table for {provider}/{model}")
        return None
    total = Decimal(0)
    for unit, qty in units.items():
        price = table.get(unit)
        if price is None:
            if strict:
                raise UnknownPriceError(f"no price for unit {unit!r} of {provider}/{model}")
            return None
        if qty < 0:
            raise ValueError(f"negative quantity for {unit!r}: {qty}")
        total += price * Decimal(str(qty))
    return float(total.quantize(_CENTS6, rounding=ROUND_HALF_UP))


# --------------------------------------------------------------------------
# Secret scrubbing (defense in depth; see POLICY.md).
# The ledger schema has no key fields, but callers may pass free-form
# metadata (prompt titles, error strings). Scrub anything key-shaped.
# --------------------------------------------------------------------------

_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_\-]{20,}"),          # OpenAI-style secret keys
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),           # Google API keys
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{16,}"),
]
_REDACTED = "[REDACTED]"


def scrub_secrets(value: Any) -> Any:
    """Recursively replace key-shaped substrings in strings with [REDACTED]."""
    if isinstance(value, str):
        for pat in _SECRET_PATTERNS:
            value = pat.sub(_REDACTED, value)
        return value
    if isinstance(value, Mapping):
        return {k: scrub_secrets(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [scrub_secrets(v) for v in value]
    return value


# --------------------------------------------------------------------------
# Ledger
# --------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS usage_events (
    id                 TEXT PRIMARY KEY,
    ts                 REAL NOT NULL,             -- unix epoch seconds (UTC)
    provider           TEXT NOT NULL,
    model              TEXT NOT NULL,
    units              TEXT NOT NULL,             -- JSON {unit: qty}
    estimated_cost_usd REAL,                      -- NULL when unpriceable
    thread_id          TEXT NOT NULL,
    request_id         TEXT,                      -- provider request id, if any
    metadata           TEXT NOT NULL DEFAULT '{}' -- JSON, secret-scrubbed
);
CREATE INDEX IF NOT EXISTS idx_usage_ts     ON usage_events (ts);
CREATE INDEX IF NOT EXISTS idx_usage_thread ON usage_events (thread_id, ts);
"""


@dataclass(frozen=True)
class UsageEvent:
    id: str
    ts: float
    provider: str
    model: str
    units: dict[str, float]
    estimated_cost_usd: Optional[float]
    thread_id: str
    request_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def when(self) -> _dt.datetime:
        return _dt.datetime.fromtimestamp(self.ts, tz=_dt.timezone.utc)


class UsageLedger:
    """Append-only usage ledger backed by SQLite.

    A short-lived connection is opened per operation, which makes the class
    safe to share across threads and across processes (SQLite + WAL handle
    the locking).
    """

    def __init__(self, path: str | os.PathLike[str] = "usage.sqlite3") -> None:
        self.path = os.fspath(path)
        parent = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(parent, exist_ok=True)
        with self._connect() as con:
            con.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path, timeout=10.0)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        return con

    # -- writing ------------------------------------------------------------

    def record(
        self,
        provider: str,
        model: str,
        units: Mapping[str, float],
        *,
        thread_id: str,
        request_id: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        estimated_cost_usd: Optional[float] = None,
        ts: Optional[float] = None,
    ) -> UsageEvent:
        """Append one event. Cost is computed from PRICES unless given."""
        if not units:
            raise ValueError("units must be a non-empty mapping")
        provider = provider.lower().strip()
        model = model.lower().strip()
        if estimated_cost_usd is None:
            estimated_cost_usd = estimate_cost(provider, model, units)
        event = UsageEvent(
            id=str(uuid.uuid4()),
            ts=float(ts if ts is not None else time.time()),
            provider=provider,
            model=model,
            units={k: float(v) for k, v in units.items()},
            estimated_cost_usd=estimated_cost_usd,
            thread_id=str(thread_id),
            request_id=request_id,
            metadata=scrub_secrets(dict(metadata or {})),
        )
        with self._connect() as con:
            con.execute(
                "INSERT INTO usage_events"
                " (id, ts, provider, model, units, estimated_cost_usd,"
                "  thread_id, request_id, metadata)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event.id,
                    event.ts,
                    event.provider,
                    event.model,
                    json.dumps(event.units, sort_keys=True),
                    event.estimated_cost_usd,
                    event.thread_id,
                    event.request_id,
                    json.dumps(event.metadata, sort_keys=True, default=str),
                ),
            )
        return event

    def estimate_cost(
        self, provider: str, model: str, units: Mapping[str, float], *, strict: bool = False
    ) -> Optional[float]:
        return estimate_cost(provider.lower(), model.lower(), units, strict=strict)

    # -- reading ------------------------------------------------------------

    def events(
        self,
        *,
        thread_id: Optional[str] = None,
        since: Optional[float] = None,
        limit: int = 100,
    ) -> Iterator[UsageEvent]:
        """Most-recent-first events, optionally filtered by thread and time."""
        q = "SELECT id, ts, provider, model, units, estimated_cost_usd, thread_id, request_id, metadata FROM usage_events"
        clauses, params = [], []
        if thread_id is not None:
            clauses.append("thread_id = ?")
            params.append(thread_id)
        if since is not None:
            clauses.append("ts >= ?")
            params.append(since)
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        q += " ORDER BY ts DESC LIMIT ?"
        params.append(int(limit))
        with self._connect() as con:
            for row in con.execute(q, params):
                yield UsageEvent(
                    id=row[0], ts=row[1], provider=row[2], model=row[3],
                    units=json.loads(row[4]), estimated_cost_usd=row[5],
                    thread_id=row[6], request_id=row[7], metadata=json.loads(row[8]),
                )

    def spend_usd(
        self,
        *,
        since: Optional[float] = None,
        thread_id: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> float:
        """Total estimated USD spend matching the filters (NULL costs = 0)."""
        q = "SELECT COALESCE(SUM(estimated_cost_usd), 0) FROM usage_events"
        clauses, params = [], []
        if since is not None:
            clauses.append("ts >= ?")
            params.append(since)
        if thread_id is not None:
            clauses.append("thread_id = ?")
            params.append(thread_id)
        if provider is not None:
            clauses.append("provider = ?")
            params.append(provider.lower())
        if clauses:
            q += " WHERE " + " AND ".join(clauses)
        with self._connect() as con:
            (total,) = con.execute(q, params).fetchone()
        return float(total)

    def spend_by_model(self, *, since: Optional[float] = None) -> list[tuple[str, str, float, int]]:
        """[(provider, model, est_usd, n_calls)] descending by spend."""
        q = (
            "SELECT provider, model, COALESCE(SUM(estimated_cost_usd),0), COUNT(*)"
            " FROM usage_events"
        )
        params: list[Any] = []
        if since is not None:
            q += " WHERE ts >= ?"
            params.append(since)
        q += " GROUP BY provider, model ORDER BY 3 DESC"
        with self._connect() as con:
            return [(r[0], r[1], float(r[2]), int(r[3])) for r in con.execute(q, params)]

    def unpriced_count(self, *, since: Optional[float] = None) -> int:
        """Events recorded with no estimable cost (should stay at zero)."""
        q = "SELECT COUNT(*) FROM usage_events WHERE estimated_cost_usd IS NULL"
        params: list[Any] = []
        if since is not None:
            q += " AND ts >= ?"
            params.append(since)
        with self._connect() as con:
            (n,) = con.execute(q, params).fetchone()
        return int(n)


# --------------------------------------------------------------------------
# Quotas
# --------------------------------------------------------------------------

class QuotaExceeded(RuntimeError):
    def __init__(self, scope: str, limit_usd: float, spent_usd: float, projected_usd: float):
        self.scope = scope
        self.limit_usd = limit_usd
        self.spent_usd = spent_usd
        self.projected_usd = projected_usd
        super().__init__(
            f"{scope} budget exceeded: spent ${spent_usd:.4f}"
            f" + projected ${projected_usd:.4f} > limit ${limit_usd:.2f}"
        )


def _utc_midnight_epoch(now: Optional[float] = None) -> float:
    dt = _dt.datetime.fromtimestamp(now if now is not None else time.time(), tz=_dt.timezone.utc)
    return dt.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()


@dataclass
class BudgetGuard:
    """Pre-call budget enforcement over a UsageLedger.

    ``daily_usd``      – cap on total estimated spend since UTC midnight.
    ``per_thread_usd`` – lifetime cap per thread_id (a canvas conversation).
    Either may be None to disable that check.

    Call ``check(thread_id, projected_cost)`` BEFORE the provider call, with a
    strict cost estimate; it raises QuotaExceeded when the call would cross a
    cap. This is what bounds prompt-injection spend loops (THREAT_MODEL.md T3).
    """

    ledger: UsageLedger
    daily_usd: Optional[float] = 10.0
    per_thread_usd: Optional[float] = 2.0

    def check(self, thread_id: str, projected_cost_usd: float) -> None:
        if projected_cost_usd < 0:
            raise ValueError("projected cost must be >= 0")
        if self.daily_usd is not None:
            spent = self.ledger.spend_usd(since=_utc_midnight_epoch())
            if spent + projected_cost_usd > self.daily_usd:
                raise QuotaExceeded("daily", self.daily_usd, spent, projected_cost_usd)
        if self.per_thread_usd is not None:
            spent = self.ledger.spend_usd(thread_id=thread_id)
            if spent + projected_cost_usd > self.per_thread_usd:
                raise QuotaExceeded(
                    f"thread {thread_id!r}", self.per_thread_usd, spent, projected_cost_usd
                )

    def headroom(self, thread_id: str) -> dict[str, Optional[float]]:
        """Remaining budget in USD per scope (None = unlimited)."""
        out: dict[str, Optional[float]] = {"daily": None, "thread": None}
        if self.daily_usd is not None:
            out["daily"] = max(0.0, self.daily_usd - self.ledger.spend_usd(since=_utc_midnight_epoch()))
        if self.per_thread_usd is not None:
            out["thread"] = max(0.0, self.per_thread_usd - self.ledger.spend_usd(thread_id=thread_id))
        return out


# --------------------------------------------------------------------------
# CLI:  python usage.py record|report|selftest
# --------------------------------------------------------------------------

def _default_db_path() -> str:
    base = os.environ.get("ATELIER_DATA_DIR") or os.path.join(
        os.path.expanduser("~"), ".local", "share", "atelier"
    )
    return os.path.join(base, "usage.sqlite3")


def _cmd_record(args: argparse.Namespace) -> int:
    ledger = UsageLedger(args.db)
    units = json.loads(args.units)
    ev = ledger.record(
        args.provider, args.model, units,
        thread_id=args.thread_id, request_id=args.request_id,
        metadata=json.loads(args.metadata) if args.metadata else None,
    )
    cost = "n/a (no list price)" if ev.estimated_cost_usd is None else f"${ev.estimated_cost_usd:.6f}"
    print(f"recorded {ev.id}  {ev.provider}/{ev.model}  est {cost}")
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    ledger = UsageLedger(args.db)
    since = _utc_midnight_epoch() if args.today else None
    label = "today (UTC)" if args.today else "all time"
    print(f"# usage report — {label}   (prices as of {PRICES_AS_OF})")
    rows = ledger.spend_by_model(since=since)
    if not rows:
        print("(no events)")
        return 0
    width = max(len(f"{p}/{m}") for p, m, _, _ in rows)
    for provider, model, usd, n in rows:
        print(f"{provider + '/' + model:<{width}}  {n:>5} calls  ${usd:>10.4f}")
    print(f"{'TOTAL':<{width}}  {sum(n for *_, n in rows):>5} calls  ${ledger.spend_usd(since=since):>10.4f}")
    unpriced = ledger.unpriced_count(since=since)
    if unpriced:
        print(f"warning: {unpriced} event(s) had no estimable cost")
    return 0


def _cmd_selftest(_args: argparse.Namespace) -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        ledger = UsageLedger(os.path.join(tmp, "t.sqlite3"))

        # Cost math: 1M in + 1M out of gpt-5.6-terra = $2 + $12.
        assert estimate_cost("openai", "gpt-5.6-terra",
                             {"input_tokens": 1_000_000, "output_tokens": 1_000_000}) == 14.0
        # Gemini per-image convenience units.
        assert estimate_cost("gemini", "gemini-3-pro-image", {"images_1k": 2}) == 0.268
        # Unknown model -> None (lenient) / raises (strict).
        assert estimate_cost("openai", "mystery-model", {"input_tokens": 5}) is None
        try:
            estimate_cost("openai", "mystery-model", {"input_tokens": 5}, strict=True)
            raise AssertionError("strict mode should raise")
        except UnknownPriceError:
            pass

        # Recording computes cost and scrubs secrets from metadata.
        ev = ledger.record(
            "OpenAI", "GPT-5.6-LUNA",
            {"input_tokens": 10_000, "output_tokens": 2_000},
            thread_id="th-1",
            metadata={"note": "auth was Bearer abc123def456ghi789 and sk-" + "a" * 24},
        )
        assert ev.estimated_cost_usd == 0.0044, ev.estimated_cost_usd
        assert "sk-" not in json.dumps(ev.metadata)
        assert "abc123def456ghi789" not in json.dumps(ev.metadata)
        assert "[REDACTED]" in ev.metadata["note"]

        # Aggregation and filters.
        ledger.record("gemini", "gemini-3.5-flash", {"input_tokens": 1000, "output_tokens": 500},
                      thread_id="th-2")
        assert ledger.spend_usd() > 0
        assert ledger.spend_usd(thread_id="th-1") == 0.0044
        assert len(list(ledger.events(thread_id="th-2"))) == 1
        assert ledger.unpriced_count() == 0

        # Budget guard: per-thread cap blocks, daily cap blocks.
        guard = BudgetGuard(ledger, daily_usd=1.00, per_thread_usd=0.005)
        guard.check("th-1", 0.0005)  # 0.0044 + 0.0005 <= 0.005: ok
        try:
            guard.check("th-1", 0.001)
            raise AssertionError("per-thread quota should trip")
        except QuotaExceeded as e:
            assert e.scope == "thread 'th-1'"
        ledger.record("openai", "gpt-5.6-sol", {"output_tokens": 33_000},
                      thread_id="th-3")  # ~$0.99 today
        try:
            guard.check("th-9", 0.05)
            raise AssertionError("daily quota should trip")
        except QuotaExceeded as e:
            assert e.scope == "daily"
        hr = guard.headroom("th-9")
        assert hr["daily"] is not None and hr["daily"] < 0.02

    print("selftest ok")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Atelier usage ledger")
    p.add_argument("--db", default=_default_db_path(), help="path to sqlite ledger")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="append a usage event")
    r.add_argument("provider")
    r.add_argument("model")
    r.add_argument("units", help='JSON, e.g. {"input_tokens": 1200, "output_tokens": 400}')
    r.add_argument("--thread-id", required=True)
    r.add_argument("--request-id")
    r.add_argument("--metadata", help="JSON object")
    r.set_defaults(fn=_cmd_record)

    rep = sub.add_parser("report", help="spend by provider/model")
    rep.add_argument("--today", action="store_true", help="restrict to today (UTC)")
    rep.set_defaults(fn=_cmd_report)

    st = sub.add_parser("selftest", help="run built-in tests against a temp db")
    st.set_defaults(fn=_cmd_selftest)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
