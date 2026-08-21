"""Atelier LLM gateway — LiteLLM *patterns* without the LiteLLM dependency.

Patterns adopted (see ADAPTERS.md #1):
  * one `complete()` signature for every provider
  * the OpenAI chat-completions HTTP schema as the universal wire format
  * router with model aliases, ordered fallbacks, retry/backoff, cooldowns
  * cost accounting at the single choke point

Stdlib only. Swapping in the real `litellm` package later means adding a
``LiteLLMProvider`` that satisfies the same ``Provider`` protocol; callers do
not change.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol

Message = dict[str, str]  # {"role": "...", "content": "..."}


@dataclass
class CompletionResult:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    raw: dict | None = None


class Provider(Protocol):
    """Anything that can answer a chat completion. The only seam that matters."""

    def complete(
        self,
        model: str,
        messages: list[Message],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> CompletionResult: ...


class OpenAICompatProvider:
    """Speaks POST {base_url}/chat/completions.

    Covers OpenAI, Azure OpenAI, Ollama, vLLM, OpenRouter, LM Studio, a LiteLLM
    proxy, and Anthropic/Gemini via their OpenAI-compatible endpoints.
    """

    def __init__(self, base_url: str, api_key: str = "", timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def complete(
        self,
        model: str,
        messages: list[Message],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> CompletionResult:
        body: dict = {"model": model, "messages": messages, "temperature": temperature}
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if response_format is not None:
            body["response_format"] = response_format

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read())

        usage = data.get("usage") or {}
        return CompletionResult(
            text=data["choices"][0]["message"]["content"] or "",
            model=data.get("model", model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            raw=data,
        )


@dataclass
class Deployment:
    """One concrete (provider, model) pair a logical alias can resolve to."""

    provider: Provider
    model: str
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0


RETRYABLE_HTTP = {408, 409, 429, 500, 502, 503, 504}


@dataclass
class Router:
    """LiteLLM-style router: alias -> ordered fallback list of deployments.

    Retries transient HTTP errors with exponential backoff, puts failing
    deployments on cooldown, and reports spend through ``on_usage``.
    """

    routes: dict[str, list[Deployment]]
    max_retries: int = 2
    cooldown_s: float = 60.0
    on_usage: "callable | None" = None  # fn(alias, deployment, result, cost_usd)
    _cooldowns: dict[int, float] = field(default_factory=dict)

    def complete(self, alias: str, messages: list[Message], **kw) -> CompletionResult:
        deployments = self.routes.get(alias)
        if not deployments:
            raise KeyError(f"no route for alias {alias!r}")

        last_error: Exception | None = None
        now = time.monotonic()
        for dep in deployments:
            if self._cooldowns.get(id(dep), 0.0) > now:
                continue
            for attempt in range(self.max_retries + 1):
                try:
                    result = dep.provider.complete(dep.model, messages, **kw)
                    self._record(alias, dep, result)
                    return result
                except urllib.error.HTTPError as e:
                    last_error = e
                    if e.code not in RETRYABLE_HTTP:
                        break  # non-transient: fall through to next deployment
                    time.sleep(min(2**attempt, 8))
                except (urllib.error.URLError, TimeoutError) as e:
                    last_error = e
                    time.sleep(min(2**attempt, 8))
            self._cooldowns[id(dep)] = time.monotonic() + self.cooldown_s
        raise RuntimeError(f"all deployments failed for {alias!r}") from last_error

    def _record(self, alias: str, dep: Deployment, result: CompletionResult) -> None:
        if self.on_usage is None:
            return
        cost = (
            result.prompt_tokens / 1000 * dep.input_cost_per_1k
            + result.completion_tokens / 1000 * dep.output_cost_per_1k
        )
        self.on_usage(alias, dep, result, cost)


if __name__ == "__main__":
    # Wiring example: "planner" falls back from a hosted model to local Ollama.
    import os

    router = Router(
        routes={
            "planner": [
                Deployment(
                    OpenAICompatProvider(
                        "https://api.openai.com/v1", os.environ.get("OPENAI_API_KEY", "")
                    ),
                    model="gpt-4o-mini",
                    input_cost_per_1k=0.00015,
                    output_cost_per_1k=0.0006,
                ),
                Deployment(
                    OpenAICompatProvider("http://localhost:11434/v1"),
                    model="llama3.1",
                ),
            ]
        },
        on_usage=lambda alias, dep, res, cost: print(
            f"[usage] {alias} via {dep.model}: {res.prompt_tokens}+{res.completion_tokens} tok, ${cost:.5f}"
        ),
    )
    print(router.complete("planner", [{"role": "user", "content": "Say hi in 3 words."}]).text)
