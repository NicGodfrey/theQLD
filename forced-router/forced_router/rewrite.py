from __future__ import annotations

import re
from typing import Any

from .config import ForcedModelConfig

_BRACKET = re.compile(r"\[.*\]$")


def normalize_model(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return normalize_model(value.get("id") or value.get("model") or value.get("name"))
    text = str(value).strip().lower().replace("_", "-")
    text = _BRACKET.sub("", text)
    if text.endswith("-thinking"):
        text = text[: -len("-thinking")]
    return text


def is_auto_model(value: Any, cfg: ForcedModelConfig) -> bool:
    name = normalize_model(value)
    if name == "":
        return True
    if name in cfg.auto_aliases:
        return True
    if name.startswith("auto-") or name.endswith("-auto"):
        return True
    return False


def is_specified_model(value: Any, cfg: ForcedModelConfig) -> bool:
    name = normalize_model(value)
    if not name:
        return False
    needles = {normalize_model(cfg.spec.id), normalize_model(cfg.spec.cli_model)}
    needles.update(normalize_model(x) for x in cfg.spec.match)
    for needle in needles:
        if not needle:
            continue
        if name == needle or name.startswith(needle + "-") or needle.startswith(name + "-"):
            return True
    return False


def extract_model(payload: dict[str, Any]) -> Any:
    for key in ("model", "model_id", "subagent_model"):
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def _force_model_id(cfg: ForcedModelConfig, for_api: bool = False) -> str:
    return cfg.spec.id if for_api else cfg.spec.cli_model


def should_rewrite(model: Any, cfg: ForcedModelConfig) -> bool:
    if cfg.policy.force_all_api_models:
        return not is_specified_model(model, cfg)
    return is_auto_model(model, cfg)


def rewrite_model_value(model: Any, cfg: ForcedModelConfig, *, for_api: bool = False) -> Any:
    if not should_rewrite(model, cfg):
        if isinstance(model, dict):
            return dict(model)
        return model if model not in (None, "") else _force_model_id(cfg, for_api=for_api)
    if isinstance(model, dict):
        out = dict(model)
        out["id"] = cfg.spec.id
        if cfg.spec.params:
            out["params"] = [dict(p) for p in cfg.spec.params]
        return out
    return cfg.spec.id if for_api else cfg.spec.cli_model


def rewrite_payload(payload: dict[str, Any], cfg: ForcedModelConfig, *, for_api: bool = False) -> dict[str, Any]:
    out = dict(payload)
    original = extract_model(out)
    if "model" in out or should_rewrite(original, cfg) or original in (None, ""):
        out["model"] = rewrite_model_value(out.get("model"), cfg, for_api=for_api)
    return out


def rewrite_cursor_agent(payload: dict[str, Any], cfg: ForcedModelConfig) -> dict[str, Any]:
    out = dict(payload)
    current = out.get("model")
    if should_rewrite(current, cfg) or current in (None, ""):
        out["model"] = cfg.spec.api_model()
    elif isinstance(current, str):
        out["model"] = cfg.spec.api_model()
    return out


def rewrite_cli_argv(argv: list[str], cfg: ForcedModelConfig) -> list[str]:
    """Drop caller --model flags and inject the specified CLI model."""
    forced = ["--model", cfg.spec.cli_model]
    out: list[str] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in {"--model", "-m"}:
            i += 2
            continue
        if arg.startswith("--model="):
            i += 1
            continue
        out.append(arg)
        i += 1
    if not out:
        return ["agent", *forced]
    insert_at = 1 if out[0] in {"agent", "cursor-agent"} else 0
    return [*out[:insert_at], *forced, *out[insert_at:]]
