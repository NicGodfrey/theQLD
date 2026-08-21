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
    "KNOWN_PROVIDERS",
    "build_spoke",
]


KNOWN_PROVIDERS = frozenset(
    {"demo", "openai", "gemini", "ollama", "openai_compat", "compat"}
)


def build_spoke(provider: str, keyring) -> Spoke:
    provider = (provider or "demo").strip().lower()
    if provider in {"", "demo"}:
        from .base import DemoSpoke

        return DemoSpoke()
    if provider == "openai":
        return OpenAISpoke(keyring)
    if provider == "gemini":
        return GeminiSpoke(keyring)
    if provider == "ollama":
        return OllamaSpoke(keyring)
    if provider in {"openai_compat", "compat"}:
        return OpenAISpoke(keyring, provider_name="openai_compat")
    raise SpokeError(f"Unknown provider {provider!r}")
