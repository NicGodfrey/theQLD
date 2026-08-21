"""Spoke protocol — official-host adapters only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


class SpokeError(RuntimeError):
    pass


@dataclass
class ChatResult:
    text: str
    provider: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    raw: dict = field(default_factory=dict)


@dataclass
class ImageResult:
    data: bytes
    mime: str
    provider: str
    model: str
    prompt: str
    raw: dict = field(default_factory=dict)


class Spoke:
    name = "base"

    def chat(self, messages: list[dict], model: str, **kwargs) -> ChatResult:
        raise NotImplementedError

    def image(self, prompt: str, model: str, **kwargs) -> ImageResult:
        raise NotImplementedError


def assert_official_host(
    url: str,
    allowed_suffixes: tuple[str, ...],
    *,
    require_https: bool = False,
) -> None:
    parsed = urlparse(url)
    if require_https and (parsed.scheme or "").lower() != "https":
        raise SpokeError(f"Refusing non-https official host ({parsed.scheme or 'missing'})")
    host = (parsed.hostname or "").lower()
    if not host:
        raise SpokeError(f"Refusing empty host for {url}")
    if not any(host == s or host.endswith("." + s) for s in allowed_suffixes):
        raise SpokeError(f"Refusing unofficial host {host}")


def is_blocked_fetch_host(host: str) -> bool:
    """Loopback / link-local / RFC1918 / non-global IPs — never fetch an image URL here."""
    import ipaddress
    import socket

    host = (host or "").lower().rstrip(".")
    if not host:
        return True
    if host == "localhost" or host.endswith(".localhost"):
        return True
    candidate = host.strip("[]")
    try:
        ip = ipaddress.ip_address(candidate)
    except ValueError:
        try:
            # inet_aton mirrors the connector's legacy IPv4 parsing, so
            # "127.1", "0x7f.0.0.1" and "2130706433" all count as loopback.
            ip = ipaddress.IPv4Address(socket.inet_aton(candidate))
        except OSError:
            return False
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None:
        ip = mapped
    return not ip.is_global


class DemoSpoke(Spoke):
    name = "demo"

    def chat(self, messages: list[dict], model: str = "demo-conductor", **kwargs) -> ChatResult:
        import json

        system = " ".join(m.get("content") or "" for m in messages if m.get("role") == "system")
        user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        brief = user
        if "Brief:" in user:
            brief = user.split("Brief:", 1)[-1].strip().split("\n")[0].strip()
        if "Critic" in system:
            text = (
                "Type hierarchy is readable and the navy field is quiet enough for a public-interest brand. "
                "Next: lock a two-colour kit and pin one category grid, not a collage of icons."
            )
            return ChatResult(text=text, provider="demo", model=model, tokens_in=len(user) // 4, tokens_out=40)
        plan = {
            "mode": "fast",
            "intent": (brief or user)[:240],
            "score": {"audience": "public", "format": "poster", "constraints": ["readable type", "calm navy"]},
            "route": {"provider": "demo", "model": model, "capability": "image"},
            "weave": [{"kind": "image", "prompt": brief or user or "abstract studio mark", "count": 1}],
            "notes": "Demo spoke — no third-party quota used.",
        }
        return ChatResult(
            text=json.dumps(plan, ensure_ascii=False),
            provider="demo",
            model=model,
            tokens_in=len(user) // 4,
            tokens_out=40,
        )

    def image(self, prompt: str, model: str = "demo-svg", **kwargs) -> ImageResult:
        from atelier.helix.loom import demo_svg

        return ImageResult(
            data=demo_svg(
                prompt,
                title=kwargs.get("title") or "Atelier",
                palette=kwargs.get("palette"),
            ).encode("utf-8"),
            mime="image/svg+xml",
            provider="demo",
            model=model,
            prompt=prompt,
        )
