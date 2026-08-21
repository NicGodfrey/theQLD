"""Google Gemini spoke for Atelier — official Generative Language API only.

Endpoints (all pinned to generativelanguage.googleapis.com):
  * chat        POST /v1beta/models/{model}:generateContent
  * chat stream POST /v1beta/models/{model}:streamGenerateContent?alt=sse
  * image       POST /v1beta/models/{model}:generateContent
                (native image output, e.g. gemini-2.5-flash-image), or
                POST /v1beta/models/{model}:predict for imagen-* models
  * video       contract stub (Veo would go through :predictLongRunning;
                see CONTRACT.md §Video)

Auth is the user's own API key in the ``x-goog-api-key`` header — the
documented mechanism for AI Studio keys. No OAuth dance, no scraping.

Stdlib only (urllib via spokes_base). Python 3.9+.
"""
from __future__ import annotations

import base64
from typing import Any, Callable, Optional, Sequence, Tuple

from spokes_base import (AuthError, ChatMessage, ChatResult, ImageResult,
                         NotSupported, ProviderError, Spoke, Usage,
                         UrllibTransport, assert_key_safe, default_keyring,
                         default_ledger, http_call, iter_sse_json)

__all__ = ["GeminiSpoke", "BASE_URL", "OFFICIAL_HOST"]

BASE_URL = "https://generativelanguage.googleapis.com"
OFFICIAL_HOST = "generativelanguage.googleapis.com"


def _aspect_from_size(size: str) -> Optional[str]:
    """Best-effort map of a WIDTHxHEIGHT size onto Gemini aspect ratios."""
    try:
        width, height = (int(x) for x in size.lower().split("x"))
    except (ValueError, AttributeError):
        return None
    if width <= 0 or height <= 0:
        return None
    if width == height:
        return "1:1"
    ratio = width / height
    table = {16 / 9: "16:9", 9 / 16: "9:16", 4 / 3: "4:3", 3 / 4: "3:4"}
    best = min(table, key=lambda r: abs(r - ratio))
    return table[best]


class GeminiSpoke(Spoke):
    """Chat (+streaming) and image generation on Google's official API."""

    provider_id = "gemini"

    def __init__(self, api_key: Optional[str] = None, *,
                 keyring: Any = None,
                 ledger: Any = None,
                 record_usage: bool = True,
                 transport: Any = None,
                 timeout: float = 180.0,
                 api_version: str = "v1beta",
                 default_chat_model: str = "gemini-2.5-flash",
                 default_image_model: str = "gemini-2.5-flash-image") -> None:
        self.timeout = timeout
        self.api_version = api_version
        self.default_chat_model = default_chat_model
        self.default_image_model = default_image_model
        self._transport = transport if transport is not None else UrllibTransport()

        if api_key is None:
            kr = keyring if keyring is not None else default_keyring()
            if kr is not None:
                api_key = kr.get_key(self.provider_id)
        self.api_key = (api_key or "").strip() or None
        if not self.api_key:
            raise AuthError(
                "no Gemini API key found - set GEMINI_API_KEY (or "
                "GOOGLE_API_KEY) or run `python keyring.py set gemini`",
                provider=self.provider_id)

        self.allowed_hosts = (OFFICIAL_HOST,)
        self._caps = frozenset({"chat", "chat_stream", "image"})
        self._ledger = None
        if record_usage:
            self._ledger = ledger if ledger is not None else default_ledger()

    # -- plumbing -------------------------------------------------------------

    def _url(self, model: str, verb: str) -> str:
        model = model.rsplit("/", 1)[-1]          # accept "models/gemini-..."
        return f"{BASE_URL}/{self.api_version}/models/{model}:{verb}"

    def _headers(self) -> dict:
        return {"Content-Type": "application/json",
                "User-Agent": "atelier-spoke/1",
                "x-goog-api-key": self.api_key}

    def _post(self, url: str, payload: dict, *, stream: bool = False):
        assert_key_safe(url, self.allowed_hosts, self.provider_id)
        return http_call(self._transport, "POST", url, headers=self._headers(),
                         payload=payload, provider=self.provider_id,
                         timeout=self.timeout, stream=stream)

    @staticmethod
    def _wire_contents(messages: Sequence[ChatMessage]) -> Tuple[list, str]:
        """Split provider-neutral messages into Gemini contents + a single
        merged system instruction."""
        system_parts, contents = [], []
        for msg in messages:
            if msg.role == "system":
                system_parts.append(msg.text())
                continue
            role = "model" if msg.role == "assistant" else "user"
            parts = []
            for part in msg.parts():
                if part.kind == "text":
                    parts.append({"text": part.text})
                elif part.kind == "image":
                    parts.append({"inlineData": {
                        "mimeType": part.mime,
                        "data": base64.b64encode(part.data).decode("ascii")}})
                else:
                    raise NotSupported(
                        f"unknown message part kind {part.kind!r}")
            contents.append({"role": role, "parts": parts})
        return contents, "\n".join(p for p in system_parts if p)

    @staticmethod
    def _usage_from(meta: Optional[dict]) -> Usage:
        meta = meta or {}
        output = (int(meta.get("candidatesTokenCount") or 0)
                  + int(meta.get("thoughtsTokenCount") or 0))
        return Usage(input_tokens=int(meta.get("promptTokenCount") or 0),
                     output_tokens=output)

    def _candidate_parts(self, data: dict) -> list:
        candidates = data.get("candidates") or []
        if not candidates:
            feedback = data.get("promptFeedback") or {}
            raise ProviderError(
                f"gemini: empty response "
                f"(blockReason={feedback.get('blockReason')!r})",
                provider=self.provider_id)
        content = candidates[0].get("content") or {}
        return content.get("parts") or []

    # -- chat -----------------------------------------------------------------

    def chat(self, messages: Sequence[ChatMessage], *,
             model: Optional[str] = None,
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None,
             stream_cb: Optional[Callable[[str], None]] = None,
             **extra: Any) -> ChatResult:
        model = (model or self.default_chat_model).rsplit("/", 1)[-1]
        contents, system = self._wire_contents(messages)
        payload: dict = {"contents": contents}
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        generation_config = dict(extra.pop("generation_config", None) or {})
        if temperature is not None:
            generation_config.setdefault("temperature", temperature)
        if max_tokens is not None:
            generation_config.setdefault("maxOutputTokens", max_tokens)
        if generation_config:
            payload["generationConfig"] = generation_config
        payload.update(extra)

        if stream_cb is not None:
            return self._chat_stream(model, payload, stream_cb)

        data = self._post(self._url(model, "generateContent"), payload).json()
        parts = self._candidate_parts(data)
        text = "".join(p.get("text", "") for p in parts if "text" in p)
        finish = (data["candidates"][0].get("finishReason") or "")
        usage = self._usage_from(data.get("usageMetadata"))
        self._record("chat", model, usage, meta={"stream": False})
        return ChatResult(text=text, model=model, provider=self.provider_id,
                          usage=usage, finish_reason=finish, raw=data)

    def _chat_stream(self, model: str, payload: dict,
                     stream_cb: Callable[[str], None]) -> ChatResult:
        url = self._url(model, "streamGenerateContent") + "?alt=sse"
        resp = self._post(url, payload, stream=True)
        pieces: list = []
        finish, usage_raw, last_event = "", None, None
        for event in iter_sse_json(resp):
            last_event = event
            if event.get("usageMetadata"):
                usage_raw = event["usageMetadata"]   # cumulative; keep last
            for candidate in event.get("candidates") or []:
                content = candidate.get("content") or {}
                for part in content.get("parts") or []:
                    text = part.get("text")
                    if text:
                        pieces.append(text)
                        stream_cb(text)
                if candidate.get("finishReason"):
                    finish = candidate["finishReason"]
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
        model = (model or self.default_image_model).rsplit("/", 1)[-1]
        if model.startswith("imagen"):
            return self._imagen_predict(model, prompt, size=size, n=n,
                                        quality=quality, **extra)

        # Native Gemini image output (e.g. gemini-2.5-flash-image): one
        # image per generateContent call, so n > 1 loops.
        payload: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        aspect = extra.pop("aspect_ratio", None) or _aspect_from_size(size)
        if aspect:
            payload["generationConfig"]["imageConfig"] = {"aspectRatio": aspect}
        payload.update(extra)

        images, texts, raws = [], [], []
        mime = "image/png"
        usage = Usage()
        for _ in range(max(1, n)):
            data = self._post(self._url(model, "generateContent"), payload).json()
            raws.append(data)
            got_image = False
            for part in self._candidate_parts(data):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    images.append(base64.b64decode(inline["data"]))
                    mime = (inline.get("mimeType") or inline.get("mime_type")
                            or mime)
                    got_image = True
                elif part.get("text"):
                    texts.append(part["text"])
            if not got_image:
                raise ProviderError(
                    "gemini: model returned no image data (is "
                    f"{model!r} an image-capable model?)",
                    provider=self.provider_id)
            call_usage = self._usage_from(data.get("usageMetadata"))
            usage.input_tokens += call_usage.input_tokens
            usage.output_tokens += call_usage.output_tokens
        self._record("image", model, usage, images=len(images), size=size,
                     quality=quality or "")
        return ImageResult(images=images, mime=mime, model=model,
                           provider=self.provider_id, usage=usage,
                           text="\n".join(texts),
                           raw=raws[0] if len(raws) == 1 else raws)

    def _imagen_predict(self, model: str, prompt: str, *, size: str, n: int,
                        quality: Optional[str], **extra: Any) -> ImageResult:
        parameters: dict = {"sampleCount": max(1, n)}
        aspect = extra.pop("aspect_ratio", None) or _aspect_from_size(size)
        if aspect:
            parameters["aspectRatio"] = aspect
        parameters.update(extra.pop("parameters", None) or {})
        payload = {"instances": [{"prompt": prompt}], "parameters": parameters}

        data = self._post(self._url(model, "predict"), payload).json()
        images, mime = [], "image/png"
        for prediction in data.get("predictions") or []:
            b64 = prediction.get("bytesBase64Encoded")
            if b64:
                images.append(base64.b64decode(b64))
                mime = prediction.get("mimeType") or mime
        if not images:
            raise ProviderError("gemini: Imagen returned no predictions",
                                provider=self.provider_id)
        usage = Usage()   # Imagen predict does not report token usage
        self._record("image", model, usage, images=len(images), size=size,
                     quality=quality or "")
        return ImageResult(images=images, mime=mime, model=model,
                           provider=self.provider_id, usage=usage, raw=data)
