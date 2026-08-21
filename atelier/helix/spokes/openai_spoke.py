"""Official OpenAI API spoke. Host locked to api.openai.com unless openai_compat."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request

from atelier.helix.http import urlopen_no_redirect

from .base import ChatResult, ImageResult, Spoke, SpokeError, assert_official_host


class OpenAISpoke(Spoke):
    def __init__(self, keyring, provider_name: str = "openai"):
        self.keyring = keyring
        self.name = provider_name

    def _headers(self) -> dict:
        key = self.keyring.get_secret(self.name)
        if not key:
            raise SpokeError(
                "OpenAI key missing. Set OPENAI_API_KEY or add it in Atelier Settings. "
                "Use a platform.openai.com API key — this spends your OpenAI quota, not Lovart credits."
            )
        return {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def _url(self, path: str) -> str:
        base = self.keyring.get_base_url(self.name) or "https://api.openai.com"
        if self.name == "openai":
            assert_official_host(base, ("api.openai.com",))
        return f"{base}{path}"

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self._url(path),
            data=json.dumps(body).encode(),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urlopen_no_redirect(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise SpokeError(f"OpenAI HTTP {exc.code}: {exc.read().decode()[:400]}") from exc

    def chat(self, messages: list[dict], model: str = "gpt-4o-mini", **kwargs) -> ChatResult:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.4),
        }
        data = self._post("/v1/chat/completions", payload)
        choice = (data.get("choices") or [{}])[0]
        text = ((choice.get("message") or {}).get("content")) or ""
        usage = data.get("usage") or {}
        return ChatResult(
            text=text,
            provider=self.name,
            model=data.get("model", model),
            tokens_in=int(usage.get("prompt_tokens") or 0),
            tokens_out=int(usage.get("completion_tokens") or 0),
            raw={"id": data.get("id")},
        )

    def image(self, prompt: str, model: str = "gpt-image-1", **kwargs) -> ImageResult:
        from atelier.helix.loom import style_lock

        prompt = style_lock(prompt, palette=kwargs.get("palette"), title=kwargs.get("title"))
        size = kwargs.get("size", "1024x1024")
        # gpt-image-1 and dall-e-3 share the images generations endpoint.
        body = {"model": model, "prompt": prompt, "n": 1, "size": size}
        if model.startswith("dall-e"):
            body["response_format"] = "b64_json"
        data = self._post("/v1/images/generations", body)
        item = (data.get("data") or [{}])[0]
        if item.get("b64_json"):
            raw = base64.b64decode(item["b64_json"])
            mime = "image/png"
        elif item.get("url"):
            raw, mime = _download(item["url"])
        else:
            raise SpokeError("OpenAI image response had no b64_json or url")
        return ImageResult(data=raw, mime=mime, provider=self.name, model=model, prompt=prompt)


def _download(url: str) -> tuple[bytes, str]:
    from urllib.parse import urlparse

    from atelier.helix.http import urlopen_no_redirect

    scheme = (urlparse(url).scheme or "").lower()
    if scheme != "https":
        raise SpokeError(f"Refusing non-https image URL ({scheme or 'missing'})")
    req = urllib.request.Request(url, headers={"User-Agent": "AtelierHelix/1.0"})
    with urlopen_no_redirect(req, timeout=120) as resp:
        mime = resp.headers.get("Content-Type", "image/png").split(";")[0]
        return resp.read(), mime
