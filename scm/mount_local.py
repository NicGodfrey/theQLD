#!/usr/bin/env python3
"""Mount a local SCM JSON dump into the sidecar SQLite database."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from store import DEFAULT_DB, ScmStore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Mount a local SCM JSON export")
    parser.add_argument("dump", type=Path, help="Path to schema.json-compatible export")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--mode", choices=("replace", "merge"), default="replace")
    parser.add_argument("--source", default="")
    args = parser.parse_args()
    payload = json.loads(args.dump.read_text(encoding="utf-8"))
    source = args.source or str(payload.get("source") or args.dump)
    store = ScmStore(args.db)
    try:
        if args.mode == "merge":
            state = store.merge(payload, source=source)
        else:
            state = store.replace(payload, source=source)
    finally:
        store.close()
    print(
        json.dumps(
            {
                "ok": True,
                "mode": args.mode,
                "source": state.get("source"),
                "counts": {name: len(state.get(name, [])) for name in (
                    "suppliers",
                    "products",
                    "warehouses",
                    "stock",
                    "purchaseOrders",
                    "salesOrders",
                    "shipments",
                )},
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
