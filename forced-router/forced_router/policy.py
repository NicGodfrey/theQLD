from __future__ import annotations

from typing import Any

from .config import ForcedModelConfig
from .rewrite import extract_model, is_auto_model, is_specified_model, normalize_model

BUILTIN_SUBAGENT_TYPES = frozenset(
    {"explore", "shell", "bash", "browser", "cursor-guide"}
)


def _model_label(value: Any) -> str:
    name = normalize_model(value)
    return name or "(empty)"


def allow_prompt(payload: dict[str, Any], cfg: ForcedModelConfig) -> tuple[bool, str]:
    model = extract_model(payload)
    missing = model in (None, "")
    if missing:
        if cfg.policy.allow_when_model_missing:
            return True, ""
        return False, (
            f"Model field missing. Select {cfg.spec.display} ({cfg.spec.cli_model}) "
            "in the picker. Auto is not allowed in this repo."
        )
    if is_specified_model(model, cfg):
        return True, ""
    if is_auto_model(model, cfg) and cfg.policy.block_auto_in_ide:
        return False, (
            f"Cursor Auto / Router is blocked in this project. "
            f"Switch the model picker to {cfg.spec.display} ({cfg.spec.cli_model}). "
            f"Edit .cursor/forced-model.json to change the specified model."
        )
    if cfg.policy.block_other_models_in_ide:
        return False, (
            f"Model {_model_label(model)} is not allowed. "
            f"Use {cfg.spec.display} ({cfg.spec.cli_model})."
        )
    return True, ""


def allow_subagent(payload: dict[str, Any], cfg: ForcedModelConfig) -> tuple[bool, str]:
    if not cfg.policy.deny_mismatched_subagents:
        return True, ""
    subagent_type = str(payload.get("subagent_type") or "").lower()
    if subagent_type in BUILTIN_SUBAGENT_TYPES:
        return True, ""
    model = payload.get("subagent_model") or extract_model(payload)
    if model in (None, "") or normalize_model(model) in {"inherit", "parent"}:
        return False, (
            f"Subagent model inherit/Auto is denied. "
            f"Pin subagents to {cfg.spec.subagent_model}."
        )
    if is_specified_model(model, cfg):
        return True, ""
    if is_auto_model(model, cfg):
        return False, (
            f"Subagent Auto routing is denied. Use {cfg.spec.subagent_model}."
        )
    return False, (
        f"Subagent model {_model_label(model)} is not the specified model "
        f"{cfg.spec.subagent_model}."
    )


def hook_response(payload: dict[str, Any], cfg: ForcedModelConfig) -> dict[str, Any]:
    event = str(payload.get("hook_event_name") or "")
    if event == "subagentStart" or "subagent_model" in payload or "subagent_type" in payload:
        ok, message = allow_subagent(payload, cfg)
        body: dict[str, Any] = {"permission": "allow" if ok else "deny"}
        if message:
            body["user_message"] = message
        return body
    ok, message = allow_prompt(payload, cfg)
    body = {"continue": ok}
    if not ok:
        body["user_message"] = message
    return body
