"""Anthropic spoke for Atelier (optional provider) — official
https://api.anthropic.com Messages API only.

Chat and streaming chat; no image or video generation (Claude models do
not generate images). Auth is the user's own key in ``x-api-key``.

Stdlib only (urllib via spokes_base). Python 3.9+.
"""
from __future__ import annotations

import base64
from typing import Any, Callable, Optional, Sequence

from spokes_base import (AuthError, ChatMessage, ChatResult, NotSupported,
                         Spoke, Usage, UrllibTransport, assert_key_safe,
                         default_keyring, default_ledger, http_call,
                         iter_sse_json)

__all__ = ["AnthropicSpoke", "BASE_URL", "OFFICIAL_HOST"]

BASE_URL = "https://api.anthropic.com"
OFFICIAL_HOST = "api.anthropic.com"
ANTHROPIC_VERSION = "2023-06-01"

# The Messages API requires max_tokens; used when the caller passes none.
DEFAULT_MAX_TOKENS = 1024


class AnthropicSpoke(Spoke):
    provider_id = "anthropic"

    def __init__(self, api_key: Optional[str] = None, *,
                 keyring: Any = None,
                 ledger: Any = None,
                 record_usage: bool = True,
                 transport: Any = None,
                 timeout: float = 120.0,
                 default_chat_model: str = "claude-sonnet-4-20250514") -> None:
        self.timeout = timeout
        self.default_chat_model = default_chat_model
        self._transport = transport if transport is not None else UrllibTransport()

        if api_key is None:
            kr = keyring if keyring is not None else default_keyring()
            if kr is not None:
                api_key = kr.get_key(self.provider_id)
        self.api_key = (api_key or "").strip() or None
        if not self.api_key:
            raise AuthError(
                "no Anthropic API key found - set ANTHROPIC_API_KEY or run "
                "`python keyring.py set anthropic`", provider=self.provider_id)

        self.allowed_hosts = (OFFICIAL_HOST,)
        self._caps = frozenset({"chat", "chat_stream"})
        self._ledger = None
        if record_usage:
            self._ledger = ledger if ledger is not None else default_ledger()

    # -- plumbing -------------------------------------------------------------

    def _headers(self) -> dict:
        return {"Content-Type": "application/json",
                "User-Agent": "atelier-spoke/1",
                "x-api-key": self.api_key,
                "anthropic-version": ANTHROPIC_VERSION}

    def _post(self, path: str, payload: dict, *, stream: bool = False):
        url = f"{BASE_URL}{path}"
        assert_key_safe(url, self.allowed_hosts, self.provider_id)
        return http_call(self._transport, "POST", url, headers=self._headers(),
                         payload=payload, provider=self.provider_id,
                         timeout=self.timeout, stream=stream)

    @staticmethod
    def _wire_messages(messages: Sequence[ChatMessage]):
        system_parts, wire = [], []
        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.text())
                continue
            content = []
            for part in msg.parts():
                if part.kind == "text":
                    content.append({"type": "text", "text": part.text})
                elif part.kind == "image":
                    content.append({"type": "image", "source": {
                        "type": "base64", "media_type": part.mime,
                        "data": base64.b64encode(part.data).decode("ascii")}})
                else:
                    raise NotSupported(
                        f"unknown message part kind {part.kind!r}")
            wire.append({"role": msg.role, "content": content})
        return wire, "\n".join(p for p in system_parts if p)

    # -- chat -----------------------------------------------------------------

    def chat(self, messages: Sequence[ChatMessage], *,
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream_cb: Optional[Callable[[str], None]] = None,
             **extra: Any) -> ChatResult:
        model = model or self.default_chat_model
        wire, system = self._wire_messages(messages)
        payload: dict = {"model": model,
                         "max_tokens": max_tokens or DEFAULT_MAX_TOKENS,
                         "messages": wire}
        if system:
            payload["system"] = system
        if temperature is not None:
            payload["temperature"] = temperature
        payload.update(extra)
        if stream_cb is not None:
            return self._chat_stream(model, payload, stream_cb)

        data = self._post("/v1/messages", payload).json()
        text = "".join(block.get("text", "")
                       for block in data.get("content") or []
                       if block.get("type") == "text")
        raw_usage = data.get("usage") or {}
        usage = Usage(input_tokens=int(raw_usage.get("input_tokens") or 0),
                      output_tokens=int(raw_usage.get("output_tokens") or 0))
        self._record("chat", data.get("model") or model, usage,
                     meta={"stream": False})
        return ChatResult(text=text, model=data.get("model") or model,
                          provider=self.provider_id, usage=usage,
                          finish_reason=data.get("stop_reason") or "", raw=data)

    def _chat_stream(self, model: str, payload: dict,
                     stream_cb: Callable[[str], None]) -> ChatResult:
        payload = dict(payload, stream=True)
        resp = self._post("/v1/messages", payload, stream=True)
        pieces: list = []
        input_tokens = output_tokens = 0
        stop_reason, last_event = "", None
        for event in iter_sse_json(resp):
            last_event = event
            kind = event.get("type")
            if kind == "message_start":
                raw_usage = (event.get("message") or {}).get("usage") or {}
                input_tokens = int(raw_usage.get("input_tokens") or 0)
                output_tokens = int(raw_usage.get("output_tokens") or 0)
            elif kind == "content_block_delta":
                delta = event.get("delta") or {}
                if delta.get("type") == "text_delta" and delta.get("text"):
                    pieces.append(delta["text"])
                    stream_cb(delta["text"])
            elif kind == "message_delta":
                raw_usage = event.get("usage") or {}
                if raw_usage.get("output_tokens") is not None:
                    output_tokens = int(raw_usage["output_tokens"])
                delta = event.get("delta") or {}
                stop_reason = delta.get("stop_reason") or stop_reason
        text = "".join(pieces)
        usage = Usage(input_tokens=input_tokens, output_tokens=output_tokens)
        self._record("chat", model, usage, meta={"stream": True})
        return ChatResult(text=text, model=model, provider=self.provider_id,
                          usage=usage, finish_reason=stop_reason,
                          raw=last_event)
