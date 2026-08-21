"""Official Google Gemini API spoke. Host locked to generativelanguage.googleapis.com."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request

from atelier.helix.http import urlopen_no_redirect

from .base import ChatResult, ImageResult, Spoke, SpokeError, assert_official_host


class GeminiSpoke(Spoke):
    name = "gemini"

    def __init__(self, keyring):
        self.keyring = keyring

    def _key(self) -> str:
        key = self.keyring.get_secret("gemini")
        if not key:
            raise SpokeError(
                "Gemini key missing. Set GEMINI_API_KEY or add it in Atelier Settings. "
                "Create a key at aistudio.google.com — this spends your Google quota."
            )
        return key

    def _url(self, path: str) -> str:
        base = self.keyring.get_base_url("gemini") or "https://generativelanguage.googleapis.com"
        assert_official_host(base, ("generativelanguage.googleapis.com",), require_https=True)
        return f"{base}{path}"

    def _post(self, path: str, body: dict) -> dict:
        sep = "&" if "?" in path else "?"
        url = f"{self._url(path)}{sep}key={urllib.parse.quote(self._key())}"
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen_no_redirect(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise SpokeError(f"Gemini HTTP {exc.code}: {exc.read().decode()[:400]}") from exc

    def chat(self, messages: list[dict], model: str = "gemini-2.0-flash", **kwargs) -> ChatResult:
        contents = []
        system = ""
        for msg in messages:
            role = msg.get("role")
            if role == "system":
                system += msg.get("content") or ""
                continue
            contents.append(
                {
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": msg.get("content") or ""}],
                }
            )
        body = {"contents": contents, "generationConfig": {"temperature": kwargs.get("temperature", 0.4)}}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        data = self._post(f"/v1beta/models/{model}:generateContent", body)
        parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or []
        text = "".join(p.get("text") or "" for p in parts)
        usage = data.get("usageMetadata") or {}
        return ChatResult(
            text=text,
            provider="gemini",
            model=model,
            tokens_in=int(usage.get("promptTokenCount") or 0),
            tokens_out=int(usage.get("candidatesTokenCount") or 0),
            raw={},
        )

    def image(self, prompt: str, model: str = "gemini-2.5-flash-image", **kwargs) -> ImageResult:
        from atelier.helix.loom import style_lock

        prompt = style_lock(prompt, palette=kwargs.get("palette"), title=kwargs.get("title"))
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
        }
        data = self._post(f"/v1beta/models/{model}:generateContent", body)
        parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts")) or []
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data") or {}
            if inline.get("data"):
                raw = base64.b64decode(inline["data"])
                mime = inline.get("mimeType") or inline.get("mime_type") or "image/png"
                return ImageResult(data=raw, mime=mime, provider="gemini", model=model, prompt=prompt)
        raise SpokeError("Gemini image response contained no inline image data")
