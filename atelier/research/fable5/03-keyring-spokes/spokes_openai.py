"""OpenAI spoke for Atelier — official https://api.openai.com only.

This one class also powers two more providers, because they speak the same
wire protocol:

  * ``ollama_spoke()``      -> local Ollama at http://127.0.0.1:11434/v1
  * ``compatible_spoke()``  -> any generic OpenAI-compatible server the
                               user explicitly configures (vLLM, LM Studio,
                               llama.cpp server, a corporate proxy, ...)

Hard rules honored here:
  * provider_id "openai" is PINNED to api.openai.com — passing any other
    base_url raises KeyLeakError at construction time; there is no code
    path that talks to the consumer chat website or reuses browser
    sessions/cookies;
  * every credentialed request goes through assert_key_safe(), which
    refuses non-official hosts and refuses plaintext HTTP off loopback;
  * every completed call is written to the usage ledger.

Stdlib only (urllib via spokes_base). Python 3.9+.
"""
from __future__ import annotations

import base64
from typing import Any, Callable, Optional, Sequence

from spokes_base import (AuthError, ChatMessage, ChatResult, ImageResult,
                         KeyLeakError, NotSupported, ProviderError, Spoke,
                         Usage, UrllibTransport, assert_key_safe,
                         default_keyring, default_ledger, host_of, http_call,
                         iter_sse_json)

__all__ = ["OpenAISpoke", "ollama_spoke", "compatible_spoke",
           "DEFAULT_BASE_URL", "OFFICIAL_HOST"]

DEFAULT_BASE_URL = "https://api.openai.com/v1"
OFFICIAL_HOST = "api.openai.com"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"


class OpenAISpoke(Spoke):
    """Chat (+streaming) and image generation over the OpenAI wire API."""

    def __init__(self, api_key: Optional[str] = None, *,
                 provider_id: str = "openai",
                 base_url: Optional[str] = None,
                 fallback_base_url: Optional[str] = None,
                 keyring: Any = None,
                 ledger: Any = None,
                 record_usage: bool = True,
                 transport: Any = None,
                 timeout: float = 120.0,
                 organization: Optional[str] = None,
                 default_chat_model: str = "gpt-4o-mini",
                 default_image_model: str = "gpt-image-1",
                 capabilities: Optional[Sequence[str]] = None) -> None:
        self.provider_id = provider_id
        self.timeout = timeout
        self.organization = organization
        self.default_chat_model = default_chat_model
        self.default_image_model = default_image_model
        self._transport = transport if transport is not None else UrllibTransport()

        # Only touch the keyring/env when the caller left something for us
        # to resolve; explicit arguments keep construction fully hermetic.
        creds = None
        need_creds = api_key is None or (provider_id != "openai" and base_url is None)
        if need_creds:
            kr = keyring if keyring is not None else default_keyring()
            if kr is not None:
                creds = kr.get(provider_id)

        if provider_id == "openai":
            if base_url not in (None, DEFAULT_BASE_URL, DEFAULT_BASE_URL + "/"):
                raise KeyLeakError(
                    "the 'openai' spoke is pinned to https://api.openai.com; "
                    "use compatible_spoke()/ollama_spoke() for other "
                    "endpoints", provider=provider_id)
            base_url = DEFAULT_BASE_URL
        else:
            if base_url is None and creds is not None and creds.base_url:
                base_url = creds.base_url
            if base_url is None:
                base_url = fallback_base_url
            if not base_url:
                raise ValueError(
                    f"provider {provider_id!r} needs a base_url (constructor "
                    "argument, or `python keyring.py set "
                    f"{provider_id} --no-key --base-url ...`)")
        self.base_url = base_url.rstrip("/")
        self.allowed_hosts = (host_of(self.base_url),)

        if api_key is None and creds is not None:
            api_key = creds.api_key
        self.api_key = (api_key or "").strip() or None
        if provider_id == "openai" and self.api_key is None:
            raise AuthError(
                "no OpenAI API key found - set OPENAI_API_KEY or run "
                "`python keyring.py set openai`", provider=provider_id)

        if capabilities is None:
            capabilities = (("chat", "chat_stream", "image")
                            if provider_id == "openai"
                            else ("chat", "chat_stream"))
        self._caps = frozenset(capabilities)
        self._ledger = None
        if record_usage:
            self._ledger = ledger if ledger is not None else default_ledger()

    # -- plumbing -------------------------------------------------------------

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json",
                   "User-Agent": "atelier-spoke/1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if self.organization:
            headers["OpenAI-Organization"] = self.organization
        return headers

    def _post(self, path: str, payload: dict, *, stream: bool = False):
        url = f"{self.base_url}{path}"
        if self.api_key:
            assert_key_safe(url, self.allowed_hosts, self.provider_id)
        return http_call(self._transport, "POST", url, headers=self._headers(),
                         payload=payload, provider=self.provider_id,
                         timeout=self.timeout, stream=stream)

    @staticmethod
    def _wire_message(msg: ChatMessage) -> dict:
        if isinstance(msg.content, str):
            return {"role": msg.role, "content": msg.content}
        parts = []
        for part in msg.parts():
            if part.kind == "text":
                parts.append({"type": "text", "text": part.text})
            elif part.kind == "image":
                b64 = base64.b64encode(part.data).decode("ascii")
                parts.append({"type": "image_url", "image_url": {
                    "url": f"data:{part.mime};base64,{b64}"}})
            else:
                raise NotSupported(f"unknown message part kind {part.kind!r}")
        return {"role": msg.role, "content": parts}

    @staticmethod
    def _usage_from(raw: Optional[dict]) -> Usage:
        raw = raw or {}
        return Usage(input_tokens=int(raw.get("prompt_tokens") or 0),
                     output_tokens=int(raw.get("completion_tokens") or 0))

    # -- chat -----------------------------------------------------------------

    def chat(self, messages: Sequence[ChatMessage], *,
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream_cb: Optional[Callable[[str], None]] = None,
             **extra: Any) -> ChatResult:
        model = model or self.default_chat_model
        payload: dict = {"model": model,
                         "messages": [self._wire_message(m) for m in messages]}
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            # api.openai.com deprecated `max_tokens` in favour of
            # `max_completion_tokens`; most compatible servers (Ollama,
            # vLLM, LM Studio) still expect the old name.
            key = ("max_completion_tokens" if self.provider_id == "openai"
                   else "max_tokens")
            payload[key] = max_tokens
        payload.update(extra)
        if stream_cb is not None:
            return self._chat_stream(payload, stream_cb)

        data = self._post("/chat/completions", payload).json()
        choice = (data.get("choices") or [{}])[0]
        text = ((choice.get("message") or {}).get("content")) or ""
        usage = self._usage_from(data.get("usage"))
        self._record("chat", data.get("model") or model, usage,
                     meta={"stream": False})
        return ChatResult(text=text, model=data.get("model") or model,
                          provider=self.provider_id, usage=usage,
                          finish_reason=choice.get("finish_reason") or "",
                          raw=data)

    def _chat_stream(self, payload: dict,
                     stream_cb: Callable[[str], None]) -> ChatResult:
        payload = dict(payload)
        payload["stream"] = True
        # Callers hitting a compat server that rejects stream_options can
        # pass stream_options=None through **extra to drop it.
        payload.setdefault("stream_options", {"include_usage": True})
        if payload.get("stream_options") is None:
            payload.pop("stream_options")
        model = payload["model"]

        resp = self._post("/chat/completions", payload, stream=True)
        pieces: list = []
        finish, usage_raw, last_event = "", None, None
        for event in iter_sse_json(resp):
            last_event = event
            if event.get("usage"):
                usage_raw = event["usage"]
            for choice in event.get("choices") or []:
                delta = (choice.get("delta") or {}).get("content")
                if delta:
                    pieces.append(delta)
                    stream_cb(delta)
                if choice.get("finish_reason"):
                    finish = choice["finish_reason"]
        text = "".join(pieces)
        usage = self._usage_from(usage_raw)
        meta = {"stream": True}
        if usage_raw is None:
            meta["usage_missing"] = True
        self._record("chat", model, usage, meta=meta)
        return ChatResult(text=text, model=model, provider=self.provider_id,
                          usage=usage, finish_reason=finish, raw=last_event)

    # -- images ---------------------------------------------------------------

    def generate_image(self, prompt: str, *,
                       model: Optional[str] = None,
                       size: str = "1024x1024",
                       n: int = 1,
                       quality: Optional[str] = None,
                       **extra: Any) -> ImageResult:
        if "image" not in self._caps:
            raise NotSupported(
                f"{self.provider_id}: image generation is not enabled for "
                "this endpoint", provider=self.provider_id)
        model = model or self.default_image_model
        payload: dict = {"model": model, "prompt": prompt, "n": n, "size": size}
        if quality:
            payload["quality"] = quality
        if model.startswith("dall-e"):
            # gpt-image-1 always returns b64 and rejects this parameter;
            # dall-e defaults to short-lived URLs unless asked for b64.
            payload.setdefault("response_format", "b64_json")
        payload.update(extra)

        data = self._post("/images/generations", payload).json()
        images = []
        for item in data.get("data") or []:
            b64 = item.get("b64_json")
            if b64:
                images.append(base64.b64decode(b64))
        if not images:
            raise ProviderError(f"{self.provider_id}: response contained no "
                                "image payload", provider=self.provider_id)
        raw_usage = data.get("usage") or {}
        usage = Usage(input_tokens=int(raw_usage.get("input_tokens") or 0),
                      output_tokens=int(raw_usage.get("output_tokens") or 0))
        self._record("image", model, usage, images=len(images), size=size,
                     quality=quality or "")
        return ImageResult(images=images, mime="image/png", model=model,
                           provider=self.provider_id, usage=usage, raw=data)


# --------------------------------------------------------------------------
# Factories for the OpenAI-compatible family
# --------------------------------------------------------------------------

def ollama_spoke(base_url: Optional[str] = None, **kwargs: Any) -> OpenAISpoke:
    """Local Ollama over its OpenAI-compatible endpoint. Keyless by
    default; base_url resolves explicit arg > keyring/env > localhost."""
    kwargs.setdefault("provider_id", "ollama")
    kwargs.setdefault("default_chat_model", "llama3.1:8b")
    kwargs.setdefault("fallback_base_url", DEFAULT_OLLAMA_BASE_URL)
    return OpenAISpoke(base_url=base_url, **kwargs)


def compatible_spoke(base_url: Optional[str] = None, *,
                     provider_id: str = "openai_compatible",
                     **kwargs: Any) -> OpenAISpoke:
    """Any generic OpenAI-compatible server the USER explicitly configured.
    The API key (if any) is only ever sent to that configured host, and
    only over HTTPS unless the host is loopback."""
    return OpenAISpoke(base_url=base_url, provider_id=provider_id, **kwargs)
