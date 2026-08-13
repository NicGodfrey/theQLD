from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow `python3 .cursor/hooks/force_model.py` and in-process tests.
_ROOT = Path(__file__).resolve().parents[2]
_LIB = _ROOT / "forced-router"
if str(_LIB) not in sys.path:
    sys.path.insert(0, str(_LIB))

from forced_router.config import load_config
from forced_router.policy import hook_response


def run(raw: str, start: Path | None = None) -> dict:
    payload = json.loads(raw) if raw.strip() else {}
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be a JSON object")
    cfg = load_config(start or _ROOT)
    return hook_response(payload, cfg)


def main() -> int:
    import json as _json

    raw = sys.stdin.read()
    try:
        response = run(raw)
    except Exception as exc:
        response = {
            "continue": False,
            "permission": "deny",
            "user_message": f"forced-model hook failed: {exc}",
        }
    sys.stdout.write(_json.dumps(response, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
