from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


class SessionLedger:
    """Append-only JSONL log with a per-session hash chain."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._heads: dict[str, str] = {}
        self._seq: dict[str, int] = {}

    def path_for(self, session_id: str) -> Path:
        return self.root / f"{session_id}.jsonl"

    def append(self, session_id: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        seq = self._seq.get(session_id, 0) + 1
        prev = self._heads.get(session_id, "0" * 64)
        record = {
            "session_id": session_id,
            "seq": seq,
            "event_type": event_type,
            "committed_at": _utcnow(),
            "payload": payload,
            "prev_hash": prev,
        }
        digest_source = {k: v for k, v in record.items()}
        record_hash = hashlib.sha256(canonical_json(digest_source).encode("utf-8")).hexdigest()
        record["record_hash"] = record_hash
        path = self.path_for(session_id)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(canonical_json(record) + "\n")
            handle.flush()
        self._heads[session_id] = record_hash
        self._seq[session_id] = seq
        return record

    def read_all(self, session_id: str) -> list[dict[str, Any]]:
        path = self.path_for(session_id)
        if not path.exists():
            return []
        events = []
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events

    def verify_chain(self, session_id: str) -> bool:
        events = self.read_all(session_id)
        prev = "0" * 64
        for event in events:
            if event.get("prev_hash") != prev:
                return False
            check = {k: v for k, v in event.items() if k != "record_hash"}
            expected = hashlib.sha256(canonical_json(check).encode("utf-8")).hexdigest()
            if event.get("record_hash") != expected:
                return False
            prev = event["record_hash"]
        return True
