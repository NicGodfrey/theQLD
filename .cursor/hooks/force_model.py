#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LIB = ROOT / "forced-router"
if str(LIB) not in sys.path:
    sys.path.insert(0, str(LIB))

from forced_router.config import load_config  # noqa: E402
from forced_router.policy import hook_response  # noqa: E402


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            raise ValueError("hook payload must be a JSON object")
        cfg = load_config(ROOT)
        response = hook_response(payload, cfg)
    except Exception as exc:  # pragma: no cover - fail-closed path
        response = {
            "continue": False,
            "permission": "deny",
            "user_message": f"forced-model hook failed: {exc}",
            "error": traceback.format_exc(),
        }
    sys.stdout.write(json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
