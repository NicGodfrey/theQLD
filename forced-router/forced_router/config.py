from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_AUTO_ALIASES = (
    "auto",
    "auto-smart",
    "default",
    "cursor-auto",
    "composer-auto",
    "cursor-router",
    "smart-auto",
)


@dataclass(frozen=True)
class ModelSpec:
    id: str
    display: str
    cli_model: str
    subagent_model: str
    params: tuple[dict[str, str], ...] = ()
    match: tuple[str, ...] = ()

    def api_model(self) -> dict[str, Any]:
        body: dict[str, Any] = {"id": self.id}
        if self.params:
            body["params"] = [dict(p) for p in self.params]
        return body


@dataclass(frozen=True)
class Policy:
    block_auto_in_ide: bool = True
    block_other_models_in_ide: bool = True
    deny_mismatched_subagents: bool = True
    force_all_api_models: bool = True
    allow_when_model_missing: bool = True


@dataclass(frozen=True)
class ForcedModelConfig:
    spec: ModelSpec
    auto_aliases: frozenset[str]
    policy: Policy
    source_path: Path
    specified_key: str
    presets: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.spec.id

    @property
    def display(self) -> str:
        return self.spec.display

    @property
    def cli_model(self) -> str:
        return self.spec.cli_model

    @property
    def subagent_model(self) -> str:
        return self.spec.subagent_model


def find_config_path(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for path in [cur, *cur.parents]:
        candidate = path / ".cursor" / "forced-model.json"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "No .cursor/forced-model.json found. Create one to specify the forced model."
    )


def _as_params(raw: Any) -> tuple[dict[str, str], ...]:
    if not raw:
        return ()
    out: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict) or "id" not in item:
            continue
        out.append({"id": str(item["id"]), "value": str(item.get("value", ""))})
    return tuple(out)


def spec_from_mapping(raw: dict[str, Any], fallback_id: str) -> ModelSpec:
    model_id = str(raw.get("id") or fallback_id)
    return ModelSpec(
        id=model_id,
        display=str(raw.get("display") or model_id),
        cli_model=str(raw.get("cli_model") or model_id),
        subagent_model=str(raw.get("subagent_model") or model_id),
        params=_as_params(raw.get("params")),
        match=tuple(str(x) for x in raw.get("match") or (model_id,)),
    )


def parse_config(data: dict[str, Any], source_path: Path) -> ForcedModelConfig:
    specified = data.get("specified_model", "fable5")
    presets = data.get("presets") or {}
    if isinstance(specified, dict):
        spec = spec_from_mapping(specified, "custom")
        specified_key = str(specified.get("id") or "custom")
    elif isinstance(specified, str) and specified in presets:
        spec = spec_from_mapping(presets[specified], specified)
        specified_key = specified
    elif isinstance(specified, str):
        spec = spec_from_mapping({"id": specified}, specified)
        specified_key = specified
    else:
        raise ValueError("specified_model must be a preset name, model id, or object")

    aliases = data.get("auto_aliases") or DEFAULT_AUTO_ALIASES
    policy_raw = data.get("policy") or {}
    policy = Policy(
        block_auto_in_ide=bool(policy_raw.get("block_auto_in_ide", True)),
        block_other_models_in_ide=bool(policy_raw.get("block_other_models_in_ide", True)),
        deny_mismatched_subagents=bool(policy_raw.get("deny_mismatched_subagents", True)),
        force_all_api_models=bool(policy_raw.get("force_all_api_models", True)),
        allow_when_model_missing=bool(policy_raw.get("allow_when_model_missing", True)),
    )
    return ForcedModelConfig(
        spec=spec,
        auto_aliases=frozenset(str(a).strip().lower() for a in aliases if str(a).strip()),
        policy=policy,
        source_path=source_path,
        specified_key=specified_key,
        presets=presets if isinstance(presets, dict) else {},
    )


def load_config(start: Path | None = None) -> ForcedModelConfig:
    path = find_config_path(start)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return parse_config(data, path)


def dump_public(cfg: ForcedModelConfig) -> dict[str, Any]:
    return {
        "specified_model": cfg.specified_key,
        "id": cfg.spec.id,
        "display": cfg.spec.display,
        "cli_model": cfg.spec.cli_model,
        "subagent_model": cfg.spec.subagent_model,
        "params": [dict(p) for p in cfg.spec.params],
        "auto_aliases": sorted(cfg.auto_aliases),
        "policy": {
            "block_auto_in_ide": cfg.policy.block_auto_in_ide,
            "block_other_models_in_ide": cfg.policy.block_other_models_in_ide,
            "deny_mismatched_subagents": cfg.policy.deny_mismatched_subagents,
            "force_all_api_models": cfg.policy.force_all_api_models,
            "allow_when_model_missing": cfg.policy.allow_when_model_missing,
        },
        "source": str(cfg.source_path),
    }
