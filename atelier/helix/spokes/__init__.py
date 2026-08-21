from .base import Spoke, SpokeError, ChatResult, ImageResult
from .openai_spoke import OpenAISpoke
from .gemini_spoke import GeminiSpoke
from .ollama_spoke import OllamaSpoke

__all__ = [
    "Spoke",
    "SpokeError",
    "ChatResult",
    "ImageResult",
    "OpenAISpoke",
    "GeminiSpoke",
    "OllamaSpoke",
    "build_spoke",
]


def build_spoke(provider: str, keyring) -> Spoke:
    provider = (provider or "demo").lower()
    if provider == "openai":
        return OpenAISpoke(keyring)
    if provider == "gemini":
        return GeminiSpoke(keyring)
    if provider == "ollama":
        return OllamaSpoke(keyring)
    if provider in {"openai_compat", "compat"}:
        return OpenAISpoke(keyring, provider_name="openai_compat")
    from .base import DemoSpoke

    return DemoSpoke()
