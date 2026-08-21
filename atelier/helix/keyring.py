"""Local BYOK vault. Keys leave this process only toward official provider hosts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

ENV_MAP = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "ollama": "OLLAMA_HOST",
    "openai_compat": "OPENAI_COMPAT_API_KEY",
}

DEFAULT_HOSTS = {
    "openai": "https://api.openai.com",
    "gemini": "https://generativelanguage.googleapis.com",
    "anthropic": "https://api.anthropic.com",
    "ollama": "http://127.0.0.1:11434",
    "openai_compat": "",
}

ALLOWED_HOST_SUFFIXES = {
    "openai": ("api.openai.com",),
    "gemini": ("generativelanguage.googleapis.com",),
    "anthropic": ("api.anthropic.com",),
    "ollama": ("127.0.0.1", "localhost"),
}


def default_path() -> Path:
    override = os.environ.get("ATELIER_HOME")
    root = Path(override) if override else Path.home() / ".atelier"
    return root / "keyring.json"


class Keyring:
    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path) if path else default_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict:
        if not self.path.exists():
            return {"providers": {}}
        return json.loads(self.path.read_text())

    def _save(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2) + "\n")
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass

    def get_secret(self, provider: str) -> str:
        env_name = ENV_MAP.get(provider)
        if env_name and os.environ.get(env_name):
            return os.environ[env_name].strip()
        stored = self._load().get("providers", {}).get(provider, {})
        return (stored.get("key") or "").strip()

    def get_base_url(self, provider: str) -> str:
        stored = self._load().get("providers", {}).get(provider, {})
        return (stored.get("base_url") or DEFAULT_HOSTS.get(provider) or "").rstrip("/")

    def put(self, provider: str, key: str = "", base_url: str = "") -> dict:
        data = self._load()
        providers = data.setdefault("providers", {})
        entry = providers.get(provider, {})
        if key:
            entry["key"] = key.strip()
        if base_url:
            entry["base_url"] = base_url.strip().rstrip("/")
        elif "base_url" not in entry:
            entry["base_url"] = DEFAULT_HOSTS.get(provider, "")
        providers[provider] = entry
        self._save(data)
        return self.public_status()

    def delete(self, provider: str) -> dict:
        data = self._load()
        data.get("providers", {}).pop(provider, None)
        self._save(data)
        return self.public_status()

    def public_status(self) -> dict:
        """Never returns raw keys."""
        out = {}
        for provider in ENV_MAP:
            secret = self.get_secret(provider)
            out[provider] = {
                "configured": bool(secret),
                "source": "env" if (ENV_MAP.get(provider) and os.environ.get(ENV_MAP[provider])) else (
                    "keyring" if secret else "none"
                ),
                "base_url": self.get_base_url(provider),
                "hint": (secret[:3] + "…" + secret[-4:]) if len(secret) > 8 else ("set" if secret else ""),
            }
        return out
