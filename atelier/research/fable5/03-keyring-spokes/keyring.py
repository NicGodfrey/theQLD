"""BYOK key storage for Atelier.

Keys live in ``~/.atelier/keyring.json`` (file 0600, directory 0700).
Environment variables ALWAYS win over the file, so CI jobs and one-off
shells never need to write a key to disk. Keys never appear in argv, in
logs, or in repr() output.

Security properties enforced here:
  * the keyring file is written atomically (temp file + os.replace) and is
    created with mode 0600 before any secret byte is written;
  * a keyring file with group/other permission bits is tightened to 0600
    on first read (with a stderr warning);
  * a symlinked keyring file is refused outright;
  * the CLI reads keys via getpass or stdin — never via a --key argument,
    so secrets stay out of shell history and `ps` output.

Stdlib only. Python 3.9+. No relation to the PyPI "keyring" package.
"""
from __future__ import annotations

import getpass
import json
import os
import stat
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional

__all__ = ["Keyring", "KeyringError", "ProviderCreds", "mask",
           "ENV_VARS", "BASE_URL_ENV_VARS", "DEFAULT_PATH"]

DEFAULT_PATH = os.path.join(os.path.expanduser("~"), ".atelier", "keyring.json")

# Environment override order per provider: first hit wins.
# ATELIER_* names let users scope a key to Atelier without touching the
# conventional variable their other tooling reads.
ENV_VARS: Dict[str, tuple] = {
    "openai": ("ATELIER_OPENAI_API_KEY", "OPENAI_API_KEY"),
    "gemini": ("ATELIER_GEMINI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "anthropic": ("ATELIER_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
    "ollama": ("ATELIER_OLLAMA_API_KEY",),
    "openai_compatible": ("ATELIER_COMPAT_API_KEY",),
}

BASE_URL_ENV_VARS: Dict[str, tuple] = {
    "ollama": ("ATELIER_OLLAMA_BASE_URL",),
    "openai_compatible": ("ATELIER_COMPAT_BASE_URL",),
}


class KeyringError(RuntimeError):
    pass


def mask(key: Optional[str]) -> str:
    """Redact a key for display/logging: 'sk-a…wxyz'."""
    if not key:
        return "(none)"
    if len(key) <= 8:
        return "\u2026"
    return f"{key[:4]}\u2026{key[-4:]}"


@dataclass
class ProviderCreds:
    """Resolved credentials for one provider. repr() masks the key."""
    provider: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extras: dict = field(default_factory=dict)
    source: str = "none"      # "env:<VAR>" | "file" | "none"

    def __repr__(self) -> str:            # pragma: no cover - cosmetic
        return (f"ProviderCreds(provider={self.provider!r}, "
                f"api_key={mask(self.api_key)!r}, "
                f"base_url={self.base_url!r}, source={self.source!r})")


class Keyring:
    """Read/write access to the Atelier keyring.

    ``path`` defaults to $ATELIER_KEYRING or ~/.atelier/keyring.json.
    ``env`` defaults to os.environ; tests pass a plain dict for hermeticity.
    """

    def __init__(self, path: Optional[str] = None,
                 env: Optional[Mapping[str, str]] = None) -> None:
        self.path = path or os.environ.get("ATELIER_KEYRING") or DEFAULT_PATH
        self._env = os.environ if env is None else env
        self._warned_perms = False

    # -- resolution -----------------------------------------------------------

    def get(self, provider: str) -> ProviderCreds:
        """Resolve creds for a provider: env vars first, then the file."""
        provider = provider.strip().lower()
        entry = dict(self._entries().get(provider) or {})
        base_url = entry.get("base_url")
        for var in BASE_URL_ENV_VARS.get(provider, ()):
            val = (self._env.get(var) or "").strip()
            if val:
                base_url = val
                break
        extras = dict(entry.get("extras") or {})
        for var in ENV_VARS.get(provider, ()):
            val = (self._env.get(var) or "").strip()
            if val:
                return ProviderCreds(provider, val, base_url, extras,
                                     source=f"env:{var}")
        key = (entry.get("api_key") or "").strip() or None
        source = "file" if entry else "none"
        return ProviderCreds(provider, key, base_url, extras, source=source)

    def get_key(self, provider: str) -> Optional[str]:
        return self.get(provider).api_key

    def providers(self) -> list:
        """Providers with any configuration (file entries or live env vars)."""
        names = set(self._entries())
        for prov, env_vars in ENV_VARS.items():
            if any((self._env.get(v) or "").strip() for v in env_vars):
                names.add(prov)
        return sorted(names)

    # -- mutation -------------------------------------------------------------

    def set_key(self, provider: str, api_key: Optional[str], *,
                base_url: Optional[str] = None, **extras: Any) -> None:
        """Store/update a provider entry.

        ``api_key=None`` keeps any existing key (useful for updating just
        the base_url of an OpenAI-compatible endpoint).
        """
        provider = provider.strip().lower()
        if not provider:
            raise ValueError("provider name is required")
        data = self._load()
        entry = data["providers"].get(provider, {})
        if api_key is not None:
            api_key = api_key.strip()
            if not api_key:
                raise ValueError("refusing to store an empty API key")
            entry["api_key"] = api_key
        if base_url is not None:
            entry["base_url"] = base_url.strip() or None
        if extras:
            entry.setdefault("extras", {}).update(extras)
        entry["updated_at"] = int(time.time())
        data["providers"][provider] = entry
        self._save(data)

    def delete(self, provider: str) -> bool:
        data = self._load()
        removed = data["providers"].pop(provider.strip().lower(), None) is not None
        if removed:
            self._save(data)
        return removed

    # -- storage --------------------------------------------------------------

    def _entries(self) -> dict:
        return self._load()["providers"]

    def _load(self) -> dict:
        if os.path.islink(self.path):
            raise KeyringError(
                f"{self.path} is a symlink; refusing to read secrets "
                "through it")
        if not os.path.exists(self.path):
            return {"version": 1, "providers": {}}
        st = os.stat(self.path)
        if stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode) & 0o077:
            os.chmod(self.path, 0o600)
            if not self._warned_perms:
                print(f"[atelier-keyring] tightened permissions on "
                      f"{self.path} to 0600", file=sys.stderr)
                self._warned_perms = True
        with open(self.path, encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as err:
                raise KeyringError(f"{self.path} is not valid JSON: {err}") from err
        if not isinstance(data, dict) or not isinstance(data.get("providers"), dict):
            raise KeyringError(f"{self.path}: unexpected file structure")
        return data

    def _save(self, data: dict) -> None:
        parent = os.path.dirname(self.path) or "."
        os.makedirs(parent, mode=0o700, exist_ok=True)
        try:
            os.chmod(parent, 0o700)
        except OSError:
            pass
        fd, tmp = tempfile.mkstemp(dir=parent, prefix=".keyring-")
        try:
            os.fchmod(fd, 0o600)   # locked down BEFORE any secret is written
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, sort_keys=True)
                fh.write("\n")
            os.replace(tmp, self.path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise


# ------------------------------------------------------------------------
# CLI:  python keyring.py {set,get,list,delete,path} ...
# ------------------------------------------------------------------------

def _cmd_set(kr: Keyring, args) -> int:
    key: Optional[str] = None
    if not args.no_key:
        if args.stdin:
            key = sys.stdin.readline().strip()
        else:
            key = getpass.getpass(
                f"API key for {args.provider} (input hidden): ").strip()
        if not key:
            print("no key entered; nothing stored", file=sys.stderr)
            return 1
    kr.set_key(args.provider, key, base_url=args.base_url)
    stored = kr.get(args.provider)
    print(f"stored {args.provider}: key={mask(stored.api_key)}"
          + (f" base_url={stored.base_url}" if stored.base_url else "")
          + f"  ({kr.path})")
    return 0


def _cmd_get(kr: Keyring, args) -> int:
    creds = kr.get(args.provider)
    shown = creds.api_key if args.reveal else mask(creds.api_key)
    print(f"{creds.provider}: key={shown} source={creds.source}"
          + (f" base_url={creds.base_url}" if creds.base_url else ""))
    return 0 if creds.api_key or creds.base_url else 1


def _cmd_list(kr: Keyring, args) -> int:
    names = kr.providers()
    if not names:
        print(f"no providers configured (file: {kr.path})")
        return 0
    for name in names:
        creds = kr.get(name)
        line = f"{name:<20} key={mask(creds.api_key):<14} source={creds.source}"
        if creds.base_url:
            line += f" base_url={creds.base_url}"
        print(line)
    return 0


def _cmd_delete(kr: Keyring, args) -> int:
    if kr.delete(args.provider):
        print(f"deleted {args.provider} from {kr.path}")
        return 0
    print(f"{args.provider}: no stored entry", file=sys.stderr)
    return 1


def _main(argv) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Atelier keyring: store BYOK API keys locally "
                    "(0600 file; env vars always override)")
    parser.add_argument("--path", default=None,
                        help=f"keyring file (default: $ATELIER_KEYRING or {DEFAULT_PATH})")
    sub = parser.add_subparsers(dest="command", required=True)

    p_set = sub.add_parser("set", help="store a key (prompted, never via argv)")
    p_set.add_argument("provider")
    p_set.add_argument("--base-url", default=None,
                       help="endpoint for ollama / openai_compatible")
    p_set.add_argument("--stdin", action="store_true",
                       help="read the key from stdin instead of prompting")
    p_set.add_argument("--no-key", action="store_true",
                       help="store only metadata (e.g. base_url for ollama)")

    p_get = sub.add_parser("get", help="show a provider's resolved creds")
    p_get.add_argument("provider")
    p_get.add_argument("--reveal", action="store_true",
                       help="print the full key instead of a masked form")

    sub.add_parser("list", help="list configured providers (keys masked)")

    p_del = sub.add_parser("delete", help="remove a provider's stored entry")
    p_del.add_argument("provider")

    sub.add_parser("path", help="print the keyring file path")

    args = parser.parse_args(argv)
    kr = Keyring(path=args.path)
    if args.command == "set":
        return _cmd_set(kr, args)
    if args.command == "get":
        return _cmd_get(kr, args)
    if args.command == "list":
        return _cmd_list(kr, args)
    if args.command == "delete":
        return _cmd_delete(kr, args)
    if args.command == "path":
        print(kr.path)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
