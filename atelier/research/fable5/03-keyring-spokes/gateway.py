"""Atelier BYOK gateway hub: one entry point over all spokes.

The Gateway owns a shared Keyring (key resolution) and a shared Ledger
(usage accounting), builds spokes lazily on first use, and routes calls by
provider id:

    from gateway import Gateway
    from spokes_base import ChatMessage

    gw = Gateway()
    result = gw.chat("gemini", [ChatMessage("user", "Suggest a palette")])
    art = gw.generate_image("openai", "an atelier at dusk, gouache")
    print(gw.usage_summary())

Provider ids: openai | gemini | anthropic | ollama | openai_compatible.

Stdlib only. Python 3.9+.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from keyring import Keyring
from ledger import Ledger
from spokes_anthropic import AnthropicSpoke
from spokes_base import (ChatMessage, ChatResult, ImageResult, Spoke,
                         SpokeError, VideoResult)
from spokes_gemini import GeminiSpoke
from spokes_openai import OpenAISpoke, compatible_spoke, ollama_spoke

__all__ = ["Gateway", "PROVIDERS"]

PROVIDERS = ("openai", "gemini", "anthropic", "ollama", "openai_compatible")


class Gateway:
    def __init__(self, keyring: Optional[Keyring] = None,
                 ledger: Optional[Ledger] = None,
                 transport: Any = None) -> None:
        self.keyring = keyring if keyring is not None else Keyring()
        self.ledger = ledger if ledger is not None else Ledger()
        self._transport = transport
        self._spokes: Dict[str, Spoke] = {}

    # -- spoke construction/caching --------------------------------------------

    def spoke(self, provider_id: str) -> Spoke:
        provider_id = provider_id.strip().lower()
        if provider_id not in self._spokes:
            self._spokes[provider_id] = self._build(provider_id)
        return self._spokes[provider_id]

    def _build(self, provider_id: str) -> Spoke:
        common: Dict[str, Any] = {"keyring": self.keyring,
                                  "ledger": self.ledger}
        if self._transport is not None:
            common["transport"] = self._transport
        if provider_id == "openai":
            return OpenAISpoke(**common)
        if provider_id == "gemini":
            return GeminiSpoke(**common)
        if provider_id == "anthropic":
            return AnthropicSpoke(**common)
        if provider_id == "ollama":
            return ollama_spoke(**common)
        if provider_id == "openai_compatible":
            creds = self.keyring.get(provider_id)
            if not creds.base_url:
                raise SpokeError(
                    "openai_compatible needs a base_url - run `python "
                    "keyring.py set openai_compatible --base-url "
                    "https://your-endpoint/v1` (add --no-key for keyless "
                    "servers)", provider=provider_id)
            return compatible_spoke(creds.base_url, **common)
        raise SpokeError(f"unknown provider {provider_id!r}; expected one of "
                         f"{PROVIDERS}", provider=provider_id)

    # -- routed calls -----------------------------------------------------------

    def chat(self, provider_id: str, messages: Sequence[ChatMessage],
             **kwargs: Any) -> ChatResult:
        return self.spoke(provider_id).chat(messages, **kwargs)

    def generate_image(self, provider_id: str, prompt: str,
                       **kwargs: Any) -> ImageResult:
        return self.spoke(provider_id).generate_image(prompt, **kwargs)

    def generate_video(self, provider_id: str, prompt: str,
                       **kwargs: Any) -> VideoResult:
        return self.spoke(provider_id).generate_video(prompt, **kwargs)

    def capabilities(self, provider_id: str) -> frozenset:
        return self.spoke(provider_id).capabilities()

    # -- accounting --------------------------------------------------------------

    def usage_summary(self, since: Optional[float] = None) -> dict:
        return self.ledger.summary(since=since)
