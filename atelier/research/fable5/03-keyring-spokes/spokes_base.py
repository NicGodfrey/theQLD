"""Atelier spoke contract: shared types, errors, transport, and helpers.

Every provider adapter ("spoke") builds on this module. The security
invariants live HERE, in one place, so no individual spoke can forget them:

  * ``assert_key_safe()`` refuses to send a credentialed request anywhere
    except the spoke's pinned official host(s), and refuses plaintext HTTP
    for any non-loopback host.
  * ``UrllibTransport`` never follows redirects, because urllib would
    replay the original headers (including ``Authorization``) against an
    attacker-chosen ``Location`` target.
  * All network I/O flows through a ``Transport`` object so the test suite
    can substitute a scripted fake and never open a socket.

Stdlib only. Python 3.9+. See CONTRACT.md for the full interface spec.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import (Any, Callable, Iterator, Mapping, Optional, Sequence,
                    Union)

__all__ = [
    "SpokeError", "AuthError", "RateLimitError", "ProviderError",
    "NotSupported", "KeyLeakError",
    "Part", "ChatMessage", "Usage", "ChatResult", "ImageResult",
    "VideoResult", "Spoke",
    "HttpResponse", "UrllibTransport",
    "assert_key_safe", "host_of", "http_call", "iter_sse_json",
    "default_keyring", "default_ledger",
]

# --------------------------------------------------------------------------
# Errors
# --------------------------------------------------------------------------

class SpokeError(Exception):
    """Base error for all spoke failures."""

    def __init__(self, message: str, *, provider: str = "", status: int = 0,
                 code: str = "", retryable: bool = False) -> None:
        super().__init__(message)
        self.provider = provider
        self.status = status
        self.code = code
        self.retryable = retryable


class AuthError(SpokeError):
    """401/403 or a missing/invalid API key."""


class RateLimitError(SpokeError):
    """429 — the provider throttled us or the account quota ran out."""


class ProviderError(SpokeError):
    """Any other provider-side or network failure."""


class NotSupported(SpokeError):
    """The spoke does not implement the requested capability."""


class KeyLeakError(SpokeError):
    """We refused to send a credential somewhere unsafe. This firing is a
    bug in the caller's configuration, never a provider problem."""


# --------------------------------------------------------------------------
# Message / result types
# --------------------------------------------------------------------------

@dataclass
class Part:
    """One piece of multimodal content inside a chat message."""
    kind: str                 # "text" | "image"
    text: str = ""
    data: bytes = b""         # raw image bytes when kind == "image"
    mime: str = "image/png"


@dataclass
class ChatMessage:
    """Provider-neutral chat message.

    ``content`` is either a plain string (text-only, the common case) or a
    sequence of Parts for multimodal input.
    """
    role: str                                   # "system" | "user" | "assistant"
    content: Union[str, Sequence[Part]]

    def parts(self) -> "list[Part]":
        if isinstance(self.content, str):
            return [Part("text", text=self.content)]
        return list(self.content)

    def text(self) -> str:
        return "".join(p.text for p in self.parts() if p.kind == "text")


@dataclass
class Usage:
    """Normalized usage for one call. ``est_usd`` is filled in by the
    ledger when a price is known, else left as None (never guessed)."""
    input_tokens: int = 0
    output_tokens: int = 0
    images: int = 0
    est_usd: Optional[float] = None


@dataclass
class ChatResult:
    text: str
    model: str
    provider: str
    usage: Usage
    finish_reason: str = ""
    raw: Any = None           # the provider's decoded response, for debugging


@dataclass
class ImageResult:
    images: "list[bytes]"     # decoded image bytes, one entry per image
    mime: str
    model: str
    provider: str
    usage: Usage
    text: str = ""            # some providers interleave text (Gemini does)
    raw: Any = None


@dataclass
class VideoResult:
    video: bytes
    mime: str
    model: str
    provider: str
    usage: Usage
    raw: Any = None


# --------------------------------------------------------------------------
# Spoke base class
# --------------------------------------------------------------------------

class Spoke:
    """Abstract provider adapter. Concrete spokes override the methods for
    the capabilities they advertise; everything else raises NotSupported."""

    provider_id: str = ""
    _caps: frozenset = frozenset()
    _ledger: Any = None       # duck-typed: anything with .record(**kw)

    def capabilities(self) -> frozenset:
        """Subset of {"chat", "chat_stream", "image", "video"}."""
        return self._caps

    def chat(self, messages: Sequence[ChatMessage], *,
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream_cb: Optional[Callable[[str], None]] = None,
             **extra: Any) -> ChatResult:
        raise NotSupported(f"{self.provider_id or type(self).__name__}: "
                           "chat is not supported", provider=self.provider_id)

    def generate_image(self, prompt: str, *,
                       model: Optional[str] = None,
                       size: str = "1024x1024",
                       n: int = 1,
                       quality: Optional[str] = None,
                       **extra: Any) -> ImageResult:
        raise NotSupported(f"{self.provider_id or type(self).__name__}: "
                           "image generation is not supported",
                           provider=self.provider_id)

    def generate_video(self, prompt: str, *,
                       model: Optional[str] = None,
                       seconds: int = 4,
                       size: Optional[str] = None,
                       **extra: Any) -> VideoResult:
        # Contract stub: the signature and VideoResult are reserved now so
        # the hub does not need to change when Sora / Veo adapters land.
        # See CONTRACT.md §Video.
        raise NotSupported(
            f"{self.provider_id or type(self).__name__}: video generation is "
            "a contract stub for this spoke (see CONTRACT.md §Video)",
            provider=self.provider_id)

    # -- shared ledger hook -------------------------------------------------

    def _record(self, kind: str, model: str, usage: Usage, *,
                images: int = 0, size: str = "", quality: str = "",
                meta: Optional[dict] = None) -> None:
        """Write one row to the usage ledger and back-fill usage.est_usd."""
        usage.images = images
        if self._ledger is None:
            return
        rec = self._ledger.record(
            provider=self.provider_id, model=model, kind=kind,
            input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
            images=images, size=size, quality=quality, meta=meta)
        usage.est_usd = rec.est_usd if rec.priced else None


# --------------------------------------------------------------------------
# Transport
# --------------------------------------------------------------------------

@dataclass
class HttpResponse:
    """Uniform response wrapper for real and fake transports."""
    status: int
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""
    _line_iter: Optional[Iterator[bytes]] = None

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def header(self, name: str, default: str = "") -> str:
        for k, v in self.headers.items():
            if k.lower() == name.lower():
                return v
        return default

    def iter_lines(self) -> Iterator[bytes]:
        if self._line_iter is not None:
            yield from self._line_iter
        else:
            yield from self.body.splitlines()


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Returning None makes urllib raise the 3xx as an HTTPError instead
        # of replaying our headers (Authorization included) at `newurl`.
        return None


class UrllibTransport:
    """Real HTTP transport on urllib. Redirects are hard-disabled."""

    def __init__(self) -> None:
        self._opener = urllib.request.build_opener(_NoRedirect())

    def request(self, method: str, url: str, *,
                headers: Optional[Mapping[str, str]] = None,
                body: Optional[bytes] = None,
                timeout: float = 120.0,
                stream: bool = False) -> HttpResponse:
        req = urllib.request.Request(url, data=body, method=method)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            resp = self._opener.open(req, timeout=timeout)
        except urllib.error.HTTPError as err:
            data = err.read()
            err.close()
            return HttpResponse(err.code, dict(err.headers or {}), data)
        except urllib.error.URLError as err:
            raise ProviderError(f"network error calling {url!r}: {err.reason}",
                                retryable=True) from err
        status = getattr(resp, "status", None) or resp.getcode()
        hdrs = dict(resp.headers)
        if stream:
            return HttpResponse(status, hdrs, _line_iter=_close_after(resp))
        with resp:
            return HttpResponse(status, hdrs, resp.read())


def _close_after(resp) -> Iterator[bytes]:
    try:
        for line in resp:
            yield line
    finally:
        resp.close()


# --------------------------------------------------------------------------
# Key-safety guard
# --------------------------------------------------------------------------

_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}


def host_of(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def assert_key_safe(url: str, allowed_hosts: Sequence[str], provider: str) -> None:
    """Refuse to let a credentialed request leave for anywhere except the
    provider's official host, over anything except TLS (loopback exempt).

    Call this before EVERY request that carries an API key. It raises
    KeyLeakError before a single byte hits the network.
    """
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower()
    allowed = {h.lower() for h in allowed_hosts}
    if host not in allowed:
        raise KeyLeakError(
            f"{provider}: refusing to send credentials to {host!r}; "
            f"allowed hosts: {sorted(allowed)}", provider=provider)
    if parts.scheme != "https" and host not in _LOOPBACK_HOSTS:
        raise KeyLeakError(
            f"{provider}: refusing to send credentials over "
            f"{parts.scheme!r} to non-loopback host {host!r}; use https",
            provider=provider)


# --------------------------------------------------------------------------
# Request helper: JSON in, retries on 429/5xx, mapped errors out
# --------------------------------------------------------------------------

RETRYABLE_STATUS = (429, 500, 502, 503, 504)


def http_call(transport: Any, method: str, url: str, *,
              headers: Mapping[str, str],
              payload: Optional[Any],
              provider: str,
              timeout: float = 120.0,
              retries: int = 2,
              stream: bool = False,
              sleep: Callable[[float], None] = time.sleep) -> HttpResponse:
    """POST/GET with bounded retries. Returns the HttpResponse on 2xx,
    raises a mapped SpokeError subclass otherwise."""
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    attempt = 0
    while True:
        resp = transport.request(method, url, headers=dict(headers),
                                 body=body, timeout=timeout, stream=stream)
        if resp.status in RETRYABLE_STATUS and attempt < retries:
            sleep(_retry_delay(resp, attempt))
            attempt += 1
            continue
        if resp.status >= 400:
            raise error_for_status(resp, provider)
        return resp


def _retry_delay(resp: HttpResponse, attempt: int) -> float:
    retry_after = resp.header("Retry-After")
    if retry_after:
        try:
            return max(0.0, float(retry_after))
        except ValueError:
            pass
    return min(8.0, 0.5 * (2 ** attempt))


def error_for_status(resp: HttpResponse, provider: str) -> SpokeError:
    """Map an HTTP error response to the spoke error taxonomy."""
    detail, code = "", ""
    try:
        parsed = json.loads(resp.body.decode("utf-8", "replace"))
        err = parsed.get("error") if isinstance(parsed, dict) else None
        if isinstance(err, dict):
            detail = str(err.get("message") or "")
            code = str(err.get("code") or err.get("status") or err.get("type") or "")
        elif isinstance(err, str):
            detail = err
    except (json.JSONDecodeError, AttributeError):
        detail = resp.body[:400].decode("utf-8", "replace")
    msg = f"{provider}: HTTP {resp.status}" + (f" - {detail}" if detail else "")
    kw = dict(provider=provider, status=resp.status, code=code)
    if resp.status in (401, 403):
        return AuthError(msg, **kw)
    if resp.status == 429:
        return RateLimitError(msg, retryable=True, **kw)
    return ProviderError(msg, retryable=resp.status >= 500, **kw)


# --------------------------------------------------------------------------
# SSE helper
# --------------------------------------------------------------------------

def iter_sse_json(resp: HttpResponse) -> Iterator[Any]:
    """Yield parsed JSON payloads from a server-sent-events body.

    Handles the framing used by OpenAI, Gemini (?alt=sse), and Anthropic:
    ``data: {json}`` lines, blank separators, optional ``event:`` lines
    (skipped), and OpenAI's ``data: [DONE]`` terminator.
    """
    for raw in resp.iter_lines():
        line = raw.strip()
        if not line.startswith(b"data:"):
            continue
        data = line[len(b"data:"):].strip()
        if data == b"[DONE]":
            return
        try:
            yield json.loads(data.decode("utf-8"))
        except json.JSONDecodeError:
            continue


# --------------------------------------------------------------------------
# Lazy default collaborators (keep spoke modules importable standalone)
# --------------------------------------------------------------------------

def default_keyring() -> Any:
    """Best-effort default Keyring; None if the sibling module is absent."""
    try:
        import keyring as _keyring_mod
        return _keyring_mod.Keyring()
    except Exception:
        return None


def default_ledger() -> Any:
    """Best-effort default Ledger; None if the sibling module is absent."""
    try:
        import ledger as _ledger_mod
        return _ledger_mod.Ledger()
    except Exception:
        return None
