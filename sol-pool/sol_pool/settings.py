from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    data_dir: Path
    api_key: str = "dev-key"
    slot_count: int = 10
    lease_seconds: float = 30.0
    display_name: str = "GPT5.6 sol"
    pricebook_id: str = "sol-prototype"
    pricebook_version: str = "2026-08-12.1"
    currency: str = "USD"
    # USD per 1 token (prototype rates; replace with a real pricebook later)
    price_input_uncached: str = "0.000010"
    price_input_cached: str = "0.000001"
    price_output_visible: str = "0.000030"
    price_reasoning: str = "0.000020"
    sweep_interval_seconds: float = 0.25

    def ledger_dir(self) -> Path:
        path = self.data_dir / "ledger"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def billing_dir(self) -> Path:
        path = self.data_dir / "billing"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def slots_dir(self) -> Path:
        path = self.data_dir / "slots"
        path.mkdir(parents=True, exist_ok=True)
        return path
