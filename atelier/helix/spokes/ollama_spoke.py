"""Local Ollama spoke. Host locked to localhost / 127.0.0.1."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from atelier.helix.http import urlopen_no_redirect

from .base import ChatResult, ImageResult, Spoke, SpokeError, assert_official_host


class OllamaSpoke(Spoke):
    name = "ollama"

    def __init__(self, keyring):
        self.keyring = keyring

    def _url(self, path: str) -> str:
        base = self.keyring.get_base_url("ollama") or "http://127.0.0.1:11434"
        assert_official_host(base, ("127.0.0.1", "localhost"))
        return f"{base}{path}"

    def _post(self, path: str, body: dict) -> dict:
        req = urllib.request.Request(
            self._url(path),
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen_no_redirect(req, timeout=180) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise SpokeError(f"Ollama HTTP {exc.code}: {exc.read().decode()[:400]}") from exc
        except urllib.error.URLError as exc:
            raise SpokeError(f"Ollama unreachable: {exc}") from exc

    def chat(self, messages: list[dict], model: str = "llama3.2", **kwargs) -> ChatResult:
        data = self._post("/api/chat", {"model": model, "messages": messages, "stream": False})
        text = ((data.get("message") or {}).get("content")) or ""
        return ChatResult(text=text, provider="ollama", model=model, tokens_in=0, tokens_out=0)

    def image(self, prompt: str, model: str = "llama3.2", **kwargs) -> ImageResult:
        raise SpokeError("Ollama image generation is not wired; use OpenAI or Gemini, or demo mode")
